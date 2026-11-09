#!/bin/sh
# Run from the repo root: sh paper_analysis/gamma_gamma/run_all.sh
# Roughly 35 minutes on one CPU. The scripts are independent except plot_all.py, which needs all tables.
set -e
cd "$(dirname "$0")"
python3 distance_sweeps.py   > results/distance_sweeps.log  2>&1
python3 fading_decomposition_alpha.py > results/fading_decomposition_alpha.log 2>&1
python3 finite_decoy.py   > results/finite_decoy.log 2>&1
python3 analytic_vs_quad.py > results/analytic_vs_quadrature.log 2>&1
python3 master_table.py points > results/master_points.log 2>&1
python3 master_table.py ranges > results/master_ranges.log 2>&1
python3 plot_all.py
