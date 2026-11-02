# IWS-RL: equity-aware RL for intermittent water supply

**Project status (2026-11-02):** experiments are finished on the harder v2 environment (`IWS_V2=1`, demand x8). Headline: a tuned fixed daily schedule is hard to beat when conditions match what it was tuned for; RL (DQN, domain-randomised PPO) beats it when conditions shift (demand surge, small tanks, scarce supply); the equity weight gives a controllable fairness trade-off. Details: `understanding.pdf` and the "Results v2" table below. The v1 results further down are kept for the record but are superseded (v1 was saturated).
Remaining: slides and rehearsal, and the full-text literature check (`docs/VERIFY_PAPERS.md`, background in `docs/reference/iws-rl-literature-audit.md`).

## START HERE (for teammates)
1. **What is this?** A city water network gives each of 4 zones water only some hours per day. An RL agent decides every hour which zones get water. Households have roof tanks we cannot see. Goal: serve as much demand as possible *and* keep the worst-off zone from being starved (equity).
2. **Read in this order:** this README -> `understanding.pdf` (whole story, sources, results) -> `docs/PROJECT_LOG.md` (what we did, and why, in order; starts with a current-state summary) -> `docs/PLAN_v1.md` (who does what) -> `docs/reference/iws-rl-literature-audit.md` (literature and novelty check). Old numbers: `results/RESULTS_SUMMARY.md` (v1). `docs/ROADMAP.md` is the original improvement list, now annotated with what was done.
3. **Run it yourself:**
```
python3.12 -m venv venv && source venv/bin/activate
pip install -r requirements.txt          # needs Python 3.11 or 3.12
python check_setup.py                    # quick sanity test
python eval_all.py                       # v1 evaluation (~15 min on 10 cores) -> results/
IWS_V2=1 python eval_all.py              # v2 evaluation (~40 min on 10 cores) -> results_v2/ (use IWS_V2=1 for everything v2)
IWS_V2=1 python analyze_final.py         # paired CIs vs the tuned schedule + figures -> results_v2/
python train_variant.py ppo 0 150000     # train one model (~10 min) -> models/ppo_s0.zip
```
4. **Key files:** `iws_env.py` (the environment), `baselines.py` (non-learning policies), `train_variant.py` (PPO/DQN/A2C and ablations), `bo_schedule.py` (optimised fixed daily schedule), `eval_all.py` (all methods x 11 conditions), `scarce_diag.py`/`scarce_trace.py` (explain the scarce-supply anomaly).
5. **Result files:** `results/summary.csv` (per method and condition, with 95% confidence intervals), `results/paired_vs_greedy.csv` (differences vs the best simple baseline), `results/episodes.csv` (every episode), `results/v1/` (first round, before the extra baselines).

## Results v2 (the results to present; default test set; higher is better)
Source: `results_v2/summary.csv`; paired CIs in `results_v2/paired_vs_ce_tuned.csv`; figures in `results_v2/figs/`. Seeds: PPO 5, PPO+DR 5, DQN 5, no-equity 5, tuned schedule 3 (CE 40 iterations, population 60), lambda sweep 2-3 per point (506 evaluation jobs, 27,600 episodes).
| Method | return | mean_sr | worst-zone sr |
|---|---|---|---|
| Clairvoyant oracle (30 scenarios, not deployable) | -8.49 | 0.725 | 0.631 |
| Tuned fixed daily schedule (`ce_tuned`) | -9.15 | 0.716 | 0.630 |
| PPO | -9.67 | 0.716 | 0.601 |
| PPO + domain randomisation | -9.92 | 0.711 | 0.612 |
| No-equity PPO | -10.14 | 0.718 | 0.564 |
| DQN | -10.02 | 0.714 | 0.590 |
| Old (under-tuned) fixed schedule | -10.05 | 0.708 | 0.612 |
| LSTM PPO (`rec`) | -11.24 | 0.702 | 0.573 |
| Random | -14.33 | 0.672 | 0.527 |
Under shift (return): alpha=2 DQN -8.80, PPO+DR -9.15 vs tuned schedule -10.81; small tanks DQN -16.48 (significantly better) and PPO+DR -17.57 (tie) vs -17.62. The tuned schedule is significantly better than RL in most other conditions.
Fairness sweep (PPO, lambda 0 / 0.5 / 1 / 2 / 4): worst-zone 0.573 / 0.586 / 0.601 / 0.598 / 0.635, mean supply 0.718 / 0.716 / 0.716 / 0.712 / 0.708.
Claims we may NOT make (from the literature audit): "first/novel" without "in our search"; "RL beats optimised schedules" without "under the shifts we tested"; "constrained/Lagrangian RL" (our lambda is a reward penalty); results transfer to real networks.

## Results v1 (superseded: v1 was saturated, PPO at 99% of the supply ceiling; kept for the record)
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

## Known problems (status at 2 Nov)
**Fixed in v2 or by the evaluation:** scarce supply degenerate (env diagnosed; judge scarce on worst-zone only), pressure thresholds not binding (v2: they matter), fragile at alpha=2 (domain randomisation addresses it), under-tuned fixed schedule (retuned).
**Still true:**
- (v1) **Scarce supply is degenerate:** the budget is spent in ~3 hours, so every policy gives the same result. Do not read those rows as evidence.
- (v1) **Pressure thresholds don't matter:** 10/20/30 m give identical results, so the hydraulics are not binding.
- (v1) **Fragile to a changed surge cap:** at alpha=2, PPO (0.723) is worse than random (0.759).
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
| `v2cfg.py` | Switches everything to the v2 environment when `IWS_V2=1` (demand x8, `models_v2/`, `results_v2/`). |
| `train_variant.py` | Trains PPO, DQN, A2C and variants (no-equity, no-forecast, domain randomisation `ppo_dr`, lambda sweep `ppo_lam*`). `IWS_V2=1 python train_variant.py ppo 0 300000` |
| `train_rec.py` | Recurrent (LSTM) PPO: variants `rec`, `rec_dr`. |
| `bo_schedule.py` / `bo_schedule_tuned.py` | Cross-entropy search for a fixed daily 24x4 valve schedule. The first is the old under-tuned one (12 iterations); the second is the tuned one (`python bo_schedule_tuned.py 40 60 SEED` -> `results_v2/ce_tuned_sSEED.npy`). Both are CE search, not Bayesian optimisation. |
| `oracle.py`, `gate1.py` | Clairvoyant oracle (per-scenario search over the 72-step action sequence; hindsight upper bound) and the Gate 1 headroom check. |
| `analyze_final.py` | Paired bootstrap CIs vs the tuned schedule and the Pareto/regime-map figures. |
| `run_jobs.py` | Resumable job queue: `python run_jobs.py JOBFILE [N_PARALLEL]`. Job files: `jobs_M1_v1.txt` (v1 overnight), `jobs_v2.txt`, `jobs_v2_laptopC.txt`, `jobs_M1_pareto.txt` (lambda sweep), `jobs_M2_v1.txt` (no-equity and DQN), `jobs_M1_seeds.txt` (extra seeds), `jobs_M3_v1.txt` (optional PPO seeds 5-9, not run), `jobs.txt` and `jobs2.txt` (first v1 batches). |
| `jobs_chain.sh`, `chain2.sh`, `chain3.sh` | One-off shell chains that ran queued jobs then evaluations unattended on the MacBook. Not needed to reproduce results. |
| `cap_study.py`, `scale_study.py`, `hyd_probe.py`, `scarce_diag.py`, `scarce_trace.py` | Diagnostic studies behind the v2 environment (supply ceiling, demand scale, hydraulic probe, scarce-supply anomaly). |
| `docs/` | `PROJECT_LOG.md` (chronological log), `PLAN_v1.md` (3-person plan), `GIT_GUIDE.md`, `ROADMAP.md`, `understanding_source.md` -> `understanding.pdf`, `reference/` (external review and literature audit). `TEAM_PLAN.md` is superseded by `PLAN_v1.md`. |

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
