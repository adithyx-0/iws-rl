# IWS-RL: equity-aware RL for intermittent water supply

**Project status (2026-11-01):** environment, baselines, PPO/DQN/A2C training and a full evaluation are done. Next: improve the environment and add a method contribution (see `docs/ROADMAP.md`).

## START HERE (for teammates)
1. **What is this?** A city water network gives each of 4 zones water only some hours per day. An RL agent decides every hour which zones get water. Households have roof tanks we cannot see. Goal: serve as much demand as possible *and* keep the worst-off zone from being starved (equity).
2. **Read in this order:** this README -> `results/RESULTS_SUMMARY.md` (numbers) -> `docs/PROJECT_LOG.md` (what we did, and why, in order) -> `docs/ROADMAP.md` (what we plan next).
3. **Run it yourself:**
```
python3.12 -m venv venv && source venv/bin/activate
pip install -r requirements.txt          # needs Python 3.11 or 3.12
python check_setup.py                    # quick sanity test
python eval_all.py                       # re-runs the full evaluation (~15 min on 10 cores) -> results/
python train_variant.py ppo 0 150000     # train one model (~10 min) -> models/ppo_s0.zip
```
4. **Key files:** `iws_env.py` (the environment), `baselines.py` (non-learning policies), `train_variant.py` (PPO/DQN/A2C and ablations), `bo_schedule.py` (optimised fixed daily schedule), `eval_all.py` (all methods x 11 conditions), `scarce_diag.py`/`scarce_trace.py` (explain the scarce-supply anomaly).
5. **Result files:** `results/summary.csv` (per method and condition, with 95% confidence intervals), `results/paired_vs_greedy.csv` (differences vs the best simple baseline), `results/episodes.csv` (every episode), `results/v1/` (first round, before the extra baselines).

## Results so far (default test set, mean supply ratio; higher is better)
| Method | mean_sr | worst-zone sr |
|---|---|---|
| PPO (500k steps, 5 seeds) | 0.767 | 0.737 |
| PPO (150k steps, 5 seeds) | 0.766 | 0.735 |
| Privileged greedy (reads hidden tank levels; not realistic) | 0.766 | 0.736 |
| PPO without equity reward | 0.763 | 0.724 |
| PPO without budget forecast | 0.763 | 0.727 |
| Optimised fixed daily schedule | 0.759 | 0.712 |
| DQN (3 seeds) | 0.753 | 0.691 |
| Greedy (most-deprived-first) | 0.737 | 0.658 |
| Random | 0.701 | 0.618 |
| A2C (untuned, failed) | 0.440 | 0.143 |

**Honest reading:** PPO beats the best simple baseline by +0.029 (CI 0.026-0.032) but the optimised fixed schedule is only 0.007 behind. PPO just ties the privileged greedy. Longer training and the forecast feature add nothing; the equity term helps the worst zone slightly.

## Known problems (we are fixing these)
- **Scarce supply is degenerate:** the budget is spent in ~3 hours, so every policy gives the same result. Do not read those rows as evidence.
- **Pressure thresholds don't matter:** 10/20/30 m give identical results, so the hydraulics are not binding.
- **Fragile to a changed surge cap:** at alpha=2, PPO (0.723) is worse than random (0.759).
- Tank sizes, surge factor and thresholds are assumptions, not measured data. Everything is simulation only.
- SAC not run (the action space is discrete); the literature check read only titles/snippets.

---

## Technical documentation (original)
Everything runs from free, pip-installable software. No external dataset is needed:
the water network (EPANET `Net3.inp`) ships inside the `wntr` package.

## Install
```
pip install wntr gymnasium stable-baselines3
```
(CPU-only PyTorch is enough: `pip install torch --index-url https://download.pytorch.org/whl/cpu` first saves ~2 GB.)

## Files
| File | What it does |
|---|---|
| `iws_env.py` | Gymnasium environment. Hourly zone open/close decisions on Net3 with EPANET pressure-dependent hydraulics, household roof tanks, a daily source budget, and an equity term in the reward. `python iws_env.py` runs Gymnasium's `check_env` plus one episode. |
| `baselines.py` | Random, all-open, fixed rota (k zones at a time), and most-deprived-first greedy. `python baselines.py` evaluates them on 30 fixed scenarios (seeds 10000–10029). |
| `train_ppo.py` | PPO (Stable-Baselines3) with 8 parallel environments; evaluates on the same 30 scenarios every 20% of training. `python train_ppo.py 150000 0` |

## Environment summary
- **Network:** Net3 (92 junctions, 59 with demand, 2 sources, 2 pumps, 3 network tanks). Controls removed; one EPANET snapshot per hour.
- **Zones:** 4 zones from k-means on node coordinates (11/16/16/16 demand nodes).
- **Action:** `Discrete(16)`, one bit per zone (open/closed this hour). Closed zone = its consumers are cut off.
- **Household storage:** each demand node has a roof tank of 0.3–0.8 days of consumption (random per episode). An open node requests `min(4 × mean demand, refill need + current use)`, which is the tank-filling surge. EPANET PDD (required 20 m, minimum 2 m) decides how much actually arrives.
- **Shortage:** daily source volume = 50–90% of total daily consumption (random per day), known one day ahead.
- **Observation (24 values):** per zone mean pressure, inflow, supply ratio so far today, hours since last supply; hour of day (sin/cos), budget left today, tomorrow's budget, episode progress, 3 network tank levels. Household tank levels are hidden (the utility cannot see them).
- **Reward:** −(unmet consumption this hour) / (mean hourly consumption), plus at the end of each day `λ · (worst zone's supply ratio) · 24 / Z`.
- **Episode:** 3 days = 72 steps; ~12 ms per step on one CPU core.

## Metrics reported
`mean_sr` (fraction of desired consumption actually served), `min_zone_sr` (worst zone), `p10_node_sr` (10th-percentile node), `gini_node` (inequality across nodes; lower is fairer).

## Assumptions to state in the report
Zone closure modelled as consumer cut-off rather than a physical valve on a main; pipe filling and draining not modelled (EPANET limitation); household tank sizes, surge factor, and pressure thresholds are assumed and should be swept in a sensitivity study.
