# IWS-RL project log

## 2026-11-01 - scarce-supply anomaly explained (not a bug)
- Scarce condition (supply 0.3-0.5 of demand): all 10 PPO variants give identical mean_sr (0.4754) and min_zone_sr.
- Cause: every PPO policy opens all zones (action 15) in ~3 hours per day, which spends the whole daily budget by ~12:00
  (delivery capped at alpha=4x mean demand per hour); later actions are no-ops. Policies differ only in post-exhaustion actions.
- Implication: in the scarce regime the env has no zone-scheduling decision (budget is gone in 3 h), so no method can differ. 
  Treat scarce rows as "env degenerate", not as evidence for/against PPO. Env design issue: budget/surge coupling makes rotation moot.
- Scripts: scarce_diag.py, scarce_trace.py (run with ./venv/bin/python).
