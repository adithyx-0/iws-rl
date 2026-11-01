"""
IWSEnv: equity-aware intermittent water supply scheduling on a bundled EPANET network.

Hydraulics: EPANET (via WNTR) pressure-dependent demand (PDD) snapshot every hour.
Each decision step = 1 hour. Episode = n_days days.

Model (all parameters below are assumptions to be justified / swept in the report):
- Demand junctions are grouped into Z zones by location (k-means on coordinates).
- Action: which zones are open this hour (Z-bit vector, encoded as one Discrete int).
  A closed zone = consumers in that zone are cut off (their demand set to 0); mains stay live.
- Each demand junction j aggregates households with a roof tank of capacity S_j.
  Households consume c_j(t) from their tank every hour (diurnal pattern).
  When the zone is open, node j requests q_req = min(alpha*qbar_j, refill_need/3600 + c_j)
  (the "tank-filling surge"); EPANET PDD returns the delivered flow q_del <= q_req.
- Daily source budget V_d = s_d * (total daily consumption), s_d ~ U[s_lo, s_hi],
  announced one day ahead. Once the day's budget is used, no zone can draw water.
- The agent does NOT see household tank levels (utility cannot observe them):
  it sees zone pressure, zone inflow, zone supply ratio so far today, hours since last
  supply, hour of day, remaining budget, tomorrow's budget, network tank levels.
- Reward per hour: -(unmet consumption this hour) / (mean hourly consumption).
  End of each day: + lam * (min over zones of daily supply ratio) * 24  (equity term).
"""
import os, glob, tempfile, uuid, warnings
import numpy as np
import gymnasium as gym
from gymnasium import spaces
import wntr

warnings.filterwarnings("ignore")

DIURNAL = np.array([0.4, 0.3, 0.3, 0.3, 0.5, 1.0, 1.6, 1.8, 1.5, 1.2, 1.0, 1.0,
                    1.1, 1.0, 0.9, 0.9, 1.0, 1.3, 1.6, 1.5, 1.2, 0.9, 0.7, 0.5])
DIURNAL = DIURNAL / DIURNAL.mean()


def _net_path(name):
    d = os.path.dirname(wntr.__file__)
    return [p for p in glob.glob(d + "/**/" + name, recursive=True)][0]


def _kmeans(X, k, rng, iters=50):
    C = X[rng.choice(len(X), k, replace=False)]
    for _ in range(iters):
        lab = np.argmin(((X[:, None, :] - C[None]) ** 2).sum(-1), 1)
        newC = np.array([X[lab == i].mean(0) if (lab == i).any() else C[i] for i in range(k)])
        if np.allclose(newC, C):
            break
        C = newC
    return lab


class IWSEnv(gym.Env):
    metadata = {"render_modes": []}

    def __init__(self, network="Net3.inp", n_zones=4, n_days=3,
                 supply_range=(0.5, 0.9), tank_days=(0.3, 0.8), alpha=4.0,
                 required_pressure=20.0, minimum_pressure=2.0,
                 lam=1.0, equity_reward=True, forecast=True, demand_noise=0.1,
                 zone_seed=0):
        super().__init__()
        self.Z, self.n_days = n_zones, n_days
        self.H = 24 * n_days
        self.supply_range, self.tank_days, self.alpha = supply_range, tank_days, alpha
        self.lam, self.equity_reward, self.forecast = lam, equity_reward, forecast
        self.demand_noise = demand_noise

        wn = wntr.network.WaterNetworkModel(_net_path(network))
        for c in list(wn.control_name_list):
            wn.remove_control(c)
        wn.options.time.duration = 0
        wn.options.hydraulic.demand_model = "PDD"
        wn.options.hydraulic.required_pressure = required_pressure
        wn.options.hydraulic.minimum_pressure = minimum_pressure
        self.wn = wn

        # demand junctions and their base demand
        jn, qb, xy = [], [], []
        for j in wn.junction_name_list:
            node = wn.get_node(j)
            b = node.demand_timeseries_list[0].base_value if node.demand_timeseries_list else 0.0
            if b > 0:
                jn.append(j); qb.append(b); xy.append(node.coordinates)
                node.demand_timeseries_list[0].pattern_name = None   # we set demand each hour ourselves
        self.jn = jn
        self.qbar = np.array(qb)                         # m3/s mean consumption
        xy = np.array(xy, float)
        xy = (xy - xy.mean(0)) / xy.std(0)
        self.zone = _kmeans(xy, n_zones, np.random.default_rng(zone_seed))
        self.zone_masks = [self.zone == z for z in range(n_zones)]
        self.J = len(jn)
        self.tank_names = wn.tank_name_list
        self.tank_init = {t: wn.get_node(t).init_level for t in self.tank_names}
        self.day_volume = self.qbar.sum() * 86400.0      # m3/day of consumption

        self._prefix = os.path.join(tempfile.gettempdir(), "iws_" + uuid.uuid4().hex[:8])
        self.action_space = spaces.Discrete(2 ** n_zones)
        self.obs_dim = 4 * n_zones + 5 + len(self.tank_names)
        self.observation_space = spaces.Box(-1.0, 5.0, (self.obs_dim,), np.float32)

    # ---------- helpers ----------
    def decode(self, a):
        return np.array([(int(a) >> z) & 1 for z in range(self.Z)], bool)

    def _hydraulics(self, q_req):
        for j, q in zip(self.jn, q_req):
            self.wn.get_node(j).demand_timeseries_list[0].base_value = float(q)
        for t in self.tank_names:
            self.wn.get_node(t).init_level = float(self.tank_lvl[t])
        res = wntr.sim.EpanetSimulator(self.wn).run_sim(file_prefix=self._prefix)
        dem = res.node["demand"].iloc[0]
        prs = res.node["pressure"].iloc[0]
        q_del = np.clip(dem[self.jn].values, 0, None)
        p = prs[self.jn].values
        # carry network tank levels forward one hour (EPANET demand at tank = net inflow)
        for t in self.tank_names:
            node = self.wn.get_node(t)
            area = np.pi * node.diameter ** 2 / 4
            lvl = self.tank_lvl[t] + dem[t] * 3600.0 / area
            self.tank_lvl[t] = float(np.clip(lvl, node.min_level + 0.1, node.max_level - 0.05))
        return q_del, p

    def _obs(self):
        o = []
        for z, m in enumerate(self.zone_masks):
            o += [np.clip(self.last_p[m].mean() / 40.0, -1, 5),
                  self.last_inflow_z[z],
                  self.day_served[m].sum() / max(self.day_desired[m].sum(), 1e-9),
                  min(self.hours_since[z] / 24.0, 5.0)]
        h = self.t % 24
        rem = max(self.budget_today - self.used_today, 0) / self.day_volume
        tom = self.budgets[min(self.t // 24 + 1, self.n_days - 1)] / self.day_volume if self.forecast else 0.0
        o += [np.sin(2 * np.pi * h / 24), np.cos(2 * np.pi * h / 24), rem, tom, self.t / self.H]
        for t in self.tank_names:
            node = self.wn.get_node(t)
            o.append(self.tank_lvl[t] / node.max_level)
        return np.array(o, np.float32)

    # ---------- gym API ----------
    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        r = self.np_random
        self.S = self.qbar * 86400.0 * r.uniform(*self.tank_days, self.J)   # roof tank capacity m3
        self.L = self.S * r.uniform(0.2, 0.6, self.J)                       # initial storage
        self.node_scale = np.clip(1 + self.demand_noise * r.standard_normal(self.J), 0.5, 1.5)
        self.budgets = self.day_volume * r.uniform(*self.supply_range, self.n_days)
        self.tank_lvl = dict(self.tank_init)
        self.t = 0
        self.last_p = np.zeros(self.J)
        self.last_inflow_z = np.zeros(self.Z)
        self.hours_since = np.zeros(self.Z)
        self._new_day()
        self.log = {"served": np.zeros(self.J), "desired": np.zeros(self.J), "daily_min_zone_sr": [],
                    "daily_zone_sr": [], "delivered": 0.0}
        return self._obs(), {}

    def _new_day(self):
        self.budget_today = self.budgets[self.t // 24]
        self.used_today = 0.0
        self.day_served = np.zeros(self.J)
        self.day_desired = np.zeros(self.J)

    def step(self, action):
        open_z = self.decode(action)
        h = self.t % 24
        c = self.qbar * self.node_scale * DIURNAL[h]          # consumption this hour (m3/s)
        open_j = open_z[self.zone]
        need = np.clip(self.S - self.L, 0, None) / 3600.0 + c
        q_req = np.where(open_j, np.minimum(self.alpha * self.qbar, need), 0.0)
        # source budget: scale requests if they would exceed what is left today
        left = max(self.budget_today - self.used_today, 0.0)
        if q_req.sum() * 3600.0 > left:
            q_req *= left / (q_req.sum() * 3600.0 + 1e-12)
        if q_req.sum() > 0:
            q_del, p = self._hydraulics(q_req)
        else:
            q_del, p = np.zeros(self.J), np.zeros(self.J)
        q_del = np.minimum(q_del, q_req)
        vin = q_del * 3600.0
        self.used_today += vin.sum()
        # household tank balance
        self.L = self.L + vin
        overflow = np.clip(self.L - self.S, 0, None)
        self.L -= overflow
        want = c * 3600.0
        served = np.minimum(self.L, want)
        self.L -= served
        unmet = want - served
        self.day_served += served; self.day_desired += want
        self.log["served"] += served; self.log["desired"] += want; self.log["delivered"] += vin.sum()

        self.last_p = np.where(open_j, p, 0.0)
        self.last_inflow_z = np.array([vin[m].sum() for m in self.zone_masks]) / (self.day_volume / 24)
        self.hours_since = np.where(open_z & (np.array([vin[m].sum() for m in self.zone_masks]) > 0),
                                    0, self.hours_since + 1)

        reward = -unmet.sum() / (self.day_volume / 24)
        self.t += 1
        info = {}
        if self.t % 24 == 0:
            zsr = np.array([self.day_served[m].sum() / self.day_desired[m].sum() for m in self.zone_masks])
            self.log["daily_zone_sr"].append(zsr)
            self.log["daily_min_zone_sr"].append(zsr.min())
            if self.equity_reward:
                reward += self.lam * zsr.min() * 24 / self.Z
            if self.t < self.H:
                self._new_day()
        terminated = self.t >= self.H
        if terminated:
            info = self.metrics()
        return self._obs(), float(reward), terminated, False, info

    def metrics(self):
        sr_node = self.log["served"] / self.log["desired"]
        sr_zone = np.array([self.log["served"][m].sum() / self.log["desired"][m].sum() for m in self.zone_masks])
        s = np.sort(sr_node); n = len(s)
        gini = (2 * np.arange(1, n + 1) - n - 1).dot(s) / (n * s.sum() + 1e-12)
        return {"mean_sr": float(self.log["served"].sum() / self.log["desired"].sum()),
                "min_zone_sr": float(sr_zone.min()), "zone_sr": sr_zone.round(3).tolist(),
                "gini_node": float(gini), "p10_node_sr": float(np.percentile(sr_node, 10)),
                "budget_used": float(self.log["delivered"] / self.budgets.sum())}


if __name__ == "__main__":
    from gymnasium.utils.env_checker import check_env
    import time
    env = IWSEnv()
    check_env(env, skip_render_check=True)
    print("check_env passed | obs", env.observation_space.shape, "actions", env.action_space.n,
          "| demand junctions", env.J, "| zone sizes", [int(m.sum()) for m in env.zone_masks])
    obs, _ = env.reset(seed=0); t0 = time.time(); done = False
    while not done:
        obs, r, done, _, info = env.step(env.action_space.n - 1)   # all zones open
    print("all-open episode: %.2fs" % (time.time() - t0), info)
