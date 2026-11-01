# IWS-RL review: progress, brief verification and novelty options

Date: 2026-11-01. Sources: the improvement plan, the full repo in `iws_extract/iws` (code, logs, results, git history, v2 files), the other reference documents, and web searches. Web findings come from abstracts and snippets, not full papers.

Notes:
- Files `01`–`07` in this folder describe a different project (exam-aware study scheduling, with a faculty approval message). Nothing there mentions the water project. Confirm that IWS-RL was approved by faculty.

## 1. Verdict

The engineering is solid and the reporting is honest. The scientific claim is thin, and there is **no method contribution yet**. The report spec rules out "extra features or a revised MDP" as novelty. Right now the project is PPO plus a custom environment.

There is a real opening: I found no RL paper on intermittent water supply (IWS) with equity. That came from a handful of searches, so it needs a proper literature check before it is claimed.

## 2. Why v1 is saturated

**Mean supply ratio is almost fixed by the water budget alone.**

- Budget is 0.5–0.9 of daily demand over 3 days, plus initial household storage of about 0.22 days.
- That caps mean supply ratio at about (2.1 + 0.22) / 3 = **0.773** (confirmed by Monte Carlo: 0.773).
- PPO scores 0.767, which is 99% of the ceiling. Greedy with hidden-tank access scores 0.766.
- Scarce condition: budget 0.3–0.5 gives a ceiling of 0.473, and every PPO variant scores exactly 0.473. That is an accounting identity, not a learning result.

Realistic headroom is about 0.006 on mean supply and roughly 0.03 on worst-zone supply. Any "PPO beats X" claim on mean supply ratio in v1 is meaningless. Only worst-zone and fairness metrics carry information.

Hydraulics are slack because the budget cap is applied to requested flow before EPANET runs. `hyd_probe.py` shows pressure at 37–46 m and fill at 1.00, which is why the 10, 20 and 30 m thresholds gave identical results.

## 3. Progress against the brief's gates

| Item | Status |
|---|---|
| Gate 0: verify the code | Mostly confirmed (details below) |
| Environment fix | Started. `demand_scale` and `source_cap` exist. `source_cap` was rejected after testing. `demand_scale=8` is the v2 candidate. |
| v2 runs | PPO x5 trained (300k steps). CE schedule done. PPO-no-equity x3 and DQN x3 are listed for the second laptop, no models yet. **v2 not evaluated**: `eval_v2.log` is empty and `results_v2` holds only the CE schedule. |
| Look-ahead planner | **Not started.** Biggest gap, since it is needed to run Gate 1 (headroom). |
| Domain randomisation, Lagrangian PPO, CVaR, extra metrics | Not started (on the ROADMAP) |
| Second network | Not started. Observation size is built from the Net3 zone and tank counts. |
| Related work | Only titles and snippets read. Full reading assigned to a teammate. |
| Learning curves | **Missing.** `train_variant.py` logs nothing during training, but the report spec requires curves, convergence speed and sample efficiency. |

Findings from the "must verify" list:
- **Budget accounting** is correct. It is capped on delivered volume, and unused budget is lost each day.
- **The CE schedule** is a fixed 24x4 daily pattern, not a planner.
  - `bo_schedule.py` is mislabelled: it uses cross-entropy search, not Bayesian optimisation.
  - It ran only 12 iterations with population 40 and was **still improving** at the end (v2 train return -10.5 to -8.2). It is under-tuned, so the PPO-vs-schedule comparison currently flatters PPO.
- **The reward** matches the README.
- **A2C** is simply untuned. Fix or delete it.
- **Repo hygiene:** stray EPANET temp files (`enaPd9c7`, `enlPnvzL`) in the repo root, and v2 work is uncommitted.

On `demand_scale=8`: Net3 is designed for continuous supply. Delivering the same daily volume in a 3–6 hour window raises peak flow by about 24/hours, so 4–8x. This is my own reasoning, not a citation, but it is easy to defend and matches the alpha=4 surge.

## 4. Research on each topic in the brief

- **The "Sept 2026 npj Clean Water equity paper" was not found.** Searches returned adjacent npj papers only. The closest real work is Kurian et al. (2023), *Water Supply*: MINLP schedule plus a data-driven flow-measurement approach, tested on a real-network simulation and a lab network. Treat the brief's citation as unconfirmed.
- **Hendrickson & Sela** is real: *Sustainable Cities and Society*, 2024, with a conference version at MDPI Eng. Proc. 69/1/75. It uses Bayesian optimisation of flow-control valve schedules with volume-driven demand and private tanks. **The project log cites "69/1/184"; search results suggest 184 belongs to the Kurian line of work. Verify before it goes in the report.** This is the main paper to beat or position against.
- **RL for IWS with equity:** none found. Nearest RL work is valve scheduling for contamination, and MADDPG pump-and-valve scheduling. Neither considers equity or intermittent supply.
- **Constrained RL / Lagrangian:** established. No Lagrangian method applied to water networks found; water work uses supervisor/shield approaches. Plain PPO-Lagrangian oscillates; PID-Lagrangian (in OmniSafe) reduces this, not consistently. It enforces constraints only in expectation, so report per-episode violation rates.
- **Fair RL:** Siddique et al., ICML 2020, optimise generalised Gini welfare (max-min, leximin or utilitarian by weights). Two 2026 arXiv papers (2606.18111, 2608.00175) argue that expected-welfare training does not guarantee fairness because welfare is nonlinear in return. This is directly relevant: the worst-zone metric is a minimum over episode totals. Past-discounting for Markovian fairness (arXiv 2504.01154) is also related.
- **Hidden state and privileged information:** Cai et al., NeurIPS 2024, analyse asymmetric actor-critic and teacher-student distillation. This fits the hidden household tanks and the privileged-greedy oracle.
- **CVaR:** well established (Tamar et al.; Predictive CVaR PG, ICML 2024). Use it as an evaluation metric first. Training on it is unstable.
- **GNN / transfer:** no GNN-RL for control that transfers across networks found. GNN work in this area is on surrogates, pressure estimation and partitioning. An open gap, but very risky. Defer.
- **MPC vs RL in water:** no clean head-to-head benchmark exists; comparisons are mostly about speed. A fair planner baseline is necessary and a small contribution in itself.
- **Real tank sizes:** household surveys exist, but nothing on pipe-filling transients. Tank sizes 0.3–0.8 days and alpha=4 remain assumptions, so cite ranges.

## 5. Where novelty could come from

Ranked by value over risk:

1. **Adaptive policy under household-behaviour uncertainty (recommended core).** Domain randomisation over alpha, tank size and demand, a recurrent policy that infers hidden storage from supply-response history, and an asymmetric critic or teacher using the privileged tank state. This fixes the worst result (failure at alpha=2), reuses the privileged-greedy oracle, and gives a defensible claim: no utility knows these parameters. The recurrent-inference idea resembles rapid-motor-adaptation work in robotics (from memory, verify before citing).
2. **Fairness as welfare or constraint, not a reward bonus.** Compare the reward-lambda term, a Lagrangian worst-zone constraint (PID variant) and a generalised-Gini objective. Produce a Pareto front of mean against worst-zone supply. This is the cheapest strong figure. The method is known; applying it to IWS equity is the novelty.
3. **A validated benchmark environment plus "when does RL beat heuristics".** The report spec lists "custom environment" as acceptable novelty. Regime maps are the fallback (Option D).
4. **A strong look-ahead planner baseline.** Not novelty, but it supplies the oracle for regret and for Gate 1.
5. **Second network.** Late extra only.

Skip physics-informed GNNs, multi-agent RL, digital twins, and CVaR as a training objective.

## 6. Risks and recommendations

- **Biggest risk:** even at `demand_scale=8`, heuristics may still match PPO. If the planner does not beat the best simple baseline by roughly 0.02–0.03 mean (or a large worst-zone gain), headroom is not there. Plan for Option D.
- **Report mean supply ratio with the ceiling shown**, and lead with worst-zone, Jain's index, p10 and CVaR.
- **Order of work:**
  1. Evaluate v2 and freeze the environment.
  2. Build the planner (beam search or CEM over action sequences, plus an oracle variant) and run Gate 1.
  3. Fix the CE baseline (more iterations, multiple seeds, budget-conditioned).
  4. Add learning-curve logging.
  5. Build the method (item 1 or 2 above).
  6. Run 5+ seeds with paired CIs against the strongest realistic baseline, not greedy.
- **Report gaps against the spec:** regret, convergence speed, generalisation gap and a compute table do not exist yet. The planner and logging cover most of them.
- **Discrete SAC is not strictly needed.** The spec asks for SAC only for continuous actions, and the actions here are discrete.

## Sources

- Kurian et al. 2023, Water Supply: https://iwaponline.com/ws/article/23/11/4520/98117/Equitable-supply-in-intermittently-operated-rural
- Hendrickson & Sela 2024: https://doi.org/10.1016/j.scs.2024.105615
- MDPI Eng. Proc. 69/1/75: https://www.mdpi.com/2673-4591/69/1/75
- MADDPG pump/valve scheduling: https://bohrium.dp.tech/paper/arxiv/2408.08442
- Safe RL for water networks (Aalborg): https://vbn.aau.dk/en/publications/safe-reinforcement-learning-control-for-water-distribution-networ-2
- Safety-Gymnasium: https://arxiv.org/pdf/2310.12567
- OmniSafe: https://github.com/PKU-Alignment/omnisafe
- Siddique et al. 2020: https://arxiv.org/pdf/2008.07773
- arXiv 2606.18111: https://arxiv.org/pdf/2606.18111
- arXiv 2608.00175: https://arxiv.org/pdf/2608.00175
- Past-discounting fairness: https://arxiv.org/abs/2504.01154v2
- Cai et al. NeurIPS 2024: https://arxiv.org/abs/2412.00985
- Tamar et al. CVaR: https://arxiv.org/pdf/1406.3339v3.pdf
- Predictive CVaR PG: https://rlj.cs.umass.edu/2024/papers/RLJ_RLC_2024_81.pdf
- DRL pumps in WDS: https://arxiv.org/pdf/2010.06460
- IWS in Dehra Dun: https://sswm.info/node/1445
