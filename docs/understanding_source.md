# IWS-RL: understanding the project (edition 1, 1 Nov 2026)

Repo: https://github.com/adithyx-0/iws-rl  |  Plan for the next 30 hours: `docs/PLAN_v1.md`  |  Full history: `docs/PROJECT_LOG.md`

This document explains, for anyone on the team, what we are doing, why, where every idea came from, what we found, and what is still open. It is updated at each real milestone (see the update log at the end).

## 1. The project in one paragraph
In many cities (e.g. Indian cities) piped water arrives only a few hours per day. A utility opens valves zone by zone. Households keep roof tanks to survive the gaps, and the utility cannot see how full those tanks are. We built a simulator (EPANET hydraulics via the WNTR package, network Net3, 4 zones) and trained reinforcement-learning agents to decide every hour which zones get water, aiming to serve as much demand as possible while protecting the worst-off zone (equity). We compare the agents with simple rules, an optimised fixed daily schedule, and (soon) a clairvoyant oracle.

## 2. How we got here (chronology)
1. Early October: the first project was SafeCharge-RL (EV charging). It is finished to a large extent and pushed on GitHub, but the faculty said EV charging is too common.
2. 30 Oct: we shelved it and searched for a new topic. An earlier Claude had written candidate files (`01`-`07`, about a *different* project: exam-aware study scheduling). I eliminated all 12 candidates against the other teams' topics (Excel sheet from the course).
3. 30-31 Oct: you brought `iws-rl.zip` (intermittent water supply), built by another Claude (Opus). We trained PPO, DQN and ablations and ran a full evaluation (v1 results).
4. 1 Nov: we found the v1 environment was too easy (see section 5), built the harder v2 environment, put everything on GitHub, and an external review (`docs/reference/improvements_for_ref.md`) sharpened the plan.
5. 1-2 Nov: three-laptop sprint (`docs/PLAN_v1.md`) to finish and present.

## 3. Where each idea came from
| Idea / component | Source | Status |
|---|---|---|
| Topic: equity-aware RL for intermittent water supply (IWS) | Other Claude (Opus) produced `iws-rl.zip`; we chose it after eliminating 12 earlier candidates | Adopted, faculty approval to be confirmed (Adithyan) |
| EPANET hydraulics, network Net3 | WNTR package (bundled example network), https://github.com/USEPA/WNTR | Tool |
| PPO, DQN, A2C implementations | Stable-Baselines3, https://github.com/DLR-RM/stable-baselines3 | Tool |
| Household roof tanks, daily budget, equity reward | Original `iws-rl.zip` design; values (tank 0.3-0.8 days, alpha=4) are **assumptions** | Needs cited ranges (Adithyan) |
| Privileged greedy (reads hidden tank levels) | Added by us as an upper-ish reference | Not a true oracle (scores below PPO on v2) |
| Optimised fixed daily schedule (CE search) | Added by us as the stand-in for Bayesian-optimisation schedules in the literature (Hendrickson & Sela) | Under-tuned; mislabelled as BO in code; being redone |
| Diagnosis: scarce supply is degenerate | Our own analysis (`scarce_diag.py`, `scarce_trace.py`) | Done |
| Hydraulics never bind in v1; demand_scale=8 gives v2 | Our own probes (`hyd_probe.py`, `scale_study.py`); the 4-8x peak-flow argument is our reasoning, not a citation | Done |
| Supply ceiling (mean supply can't exceed ~0.773 in v1) | External review `docs/reference/improvements_for_ref.md`; consistent with our scarce result 0.4754 vs ceiling 0.473 | Consistent; not independently re-derived by us |
| Adaptive policy: domain randomisation + recurrent (LSTM) policy | Same review; resembles rapid-motor-adaptation ideas in robotics (from memory, **verify before citing**) | Planned (C1) |
| Equity as constraint / Pareto front; generalised Gini | Same review; Siddique et al., ICML 2020 | Planned (C2) |
| Clairvoyant oracle for regret | Our design: env is deterministic given a seed, so optimise the full action sequence per scenario | Planned (Gate 1) |

## 4. Related work found so far
**Honesty note:** every item below was read as a title or abstract/snippet only (web search). None has been read in full yet; full reading is task T3.1. Do not quote them as fact before that.

### Closest to our problem (non-RL, equity in intermittent supply)
- Hendrickson & Sela, 2024: Bayesian optimisation of flow-control valve schedules for local supply and global equity, volume-driven demand with private tanks, 6 zones. https://doi.org/10.1016/j.scs.2024.105615 ; conference version https://www.mdpi.com/2673-4591/69/1/75  (our log earlier cited `69/1/184`, which may be wrong; to be checked)
- 2023 Water Supply, MINLP minimising supply inequity under hydraulic constraints: https://doaj.org/article/37953cf59e474f7687beb590577f3458
- Kurian et al. 2023, Water Supply, equitable supply in intermittently operated rural schemes: https://iwaponline.com/ws/article/23/11/4520/98117/Equitable-supply-in-intermittently-operated-rural
- UCSB intermittent-supply scheduling thesis: https://escholarship.org/uc/item/3xb4j737
- Bengaluru thesis on inequity under intermittent supply: https://etd.iisc.ac.in/handle/2005/5925
- Delhi/Bengaluru practice and equity discussion: https://www.indiawaterportal.org/health-and-sanitation/urban-sanitation/intermittent-water-distribution-networks-tale-two-cities

### RL for water networks (no equity, not intermittent supply)
- Hu et al. 2020, deep RL valve scheduling for contamination isolation: https://aimspress.com/aimspress-data/mbe/2020/1/PDF/mbe-17-01-006.pdf
- Multi-agent RL (MADDPG) for pump and valve scheduling: https://bohrium.dp.tech/paper/arxiv/2408.08442
- PPO for pump scheduling on a real network with 18 demand zones: https://arxiv.org/pdf/2310.09412
- DRL-EPANET (NeurIPS workshop 2022): https://mlanthology.org/neuripsw/2022/belfadil2022neuripsw-drlepanet
- RL for household storage and tariffs in smart water networks (IFIP Networking 2025): https://dl.ifip.org/db/conf/networking/networking2025/1571132384.pdf
- Deep RL for pumps in water distribution systems: https://arxiv.org/pdf/2010.06460
- Safe RL control for water networks (Aalborg): https://vbn.aau.dk/en/publications/safe-reinforcement-learning-control-for-water-distribution-networ-2

### Methods we may use (from the external review; not yet verified by us)
- Fair RL with generalised Gini welfare (Siddique et al., ICML 2020): https://arxiv.org/pdf/2008.07773
- Expected-welfare training does not guarantee fairness (two 2026 arXiv papers): https://arxiv.org/pdf/2606.18111 and https://arxiv.org/pdf/2608.00175
- Past-discounting for Markovian fairness: https://arxiv.org/abs/2504.01154v2
- Asymmetric actor-critic / teacher-student with privileged information (Cai et al., NeurIPS 2024): https://arxiv.org/abs/2412.00985
- CVaR in RL (Tamar et al.): https://arxiv.org/pdf/1406.3339v3.pdf ; Predictive CVaR policy gradient: https://rlj.cs.umass.edu/2024/papers/RLJ_RLC_2024_81.pdf
- Safe RL tooling: Safety-Gymnasium https://arxiv.org/pdf/2310.12567 ; OmniSafe https://github.com/PKU-Alignment/omnisafe
- Intermittent supply background (Dehra Dun): https://sswm.info/node/1445

### Is it new?
Our searches (title/snippet level) found **no RL paper that combines intermittent supply, zone valve scheduling, equity and hidden household storage**. This is evidence of a gap, not proof. A proper audited novelty check is task T3.1. Also unconfirmed: a "Sept 2026 npj Clean Water equity paper" mentioned in an outside brief could not be found.

## 5. Results so far
### v1 environment (150k-500k steps, results in `results/`, summary `results/RESULTS_SUMMARY.md`)
| Method | mean supply | worst zone |
|---|---|---|
| PPO 500k (5 seeds) | 0.767 | 0.737 |
| PPO 150k (5 seeds) | 0.766 | 0.735 |
| Privileged greedy | 0.766 | 0.736 |
| PPO no equity / no forecast | 0.763 | 0.724 / 0.727 |
| Optimised fixed schedule | 0.759 | 0.712 |
| DQN | 0.753 | 0.691 |
| Greedy k=1 | 0.737 | 0.658 |
| Random | 0.701 | 0.618 |
| A2C (untuned, failed) | 0.440 | 0.143 |

What this means: v1 was **saturated**. Mean supply cannot exceed a ceiling of about 0.773 set by the daily water budget, and PPO reached 99% of it; the scarce-supply rows are an accounting identity (every model 0.4754 vs ceiling 0.473). Pressure thresholds of 10, 20, 30 m gave identical results because pressure stayed at 37-46 m (hydraulics never bound). PPO was also fragile: at surge factor alpha=2 it was worse than random.

### v2 environment (demand_scale=8, tag `env-v2`, results in `results_v2/`)
Hydraulic probe: at demand x8, opening all zones delivers only 54-73% of requested flow (pressure 13-18 m), one zone 90-99%.
| Method (default condition) | mean supply | worst zone |
|---|---|---|
| PPO (5 seeds, 300k) | 0.716 | 0.601 |
| Optimised fixed schedule (1 run) | 0.708 | 0.612 |
| Random | 0.672 | 0.527 |
| All open | 0.648 | 0.513 |
| Greedy k=2 | 0.648 | 0.589 |
| Privileged greedy | 0.639 | 0.494 |
| Greedy k=1 | 0.604 | 0.591 |
| Rota k=1 | 0.560 | 0.410 |

What this means: the sanity check passes (methods spread from 0.56 to 0.72; pressure thresholds now matter: 10 m 0.703, 20 m 0.716, 30 m 0.724). PPO beats greedy k=1 by +0.112 (CI 0.103-0.120). **But PPO is only about 0.008 ahead of the fixed schedule on mean supply and is worse on the worst zone**, so there is no clear RL win yet. The gap to the ceiling is about 0.057, which is the headroom an oracle may or may not be able to use (Gate 1). PPO-no-equity, DQN and A2C have not yet been run on v2.

## 6. Open problems and the plan
- No real upper bound yet -> clairvoyant oracle (Gate 1).
- No method contribution beyond environment + PPO -> C1 adaptive policy (domain randomisation + LSTM), C2 fairness Pareto front, C3 regime map (see `docs/PLAN_v1.md`).
- Fixed-schedule baseline is under-tuned and wrongly named (cross-entropy search, not Bayesian optimisation).
- No learning curves; single network; tank sizes and surge factor are assumptions; everything is simulation.
- Related work not yet read in full; faculty approval of the topic not yet confirmed.

## 7. Where things are in the repo
- `README.md` start here; `docs/PROJECT_LOG.md` chronological findings; `docs/PLAN_v1.md` the three-laptop plan; `docs/GIT_GUIDE.md` git for beginners; `docs/reference/improvements_for_ref.md` the external review.
- Code: `iws_env.py` (environment), `baselines.py`, `train_variant.py`, `eval_all.py`, `bo_schedule.py`, `v2cfg.py` (set `IWS_V2=1` for the harder environment), `run_jobs.py` (cross-platform job queue).
- Results: `results/` (v1), `results_v2/` (v2), models in `models/` and `models_v2/`.

## 8. Update log
| Date | What changed |
|---|---|
| 1 Nov 2026 | Edition 1: project history, sources, v1 and v2 results, plan v1 |
