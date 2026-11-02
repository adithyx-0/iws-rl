# Slide content draft (M3, T3.4) - 12 slides

**Status: UPDATED 2026-11-02 on M1's final results.** Numbers come only from `results_v2/summary.csv`, `results_v2/paired_vs_ce_tuned.csv`, `results_v2/oracle.csv`, `README.md` (M1's results table) and `docs/PROJECT_LOG.md`. `NO DATA` = nothing exists in the repo for it: cut the slide or the claim.
Figures: `plots/out/` (made by `python plots/make_plots.py --baseline ce_tuned --lambda-sweep`). Significance ("better/worse/tie") is M1's paired 95% CI, not my heatmap colours.
**Headline for the talk:** a tuned fixed daily schedule is hard to beat when conditions match its tuning; RL helps only under some shifts. Do NOT say "RL beats optimised scheduling" without "under the shifts we tested".

---
## 1. Problem: intermittent water supply (IWS) and inequity
- Many cities supply water only some hours a day; households fill roof tanks when water arrives.
- Who gets water first decides who goes without. Tanks help households but can widen inequity (Hendrickson & Sela 2024, abstract).
- Question: can a learned policy schedule zones to serve more water AND protect the worst-off zone?
- *Notes:* a cited real example is still needed (none verified yet).

## 2. Related work and the gap
- Optimised schedules exist (Hendrickson & Sela: Bayesian optimisation of valve schedules; Kurian et al.: MINLP): open-loop optimisation.
- RL for valves/pumps exists (Hu 2020 contamination; Hu 2023 MADDPG; DRL-EPANET), none that we found handles intermittent supply + equity.
- Wording: "In our search we did not find..." never "first". Papers are checked at abstract level only (`docs/verify/`, `docs/VERIFY_PAPERS.md`); two names from the brief could not be found.
- Source: `docs/related_work.md`.

## 3. Our environment and assumptions
- EPANET Net3, 4 zones, hourly open/close, 3-day episodes, daily source budget known one day ahead; hidden household tanks.
- Reward: unmet demand + end-of-day worst-zone bonus (weight lambda).
- Simulation only; tank sizes, surge factor, budgets are assumptions (`docs/assumptions.md`). Tank size 0.3-0.8 days is probably below typical real storage (vendor guidance ~2 days; no survey found).

## 4. Why v1 was too easy; v2
- v1: mean supply capped near 0.773 by water volume; PPO 0.767 = 99% of the ceiling; pressure thresholds 10/20/30 m gave identical results.
- v2 (`demand_scale=8`): hydraulics bind; pressure thresholds now matter (10 m 0.703, 20 m 0.716, 30 m 0.724 for PPO, early v2 run).
- Message: we found and fixed a weak benchmark before drawing conclusions.

## 5. Methods compared (seeds in brackets)
- Heuristics: random, all-open, rota, greedy k1/k2; privileged greedy (reads hidden tanks, not deployable).
- **Tuned fixed daily schedule** (`ce_tuned`: cross-entropy search, 40 iterations, population 60, 3 runs). It replaced the earlier under-tuned CE schedule (1 run). Not Bayesian optimisation.
- RL: PPO (5), PPO+domain randomisation (5), PPO no-equity (5), DQN (5), LSTM PPO (3), LSTM PPO+DR (3), lambda sweep 0/0.5/1/2/4 (2-5).
- Clairvoyant oracle: hindsight upper bound, 30 scenarios, uses the future, not deployable.

## 6. Main result (default test set, 100 scenarios)
| Method | mean supply [95% CI] | worst zone [95% CI] |
|---|---|---|
| Tuned fixed schedule (3) | 0.716 [0.706, 0.725] | 0.630 [0.623, 0.638] |
| PPO (5) | 0.716 [0.707, 0.725] | 0.601 [0.592, 0.609] |
| PPO + DR (5) | 0.711 [0.703, 0.720] | 0.612 [0.604, 0.621] |
| DQN (5) | 0.714 [0.705, 0.723] | 0.590 [0.582, 0.597] |
| PPO no-equity (5) | 0.718 [0.709, 0.727] | 0.564 [0.553, 0.574] |
| Old CE schedule (1) | 0.708 [0.698, 0.717] | 0.612 [0.606, 0.618] |
| Random | 0.672 [0.664, 0.680] | 0.527 [0.518, 0.537] |
- Paired vs the tuned schedule (M1): PPO return -0.52 [-0.59, -0.46] (worse); mean supply tie (0.000 [-0.001, 0.001]); worst zone -0.030 [-0.031, -0.028] (worse).
- Takeaway: on the conditions the schedule was tuned for, PPO matches it on mean supply and loses on worst-zone and on return. Figure: `bars_ci.png`, table: `results_table.md`.
- Caveat: the CIs are over test scenarios; the training-seed spread is separate (`*_seed_sd` columns). The 3-run schedule and 2-seed lambda points have limited seed coverage.

## 7. Regret vs the oracle
- README return: oracle -8.49 (30 scenarios), tuned schedule -9.15, PPO -9.67, DQN -10.02, random -14.33. Mean supply: oracle 0.725 vs 0.716; worst zone: oracle 0.631 vs tuned 0.630.
- Caveat: the oracle row uses 30 scenarios and the others 100, so do not quote exact percentages of gap closed. The oracle sees future budgets and tank levels, so part of its lead is unreachable. The oracle was tuned for return, not worst-zone.
- Takeaway: there is little headroom left over the tuned schedule on mean supply; some on the return objective.

## 8. Equity weight (lambda sweep)
- PPO worst zone by lambda 0 / 0.5 / 1 / 2 / 4: 0.573 / 0.586 / 0.601 / 0.598 / 0.635; mean supply 0.718 / 0.716 / 0.716 / 0.712 / 0.708 (seeds 3 / 2 / 5 / 2 / 3).
- lambda=4 reaches the tuned schedule's worst zone (0.635 vs 0.630) for about -0.008 mean supply. Not monotone (lambda=2 below lambda=1), seeds few, intervals overlap.
- Figure: `pareto_lambda.png`. Say "a reward penalty", NOT "constrained / Lagrangian RL" (README forbids it).

## 9. Robustness under shift (paired return vs the tuned schedule, M1)
| Condition | PPO | PPO+DR | DQN |
|---|---|---|---|
| default | worse (-0.52) | worse (-0.77) | worse (-0.86) |
| alpha=2 | better (+1.14) | better (+1.66) | better (+2.01) |
| alpha=8 | worse (-0.20) | tie (+0.08) | worse (-0.81) |
| small tanks | tie (-0.15) | tie (+0.05) | better (+1.14) |
| five days | worse | worse | worse |
- The tuned schedule is significantly better than all three RL methods in abundant, five_days, large_tanks, noisy_demand, press10 and press30 (not shown in the table). Overall PPO is worse in 8 of 10 non-scarce conditions, better in 1 (alpha=2), tied in 1 (small tanks).
- alpha=2 is outside the domain-randomisation training range (alpha 3-6). The schedule was tuned only on the default.
- LSTM PPO (3 seeds) is below PPO (worst zone 0.573); LSTM+DR is far worse (0.469): report as a negative result.
- Scarce supply: degenerate for mean supply (judge worst zone only); not used for claims here.

## 10. Learning curves / sample efficiency
- NO DATA: no learning-curve files exist in the repo. Cut this slide, or train/log one PPO run with periodic evaluation (needs M1 or M2).

## 11. Where RL does not help + limitations
- Heatmaps `heatmap_mean_vs_baseline.png`, `heatmap_worst_vs_baseline.png` (paired means; blue = better than the tuned schedule). On worst zone, almost every RL row is red outside alpha=2; lambda=4 is the only RL row that is non-negative in most conditions.
- Limits: one network, simulation only, unsourced tank sizes, oracle on 30 scenarios, 2-5 training seeds per method, tuned schedule tuned on one condition, literature checked at abstract level.

## 12. Conclusion, what is new, future work
- Defensible: an auditable IWS benchmark, a tuned open-loop baseline that is hard to beat, an honest map of where RL helps (demand surge alpha=2, some small-tank cases) and where it does not, and an equity-weight trade-off.
- Not defensible: "first", "RL beats optimised schedules" without the shift qualifier, "Lagrangian".
- Future: second network, cited tank data, constraint-based fairness, curves.
