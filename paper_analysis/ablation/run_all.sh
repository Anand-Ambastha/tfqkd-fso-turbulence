#!/bin/sh
# Run from anywhere: sh paper_analysis/ablation/run_all.sh
# About 35 minutes on one CPU (the stages are independent except plot_ablation.py, which needs all tables).
set -e
cd "$(dirname "$0")"
mkdir -p results/tables results/figures
python3 ablation.py all > results/ablation.log 2>&1
python3 plot_ablation.py
