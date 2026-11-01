#!/bin/zsh
cd /Users/adithya/College/RL/Project/iws_extract/iws
export IWS_V2=1
while [ ! -f logs/chain_done.txt ]; do sleep 60; done
mkdir -p results_v2/pre_final && cp results_v2/summary.csv results_v2/pre_final/ 2>/dev/null
venv/bin/python eval_all.py > logs/eval_final.log 2>&1
echo DONE > logs/eval_final_done.txt
