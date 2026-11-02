#!/bin/zsh
cd /Users/adithya/College/RL/Project/iws_extract/iws
export IWS_V2=1
venv/bin/python run_jobs.py jobs_M1_seeds.txt 8 > logs/m1_seeds.log 2>&1
cp results_v2/summary.csv results_v2/pre_seeds_summary.csv
venv/bin/python eval_all.py > logs/eval_seeds.log 2>&1
venv/bin/python analyze_final.py > logs/analyze_seeds.log 2>&1
echo DONE > logs/seeds_done.txt
