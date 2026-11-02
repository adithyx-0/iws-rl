# IWS-RL project log

## CURRENT STATE (updated 2 Nov 2026; the entries below are in time order, oldest first)
- Environment: v2 (`IWS_V2=1`, demand x8, git tag `env-v2`). v1 was saturated and is superseded.
- Main finding: a properly tuned fixed daily schedule beats plain PPO when conditions match its tuning; RL (DQN, domain-randomised PPO) beats it under demand surge, small tanks and scarce supply. The equity weight lambda trades 0.010 mean supply for +0.064 worst-zone supply (lambda 0 -> 4).
- Not RL-better everywhere; one network; assumptions uncited; "first/novel" not claimable (literature audit: `docs/reference/iws-rl-literature-audit.md`).
- Results: `results_v2/summary.csv`, `paired_vs_ce_tuned.csv`, `figs/`. Story and sources: `understanding.pdf`.
- Citation correction (from the audit, full text read): Hendrickson & Sela conference version is Eng. Proc. 69(1):75; 69/1/184 is Kurian et al. 2024; 69/1/7 is unrelated. Earlier entries below that say 69/1/184 are wrong.
- Open: slides, rehearsal, full-text reading of closest papers (Holgado-Sanchez 2024, Wanjiru 2016), assumption sources.

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
  volume-driven demand with private tanks, 6 zones (MDPI Eng. Proc. 69/1/75; originally logged here as 69/1/184, which the audit showed is wrong); 2023 Water Supply MINLP minimising supply inequity;
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

## 2026-11-01 (night) - C1 results: LSTM and domain randomisation (v2, 21 methods x 11 conditions, 12,600 episodes; results_v2/, previous round in results_v2/round1)
Paired return differences (mean [95% CI over 100/50 test scenarios; training-seed variance NOT included], higher is better):
| condition | ppo_dr - ppo | ppo_dr - CE schedule | ppo - CE schedule |
|---|---|---|---|
| default | -0.20 [-0.27,-0.15] | +0.17 [+0.10,+0.24] | +0.38 [+0.30,+0.44] |
| alpha=2 (held out) | +0.53 [+0.35,+0.71] | +0.39 [+0.12,+0.68] | -0.13 [-0.47,+0.23] |
| alpha=8 (held out) | +0.30 [+0.23,+0.36] | +0.28 [+0.16,+0.39] | -0.02 [-0.10,+0.06] |
| small tanks | +0.56 [+0.48,+0.64] | +1.03 [+0.89,+1.18] | +0.47 [+0.32,+0.62] |
| large tanks | -0.44 [-0.57,-0.33] | +0.42 [+0.28,+0.55] | +0.86 [+0.70,+1.03] |
| 5 days | -0.35 [-0.44,-0.25] | +0.05 [-0.08,+0.19] | +0.39 [+0.26,+0.54] |
- Plain PPO beats the CE schedule in-distribution but LOSES that advantage when alpha shifts (alpha=2: -0.13, alpha=8: -0.02). PPO with domain randomisation (ppo_dr, 3 seeds) beats the CE schedule in every shifted condition, at a cost of 0.2-0.4 return in-distribution. This supports C1 in its simple form (randomised training), not the LSTM.
- LSTM (rec) is worse than PPO everywhere (default return -11.2 vs -9.7); LSTM + DR (rec_dr) is worst (-13.9, worst-zone 0.469). Likely under-trained at 300k steps (not tested); report as negative result, do not claim LSTMs cannot help.
- Caveats: ppo_dr/rec 3 seeds; the CE schedule baseline is a single, under-tuned run (M2 is redoing it), so "beats CE" is optimistic until then; CIs exclude seed variance.
- Started on M1 as insurance for C2: lam sweep 0, 0.5, 2, 4 x 2 seeds (jobs_M1_pareto.txt -> models_v2/ppo_lamX_sN.zip; lam=1 is ppo). The Vivobook's own sweep goes to models_fair/.

## 2 Nov 00:40 - C2 Pareto (lam sweep), M1 insurance runs
Source: results_v2/summary.csv, condition=default, 11 conditions x 15+ families (17,400 episodes). lam=1 is `ppo` (5 seeds); others 2 seeds each.
| lam | mean_sr | min_zone_sr | gini_node | return |
|---|---|---|---|---|
| 0 | 0.717 | 0.571 | 0.143 | -10.09 |
| 0.5 | 0.716 | 0.586 | 0.150 | -9.93 |
| 1 (ppo) | 0.716 | 0.601 | 0.148 | -9.67 |
| 2 | 0.712 | 0.598 | 0.152 | -10.21 |
| 4 | 0.707 | 0.635 | 0.159 | -9.79 |
Reading: raising lam moves worst-zone supply 0.571 -> 0.635 (+0.064) for a mean-supply cost of 0.010. Monotone except lam=2 (0.598, below lam=1's 0.601; within seed noise, 2 seeds only). gini_node does NOT improve with lam (0.143 -> 0.159), so the equity term helps the worst ZONE, not node-level inequality. Not yet tested: CIs on the differences, lam>4. Caveat: 2 seeds per point.
Also noted: lam0.5 models saved without .zip (dotted name) and were missed until renamed.
Queued (fallback for absent Vivobook): noequity x3 + dqn x3 (models_v2), tuned CE (bo_schedule_tuned.py 40 60, seeds 0-2 -> results_v2/ce_tuned_s*.npy), then final eval_all (logs/eval_final_done.txt).

## 2 Nov 06:40 - Fallback runs done + tuned CE baseline (IMPORTANT, changes the story)
Done on M1 (no Vivobook): noequity x3, dqn x3 (300k), tuned CE x3 (40 iters, pop 60; train score -7.07/-7.40/-7.37), final eval 418 jobs / 22,800 episodes. Source: results_v2/summary.csv (CI = test scenarios only; training-seed variance excluded).
Return (higher better), selected conditions:
| cond | ppo(5) | ppo_dr(3) | dqn(3) | noequity(3) | ce_old(1) | ce_tuned(3) |
|---|---|---|---|---|---|---|
| default | -9.67 | -9.88 | -10.04 | -10.00 | -10.05 | -9.15 |
| alpha2 | -9.67 | -9.14 | -8.31 | -10.09 | -9.54 | -10.81 |
| alpha8 | -11.18 | -10.88 | -11.88 | -11.49 | -11.16 | -10.98 |
| small_tanks | -17.77 | -17.20 | -16.43 | -18.50 | -18.23 | -17.62 |
| scarce | -31.86 | -31.77 | -31.51 | -32.13 | -32.19 | -32.18 |
Worst-zone supply, default: ppo 0.601, ppo_dr 0.609, ce_tuned 0.630.
Findings (honest):
1. The properly tuned fixed schedule BEATS plain PPO in-distribution (return -9.15 vs -9.67; worst-zone 0.630 vs 0.601) and in 8 of 11 conditions on return. The earlier "PPO beats the fixed schedule" was an artefact of the under-tuned baseline. Gate-1 conclusion (little headroom) stands.
2. Where adaptivity wins: demand-surge shift alpha2 (dqn -8.31, ppo_dr -9.14 vs ce_tuned -10.81) and small_tanks (dqn -16.43, ppo_dr -17.20 vs -17.62). A fixed schedule cannot react to these; RL can. At alpha8 and elsewhere the schedule is as good or better.
3. Equity term helps: noequity worst-zone 0.573 vs ppo 0.601 (default); return also worse (-10.00 vs -9.67). 3 vs 5 seeds, CIs not yet computed.
4. DQN (not PPO) is best under alpha2/small_tanks in return; 3 seeds, untested significance. Do not claim PPO superiority.
5. Caveat: ce_tuned train-vs-test gap (-7.4 train vs -9.15 test) shows overfitting to train scenarios 0-9; seed spread across 3 CE runs is large (CI -9.98..-8.35).
Not yet done: paired CIs for these comparisons, regime map, pdf edition 3.

## 2 Nov 07:00 - paired CIs vs tuned schedule (analyze_final.py)
results_v2/paired_vs_ce_tuned.csv. Return: tuned schedule significantly better than ppo/ppo_dr/dqn/noequity in default, abundant, five_days, noisy, press10, press30; RL significantly better at alpha2 (all), scarce (dqn/ppo/ppo_dr), small_tanks (dqn, ppo_dr). Worst-zone: same pattern, plus ppo_dr better at small_tanks. Figures results_v2/figs/pareto.png, regime_map.png. understanding.pdf edition 3 built.

## 2 Nov 14:45 - seed top-up finished (jobs_M1_seeds.txt; 506 eval jobs, 27,600 episodes)
PPO+DR, DQN, no-equity now 5 seeds each; lambda 0 and 4 now 3 seeds; lambda 0.5 and 2 stay at 2; tuned schedule 3. Previous summary kept as results_v2/pre_seeds_summary.csv.
Default return / mean_sr / worst-zone: ppo -9.67/0.716/0.601; ppo_dr -9.92/0.711/0.612; dqn -10.02/0.714/0.590; no-equity -10.14/0.718/0.564; ce_tuned -9.15/0.716/0.630. Lambda 0/0.5/1/2/4 worst-zone 0.573/0.586/0.601/0.598/0.635.
What changed: small_tanks, PPO+DR vs tuned schedule moved from "better" to "tie" (DQN still better); alpha2 DQN -8.80 (was -8.31), all RL still significantly better; scarce no-equity now significantly worse on return. All other conclusions unchanged: tuned schedule wins in-distribution; RL wins under alpha2, DQN under small tanks, return under scarce.

## 2 Nov evening: Part A paper verification folded in
Source: `docs/results-adithya-paper.md` (AI-assisted reading of full texts; human must still find the sentence for each slide fact). Effects: (1) Holgado-Sanchez 2024 IS constrained/Lagrangian RL for equity in drought water allocation (tanker truck, 4 villages, tabular Q-learning), so the novelty wording must be narrow: hydraulic network with zonal valves, household tanks, intermittent supply. (2) Hendrickson & Sela assume no tank sensing and argue closed-loop sensing may be impractical; we must justify our observation assumptions. (3) Ansalone 2025 citation corrected (title, 4 authors). (4) Tank size 0.3-0.8 days and surge alpha=4 have no source (disclose); pressure and supply-fraction ranges partly supported. (5) Possible missing papers listed in understanding_source.md. understanding.pdf is now edition 5. Part B (Adithyan) still open.
