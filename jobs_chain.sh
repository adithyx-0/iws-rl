#!/bin/zsh
cd /Users/adithya/College/RL/Project/iws_extract/iws
export IWS_V2=1
while pgrep -f eval_all.py >/dev/null; do sleep 30; done
venv/bin/python run_jobs.py jobs_M2_v1.txt 6 > logs/m1_fallback_M2.log 2>&1 &
for s in 0 1 2; do venv/bin/python bo_schedule_tuned.py 40 60 $s > logs/ce_tuned_s$s.log 2>&1; done
wait
echo ALLDONE > logs/chain_done.txt
