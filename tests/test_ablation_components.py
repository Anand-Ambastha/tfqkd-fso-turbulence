# -*- coding: utf-8 -*-
"""Cross-check of the ablation reference against the repo's master table, and direction of the channel ablations."""
import os
import sys
import pandas as pd
import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(ROOT, 'paper_analysis', 'ablation'))
sys.path.insert(0, os.path.join(ROOT, 'paper_analysis', 'gamma_gamma'))
A = pytest.importorskip("ablation")


def R(over, cls='moderate', L=200.0):
    return A.rate(A.cfg_of(dict(alpha='fixed', **over)), cls, L)


def test_matches_master_table_table():
    m = pd.read_csv(os.path.join(ROOT, 'paper_analysis', 'gamma_gamma', 'results', 'tables', 'master_points.csv'))
    row = m[(m.finite == 0) & (m.case == 'alpha=0.2') & (m.bb == 1) & (m.cls == 'weak') & (m.L_km == 250)]
    assert R(dict(), 'weak', 250.0) == pytest.approx(float(row.R_quad.iloc[0]), rel=0.01)


def test_channel_ablations_move_the_right_way():
    ref = R(dict())
    assert R(dict(bb=0)) > ref            # beam broadening only removes mean power
    assert R(dict(model='ln')) < ref      # log-normal is pessimistic in this regime
    assert R(dict(arms='single')) < ref   # one fading factor at full length overstates the log-variance
