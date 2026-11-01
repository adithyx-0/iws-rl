# Roadmap: what we plan to improve (agreed 2026-11-01, not started yet)

The topic (equity-aware RL for intermittent water supply) is fixed. The results so far show real but modest gains and some weaknesses.
These are the planned improvements, in priority order.

## 1. Fix the environment so it tests something (highest priority)
- **Scarce supply is degenerate.** The daily budget is spent in ~3 hours (all zones open, capped by the surge factor alpha=4), so no zone scheduling decision remains. Fix: make the budget not exhaustible in a few hours (e.g. limit source flow per hour / pump capacity), or report scarce as a limitation.
- **Hydraulics never bind.** Required pressure 10/20/30 m gives identical results. Fix: tighter network or larger demand so pressure actually limits delivery; otherwise EPANET adds nothing over a simple flow model.

## 2. Method contribution (needed for novelty)
- **Robust training:** policies tuned to alpha=4 fail at alpha=2 (PPO 0.723 < random 0.759). Train with randomised alpha / tank sizes / budgets (domain randomisation).
- **Recurrent policy (LSTM/GRU):** the agent cannot see household tank levels; a privileged greedy that can ties PPO. A recurrent policy may infer them from history.
- **Explicit fairness constraint** (e.g. Lagrangian on worst-zone supply ratio) instead of a reward bonus.

## 3. Stronger evidence
- More seeds for DQN (3), the fixed schedule (1 optimisation run), A2C (3).
- Tune A2C or drop it; discrete SAC if the spec requires SAC.
- Bayesian-optimisation schedule baseline closer to the literature (we used cross-entropy search).
- Learning-curve plots; sensitivity sweeps over tank sizes and demand.
- Read the full closest-prior-work papers (we only saw titles/snippets): Hendrickson & Sela (BO valve schedules, equity), 2023 Water Supply MINLP equity paper, Kurian et al. rural India.

## 4. Report
- State assumptions: zone closure modelled as consumer cut-off; household tank sizes, surge factor and pressure thresholds are assumed.
