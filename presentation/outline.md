# Slide content draft (M3, T3.4) - 12 slides

**Status: DRAFT, 2026-11-01.** Numbers come from `results_v2/` and `docs/PROJECT_LOG.md` only. `TBD` = waiting for M1's final evaluation or M2's models; do not present TBD cells. Rule 8 of the plan: no number on a slide unless it is in `results*/` and the log.
Figures: regenerate with `python plots/make_plots.py --results-dir <final dir> --out-dir presentation/figs`.

---
## 1. Problem: intermittent water supply (IWS) and inequity
- Many cities supply water only some hours a day; households fill roof tanks when water arrives.
- Who gets water first decides who goes without. Tanks help households but can widen inequity (Hendrickson & Sela 2024, abstract).
- Question: can a learned policy schedule zones to serve more water AND protect the worst-off zone?
- *Notes:* use one cited real example (TODO: M3 to source from Hubli-Dharwad / CSE Chennai after reading them; none verified yet).

## 2. Related work and the gap
- Optimised schedules exist (Hendrickson & Sela: Bayesian optimisation of valve schedules; Kurian et al.: MINLP). Both open-loop optimisation.
- RL has been used for valves and pumps (Hu 2020 contamination; Hu 2023 MADDPG; DRL-EPANET), but none we found handles intermittent supply + equity.
- Our statement: "In our search we did not find..." (never "first"). Unchecked: the "CORE" household-refill preprint.
- Source: `docs/related_work.md` (abstract-level only until someone reads the full texts).

## 3. Our environment and assumptions
- EPANET Net3, 4 zones, hourly open/close, 3-day episodes, daily source budget known one day ahead.
- Hidden household tanks (the agent cannot see them). Reward: unmet demand + end-of-day worst-zone bonus.
- Simulation only; tank sizes, surge factor and budgets are assumptions (`docs/assumptions.md`). Tank size 0.3-0.8 days is likely below typical real storage.

## 4. Why the first version was too easy, and v2
- v1: mean supply is capped near 0.773 by water volume; PPO 0.767 was 99% of the ceiling; pressure thresholds 10/20/30 m gave identical results.
- v2 (`demand_scale=8`): hydraulics bind; baselines spread 0.56-0.72; pressure thresholds now matter (10 m 0.703, 20 m 0.716, 30 m 0.724).
- Message: we found and fixed a weak benchmark before drawing conclusions.

## 5. Methods compared
- Random, all-open, rota, greedy k1/k2 (realistic); privileged greedy (reads hidden tanks, not deployable); CE fixed schedule (optimised open-loop, closest to the literature); clairvoyant oracle (hindsight bound, not deployable); PPO, DQN (TBD), LSTM PPO +/- domain randomisation (TBD).
- Honest labels: CE schedule is cross-entropy search, not Bayesian optimisation.

## 6. Main result table (default condition, v2)
| Method | mean supply [95% CI] | worst zone [95% CI] |
|---|---|---|
| PPO (5 seeds) | 0.716 [0.707, 0.725] | 0.601 [0.592, 0.609] |
| CE schedule | 0.708 [0.698, 0.718] | 0.612 [0.606, 0.619] |
| Random | 0.672 | 0.527 |
| Greedy k1 | 0.604 | 0.591 |
- Source: `results_v2/summary.csv` via `plots/out/results_table.md`. CE schedule is 1 seed here; TBD: M2's 3-seed rerun, then compare vs the best realistic baseline, not greedy k1.
- Takeaway: PPO is not clearly better than a tuned fixed schedule; worse on worst-zone.

## 7. Regret vs the oracle (Gate 1)
- 30 test scenarios: oracle return -8.49, PPO -9.48, CE -9.83, random -14.0. Mean supply: oracle 0.725, PPO 0.719, CE 0.711 (ceiling 0.775). Worst zone: oracle 0.631, PPO 0.601, CE 0.612. (PROJECT_LOG, Gate 1 entry)
- Gate rule failed on mean/worst-zone thresholds (+0.013, +0.019); PPO closes ~26% of the CE-to-oracle return gap.
- Caveat: the oracle sees the future, so part of the gap is unreachable.

## 8. Equity trade-off (C2)
- TBD: lambda sweep {0, 0.5, 1, 2, 4} and Lagrangian worst-zone constraint (M2). Plot: `--pareto` in `make_plots.py`.
- Already known: removing the equity term lowered the worst zone by ~0.011 in v1 (5 seeds); v2 no-equity TBD.

## 9. Robustness and held-out ranges (C1)
- TBD: LSTM and domain randomisation vs plain PPO on held-out alpha 2/8, scarce supply, small/large tanks. `eval_all.py` does not yet contain the held-out conditions as a set: ask M1.
- Known v2 data: PPO alpha2 0.715, alpha8 0.701, but greedy k2 has the best worst-zone at alpha2 (0.664).

## 10. Learning curves and sample efficiency
- TBD: M2's `results_M2/curves_s*.csv` (needs columns `step, mean_sr`; confirm format with M2).

## 11. Where RL does not help + limitations
- Regime heatmap (`heatmap_*_vs_baseline.png`): on worst-zone, PPO is between -0.020 and +0.018 of the CE schedule across the 10 non-scarce conditions and below it in 7 of 10 (read from `heatmap_worst_vs_baseline.png`; re-check the mean-supply heatmap before saying anything about mean supply).
- Scarce supply is degenerate (all methods 0.44-0.47): total water, not scheduling, decides.
- Limits: one network, simulation only, unsourced assumptions, oracle small sample.

## 12. Conclusion, what is new, future work
- Contributions we can defend: an auditable IWS benchmark with a stress-tested environment, an oracle regret bound, and an honest finding that a tuned fixed schedule is near-competitive.
- Method contribution (LSTM+DR / fairness constraint): state only what results show.
- Future: second network, cited tank data, GNN, CVaR.
