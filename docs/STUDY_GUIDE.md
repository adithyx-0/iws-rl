# IWS-RL study guide: everything you need to understand and defend this project

Written for Adithyan (M3). Part 1-11 explain the project; the **Appendix** contains the complete source code of every script, so this one file is self-contained.
Numbers come from `results_v2/` (final evaluation by M1). Where something is NOT verified, it says so.

**How to read it:** Part 1-3 (15 min) gives you the story. Parts 4-6 (45 min) teach the environment, methods and evaluation, which is what an examiner will ask. Part 7 has the results. Part 10 lists what is weak. The appendix is for lookup; read `iws_env.py` once end to end.

---

## 1. The problem in plain words

In many cities the water network is not "always on". Each area (zone) gets water only some hours a day. This is **intermittent water supply (IWS)**. Households cope with **roof tanks** that fill when water arrives and are drained by use. Two things go wrong:
- **Efficiency:** water is lost if tanks overflow, or never delivered if pressure is too low when everything opens at once.
- **Equity:** whichever zone is served first or longest does better; the worst-off zone can run dry.

The **decision**: each hour, which zones should the utility open? The utility cannot see inside household tanks (hidden state) and knows only pressures, flows, how much water it supplied so far today, and the day's water budget.

**Research question:** can a reinforcement-learning (RL) agent schedule zones to supply more water **and** protect the worst-off zone, compared with (a) simple rules, (b) a carefully optimised fixed daily timetable, and (c) an all-knowing oracle?

**Short answer (our result):** a *tuned fixed daily schedule* is very hard to beat when conditions match what it was tuned for. RL ties it on mean supply, loses on the worst zone, and wins only under some shifts (a lower surge cap, small tanks for DQN). A larger equity weight raises the worst zone slightly at a small cost in mean supply.

## 2. Key terms

| Term | Meaning here |
|---|---|
| Zone | One of 4 groups of demand nodes (k-means on node coordinates). All nodes in a zone are open or closed together. |
| Supply ratio (sr) | served consumption / desired consumption. 1.0 = nobody went short. |
| `mean_sr` | supply ratio over the whole network, whole episode. |
| `min_zone_sr` (worst zone) | supply ratio of the worst zone over the episode. The equity measure we care about. |
| Return | sum of rewards in an episode (what RL maximises). Always negative-ish; higher (closer to 0) is better. |
| Budget | daily source volume the utility may deliver, 50-90% of the day's consumption, known one day ahead. |
| alpha | surge cap: an open household may request up to `alpha` x its mean demand while refilling its tank. Default 4. |
| PDD | pressure-dependent demand: delivered flow falls when pressure is low (EPANET model). |
| v1 / v2 | v1: original environment (too easy). v2: demand x8 so hydraulics bind. **All final results are v2** (`IWS_V2=1`). |
| Oracle | hindsight upper bound: optimises the whole 72-hour action list per scenario knowing the future. Not deployable. |
| Tuned schedule (`ce_tuned`) | a fixed 24x4 on/off timetable repeated daily, optimised by cross-entropy search on training scenarios. |

## 3. Repository map

| File | What it does |
|---|---|
| `iws_env.py` | The Gymnasium environment (the heart of everything). |
| `v2cfg.py` | `IWS_V2=1` switches every script to the v2 environment and the `models_v2/`, `results_v2/` folders. |
| `baselines.py` | Random, all-open, rota, most-deprived-first greedy. |
| `bo_schedule.py`, `bo_schedule_tuned.py` | Cross-entropy search for the fixed daily schedule (old and tuned versions). |
| `train_variant.py` | Trains PPO / DQN / A2C and ablations (`ppo_noequity`, `ppo_dr`, ...). |
| `train_rec.py` | Trains LSTM `RecurrentPPO`, with or without domain randomisation. |
| `train_ppo.py` | Early v1 PPO script (kept for history). |
| `oracle.py` | Clairvoyant oracle (hindsight search). |
| `eval_all.py` | Evaluates every method on 11 conditions with fixed test seeds; writes `episodes.csv`, `summary.csv`. |
| `analyze_final.py` | Paired bootstrap CIs vs the tuned schedule and M1's figures. |
| `gate1.py` | The oracle-headroom decision gate. |
| `run_jobs.py` | Resumable job queue. |
| `check_setup.py` | 10-second environment sanity test. |
| `hyd_probe.py`, `cap_study.py`, `scale_study.py`, `scarce_diag.py`, `scarce_trace.py` | Diagnostics that found the v1 problems and justified v2. |
| `plots/make_plots.py` | **M3:** plots and results table from the result CSVs (configurable paths). |
| `plots/train_curves.py` | **M3:** PPO learning curve (evaluation every 20k steps). |
| `docs/` | Logs, plans, literature notes. Your files: `related_work.md`, `assumptions.md`, `log_M3.md`, `faculty_message.md`, `verify/`. |

Data folders: `results_v2/` (final results), `models_v2/` (trained models; `eval_all.py` loads **every** zip in it, see Part 10).

## 4. The environment (`iws_env.py`) in depth

### 4.1 Network and zones
EPANET network **Net3** (shipped with the `wntr` package): 92 junctions, **59 with demand**, 2 sources, 2 pumps, 3 network tanks. All EPANET controls are removed. Demand nodes are clustered into **Z = 4 zones** by k-means (zone sizes 11/16/16/16).

### 4.2 One decision step = one hour
`step(action)`:
1. **Action**: an integer 0-15; bit z = 1 means zone z is open this hour (`decode`). Closed zone = its consumers are cut off (their request is 0); the mains stay live.
2. **Household consumption** this hour: `c = qbar * node_scale * DIURNAL[h]`, a morning/evening-peaked pattern, with per-node noise (`demand_noise`, 10%).
3. **Request** (the "tank-filling surge"): an open node asks for `min(alpha * qbar, refill_need + c)`, where `refill_need = (S - L)/3600` (S tank capacity, L current storage).
4. **Budget clipping**: if all requests together would exceed what is left of today's source volume, they are scaled down proportionally. (`source_cap` is an optional hourly draw cap, off by default.)
5. **Hydraulics**: one EPANET steady-state snapshot with pressure-dependent demand (`required_pressure` 20 m, `minimum_pressure` 2 m). It returns delivered flow `q_del <= q_req` and pressures. Network tank levels are carried forward one hour.
6. **Household tank balance**: `L += delivered volume`; overflow is lost; then households draw `want = c*3600`; `served = min(L, want)`; `unmet = want - served`.
7. **Reward** (hourly): `- sum(unmet) / (day_volume/24)` = minus the unmet demand as a fraction of an average hour's consumption. **At the end of each day**: `+ lam * (worst zone's supply ratio that day) * 24 / Z` (the equity bonus; with Z=4 it equals `6*lam*min_zone_sr`).

An episode is **3 days = 72 steps**. Each step costs about 12-25 ms (EPANET dominates).

### 4.3 What the agent sees (24 numbers)
Per zone (x4): mean pressure/40, inflow (relative to an average hour), supply ratio so far today, hours since last supply/24 (capped). Then: sin and cos of hour of day, remaining budget today, tomorrow's budget (the "forecast"; zeroed in `ppo_noforecast`), episode progress, and the 3 network-tank levels. **It does NOT see household tank levels.** That makes the problem a **POMDP**; the hidden state can only be inferred from history (this is why the LSTM variant exists).

### 4.4 Randomness per episode (`reset`)
Household tank capacity `S = qbar*86400 * U(tank_days)` with tank_days = (0.3, 0.8) days of consumption; initial storage 20-60% of capacity; per-node demand noise; the 3 daily budgets `day_volume * U(supply_range)` with supply_range = (0.5, 0.9). Everything is determined by `reset(seed)`, so **an episode is exactly reproducible given its seed** (this is what lets the oracle search action sequences).

**Domain randomisation** (`randomize=True`, used in training only): alpha ~ U[3,6], tank_days low ~ U[.2,.4] and high ~ U[.6,1.0], supply low ~ U[.4,.6] and high ~ U[.8,1.0]. Held-out test values (alpha 2 and 8, small/large tanks, scarce supply) lie outside this.

### 4.5 Why v1 was too easy and what v2 changed
Total water is capped by the budget: the best possible mean supply is the **ceiling** `min(1, (sum of budgets + initial storage)/desired)`, about 0.773 in v1. PPO reached 0.767, 99% of the ceiling, so v1 results said almost nothing. Also pressure never mattered (10/20/30 m thresholds gave identical results; fill rate was 1.00 in `hyd_probe.py`).
**v2 fix:** `demand_scale = 8` multiplies all demands by 8, so opening every zone at once starves the network (fill 0.54-0.73, pressures 13-18 m). Now *which* zones are open genuinely matters.

## 5. The methods

### 5.1 Heuristics (`baselines.py`, `eval_all.py`)
- **random**: uniform over 16 actions.
- **all_open**: action 15 every hour.
- **rota_k1**: one zone at a time, 6-hour blocks (24/Z), cycling.
- **greedy_k1 / k2**: open the 1 (or 2) zones with the lowest supply ratio so far today (ties broken by hours since supply). Uses only observations.
- **priv_greedy_k1**: opens the zone whose *hidden household tanks* are emptiest. Reads information the utility does not have; **not deployable**, and it performs poorly here (0.639 mean supply, 0.494 worst zone); the reason was not investigated.

### 5.2 Tuned fixed daily schedule (`bo_schedule_tuned.py`)
A schedule is a **24 x 4 bit matrix** (hour of day x zone), repeated every day, not reacting to anything. Optimised with the **cross-entropy method (CEM)**: sample a population of schedules from per-bit probabilities, score each by its mean return on 10 **training** scenarios (seeds 0-9), keep the top 20% (elite), and move the probabilities toward the elite's frequencies. Tuned version: 40 iterations, population 60, run with 3 seeds. It is an open-loop controller, the analogue of the "Bayesian-optimised valve schedules" in the literature (though we use CEM, not Bayesian optimisation). The older `ce_schedule` ran only 12 iterations with population 40 and was still improving; do not use it as the baseline.

### 5.3 Reinforcement learning (`train_variant.py`, `train_rec.py`)
All use Stable-Baselines3, MLP policies, 8 parallel environments, trained **300,000 steps** on v2 (about 4,000 episodes).
- **PPO** (proximal policy optimisation): `n_steps=216` (3 episodes per env per update), batch 432, 10 epochs, gamma 0.99, GAE lambda 0.95, entropy coefficient 0.01, learning rate 3e-4. Policy-gradient method that clips the probability ratio so each update stays close to the old policy.
- **DQN**: value-based; replay buffer 100k, target network updated every 1,000 steps, epsilon decays over 30% of training.
- **A2C**: untuned, failed in v1 (0.44); not used in v2.
- **ppo_noequity**: reward without the end-of-day equity bonus (ablation).
- **ppo_dr**: PPO trained with domain randomisation.
- **rec / rec_dr**: `RecurrentPPO` with an LSTM (64 units) to infer hidden tank state from history, without / with domain randomisation. Result: **negative**; LSTM+DR is far worse on the worst zone (0.469).
- **ppo_lam{0,0.5,2,4}**: PPO with different equity weights `lam` (default 1). This is a **reward penalty, not a constraint**; do not call it Lagrangian or constrained RL.

Eval uses the **deterministic** policy (arg-max action).

### 5.4 The oracle (`oracle.py`)
Because an episode is deterministic given its seed, we can search the **whole 72-action sequence** per test scenario. It is warm-started from every heuristic's, the schedule's and every PPO seed's own action sequence (replaying them open-loop reproduces their results, so the oracle is >= each of them by construction), then improved by random local block mutations and CEM. It uses hidden information (future budgets, tank levels). It is an **upper bound / regret reference**, not a policy. An earlier version without warm start scored *below* PPO and was discarded as invalid (kept as `oracle_v0_weak.csv`): a good example of sanity-checking a bound. 30 scenarios only.

## 6. Evaluation protocol (`eval_all.py`)

- **Test seeds are 10000+**, never used in training (training uses env seeds from the training seed; the schedule is tuned on seeds 0-9). 100 scenarios for `default`, 50 for each other condition.
- **11 conditions**: default; scarce (supply 0.3-0.5); abundant (0.7-1.0); small tanks (0.1-0.3 days); large tanks (0.8-1.5); noisy demand (0.3); five days; alpha 2; alpha 8; required pressure 10 m; 30 m.
- **Metrics per episode:** return, `mean_sr`, `min_zone_sr`, `p10_node_sr` (10th-percentile household), `gini_node` (inequality), `jain_zone` (Jain fairness index), `ceiling`.
- **Family averaging:** for each scenario, average the trained seeds of a method family (e.g. 5 PPO seeds); then compare families scenario by scenario. This is a **paired** comparison (same scenario for both methods).
- **Confidence intervals** (`analyze_final.py`): bootstrap (2,000 resamples) over test scenarios of the paired difference vs `ce_tuned`; "better/worse/tie" = interval entirely above/below/containing 0.
- **Limitation:** these CIs include scenario randomness but **not training-seed variance**. We checked the headline claim by hand: all 5 PPO runs are worse than all 3 tuned runs on worst-zone and return in the default condition.
- **The scarce condition is degenerate** for mean supply (budget spent in ~3 hours, every method ~0.44-0.47); judge it on the worst zone only, not as evidence for or against RL.

## 7. Results (v2, default condition, 100 test scenarios)

| Method | seeds | mean supply [95% CI] | worst zone [95% CI] |
|---|---|---|---|
| Tuned fixed schedule | 3 | 0.716 [0.706, 0.725] | 0.630 [0.623, 0.638] |
| PPO | 5 | 0.716 [0.707, 0.725] | 0.601 [0.592, 0.609] |
| PPO + domain randomisation | 5 | 0.711 [0.703, 0.720] | 0.612 [0.604, 0.621] |
| DQN | 5 | 0.714 [0.705, 0.723] | 0.590 [0.582, 0.597] |
| PPO no equity term | 5 | 0.718 [0.709, 0.727] | 0.564 [0.553, 0.574] |
| Old CE schedule | 1 | 0.708 [0.698, 0.717] | 0.612 [0.606, 0.618] |
| LSTM PPO | 3 | 0.702 [0.692, 0.710] | 0.573 [0.565, 0.582] |
| Random | 1 | 0.672 [0.664, 0.680] | 0.527 [0.518, 0.537] |

Oracle (30 scenarios, not comparable sample size): mean 0.725, worst zone 0.631, return -8.49 (tuned -9.15, PPO -9.67).

**Paired vs tuned schedule (M1):** PPO return -0.52 [-0.59, -0.46] (worse); mean supply tie; worst zone -0.030 (worse).
**Under shift** (return vs tuned schedule): alpha=2 PPO +1.14, PPO+DR +1.66, DQN +2.01 (all better); small tanks DQN +1.14 (better), PPO and PPO+DR tie; alpha=8 PPO worse, PPO+DR tie, DQN worse; the other 6 non-scarce conditions: the tuned schedule is better than all three. Overall PPO: worse in 8 of 10 non-scarce conditions, better in 1, tie in 1.
**Equity weight:** lam 0/0.5/1/2/4 gives worst zone 0.573/0.586/0.601/0.598/0.635 and mean supply 0.718/0.716/0.716/0.712/0.708 (2-5 seeds each; not monotone; overlapping intervals).

**How to read it:** the learned policy cannot beat a good timetable when the world looks like the timetable's training world, because the only information it could exploit (hidden tanks) it cannot observe. RL becomes useful when the world changes (a lower alpha means the fixed timetable no longer fits) because a reactive policy can adapt and a fixed one cannot.

## 8. How to run it (Windows notes included)

```
python -m venv venv ; venv\Scripts\activate          # Python 3.11 or 3.12
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt ; pip install six    # wntr 1.5.0 needs six but does not declare it
python check_setup.py                                # expect SETUP OK
$env:IWS_V2="1"                                      # PowerShell; use `set IWS_V2=1` in cmd
python train_variant.py ppo 0 300000                 # one PPO model, ~1-2 h
python eval_all.py                                   # full evaluation, ~40 min on 10 cores
python analyze_final.py                              # paired CIs
python plots/make_plots.py --baseline ce_tuned --lambda-sweep   # M3 plots and table
```
**Windows pitfalls we hit:** (1) Smart App Control blocks PyTorch DLLs (WinError 4551): needs it off or WSL; (2) running several EPANET trainings at once crashed with EPANET errors 305/307 ("hydraulics file"): run each training in its own folder; the cause is unconfirmed; (3) `eval_all.py` and `oracle.py` hard-code `Pool(9)`.

## 9. RL concepts you should be able to explain

- **MDP / POMDP:** states, actions, transitions, rewards, discount gamma. Ours is partially observable (hidden tanks) so the observation is not a sufficient statistic.
- **Policy gradient and PPO:** adjust policy parameters in the direction that raises expected return; PPO clips the new/old probability ratio to stop destructive large updates. **GAE** trades bias for variance in advantage estimates. The **entropy bonus** keeps exploration alive.
- **DQN:** learn Q(s,a) with a neural net, replay buffer and slowly-updated target network; act greedily (epsilon-greedy while training). Works for our discrete 16-action space.
- **On-policy vs off-policy:** PPO uses fresh data; DQN reuses a replay buffer.
- **Reward shaping:** the equity bonus changes behaviour (PPO without the equity term 0.564 vs PPO 0.601 on the worst zone; across the lam sweep 0.573 at lam 0 to 0.635 at lam 4) but it is a penalty on one number, not a guarantee.
- **Domain randomisation:** train over a range of environment parameters so the policy generalises to parameters it never saw.
- **Open-loop vs closed-loop control:** a fixed timetable ignores feedback; RL reacts to observations. Closed-loop only wins when feedback carries useful information or conditions shift.
- **Oracle / regret:** an upper bound that uses privileged information; the gap between a method and the oracle is its regret.
- **Paired bootstrap:** resample scenarios to get a CI on the mean paired difference; pairing removes scenario-to-scenario variance.
- **Pareto trade-off:** improving the worst zone costs some mean supply; the lam sweep traces that frontier.

**Related-work cheat sheet (for questions):** closest prior work on our problem is optimisation-based (Hendrickson & Sela 2024: Bayesian-optimised open-loop valve schedules with household tanks; Kurian et al. 2023: MILP). RL has been applied to pumps, valves and pressure control (Hu 2020/2023, Pei 2025, Belfadil 2024, Hajgato 2020, Gym4ReaL) with cost or pressure objectives, not equity. Fair-RL theory: Siddique et al. 2020 (generalized Gini). Our equity bonus is cruder than their GGF: say so. Seed-count guidance: Henderson 2018, Agarwal 2021.

## 10. Weaknesses and what a reviewer will ask

1. **Training-seed variance is not in the CIs.** Seeds: 5 for RL rows, 3 for the schedule, 2-3 for lam points. PPO+DR is close to the schedule on seed evidence; do not call it clearly worse.
2. **The schedule was tuned on one condition (default)**; RL was trained at default or on a randomised range. Shift results depend on that choice.
3. **One network, simulation only; tank sizes, surge factor, budgets are assumptions.** Our 0.3-0.8 days of tank storage is probably below real installed storage (vendor guidance ~2 days; no survey found).
4. **The oracle uses 30 scenarios and the future**; do not quote an exact "gap closed" percentage.
5. **The equity term is a reward penalty**, not a constraint, so it gives no per-episode guarantee.
6. **Hyper-parameters:** one PPO configuration, DQN untuned beyond a single setting; a tuned RL baseline could change the picture. We did not run a tuning sweep.
7. **Novelty:** we only say "in our search we did not find...". Papers are checked at abstract level in `docs/verify/results_ADITHYAN.md`; the newer Part B results (supplied by the user, not rechecked by me) report that the 2026 npj Clean Water equity paper DOES exist ("Equitable supply in water distribution networks using data-driven optimization and AI-assisted voice automation") but was not read. Until someone reads it, do not claim novelty over it. The forward-citation search was not done.
8. **`eval_all.py` loads every zip in `models_v2/`.** Extra seeds placed there change the "5 seeds" rows silently. Extra models live in `models_v2_extra/`; `models_v2/ppo_s8.zip` is of unknown origin and is still in `models_v2/`.
9. **Windows training crashes** (Part 8) were unexplained.

## 11. Likely questions and short answers

- *Why not just use the oracle?* It needs the future and hidden tank levels; it is a bound, not a policy.
- *Why does the privileged greedy do badly?* We measured that it does (0.639 mean supply, 0.494 worst zone) but did NOT test why. A plausible hypothesis: opening the single emptiest zone triggers a large refill surge that wastes budget and pressure, but this is untested; say "we did not investigate".
- *Why is RL not better?* The decision-relevant state is hidden, and a fixed daily pattern already captures the demand cycle. RL helps only when the pattern breaks.
- *Is a 0.03 worst-zone difference meaningful?* Statistically yes on our scenarios (CI excludes 0 and every PPO seed is below every schedule seed); practically it is 3 percentage points of one zone's supply.
- *Is this equity?* We use the worst-zone supply ratio (max-min fairness over zones) as the equity measure, plus Gini and Jain in the data. Other definitions would rank methods differently.
- *Did you tune RL?* Not systematically; say so.

---

# Appendix: complete source code

Each file is listed in full, exactly as in the repository at the time of writing (branch `feature/adithyan-m3`).


## A1. `iws_env.py` - The environment (read this one end to end) (248 lines)

```python
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
                 zone_seed=0, source_cap=None, demand_scale=1.0, randomize=False):
        super().__init__()
        self.Z, self.n_days = n_zones, n_days
        self.H = 24 * n_days
        self.supply_range, self.tank_days, self.alpha = supply_range, tank_days, alpha
        self.lam, self.equity_reward, self.forecast = lam, equity_reward, forecast
        self.demand_noise = demand_noise
        self.randomize = randomize     # domain randomisation per episode (train ranges: alpha U[3,6], tank_days lo U[.2,.4] hi U[.6,1.0], supply lo U[.4,.6] hi U[.8,1.0])
        self._base = (alpha, tank_days, supply_range)
        self.source_cap = source_cap   # max source draw per hour, in multiples of mean hourly demand (None = unlimited, v1 behaviour)

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
        self.qbar = np.array(qb) * demand_scale          # m3/s mean consumption (demand_scale>1 stresses the hydraulics)
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
        if self.randomize:
            self.alpha = float(r.uniform(3, 6)); self.tank_days = (float(r.uniform(.2, .4)), float(r.uniform(.6, 1.0)))
            self.supply_range = (float(r.uniform(.4, .6)), float(r.uniform(.8, 1.0)))
        else:
            self.alpha, self.tank_days, self.supply_range = self._base
        self.S = self.qbar * 86400.0 * r.uniform(*self.tank_days, self.J)   # roof tank capacity m3
        self.L = self.S * r.uniform(0.2, 0.6, self.J)                       # initial storage
        self.L0_total = float(self.L.sum())
        self.node_scale = np.clip(1 + self.demand_noise * r.standard_normal(self.J), 0.5, 1.5)
        self.budgets = self.day_volume * r.uniform(*self.supply_range, self.n_days)
        self.tank_lvl = dict(self.tank_init)
        self.t = 0
        self.last_p = np.zeros(self.J)
        self.last_inflow_z = np.zeros(self.Z)
        self.hours_since = np.zeros(self.Z)
        self._new_day()
        self.log = {"served": np.zeros(self.J), "desired": np.zeros(self.J), "daily_min_zone_sr": [],
                    "daily_zone_sr": [], "delivered": 0.0, "requested": 0.0}
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
        if self.source_cap is not None:
            left = min(left, self.source_cap * self.day_volume / 24)
        if q_req.sum() * 3600.0 > left:
            q_req *= left / (q_req.sum() * 3600.0 + 1e-12)
        if q_req.sum() > 0:
            q_del, p = self._hydraulics(q_req)
        else:
            q_del, p = np.zeros(self.J), np.zeros(self.J)
        q_del = np.minimum(q_del, q_req)
        self.log["requested"] += q_req.sum() * 3600.0
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
                "jain_zone": float(sr_zone.sum() ** 2 / (len(sr_zone) * (sr_zone ** 2).sum() + 1e-12)),
                "ceiling": float(min(1.0, (self.budgets.sum() + self.L0_total) / self.log["desired"].sum())),
                "gini_node": float(gini), "p10_node_sr": float(np.percentile(sr_node, 10)),
                "budget_used": float(self.log["delivered"] / self.budgets.sum()),
                "hyd_fill": float(self.log["delivered"] / max(self.log["requested"], 1e-9))}


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
```

## A2. `v2cfg.py` - v1/v2 switch (6 lines)

```python
"""IWS_V2=1 switches every script to the harder environment (demand_scale=8: hydraulics bind) with separate models_v2/ and results_v2/."""
import os
V2 = os.environ.get("IWS_V2") == "1"
BASE = {"demand_scale": 8.0} if V2 else {}
MODELS = "models_v2" if V2 else "models"
RES = "results_v2" if V2 else "results"
```

## A3. `baselines.py` - Heuristic policies (65 lines)

```python
"""Baseline policies for IWSEnv. Each policy: f(env, obs) -> action int."""
import numpy as np
from iws_env import IWSEnv


def encode(open_z):
    return int(sum(int(b) << z for z, b in enumerate(open_z)))


def all_open(env, obs):
    return env.action_space.n - 1


def random_policy(env, obs):
    return int(env.np_random.integers(env.action_space.n))


def make_rota(k):
    """Fixed rota: k zones open at a time, cycling every hour block of 24/Z*k hours (utility practice)."""
    def pol(env, obs):
        h = env.t % 24
        block = 24 // env.Z
        start = (h // block) % env.Z
        open_z = np.zeros(env.Z, bool)
        for i in range(k):
            open_z[(start + i) % env.Z] = True
        return encode(open_z)
    pol.__name__ = f"rota_k{k}"
    return pol


def make_greedy(k):
    """Most-deprived-first: open the k zones with the lowest supply ratio so far today (uses obs only)."""
    def pol(env, obs):
        sr = obs[2:4 * env.Z:4]                 # zone supply ratio so far today
        hrs = obs[3:4 * env.Z:4]                # hours since last supply (tie-break)
        order = np.lexsort((-hrs, sr))
        open_z = np.zeros(env.Z, bool); open_z[order[:k]] = True
        return encode(open_z)
    pol.__name__ = f"greedy_k{k}"
    return pol


def evaluate(policy, seeds, env_kwargs=None):
    env = IWSEnv(**(env_kwargs or {}))
    out = []
    for s in seeds:
        obs, _ = env.reset(seed=int(s)); done = False; R = 0.0
        while not done:
            obs, r, done, _, info = env.step(policy(env, obs)); R += r
        info["return"] = R
        out.append(info)
    keys = ["return", "mean_sr", "min_zone_sr", "p10_node_sr", "gini_node"]
    return {k: float(np.mean([o[k] for o in out])) for k in keys}


if __name__ == "__main__":
    import sys, time
    seeds = range(10000, 10030)
    pols = [random_policy, all_open] + [make_rota(k) for k in (1, 2, 3)] + [make_greedy(k) for k in (1, 2, 3)]
    print(f"{'policy':12s} {'return':>8s} {'meanSR':>7s} {'minZone':>8s} {'p10node':>8s} {'gini':>6s}")
    for p in pols:
        t = time.time(); m = evaluate(p, seeds)
        print(f"{p.__name__:12s} {m['return']:8.2f} {m['mean_sr']:7.3f} {m['min_zone_sr']:8.3f} "
              f"{m['p10_node_sr']:8.3f} {m['gini_node']:6.3f}  ({time.time()-t:.0f}s)")
```

## A4. `bo_schedule.py` - Fixed-schedule search, first version (12 iterations, under-tuned) (40 lines)

```python
"""Open-loop optimised daily valve schedule (stand-in for the Bayesian-optimisation schedules in the IWS literature).
A schedule is a 24 x Z bit matrix repeated every day. Optimised with the cross-entropy method on TRAIN scenarios (seeds 0-9),
objective = mean episode return of IWSEnv (same reward the RL agents see). Saves results/ce_schedule.npy.
Usage: python bo_schedule.py [iters] [pop]"""
import sys, os, warnings, time
warnings.filterwarnings("ignore")
from multiprocessing import Pool
import numpy as np
from iws_env import IWSEnv
from v2cfg import BASE, RES

SEEDS = list(range(10))
_env = None

def score(bits):
    global _env
    if _env is None: _env = IWSEnv(**BASE)
    R = 0.0
    for s in SEEDS:
        obs, _ = _env.reset(seed=s); done = False
        while not done:
            h = _env.t % 24
            a = int(sum(int(b) << z for z, b in enumerate(bits[h])))
            obs, r, done, _, _ = _env.step(a); R += r
    return R / len(SEEDS)

if __name__ == "__main__":
    iters = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    pop = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    Z = 4; rng = np.random.default_rng(0)
    p = np.full((24, Z), 0.3); best = (-1e9, None); t = time.time()
    with Pool(5) as pool:
        for it in range(iters):
            cand = (rng.random((pop, 24, Z)) < p).astype(int)
            sc = np.array(pool.map(score, list(cand)))
            elite = cand[np.argsort(sc)[-pop // 5:]]
            p = 0.3 * p + 0.7 * elite.mean(0); p = np.clip(p, 0.03, 0.97)
            if sc.max() > best[0]: best = (sc.max(), cand[sc.argmax()])
            print(f"iter {it} mean {sc.mean():.2f} best {sc.max():.2f} overall {best[0]:.2f} ({time.time()-t:.0f}s)", flush=True)
    os.makedirs(RES, exist_ok=True); np.save(f"{RES}/ce_schedule.npy", best[1]); print(best[1].T)
```

## A5. `bo_schedule_tuned.py` - Fixed-schedule search, tuned version used as the baseline (41 lines)

```python
"""Open-loop optimised daily valve schedule (stand-in for the Bayesian-optimisation schedules in the IWS literature).
A schedule is a 24 x Z bit matrix repeated every day. Optimised with the cross-entropy method on TRAIN scenarios (seeds 0-9),
objective = mean episode return of IWSEnv (same reward the RL agents see). Saves results/ce_schedule.npy.
Tuned variant. Usage: python bo_schedule_tuned.py iters pop seed"""
import sys, os, warnings, time
warnings.filterwarnings("ignore")
from multiprocessing import Pool
import numpy as np
from iws_env import IWSEnv
from v2cfg import BASE, RES

SEEDS = list(range(10))
_env = None

def score(bits):
    global _env
    if _env is None: _env = IWSEnv(**BASE)
    R = 0.0
    for s in SEEDS:
        obs, _ = _env.reset(seed=s); done = False
        while not done:
            h = _env.t % 24
            a = int(sum(int(b) << z for z, b in enumerate(bits[h])))
            obs, r, done, _, _ = _env.step(a); R += r
    return R / len(SEEDS)

if __name__ == "__main__":
    iters = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    pop = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    sd = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    Z = 4; rng = np.random.default_rng(sd)
    p = np.full((24, Z), 0.3); best = (-1e9, None); t = time.time()
    with Pool(4) as pool:
        for it in range(iters):
            cand = (rng.random((pop, 24, Z)) < p).astype(int)
            sc = np.array(pool.map(score, list(cand)))
            elite = cand[np.argsort(sc)[-pop // 5:]]
            p = 0.3 * p + 0.7 * elite.mean(0); p = np.clip(p, 0.03, 0.97)
            if sc.max() > best[0]: best = (sc.max(), cand[sc.argmax()])
            print(f"iter {it} mean {sc.mean():.2f} best {sc.max():.2f} overall {best[0]:.2f} ({time.time()-t:.0f}s)", flush=True)
    os.makedirs(RES, exist_ok=True); np.save(f"{RES}/ce_tuned_s{sd}.npy", best[1]); print(best[1].T)
```

## A6. `train_variant.py` - PPO / DQN / A2C and ablations (37 lines)

```python
"""Train one variant. Usage: python train_variant.py VARIANT SEED [STEPS]
VARIANT in: ppo, ppo_noequity, ppo_noforecast, dqn. Saves models/VARIANT_sSEED.zip"""
import sys, os, time, warnings
warnings.filterwarnings("ignore")
import torch
torch.set_num_threads(1)
from stable_baselines3 import PPO, DQN, A2C
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import DummyVecEnv
from iws_env import IWSEnv
from v2cfg import BASE, MODELS

TRAIN_KW = {"ppo": {}, "dqn": {}, "ppo_noequity": {"equity_reward": False}, "ppo_noforecast": {"forecast": False},
            "ppo_long": {}, "ppo_long_noequity": {"equity_reward": False}, "ppo_long_noforecast": {"forecast": False}, "a2c": {}, "ppo_dr": {"randomize": True},
            "ppo_lam0": {"lam": 0.0}, "ppo_lam0.5": {"lam": 0.5}, "ppo_lam2": {"lam": 2.0}, "ppo_lam4": {"lam": 4.0}}

if __name__ == "__main__":
    variant, seed = sys.argv[1], int(sys.argv[2])
    steps = int(sys.argv[3]) if len(sys.argv) > 3 else 150_000
    kw = {**BASE, **TRAIN_KW[variant]}
    os.makedirs(MODELS, exist_ok=True)
    t = time.time()
    if variant == "dqn":
        env = IWSEnv(**kw)
        model = DQN("MlpPolicy", env, learning_rate=5e-4, buffer_size=100_000, learning_starts=5_000,
                    batch_size=128, gamma=0.99, train_freq=4, target_update_interval=1_000,
                    exploration_fraction=0.3, exploration_final_eps=0.05, seed=seed, verbose=0, device="cpu")
    elif variant == "a2c":
        venv = make_vec_env(lambda: IWSEnv(**kw), n_envs=8, seed=seed, vec_env_cls=DummyVecEnv)
        model = A2C("MlpPolicy", venv, n_steps=24, gamma=0.99, ent_coef=0.01, learning_rate=7e-4, seed=seed, verbose=0, device="cpu")
    else:
        venv = make_vec_env(lambda: IWSEnv(**kw), n_envs=8, seed=seed, vec_env_cls=DummyVecEnv)
        model = PPO("MlpPolicy", venv, n_steps=216, batch_size=432, n_epochs=10, gamma=0.99,
                    gae_lambda=0.95, ent_coef=0.01, learning_rate=3e-4, seed=seed, verbose=0, device="cpu")
    model.learn(steps)
    model.save(f"{MODELS}/{variant}_s{seed}")
    print(f"{variant} seed {seed} steps {steps} done in {time.time()-t:.0f}s", flush=True)
```

## A7. `train_rec.py` - LSTM RecurrentPPO (17 lines)

```python
"""Recurrent (LSTM) PPO, optionally with domain randomisation. Usage: IWS_V2=1 python train_rec.py VARIANT SEED [STEPS]; VARIANT in rec, rec_dr -> models_v2/VARIANT_sSEED.zip"""
import sys, os, time, warnings
warnings.filterwarnings("ignore")
import torch; torch.set_num_threads(1)
from sb3_contrib import RecurrentPPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import DummyVecEnv
from iws_env import IWSEnv
from v2cfg import BASE, MODELS
variant, seed = sys.argv[1], int(sys.argv[2]); steps = int(sys.argv[3]) if len(sys.argv) > 3 else 200_000
kw = {**BASE, "randomize": variant == "rec_dr"}
os.makedirs(MODELS, exist_ok=True); t = time.time()
venv = make_vec_env(lambda: IWSEnv(**kw), n_envs=8, seed=seed, vec_env_cls=DummyVecEnv)
model = RecurrentPPO("MlpLstmPolicy", venv, n_steps=144, batch_size=576, n_epochs=10, gamma=0.99, gae_lambda=0.95, ent_coef=0.01,
                     learning_rate=3e-4, seed=seed, verbose=0, device="cpu", policy_kwargs={"lstm_hidden_size": 64, "n_lstm_layers": 1})
model.learn(steps); model.save(f"{MODELS}/{variant}_s{seed}")
print(f"{variant} seed {seed} steps {steps} done in {time.time()-t:.0f}s", flush=True)
```

## A8. `train_ppo.py` - Early v1 PPO script (25 lines)

```python
"""PPO training on IWSEnv (smoke-test scale). Usage: python train_ppo.py STEPS SEED"""
import sys, time, warnings
warnings.filterwarnings("ignore")
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import SubprocVecEnv
from iws_env import IWSEnv
from baselines import evaluate

if __name__ == "__main__":
    steps = int(sys.argv[1]) if len(sys.argv) > 1 else 100_000
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    venv = make_vec_env(IWSEnv, n_envs=8, seed=seed, vec_env_cls=SubprocVecEnv)
    model = PPO("MlpPolicy", venv, n_steps=216, batch_size=432, n_epochs=10, gamma=0.99,
                gae_lambda=0.95, ent_coef=0.01, learning_rate=3e-4, seed=seed, verbose=0, device="cpu")
    t = time.time()
    chunk = steps // 5
    for i in range(5):
        model.learn(chunk, reset_num_timesteps=False)
        pol = lambda env, obs: int(model.predict(obs, deterministic=True)[0])
        m = evaluate(pol, range(10000, 10030))
        print(f"steps {(i+1)*chunk:7d} | {time.time()-t:5.0f}s | return {m['return']:.2f} meanSR {m['mean_sr']:.3f} "
              f"minZone {m['min_zone_sr']:.3f} p10 {m['p10_node_sr']:.3f} gini {m['gini_node']:.3f}", flush=True)
    model.save(f"ppo_iws_s{seed}")
```

## A9. `oracle.py` - Clairvoyant oracle (60 lines)

```python
"""Clairvoyant open-loop oracle (hindsight upper bound). IWSEnv is deterministic given reset(seed), so for each test scenario we
optimise the whole 72-step action sequence with the cross-entropy method, warm-started from every heuristic's own action sequence
(replaying them open-loop reproduces them exactly), so oracle >= best heuristic by construction. NOT a deployable policy.
Usage: IWS_V2=1 python oracle.py [n_scenarios=30] [iters=8] [pop=48] -> {RES}/oracle.csv"""
import sys, os, warnings, time
warnings.filterwarnings("ignore")
from multiprocessing import Pool
import numpy as np, pandas as pd
from iws_env import IWSEnv
from v2cfg import BASE, RES
from baselines import all_open, make_rota, make_greedy
from eval_all import priv_greedy, ce_schedule
import glob
from stable_baselines3 import PPO
from v2cfg import MODELS

def rollout(env, seed, seq=None, policy=None):
    obs, _ = env.reset(seed=seed); R = 0.0; acts = []
    for t in range(env.H):
        a = int(seq[t]) if seq is not None else int(policy(env, obs)); acts.append(a)
        obs, r, d, _, info = env.step(a); R += r
    info["return"] = R; return R, info, acts

def solve(args):
    seed, iters, pop = args
    env = IWSEnv(**BASE); rng = np.random.default_rng(seed); H = env.H; A = env.action_space.n
    best = (-1e9, None, None); warm = []
    pols = [all_open, make_rota(1), make_greedy(1), make_greedy(2), priv_greedy, ce_schedule]
    for pth in sorted(glob.glob(f"{MODELS}/ppo_s[0-4].zip")):
        m = PPO.load(pth, device="cpu"); pols.append(lambda e, o, m=m: int(m.predict(o, deterministic=True)[0]))
    for pol in pols:
        R, info, acts = rollout(env, seed, policy=pol); warm.append(acts)
        if R > best[0]: best = (R, info, acts)
    p = np.full((H, A), 1.0 / A)
    for w in warm:
        for t, a in enumerate(w): p[t, a] += 0.5 / len(warm) * 4
    p /= p.sum(1, keepdims=True)
    # local search from the best known sequence (PPO or CE usually): random block mutations, accept if better
    cur = list(best[2]); curR = best[0]
    for k in range(150):
        c = list(cur); t0 = int(rng.integers(H)); L = int(rng.integers(1, 7))
        for t in range(t0, min(H, t0 + L)): c[t] = int(rng.integers(A)) if rng.random() < .5 else int(warm[int(rng.integers(len(warm)))][t])
        R, info, acts = rollout(env, seed, seq=c)
        if R > curR: cur, curR = c, R; best = (R, info, acts)
    for it in range(iters):
        cand = np.array([[rng.choice(A, p=p[t]) for t in range(H)] for _ in range(pop)])
        res = [rollout(env, seed, seq=c) for c in cand]
        sc = np.array([x[0] for x in res]); j = int(sc.argmax())
        if sc[j] > best[0]: best = (sc[j], res[j][1], res[j][2])
        el = cand[np.argsort(sc)[-max(2, pop // 5):]]
        f = np.zeros((H, A)); [f[np.arange(H), e].__iadd__(1) for e in el]; f /= len(el)
        p = 0.3 * p + 0.7 * f + 1e-3; p /= p.sum(1, keepdims=True)
    info = best[1]; return {"scenario": seed, "return": best[0], **{k: info[k] for k in ("mean_sr", "min_zone_sr", "p10_node_sr", "gini_node", "jain_zone", "ceiling")}}

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30; iters = int(sys.argv[2]) if len(sys.argv) > 2 else 8; pop = int(sys.argv[3]) if len(sys.argv) > 3 else 48
    t = time.time(); os.makedirs(RES, exist_ok=True)
    with Pool(9) as P: rows = list(P.imap_unordered(solve, [(10000 + i, iters, pop) for i in range(n)]))
    df = pd.DataFrame(rows).sort_values("scenario"); df.to_csv(f"{RES}/oracle.csv", index=False)
    print(f"{n} scenarios in {time.time()-t:.0f}s"); print(df[["return", "mean_sr", "min_zone_sr", "ceiling"]].mean().round(3))
```

## A10. `eval_all.py` - Evaluation of every method on 11 conditions (148 lines)

```python
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


def make_ce_tuned(sd):
    def f(env, obs):
        S = np.load(f"{RES}/ce_tuned_s{sd}.npy"); h = env.t % 24
        return int(sum(int(b) << z for z, b in enumerate(S[h])))
    return f


def baseline_policy(name):
    if name.startswith("ce_tuned_s"): return make_ce_tuned(int(name[-1]))
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
    m += [(f"ce_tuned_s{i}", None) for i in range(3) if os.path.exists(f"{RES}/ce_tuned_s{i}.npy")]
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
```

## A11. `analyze_final.py` - Paired bootstrap CIs and M1's figures (34 lines)

```python
"""Paired bootstrap CIs (over test scenarios) of family-mean differences vs ce_tuned; Pareto + regime-map figures.
Outputs results_v2/paired_vs_ce_tuned.csv, results_v2/figs/*.png. CIs exclude training-seed variance."""
import numpy as np, pandas as pd, os
e = pd.read_csv("results_v2/episodes.csv"); os.makedirs("results_v2/figs", exist_ok=True)
rng = np.random.default_rng(0)
def fam_mean(f, m):  # scenario-indexed mean over seeds of family f
    return e[e.family == f].groupby(["condition", "scenario"])[m].mean()
rows = []
for f in ["ppo", "ppo_dr", "dqn", "ppo_noequity", "ce_schedule"]:
    for m in ["return", "min_zone_sr", "mean_sr"]:
        d = (fam_mean(f, m) - fam_mean("ce_tuned", m)).dropna()
        for c, g in d.groupby(level=0):
            x = g.values; bs = [rng.choice(x, len(x)).mean() for _ in range(2000)]
            rows.append((f, m, c, len(x), x.mean(), np.percentile(bs, 2.5), np.percentile(bs, 97.5)))
P = pd.DataFrame(rows, columns=["family", "metric", "condition", "n", "diff", "lo", "hi"])
P["sig"] = np.where(P.lo > 0, "better", np.where(P.hi < 0, "worse", "tie")); P.round(3).to_csv("results_v2/paired_vs_ce_tuned.csv", index=False)
print(P[P.metric == "return"].pivot(index="condition", columns="family", values="sig").to_string())
print(P[(P.metric == "min_zone_sr")].pivot(index="condition", columns="family", values="sig").to_string())
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
s = pd.read_csv("results_v2/summary.csv"); d = s[s.condition == "default"].set_index("family")
fig, ax = plt.subplots(figsize=(5.5, 4))
lam = {"ppo_lam0": 0, "ppo_lam0.5": .5, "ppo": 1, "ppo_lam2": 2, "ppo_lam4": 4}
xs = [d.loc[k, "mean_sr"] for k in lam]; ys = [d.loc[k, "min_zone_sr"] for k in lam]
ax.plot(xs, ys, "o-", label="PPO, equity weight lambda")
for k, v in lam.items(): ax.annotate(f"λ={v}", (d.loc[k, "mean_sr"], d.loc[k, "min_zone_sr"]), textcoords="offset points", xytext=(4, 4), fontsize=8)
for k, mk in [("ce_tuned", "s"), ("ppo_noequity", "^"), ("dqn", "D"), ("ppo_dr", "v")]: ax.plot(d.loc[k, "mean_sr"], d.loc[k, "min_zone_sr"], mk, label=k)
ax.set_xlabel("mean supply ratio"); ax.set_ylabel("worst-zone supply ratio"); ax.set_title("Efficiency vs fairness (default)"); ax.legend(fontsize=7); fig.tight_layout(); fig.savefig("results_v2/figs/pareto.png", dpi=150)
R = P[(P.metric == "return") & P.family.isin(["ppo", "ppo_dr", "dqn"])]
fig, ax = plt.subplots(figsize=(7, 4)); conds = sorted(R.condition.unique())
for i, f in enumerate(["ppo", "ppo_dr", "dqn"]):
    r = R[R.family == f].set_index("condition").loc[conds]
    ax.errorbar(np.arange(len(conds)) + i * .2 - .2, r["diff"], yerr=[r["diff"] - r.lo, r.hi - r["diff"]], fmt="o", label=f, capsize=2)
ax.axhline(0, color="k", lw=.8); ax.set_xticks(range(len(conds))); ax.set_xticklabels(conds, rotation=45, ha="right", fontsize=8)
ax.set_ylabel("return minus tuned fixed schedule"); ax.set_title("Where RL beats the tuned schedule (>0)"); ax.legend(fontsize=8); fig.tight_layout(); fig.savefig("results_v2/figs/regime_map.png", dpi=150)
```

## A12. `gate1.py` - Oracle-headroom decision gate (19 lines)

```python
"""Gate 1: oracle vs PPO vs baselines on the same 30 test scenarios (v2 default). Usage: IWS_V2=1 python gate1.py"""
import numpy as np, pandas as pd
from v2cfg import RES
o = pd.read_csv(f"{RES}/oracle.csv").set_index("scenario"); ep = pd.read_csv(f"{RES}/episodes.csv")
ep = ep[(ep.condition == "default") & ep.scenario.isin(o.index)]
ep["family"] = ep.method.str.replace(r"_s\d+$", "", regex=True)
per = ep.groupby(["family", "scenario"])[["return", "mean_sr", "min_zone_sr"]].mean().reset_index()
print(f"{'method':16s} {'mean_sr':>8s} {'gap_to_oracle':>14s} {'min_zone':>9s} {'gap':>7s}")
rows = [("ORACLE", o.mean_sr.mean(), 0, o.min_zone_sr.mean(), 0)]
for f, g in per.groupby("family"):
    g = g.set_index("scenario"); rows.append((f, g.mean_sr.mean(), (o.mean_sr - g.mean_sr).mean(), g.min_zone_sr.mean(), (o.min_zone_sr - g.min_zone_sr).mean()))
for r in sorted(rows, key=lambda r: -r[1]): print(f"{r[0]:16s} {r[1]:8.3f} {r[2]:14.3f} {r[3]:9.3f} {r[4]:7.3f}")
base = [r for r in rows if r[0] not in ("ORACLE", "ppo")]; b = max(base, key=lambda r: r[1])
print(f"\nceiling (mean) {o.ceiling.mean():.3f}; best non-PPO method {b[0]} {b[1]:.3f}; oracle headroom over it: mean {o.mean_sr.mean()-b[1]:.3f}, worst-zone {o.min_zone_sr.mean()-max(r[3] for r in base):.3f}")
print("GATE 1:", "PASS (headroom)" if (o.mean_sr.mean() - b[1] >= 0.02 or o.min_zone_sr.mean() - max(r[3] for r in base) >= 0.05) else "FAIL (no headroom -> C2+C3 core)")

r = ep.groupby(["family", "scenario"])["return"].mean().unstack(0); r["oracle"] = o["return"]
print("\nreturn (the objective): " + ", ".join(f"{k} {v:.2f}" for k, v in r.mean().sort_values(ascending=False).items() if k in ("oracle", "ppo", "ce_schedule", "random", "greedy_k2")))
print(f"oracle - ppo return: {(r.oracle - r.ppo).mean():.3f} (>=0 by construction if the oracle is valid); oracle - ce: {(r.oracle - r.ce_schedule).mean():.3f}")
```

## A13. `run_jobs.py` - Resumable job queue (18 lines)

```python
"""Cross-platform job queue (works on macOS, Linux and Windows; replaces `xargs`).
Usage: python run_jobs.py JOBFILE [N_PARALLEL]      (default N = cores - 1)
Each non-empty, non-# line of JOBFILE is a command line of arguments to `python`, e.g.:  train_variant.py ppo 0 300000
Set IWS_V2=1 in the environment first (see docs/PLAN_v1.md). A finished job writes its model file; rerunning skips jobs whose log says done."""
import sys, os, subprocess, time
from concurrent.futures import ThreadPoolExecutor
jobs = [l.strip() for l in open(sys.argv[1]) if l.strip() and not l.startswith("#")]
n = int(sys.argv[2]) if len(sys.argv) > 2 else max(1, (os.cpu_count() or 2) - 1)
os.makedirs("logs", exist_ok=True)
done_log = "logs/done_" + os.path.basename(sys.argv[1]) + ".txt"
done = set(open(done_log).read().splitlines()) if os.path.exists(done_log) else set()
def run(j):
    if j in done: return
    t = time.time(); r = subprocess.run([sys.executable] + j.split())
    if r.returncode == 0:
        with open(done_log, "a") as f: f.write(j + "\n")
    print(f"[{'ok' if r.returncode == 0 else 'FAILED'}] {j} ({time.time()-t:.0f}s)", flush=True)
with ThreadPoolExecutor(n) as ex: list(ex.map(run, jobs))
```

## A14. `check_setup.py` - Setup sanity test (17 lines)

```python
"""Quick setup check (~10 s). Run: python check_setup.py"""
import sys, time, warnings
warnings.filterwarnings("ignore")
print("Python", sys.version.split()[0])
import wntr, gymnasium, stable_baselines3, torch
print("wntr", wntr.__version__, "| gymnasium", gymnasium.__version__,
      "| sb3", stable_baselines3.__version__, "| torch", torch.__version__)
from gymnasium.utils.env_checker import check_env
from iws_env import IWSEnv
env = IWSEnv()
check_env(env, skip_render_check=True)
print("check_env passed | demand nodes", env.J, "| zones", [int(m.sum()) for m in env.zone_masks])
obs, _ = env.reset(seed=0); t = time.time(); done = False
while not done:
    obs, r, done, _, info = env.step(env.action_space.n - 1)
print("one 72-hour episode: %.2fs | mean supply ratio %.3f" % (time.time() - t, info["mean_sr"]))
print("SETUP OK")
```

## A15. `hyd_probe.py` - Diagnostic: do hydraulics bind? (15 lines)

```python
"""Does opening all zones at once starve the network hydraulically? hyd_fill = delivered/requested (1.0 = hydraulics never limit)."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np
from iws_env import IWSEnv
for scale in (1, 3, 6, 10, 15):
    row = []
    for name, act in (("all-open", 15), ("1 zone", 1)):
        env = IWSEnv(demand_scale=scale, supply_range=(1.5, 1.5), tank_days=(0.05, 0.05), alpha=4.0)
        fills, pm = [], []
        for sd in range(3):
            env.reset(seed=sd); d = False
            while not d: _, _, d, _, info = env.step(act); pm.append(env.last_p[env.last_p > 0].mean() if (env.last_p > 0).any() else np.nan)
            fills.append(info["hyd_fill"])
        row.append(f"{name}: fill={np.mean(fills):.2f} pressure={np.nanmean(pm):.0f}m")
    print(f"demand_scale={scale:2d}  " + " | ".join(row))
```

## A16. `cap_study.py` - Diagnostic: hourly source cap study (17 lines)

```python
"""Does a per-hour source cap make zone scheduling matter? Evaluates baselines under several caps and supply levels."""
import sys, warnings; warnings.filterwarnings("ignore")
from multiprocessing import Pool
from baselines import all_open, random_policy, make_rota, make_greedy, evaluate
from eval_all import priv_greedy
P = {"all_open": all_open, "random": random_policy, "rota_k1": make_rota(1), "greedy_k1": make_greedy(1), "greedy_k2": make_greedy(2), "priv_greedy": priv_greedy}
CAPS = (None, 2.0, 1.5, 1.2); SUPS = ((0.3, 0.5), (0.5, 0.9))
def job(a):
    cap, sup, name = a
    m = evaluate(P[name], range(10000, 10020), {"source_cap": cap, "supply_range": sup})
    return cap, sup, name, m["mean_sr"], m["min_zone_sr"]
if __name__ == "__main__":
    jobs = [(c, s, n) for c in CAPS for s in SUPS for n in P]
    with Pool(9) as p: res = p.map(job, jobs)
    for c in CAPS:
        for s in SUPS:
            print(f"cap={c} supply={s}: " + "  ".join(f"{r[2]}={r[3]:.3f}/{r[4]:.3f}" for r in res if r[0] == c and r[1] == s))
```

## A17. `scale_study.py` - Diagnostic: demand-scale study (17 lines)

```python
"""Does a per-hour source cap make zone scheduling matter? Evaluates baselines under several caps and supply levels."""
import sys, warnings; warnings.filterwarnings("ignore")
from multiprocessing import Pool
from baselines import all_open, random_policy, make_rota, make_greedy, evaluate
from eval_all import priv_greedy
P = {"all_open": all_open, "random": random_policy, "rota_k1": make_rota(1), "greedy_k1": make_greedy(1), "greedy_k2": make_greedy(2), "priv_greedy": priv_greedy}
CAPS = (1, 6, 10); SUPS = ((0.3, 0.5), (0.5, 0.9))
def job(a):
    cap, sup, name = a
    m = evaluate(P[name], range(10000, 10020), {"demand_scale": cap, "supply_range": sup})
    return cap, sup, name, m["mean_sr"], m["min_zone_sr"]
if __name__ == "__main__":
    jobs = [(c, s, n) for c in CAPS for s in SUPS for n in P]
    with Pool(9) as p: res = p.map(job, jobs)
    for c in CAPS:
        for s in SUPS:
            print(f"cap={c} supply={s}: " + "  ".join(f"{r[2]}={r[3]:.3f}/{r[4]:.3f}" for r in res if r[0] == c and r[1] == s))
```

## A18. `scarce_diag.py` - Diagnostic: scarce-supply anomaly (15 lines)

```python
import sys, warnings, glob, collections
warnings.filterwarnings("ignore")
sys.path.insert(0,'.')
import numpy as np
from stable_baselines3 import PPO
from iws_env import IWSEnv
for cond,kw in [("default",{}),("scarce",{"supply_range":(0.3,0.5)})]:
    for p in sorted(glob.glob("models/ppo_*.zip"))[:13]:
        nf="noforecast" in p
        env=IWSEnv(**kw, **({"forecast":False} if nf else {})); m=PPO.load(p,device="cpu")
        obs,_=env.reset(seed=10000); done=False; acts=[]; ub=None
        while not done:
            a=int(m.predict(obs,deterministic=True)[0]); acts.append(a)
            obs,r,done,_,info=env.step(a)
        print(cond,p.split('/')[-1],collections.Counter(acts).most_common(4),round(info['mean_sr'],4),round(info['budget_used'],3))
```

## A19. `scarce_trace.py` - Diagnostic: scarce-supply trace (13 lines)

```python
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0,'.')
import numpy as np
from stable_baselines3 import PPO
from iws_env import IWSEnv
def trace(p):
    env=IWSEnv(supply_range=(0.3,0.5)); m=PPO.load(p,device="cpu"); obs,_=env.reset(seed=10000); d=False; out=[]
    while not d:
        a=int(m.predict(obs,deterministic=True)[0]); u0=env.log["delivered"]
        obs,r,d,_,i=env.step(a); out.append((a,round((env.log["delivered"]-u0)/env.day_volume*24,3)))
    return out
a=trace("models/ppo_s1.zip"); b=trace("models/ppo_noforecast_s2.zip")
print("hours with delivery>0: ",sum(x[1]>0 for x in a),sum(x[1]>0 for x in b))
print("first day, ppo_s1:",a[:24]); print("first day, nofc_s2:",b[:24])
```

## A20. `plots/make_plots.py` - M3: plots and results table (183 lines)

```python
"""Plots and results table for IWS-RL (M3, T3.3).  Only reads result files; never edits them.

Usage (defaults = current v2 results):
    python plots/make_plots.py
    python plots/make_plots.py --results-dir results_final --out-dir plots/final --baseline ce_schedule
Optional inputs (skipped with a message if the file is absent):
    --oracle      CSV with columns scenario, mean_sr, min_zone_sr           (default: <results-dir>/oracle.csv)
    --pareto      CSV with columns label, mean_sr, min_zone_sr [,mean_sr_lo, mean_sr_hi, min_zone_sr_lo, min_zone_sr_hi]
                  (e.g. M2's lambda / Lagrangian sweep, once it exists)
    --curves      glob of learning-curve CSVs with columns step, mean_sr (one file per seed)
"""
import argparse, glob, os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

p = argparse.ArgumentParser()
p.add_argument("--results-dir", default="results_v2", help="folder with summary.csv and episodes.csv")
p.add_argument("--summary", default=None, help="override path to summary.csv")
p.add_argument("--episodes", default=None, help="override path to episodes.csv")
p.add_argument("--oracle", default=None)
p.add_argument("--pareto", default=None)
p.add_argument("--curves", default=None)
p.add_argument("--out-dir", default="plots/out")
p.add_argument("--condition", default="default", help="condition used for the bar chart, scatter and table")
p.add_argument("--baseline", default="ce_schedule", help="method family that differences are measured against")
p.add_argument("--exclude-methods", default="", help="comma-separated families to hide")
p.add_argument("--include-scarce", action="store_true", help="keep the degenerate 'scarce' condition in the heatmap")
p.add_argument("--lambda-sweep", action="store_true", help="draw the PPO lambda sweep from summary.csv (families ppo_lam*)")
a = p.parse_args()

summary_path = a.summary or os.path.join(a.results_dir, "summary.csv")
episodes_path = a.episodes or os.path.join(a.results_dir, "episodes.csv")
oracle_path = a.oracle or os.path.join(a.results_dir, "oracle.csv")
os.makedirs(a.out_dir, exist_ok=True)

if not os.path.exists(summary_path):
    sys.exit(f"missing {summary_path} (use --results-dir or --summary)")
S = pd.read_csv(summary_path)
hide = {x for x in a.exclude_methods.split(",") if x}
S = S[~S.family.isin(hide)]
if a.condition not in set(S.condition):
    sys.exit(f"condition '{a.condition}' not in {summary_path}; available: {sorted(set(S.condition))}")

LABEL = {"ppo": "PPO", "ce_schedule": "Old CE schedule (under-tuned)", "ce_tuned": "Tuned fixed schedule",
         "ppo_lam0": "PPO λ=0", "ppo_lam0.5": "PPO λ=0.5", "ppo_lam2": "PPO λ=2", "ppo_lam4": "PPO λ=4", "greedy_k1": "Greedy k1", "greedy_k2": "Greedy k2",
         "priv_greedy_k1": "Privileged greedy", "random": "Random", "all_open": "All open", "rota_k1": "Rota k1",
         "dqn": "DQN", "ppo_noequity": "PPO no-equity", "ppo_noforecast": "PPO no-forecast",
         "rec": "LSTM PPO", "rec_dr": "LSTM PPO + DR", "ppo_dr": "PPO + DR", "a2c": "A2C", "ppo_long": "PPO 500k"}
lab = lambda f: LABEL.get(f, f)
PRIV = {"priv_greedy_k1"}                       # uses hidden info: draw hatched / flag in table
saved = []


def save(fig, name):
    path = os.path.join(a.out_dir, name); fig.savefig(path, dpi=160, bbox_inches="tight"); plt.close(fig); saved.append(path)


D = S[S.condition == a.condition].sort_values("mean_sr", ascending=False)

# 1. bar chart with 95% CI: mean supply and worst-zone supply
fig, axs = plt.subplots(1, 2, figsize=(11, 4.2), sharey=False)
for ax, k, title in zip(axs, ["mean_sr", "min_zone_sr"], ["Mean supply ratio", "Worst-zone supply ratio"]):
    d = D.sort_values(k, ascending=True)
    err = np.vstack([d[k] - d[k + "_lo"], d[k + "_hi"] - d[k]])
    bars = ax.barh([lab(f) for f in d.family], d[k], xerr=err, color="#4C78A8", capsize=2)
    for b, f in zip(bars, d.family):
        if f in PRIV: b.set_hatch("//"); b.set_alpha(0.6)
        if f == a.baseline: b.set_color("#F58518")
    ax.set_title(f"{title} ({a.condition})"); ax.set_xlim(max(0, d[k].min() - 0.08), min(1, d[k].max() + 0.05))
    ax.grid(axis="x", alpha=.3)
fig.suptitle("Higher is better. Error bars: 95% bootstrap CI over scenarios. Hatched = uses hidden tank levels (not deployable). Orange = baseline.", fontsize=8)
save(fig, "bars_ci.png")

# 2. mean vs worst-zone scatter (+ oracle if available)
fig, ax = plt.subplots(figsize=(6.2, 5))
for _, r in D.iterrows():
    ax.errorbar(r.mean_sr, r.min_zone_sr, xerr=[[r.mean_sr - r.mean_sr_lo], [r.mean_sr_hi - r.mean_sr]],
                yerr=[[r.min_zone_sr - r.min_zone_sr_lo], [r.min_zone_sr_hi - r.min_zone_sr]], fmt="o" if r.family not in PRIV else "s",
                capsize=2, label=lab(r.family))
    ax.annotate(lab(r.family), (r.mean_sr, r.min_zone_sr), textcoords="offset points", xytext=(4, 4), fontsize=7)
if os.path.exists(oracle_path):
    o = pd.read_csv(oracle_path)
    ax.scatter([o.mean_sr.mean()], [o.min_zone_sr.mean()], marker="*", s=160, c="k", zorder=5)
    ax.annotate("Oracle (30 scen., uses future info)", (o.mean_sr.mean(), o.min_zone_sr.mean()), textcoords="offset points", xytext=(4, -10), fontsize=7)
else:
    print(f"[skip] oracle point: {oracle_path} not found")
ax.set_xlabel("Mean supply ratio"); ax.set_ylabel("Worst-zone supply ratio"); ax.set_title(f"Efficiency vs equity ({a.condition})"); ax.grid(alpha=.3)
save(fig, "scatter_mean_vs_worst.png")

# 2b. lambda sweep straight from summary.csv (families ppo_lam0, ppo_lam0.5, ppo (=lambda 1), ppo_lam2, ppo_lam4)
if a.lambda_sweep:
    LAM = [("ppo_lam0", 0.0), ("ppo_lam0.5", 0.5), ("ppo", 1.0), ("ppo_lam2", 2.0), ("ppo_lam4", 4.0)]
    L = D.set_index("family"); pts = [(lm, L.loc[f]) for f, lm in LAM if f in L.index]
    if len(pts) >= 3:
        fig, ax = plt.subplots(figsize=(6.4, 5))
        xs = [r.mean_sr for _, r in pts]; ys = [r.min_zone_sr for _, r in pts]
        ax.plot(xs, ys, "-", color="#999", zorder=1)
        for lm, r in pts:
            ax.errorbar(r.mean_sr, r.min_zone_sr, xerr=[[r.mean_sr - r.mean_sr_lo], [r.mean_sr_hi - r.mean_sr]],
                        yerr=[[r.min_zone_sr - r.min_zone_sr_lo], [r.min_zone_sr_hi - r.min_zone_sr]], fmt="o", color="#4C78A8", capsize=2, zorder=2)
            ax.annotate(f"λ={lm:g} ({int(r.n_seeds)} seeds)", (r.mean_sr, r.min_zone_sr), textcoords="offset points", xytext=(5, -11), fontsize=7)
        for f, nm, c in [(a.baseline, lab(a.baseline), "#F58518"), ("dqn", "DQN", "#54A24B"), ("ppo_dr", "PPO + DR", "#B279A2")]:
            if f in L.index:
                r = L.loc[f]; ax.errorbar(r.mean_sr, r.min_zone_sr, xerr=[[r.mean_sr - r.mean_sr_lo], [r.mean_sr_hi - r.mean_sr]],
                                          yerr=[[r.min_zone_sr - r.min_zone_sr_lo], [r.min_zone_sr_hi - r.min_zone_sr]], fmt="s", color=c, capsize=2)
                ax.annotate(nm, (r.mean_sr, r.min_zone_sr), textcoords="offset points", xytext=(5, 4), fontsize=7)
        ax.set_xlabel("Mean supply ratio"); ax.set_ylabel("Worst-zone supply ratio")
        ax.set_title(f"Equity weight λ in the PPO reward ({a.condition}); a reward penalty, not a constraint", fontsize=8); ax.grid(alpha=.3)
        save(fig, "pareto_lambda.png")
    else:
        print("[skip] lambda sweep: fewer than 3 lambda families in summary")

# 3. pareto from an external sweep (M2), if given
if a.pareto:
    if os.path.exists(a.pareto):
        P = pd.read_csv(a.pareto); need = {"label", "mean_sr", "min_zone_sr"}
        if need <= set(P.columns):
            fig, ax = plt.subplots(figsize=(6.2, 5))
            for _, r in P.iterrows():
                xe = [[r.mean_sr - r.mean_sr_lo], [r.mean_sr_hi - r.mean_sr]] if "mean_sr_lo" in P else None
                ye = [[r.min_zone_sr - r.min_zone_sr_lo], [r.min_zone_sr_hi - r.min_zone_sr]] if "min_zone_sr_lo" in P else None
                ax.errorbar(r.mean_sr, r.min_zone_sr, xerr=xe, yerr=ye, fmt="o", capsize=2); ax.annotate(str(r.label), (r.mean_sr, r.min_zone_sr), textcoords="offset points", xytext=(4, 4), fontsize=7)
            ax.set_xlabel("Mean supply ratio"); ax.set_ylabel("Worst-zone supply ratio"); ax.set_title("Equity trade-off sweep"); ax.grid(alpha=.3)
            save(fig, "pareto.png")
        else:
            print(f"[skip] pareto: {a.pareto} needs columns {sorted(need)}")
    else:
        print(f"[skip] pareto: {a.pareto} not found")

# 4. regime heatmap: paired difference vs baseline per condition (from episodes.csv, per-scenario pairing)
if os.path.exists(episodes_path):
    E = pd.read_csv(episodes_path)
    E["family"] = E.family if "family" in E else E.method.str.replace(r"_s\d+$", "", regex=True)
    E = E[~E.family.isin(hide)]
    if not a.include_scarce: E = E[E.condition != "scarce"]
    if a.baseline not in set(E.family):
        print(f"[skip] heatmap: baseline '{a.baseline}' not in episodes")
    else:
        per = E.groupby(["condition", "family", "scenario"])[["mean_sr", "min_zone_sr"]].mean().reset_index()
        for k, fn in [("mean_sr", "heatmap_mean_vs_baseline.png"), ("min_zone_sr", "heatmap_worst_vs_baseline.png")]:
            base = per[per.family == a.baseline].set_index(["condition", "scenario"])[k]
            per["d"] = per.apply(lambda r: r[k] - base.get((r.condition, r.scenario), np.nan), axis=1)
            M = per[per.family != a.baseline].groupby(["family", "condition"]).d.mean().unstack()
            M = M.loc[M.mean(axis=1).sort_values(ascending=False).index]
            fig, ax = plt.subplots(figsize=(1.0 + 0.95 * M.shape[1], 0.9 + 0.45 * M.shape[0]))
            v = np.nanmax(np.abs(M.values)); im = ax.imshow(M.values, cmap="RdBu", vmin=-v, vmax=v, aspect="auto")
            ax.set_xticks(range(M.shape[1])); ax.set_xticklabels(M.columns, rotation=45, ha="right", fontsize=8)
            ax.set_yticks(range(M.shape[0])); ax.set_yticklabels([lab(f) for f in M.index], fontsize=8)
            for i in range(M.shape[0]):
                for j in range(M.shape[1]): ax.text(j, i, f"{M.values[i, j]:+.3f}", ha="center", va="center", fontsize=6.5)
            ax.set_title(f"{k}: method minus {lab(a.baseline)} (paired means; blue = better than baseline)", fontsize=8)
            fig.colorbar(im, ax=ax, shrink=0.8); save(fig, fn)
else:
    print(f"[skip] heatmaps: {episodes_path} not found")

# 5. learning curves, if provided
if a.curves:
    files = sorted(glob.glob(a.curves))
    if files:
        fig, ax = plt.subplots(figsize=(6.5, 4.2)); ok = 0
        for f in files:
            c = pd.read_csv(f)
            if {"step", "mean_sr"} <= set(c.columns): ax.plot(c.step, c.mean_sr, alpha=.7, label=os.path.basename(f)); ok += 1
            else: print(f"[skip] curve {f}: needs columns step, mean_sr")
        if ok: ax.set_xlabel("Training steps"); ax.set_ylabel("Mean supply ratio (eval)"); ax.legend(fontsize=6); ax.grid(alpha=.3); save(fig, "learning_curves.png")
        else: plt.close(fig)
    else:
        print(f"[skip] curves: no files match {a.curves}")

# 6. results table (markdown + csv) for the chosen condition
cols = ["family", "n_seeds", "mean_sr", "mean_sr_lo", "mean_sr_hi", "min_zone_sr", "min_zone_sr_lo", "min_zone_sr_hi", "jain_zone" if "jain_zone" in D else "gini_node"]
T = D[[c for c in cols if c in D]].copy(); T.insert(1, "uses_hidden_info", T.family.isin(PRIV))
T.to_csv(os.path.join(a.out_dir, "results_table.csv"), index=False)
md = ["| Method | seeds | mean supply [95% CI] | worst zone [95% CI] | hidden info |", "|---|---|---|---|---|"]
for _, r in T.iterrows():
    md.append(f"| {lab(r.family)} | {int(r.n_seeds)} | {r.mean_sr:.3f} [{r.mean_sr_lo:.3f}, {r.mean_sr_hi:.3f}] | "
              f"{r.min_zone_sr:.3f} [{r.min_zone_sr_lo:.3f}, {r.min_zone_sr_hi:.3f}] | {'yes' if r.uses_hidden_info else ''} |")
open(os.path.join(a.out_dir, "results_table.md"), "w", encoding="utf-8").write(f"Condition: {a.condition}. Source: {summary_path}\n\n" + "\n".join(md) + "\n")
saved += [os.path.join(a.out_dir, "results_table.csv"), os.path.join(a.out_dir, "results_table.md")]
print("wrote:\n  " + "\n  ".join(saved))
```

## A21. `plots/train_curves.py` - M3: learning-curve training (53 lines)

```python
"""Learning curve for PPO on the v2 environment (M3). Same hyper-parameters as train_variant.py `ppo`; the only addition is
an evaluation every EVAL_EVERY steps on 10 fixed TEST scenarios (seeds 10000-10009, never trained on), deterministic policy.
Usage: IWS_V2=1 python plots/train_curves.py SEED [STEPS=300000] [OUT_DIR=.]
Writes OUT_DIR/curve_sSEED.csv (rewritten after every evaluation, so a crash keeps the partial curve) and
OUT_DIR/curve_model_sSEED.zip (latest checkpoint). Does not touch models_v2/.
Note: same seed + same settings as train_variant.py, so the end of curve_s0/1/2 should be close to models_v2/ppo_s0/1/2."""
import sys, os, time, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd, torch
torch.set_num_threads(1)
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import DummyVecEnv
from iws_env import IWSEnv
from v2cfg import BASE

EVAL_EVERY = 20_000
EVAL_SEEDS = range(10000, 10010)


class CurveCallback(BaseCallback):
    def __init__(self, out_csv, ckpt, eval_env):
        super().__init__(); self.out_csv, self.ckpt, self.env = out_csv, ckpt, eval_env; self.rows = []; self.next = 0

    def evaluate(self):
        R, M, W = [], [], []
        for s in EVAL_SEEDS:
            o, _ = self.env.reset(seed=s); d = False; ret = 0.0
            while not d:
                o, r, d, _, info = self.env.step(int(self.model.predict(o, deterministic=True)[0])); ret += r
            R.append(ret); M.append(info["mean_sr"]); W.append(info["min_zone_sr"])
        self.rows.append({"step": self.num_timesteps, "return": np.mean(R), "mean_sr": np.mean(M), "min_zone_sr": np.mean(W)})
        pd.DataFrame(self.rows).to_csv(self.out_csv, index=False); self.model.save(self.ckpt)
        print(f"step {self.num_timesteps} mean_sr {np.mean(M):.3f} min_zone {np.mean(W):.3f} return {np.mean(R):.2f}", flush=True)

    def _on_step(self): return True

    def _on_rollout_end(self):
        if self.num_timesteps >= self.next:
            self.evaluate(); self.next += EVAL_EVERY


if __name__ == "__main__":
    seed = int(sys.argv[1]); steps = int(sys.argv[2]) if len(sys.argv) > 2 else 300_000
    out = sys.argv[3] if len(sys.argv) > 3 else "."; os.makedirs(out, exist_ok=True)
    venv = make_vec_env(lambda: IWSEnv(**BASE), n_envs=8, seed=seed, vec_env_cls=DummyVecEnv)
    model = PPO("MlpPolicy", venv, n_steps=216, batch_size=432, n_epochs=10, gamma=0.99,
                gae_lambda=0.95, ent_coef=0.01, learning_rate=3e-4, seed=seed, verbose=0, device="cpu")
    cb = CurveCallback(os.path.join(out, f"curve_s{seed}.csv"), os.path.join(out, f"curve_model_s{seed}.zip"), IWSEnv(**BASE))
    t = time.time(); model.learn(steps, callback=cb); cb.evaluate()
    print(f"seed {seed} steps {steps} done in {time.time()-t:.0f}s", flush=True)
```
