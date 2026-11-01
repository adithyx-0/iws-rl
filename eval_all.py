"""Evaluate all baselines and trained models under several conditions.
Usage: python eval_all.py   -> results/episodes.csv (one row per episode), results/summary.csv, results/paired_vs_greedy.csv
Test scenarios: seeds 10000+ (default condition: 100 scenarios, other conditions: 50)."""
import os, glob, time, warnings
warnings.filterwarnings("ignore")
from multiprocessing import Pool
import numpy as np
import pandas as pd
import torch
torch.set_num_threads(1)
from stable_baselines3 import PPO, DQN, A2C
from iws_env import IWSEnv
from v2cfg import BASE, MODELS, RES
from baselines import all_open, random_policy, make_rota, make_greedy

CONDITIONS = {   # name: (env kwargs, n scenarios)
    "default":      ({}, 100),
    "scarce":       ({"supply_range": (0.3, 0.5)}, 50),
    "abundant":     ({"supply_range": (0.7, 1.0)}, 50),
    "small_tanks":  ({"tank_days": (0.1, 0.3)}, 50),
    "large_tanks":  ({"tank_days": (0.8, 1.5)}, 50),
    "noisy_demand": ({"demand_noise": 0.3}, 50),
    "five_days":    ({"n_days": 5}, 50),
    "alpha2":       ({"alpha": 2.0}, 50),
    "alpha8":       ({"alpha": 8.0}, 50),
    "press10":      ({"required_pressure": 10.0}, 50),
    "press30":      ({"required_pressure": 30.0}, 50),
}
METRICS = ["return", "mean_sr", "min_zone_sr", "p10_node_sr", "gini_node", "jain_zone", "ceiling"]


def priv_greedy(env, obs):
    """PRIVILEGED heuristic: reads the hidden household tank levels (the utility cannot). Opens the zone whose tanks are emptiest."""
    fill = np.array([env.L[m].sum() / env.S[m].sum() for m in env.zone_masks])
    return 1 << int(np.argmin(fill))


def ce_schedule(env, obs):
    S = np.load(f"{RES}/ce_schedule.npy"); h = env.t % 24
    return int(sum(int(b) << z for z, b in enumerate(S[h])))


def baseline_policy(name):
    return {"random": random_policy, "all_open": all_open, "rota_k1": make_rota(1), "greedy_k1": make_greedy(1),
            "greedy_k2": make_greedy(2), "priv_greedy_k1": priv_greedy, "ce_schedule": ce_schedule}[name]


class RecPolicy:
    """Stateful wrapper for sb3-contrib RecurrentPPO (LSTM state carried within an episode)."""
    def __init__(self, model): self.m = model; self.reset()
    def reset(self): self.s = None; self.start = np.ones((1,), bool)
    def __call__(self, env, obs):
        a, self.s = self.m.predict(obs, state=self.s, episode_start=self.start, deterministic=True); self.start = np.zeros((1,), bool); return int(a)


def load_model(path):
    b = os.path.basename(path)
    if b.startswith("rec"):
        from sb3_contrib import RecurrentPPO
        return RecurrentPPO.load(path, device="cpu")
    return (DQN if b.startswith("dqn") else A2C if b.startswith("a2c") else PPO).load(path, device="cpu")


def run_job(job):
    method, path, cond = job
    kw, n = CONDITIONS[cond]
    kw = {**BASE, **kw}
    if "noforecast" in method:
        kw["forecast"] = False          # this policy was trained without the tomorrow-budget feature
    env = IWSEnv(**kw)
    if path:
        model = load_model(path)
        if os.path.basename(path).startswith("rec"): pol = RecPolicy(model)
        else: pol = lambda e, o: int(model.predict(o, deterministic=True)[0])
    else:
        pol = baseline_policy(method)
    rows = []
    for s in range(10000, 10000 + n):
        obs, _ = env.reset(seed=s); done = False; R = 0.0; steps = 0; t0 = time.perf_counter()
        if hasattr(pol, "reset"): pol.reset()
        while not done:
            obs, r, done, _, info = env.step(pol(env, obs)); R += r; steps += 1
        info["return"] = R
        rows.append({"method": method, "condition": cond, "scenario": s,
                     "ms_per_step": (time.perf_counter() - t0) / steps * 1000, **{k: info[k] for k in METRICS}})
    return rows


def methods():
    m = [(b, None) for b in ["random", "all_open", "rota_k1", "greedy_k1", "greedy_k2", "priv_greedy_k1", "ce_schedule"]]
    if not BASE: m.append(("ppo_s0", "ppo_iws_s0.zip"))                      # shipped model
    for p in sorted(glob.glob(f"{MODELS}/*.zip")):
        m.append((os.path.basename(p)[:-4], p))
    return m


def family(method):
    return method.rsplit("_s", 1)[0] if "_s" in method and method.rsplit("_s", 1)[1].isdigit() else method


def boot_ci(x, rng, B=2000):
    x = np.asarray(x); idx = rng.integers(0, len(x), (B, len(x)))
    m = x[idx].mean(1); return np.percentile(m, 2.5), np.percentile(m, 97.5)


if __name__ == "__main__":
    os.makedirs(RES, exist_ok=True)
    jobs = [(m, p, c) for m, p in methods() for c in CONDITIONS]
    t = time.time()
    with Pool(9) as pool:
        rows = [r for out in pool.imap_unordered(run_job, jobs) for r in out]
    df = pd.DataFrame(rows); df["family"] = df.method.map(family)
    df.to_csv(f"{RES}/episodes.csv", index=False)
    print(f"{len(jobs)} jobs, {len(df)} episodes, {time.time()-t:.0f}s")

    rng = np.random.default_rng(0)
    # family-level: average over training seeds per scenario, CI by bootstrap over scenarios; also seed spread
    out, paired = [], []
    for (cond, fam), g in df.groupby(["condition", "family"]):
        per_scn = g.groupby("scenario")[METRICS].mean()
        seeds = g.groupby("method")[METRICS].mean()
        row = {"condition": cond, "family": fam, "n_seeds": g.method.nunique(), "ms_per_step": g.ms_per_step.mean()}
        for k in METRICS:
            lo, hi = boot_ci(per_scn[k].values, rng)
            row.update({k: per_scn[k].mean(), k + "_lo": lo, k + "_hi": hi, k + "_seed_sd": seeds[k].std(ddof=0) if len(seeds) > 1 else np.nan})
        out.append(row)
    summary = pd.DataFrame(out); summary.to_csv(f"{RES}/summary.csv", index=False)
    for cond, g in df.groupby("condition"):
        base = g[g.family == "greedy_k1"].set_index("scenario")
        for fam, h in g.groupby("family"):
            if fam == "greedy_k1": continue
            per = h.groupby("scenario")[METRICS].mean()
            row = {"condition": cond, "family": fam}
            for k in METRICS:
                d = (per[k] - base[k]).values; lo, hi = boot_ci(d, rng)
                row.update({k + "_diff": d.mean(), k + "_lo": lo, k + "_hi": hi})
            paired.append(row)
    pd.DataFrame(paired).to_csv(f"{RES}/paired_vs_greedy.csv", index=False)
    print("wrote results/{episodes,summary,paired_vs_greedy}.csv")
