# M3 cross-check (not the official evaluation)
Quick 20-scenario (seeds 10000-10019), paired comparison of PPO (ppo_long, 5 seeds averaged) vs random, greedy_k1,
privileged greedy and the CE schedule over all 11 eval_all.py conditions. Reads models/ and results_v2 only; changes no M1 file.
Run from repo root: `python m3_verification/compare20_conditions.py` (mean supply) / `compare20_equity.py` (worst zone). ~10 min each.
Outputs: `mean_sr_20seed_all_conditions.txt`, `worst_zone_20seed_all_conditions.txt`. Official numbers come from M1's eval_all.py.
