# IWS-RL: Equity-aware RL for intermittent water supply scheduling

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
