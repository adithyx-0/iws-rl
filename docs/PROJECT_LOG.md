# IWS-RL project log

## 2026-11-01 - scarce-supply anomaly explained (not a bug)
- Scarce condition (supply 0.3-0.5 of demand): all 10 PPO variants give identical mean_sr (0.4754) and min_zone_sr.
- Cause: every PPO policy opens all zones (action 15) in ~3 hours per day, which spends the whole daily budget by ~12:00
  (delivery capped at alpha=4x mean demand per hour); later actions are no-ops. Policies differ only in post-exhaustion actions.
- Implication: in the scarce regime the env has no zone-scheduling decision (budget is gone in 3 h), so no method can differ. 
  Treat scarce rows as "env degenerate", not as evidence for/against PPO. Env design issue: budget/surge coupling makes rotation moot.
- Scripts: scarce_diag.py, scarce_trace.py (run with ./venv/bin/python).

## 2026-11-01 - literature check (web search, standard mode; titles/snippets only, full papers not read)
- No RL paper found combining intermittent supply + zone valve scheduling + equity + household storage.
- Closest prior art (non-RL): Hendrickson & Sela, Bayesian-optimisation flow-control valve schedules for local supply + global equity,
  volume-driven demand with private tanks, 6 zones (MDPI Eng. Proc. 69/1/184); 2023 Water Supply MINLP minimising supply inequity;
  Kurian et al. rural central India PDA inequity; Bengaluru/Delhi equity studies.
- Closest RL (no equity, not IWS): Hu et al. 2020 DRL valve scheduling (contamination); Hu/Gao/Zhong 2023 MADDPG pump+valve; DRL-EPANET 2022; PPO pump scheduling 2023.
- Positioning: RL for equity-aware zone scheduling under IWS with hidden household storage. Must compare to an open-loop optimised schedule (BO-style) baseline.

## 2026-11-01 - second round (28 methods x 11 conditions, 19,800 episodes; results/, v1 kept in results/v1)
Added: CE-optimised open-loop daily schedule (literature-style baseline), 5 seeds for ablations, PPO 500k steps (5 seeds), A2C (3 seeds), sensitivity conditions alpha2/alpha8/press10/press30.
- Default: ppo_long 0.767 = ppo 0.766 = priv_greedy 0.766 > noequity/noforecast 0.763 > CE schedule 0.759 > dqn 0.753 > greedy_k1 0.737. 500k steps gives no gain over 150k.
- PPO beats the open-loop CE schedule by only ~0.007 mean_sr; min-zone gain larger (0.735 vs 0.712).
- Equity term: min_zone 0.735 vs 0.724 (5 seeds each, seed sd 0.001 vs 0.007) -> small but now consistent.
- Forecast feature: no effect.
- A2C failed (0.44, unstable) - untuned; reported as such. SAC not run (action space is Discrete(16); would need discrete SAC).
- Pressure thresholds (10/20/30 m) change nothing -> hydraulics are not binding in this env; only budget + surge cap (alpha) matter.
- alpha=2 (smaller surge cap) breaks the learned policy: PPO 0.723 < greedy_k2 0.768 and random 0.759; priv_greedy collapses to 0.493. Policies are tuned to alpha=4 dynamics.
- Scarce: degenerate (see above).
