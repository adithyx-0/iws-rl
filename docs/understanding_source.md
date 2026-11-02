# IWS-RL: understanding the project (edition 3, morning of 2 Nov 2026)

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
| Topic: equity-aware RL for intermittent water supply (IWS) | Other Claude (Opus) produced `iws-rl.zip`; we chose it after eliminating 12 earlier candidates | Adopted; faculty approval stated as obtained by the user |
| EPANET hydraulics, network Net3 | WNTR package (bundled example network), https://github.com/USEPA/WNTR | Tool |
| PPO, DQN, A2C implementations | Stable-Baselines3, https://github.com/DLR-RM/stable-baselines3 | Tool |
| Household roof tanks, daily budget, equity reward | Original `iws-rl.zip` design; values (tank 0.3-0.8 days, alpha=4) are **assumptions** | Needs cited ranges (Adithyan) |
| Privileged greedy (reads hidden tank levels) | Added by us as an upper-ish reference | Not a true oracle (scores below PPO on v2); the true clairvoyant oracle is `oracle.py` |
| Optimised fixed daily schedule (CE search) | Added by us as the stand-in for Bayesian-optimisation schedules in the literature (Hendrickson & Sela) | Retuned (40 iterations, population 60, 3 seeds); it is CE search, not Bayesian optimisation |
| Diagnosis: scarce supply is degenerate | Our own analysis (`scarce_diag.py`, `scarce_trace.py`) | Done |
| Hydraulics never bind in v1; demand_scale=8 gives v2 | Our own probes (`hyd_probe.py`, `scale_study.py`); the 4-8x peak-flow argument is our reasoning, not a citation | Done |
| Supply ceiling (mean supply can't exceed ~0.773 in v1) | External review `docs/reference/improvements_for_ref.md`; consistent with our scarce result 0.4754 vs ceiling 0.473 | Consistent; not independently re-derived by us |
| Adaptive policy: domain randomisation + recurrent (LSTM) policy | Same review; resembles rapid-motor-adaptation ideas in robotics (from memory, **verify before citing**) | Done (C1): domain randomisation helps under shift; LSTM did not |
| Equity as a reward weight lambda; Pareto front over lambda | Same review; Siddique et al., ICML 2020 is related fair-RL work, but our method is a reward penalty, not constrained RL and not their welfare optimisation | Done (lambda sweep) |
| Clairvoyant oracle for regret | Our design: env is deterministic given a seed, so optimise the full action sequence per scenario | Done (Gate 1) |

## 4. Related work found so far
**Honesty note:** items were first found as titles or snippets. A later audit (`docs/reference/iws-rl-literature-audit.md`, 2 Nov, 23 queries, run by another AI session; check cited sources yourself before presenting) read in full: Hendrickson & Sela journal and conference versions, Kurian et al. 2024, Hajgato et al. 2020 and Gym4ReaL; abstract only: Kurian 2023, Siddique 2020, Holgado-Sanchez 2024, Wanjiru 2016; the rest snippet only. Read in full before relying on them: Holgado-Sanchez 2024 and Wanjiru 2016.

### Closest to our problem (non-RL, equity in intermittent supply)
- Hendrickson & Sela, 2024: Bayesian optimisation of flow-control valve schedules for local supply and global equity, volume-driven demand with private tanks, 6 zones. https://doi.org/10.1016/j.scs.2024.105615 ; conference version https://doi.org/10.3390/engproc2024069075 (Eng. Proc. 69(1):75, with a third author; 69/1/184 is Kurian et al. 2024 and 69/1/7 is unrelated: verified by the audit, full text read)
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

### Is it new? (audit result, 2 Nov)
Answer: **unclear (confidence low-medium)**. No paper was found combining RL, intermittent-supply zone valve control, an equity term and household storage, but absence in 23 web queries is not proof, and the search could not use Scholar, IEEE, Scopus or ScienceDirect directly. Closest prior work: Hendrickson & Sela 2024 (open-loop Bayesian-optimised valve schedules for equity with tanks in WNTR; no RL; they test fixed schedules against +-50% tank-size changes but only versus no control), Kurian et al. 2023 (MINLP schedule for equity), Holgado-Sanchez et al. 2024 (constrained RL, equity, drought; abstract only), Wanjiru et al. 2016 (open-loop vs closed-loop MPC for household tanks; already states the qualitative regime result, so the idea is not new, only our RL evidence on this network). RL for water without equity or intermittent supply: Hu et al. 2023, Hajgato et al. 2020 (demand randomisation), Gym4ReaL 2025 (EPANET, binary pump actions). "Cai et al. 2024" and an "npj Clean Water" equity paper could not be found; do not cite them.
Allowed wording: "To our knowledge, based on a targeted search, this is an exploratory study applying RL to equity-aware valve scheduling in intermittent supply; adaptive control helped under the shifts we tested, not in-distribution." Not allowed: "first/novel" without the qualifier, "RL beats optimised schedules" without "under the shifts we tested", "constrained/Lagrangian RL", "robust" in general, "statistically significant" without stating seeds and CIs, results transfer to real networks. Note also that our household tanks sit outside the EPANET hydraulics (a simplification relative to Hendrickson & Sela).

### Final M1 results (2 Nov morning): tuned fixed schedule, ablations, fairness Pareto
Source files: `results_v2/summary.csv`, `results_v2/paired_vs_ce_tuned.csv`, figures in `results_v2/figs/` (`pareto.png`, `regime_map.png`). Script: `analyze_final.py`. CIs are paired bootstraps over test scenarios only; training-seed variance is excluded. PPO has 5 seeds, ppo_dr/DQN/no-equity 3, tuned schedule 3 (CE 40 iterations, population 60), lambda sweep 2 per point.

| Condition | PPO | PPO+DR | DQN | No-equity | Tuned schedule |
|---|---|---|---|---|---|
| default (return) | -9.67 | -9.88 | -10.04 | -10.00 | -9.15 |
| alpha=2 (demand surge, shifted) | -9.67 | -9.14 | -8.31 | -10.09 | -10.81 |
| small tanks (shifted) | -17.77 | -17.20 | -16.43 | -18.50 | -17.62 |
| alpha=8 | -11.18 | -10.88 | -11.88 | -11.49 | -10.98 |

- **The tuned fixed schedule beats plain PPO in the normal setting** (paired, significant), and in most conditions on both return and worst-zone supply. Our earlier "PPO beats the fixed schedule" was an artefact of an under-tuned baseline.
- **RL significantly beats the tuned schedule where conditions shift**: alpha=2 (all RL methods, return and worst-zone), small tanks (DQN and PPO+DR on return), scarce (return, DQN/PPO/PPO+DR). A fixed schedule cannot react to these.
- **Fairness weight lambda** (PPO, default): worst-zone 0.571 (lambda 0) to 0.635 (lambda 4) for a mean-supply cost of 0.010; node-level Gini does not improve. Removing the equity term lowers worst-zone supply (0.573 vs 0.601).
- **Honest limits:** tuned schedule overfits its training scenarios somewhat (train -7.4, test -9.15); single network; assumed parameters; the lambda points have 2 seeds; the novelty claim is unverified (literature audit pending).
- **Story:** RL is not better everywhere. It matters when the system differs from what a schedule was tuned for, and the equity weight gives a controllable fairness trade-off.

## 6. Open problems and the plan
- Fairness Pareto curve (C2) not finished: lambda sweep running on the MacBook, the Vivobook has the main version.
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
| night of 1 Nov | Edition 2: oracle and Gate 1, domain-randomisation and LSTM results |
- 2 Nov morning (edition 3): added tuned-schedule baseline, no-equity/DQN runs, lambda Pareto, paired CIs; main conclusion changed (see section 5, final M1 results).
