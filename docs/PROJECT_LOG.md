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

## 2026-11-01 - environment diagnosis and v2 (hydraulics that bind)
- Added env options `source_cap` (max hourly source draw) and `demand_scale` (multiplies all demands); logged `hyd_fill` (delivered/requested flow).
- `source_cap` study (cap_study.py): a cap of 1.2-1.5x mean hourly demand makes all_open ~optimal (0.77) -> scheduling irrelevant again. Rejected as the fix.
- Hydraulic probe (hyd_probe.py): with demand_scale=1 pressure stays 37-46 m and fill = 1.00 even with every zone open, i.e. v1 hydraulics never bind (explains press10/20/30 identical results).
  demand_scale 6 -> all-open fill 0.73 / 18 m; 10 -> 0.54 / 13 m; single zone stays 0.99 / 0.90. Opening everything now starves the network, as in real IWS.
- scale_study.py: at demand_scale 6-10 heuristics disagree and the privileged greedy no longer dominates (scale 10, supply .5-.9: greedy_k2 0.632/0.604, priv 0.574/0.432, greedy_k1 0.546/0.535).
- Scarce (30-50% supply) note: mean_sr is capped by total water, so the only meaningful metric there is the worst-zone / Gini, not mean_sr.
- v2 environment = demand_scale 8 (set by `IWS_V2=1`, see v2cfg.py; models_v2/, results_v2/). Running: CE schedule, PPO x5, PPO-noequity x3, DQN x3 (300k steps).

## 2026-11-01 - v2 results (demand_scale=8; PPO x5 at 300k steps, CE schedule, 6 baselines; 7,200 episodes; results_v2/, models_v2/)
Not yet run on v2: PPO-noequity, DQN (queued in jobs_v2_laptopC.txt), A2C. Env frozen as git tag `env-v2`.
- Sanity check PASSED: baselines spread 0.56-0.72 mean_sr (v1: bunched at 0.74-0.77). Pressure thresholds now matter, monotone: 10 m 0.703, 20 m 0.716, 30 m 0.724 (v1: identical).
- Default: PPO 0.716 (worst zone 0.601) ~ CE schedule 0.708 (0.612) > random 0.672 > greedy_k2 0.648 > priv greedy 0.639 > greedy_k1 0.604.
  PPO vs CE schedule is within ~0.008 on mean_sr and PPO is WORSE on worst-zone (0.601 vs 0.612): no clear RL win over the optimised fixed schedule. PPO vs greedy_k1 +0.112 (CI 0.103-0.120).
- The privileged greedy is NOT an oracle (0.639 < PPO): we still lack a real upper bound.
- Alpha: PPO robust now (alpha2 0.715, alpha8 0.701) but beats random only narrowly at alpha2, and greedy_k2 has the best worst-zone there (0.664). Domain randomisation still needed for a clean claim.
- Scarce: all methods 0.44-0.47 mean_sr (capped by total water); judge on worst-zone only.

## 2026-11-01 (evening) - Gate 1: clairvoyant oracle (M1)
- `oracle.py`: env is deterministic given the seed, so per scenario we optimise the whole 72-step action sequence (CEM + local search), warm-started from every heuristic's and every PPO seed's own action sequence -> oracle >= each of them by construction. It uses hidden information (future budgets, tank levels): an upper bound, not a deployable policy. 30 test scenarios (seeds 10000-10029), v2 default.
- First oracle (CEM only, no PPO warm start) was INVALID: it scored below PPO (return -9.80 vs -9.48) -> search too weak. Kept as results_v2/oracle_v0_weak.csv, replaced by the warm-started one (results_v2/oracle.csv, took 27 min).
- Valid oracle: return -8.49 | PPO -9.48 | CE schedule -9.83 | random -14.0. mean_sr: oracle 0.725, PPO 0.719, CE 0.711 (ceiling 0.775). worst zone: oracle 0.631, PPO 0.601, CE 0.612.
- Gate 1 rule (headroom >= 0.02 mean_sr or >= 0.05 worst-zone over best non-PPO baseline): FAIL on those two metrics (0.013 and 0.019). But on the training objective the oracle is +0.99 return over PPO and +1.34 over the CE schedule, i.e. PPO closes only ~26% of the CE-to-oracle return gap. Interpretation: little headroom on mean supply, real headroom on worst-zone / the equity-weighted objective, partly unreachable (the oracle sees the future).
- Decision: C2 (fairness Pareto) + C3 (regime map, oracle regret) are the core; C1 (LSTM + domain randomisation) is run overnight and reported as a result either way.
- Added to env (default off): `randomize` (train ranges alpha U[3,6], tank_days lo U[.2,.4]/hi U[.6,1.0], supply lo U[.4,.6]/hi U[.8,1.0]; held-out test = alpha 2 and 8, scarce supply 0.3-0.5, small/large tanks), metrics `jain_zone`, `ceiling`.
- Overnight (jobs_M1_v1.txt, 9 runs, 300k steps, IWS_V2=1): rec x3, rec_dr x3, ppo_dr x3 -> models_v2/.
