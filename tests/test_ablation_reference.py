# -*- coding: utf-8 -*-
"""The ablation reference configuration must reproduce the repository's own Gamma-Gamma numbers, and the
one-factor variants must move in the physically required direction."""
import os
import sys
import numpy as np
import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(ROOT, 'paper_analysis', 'ablation'))
sys.path.insert(0, os.path.join(ROOT, 'paper_analysis', 'gamma_gamma'))
ablation = pytest.importorskip("ablation")


def test_deterministic_variant_matches_engine():
    """'No turbulence' (alpha = 0.2, infinite decoy) equals the engine's deterministic key rate."""
    from src.tfqkd_engine import TFQKDEngine
    from src.constants import DEFAULT_TFQKD_PARAMS as P
    c = ablation.cfg_of(dict(model='det', bb=0, alpha='fixed'))
    eta = ablation.eta_nom(150.0)
    eng = TFQKDEngine(P['pd'], P['thetaA'], P['thetaB'], Nmax=4)
    # engine uses the corrected residual (v2.4.1); ablation 'tri' mode is the same set
    assert ablation.rate(c, 'moderate', 150.0) == pytest.approx(float(eng.instantaneous_key_rate(0.2, eta)), rel=1e-6)


def test_nmax_is_monotone_and_odd_values_add_nothing():
    base = lambda n: ablation.rate(ablation.cfg_of(dict(alpha='fixed', nmax=n, bb=0)), 'weak', 250.0)
    assert base(2) <= base(4) <= base(6)
    assert base(2) == pytest.approx(ablation.rate(ablation.cfg_of(dict(alpha='fixed', nmax=3, bb=0)), 'weak', 250.0), rel=1e-12)


def test_optimised_alpha_never_below_fixed_and_oracle_above_ergodic():
    fixed = ablation.rate(ablation.cfg_of(dict(alpha='fixed')), 'weak', 200.0)
    opt = ablation.rate(ablation.cfg_of(dict(alpha='opt')), 'weak', 200.0)
    inst = ablation.rate(ablation.cfg_of(dict(alpha='inst')), 'weak', 200.0)
    assert opt >= fixed * (1 - 1e-6)
    assert inst >= opt * (1 - 1e-3)
