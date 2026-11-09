"""Ablation study of the Gamma-Gamma TF-QKD key-rate model.

Every variant changes ONE component of the reference configuration (or, in the ladder, adds components one at a
time to the deterministic baseline). Components:

  channel     fading law (Gamma-Gamma / log-normal / none), long-term beam broadening, arm structure
              (independent per arm / one link at full length / perfectly correlated arms)
  receiver    CSI vs no-CSI averaging, amplitude policy (fixed 0.2 / ergodic optimum / per-shot optimum)
  security    infinite vs finite decoy (3-decoy LP), residual Delta_j before/after v2.4.1, photon cut-off Nmax
  numerics    quadrature nodes per arm

Reference = Gamma-Gamma + beam broadening, independent arms, CSI, ergodic-optimal alpha, infinite decoy,
corrected residual, Nmax = 4, pd = 1e-7, 100 quadrature nodes per arm. Everything is deterministic (quadrature),
so no random seeds are involved.

Usage (from anywhere):  python ablation.py smoke|points|ranges|ladder|sweep|numerics|all
  smoke : ~1 min sanity run (4 variants, moderate class), writes only to results/smoke/
  all   : full study, roughly 35 min on one CPU (ranges and ladder dominate)
"""
import os, sys, csv, json, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'gamma_gamma'))
from lib import *                                    # imports src/ unchanged (see gamma_gamma/lib.py)
from src.turbulence.beam_broadening import beam_broadening_factor

OUT = os.path.join(HERE, 'results', 'tables')
os.makedirs(OUT, exist_ok=True)
T0 = time.time()
def log(*a): print(f"[{time.time()-t0_():6.0f}s]", *a, flush=True)
def t0_(): return T0

CLS = {'weak': 1e-17, 'moderate': 1e-15, 'strong': 1e-13}
POINT_L = [100, 150, 200, 250]
N_ARM = 150          # quadrature nodes per arm (same as the range searches in gamma_gamma/master_table.py)
N_ONE = N_ARM ** 2   # nodes for the one-factor variants (single link, correlated arms)

REF = dict(model='gg', bb=1, arms='indep', conv='csi', alpha='opt', decoy=False, resid='tri', nmax=4, n=N_ARM)

# ---- one-factor-at-a-time variants: (name, group, overrides) ----
VARIANTS = [
    ('Reference',                         'ref',      {}),
    ('No beam broadening',                'channel',  dict(bb=0)),
    ('No fading, beam-broadening loss kept', 'channel', dict(model='det')),
    ('No turbulence (deterministic)',     'channel',  dict(model='det', bb=0)),
    ('Log-normal fading',                 'channel',  dict(model='ln')),
    ('One link at full length',           'channel',  dict(arms='single')),
    ('Perfectly correlated arms',         'channel',  dict(arms='corr')),
    ('No CSI (averaged statistics)',      'receiver', dict(conv='nocsi')),
    ('Fixed alpha = 0.2',                 'receiver', dict(alpha='fixed')),
    ('Per-shot optimal alpha (oracle)',   'receiver', dict(alpha='inst')),
    ('Finite decoy (3 intensities, LP)',  'security', dict(decoy=True)),
    ('Residual before v2.4.1',            'security', dict(resid='repo')),
    ('Nmax = 2',                          'security', dict(nmax=2)),
    ('Nmax = 6',                          'security', dict(nmax=6)),
    ('Nmax = 8',                          'security', dict(nmax=8)),
]

# ---- cumulative ladder: deterministic baseline -> realistic receiver ----
LADDER = [
    ('S0 deterministic, alpha=0.2',        dict(model='det', bb=0, alpha='fixed')),
    ('S1 + log-normal fading',             dict(model='ln',  bb=0, alpha='fixed')),
    ('S2 log-normal -> Gamma-Gamma',       dict(model='gg',  bb=0, alpha='fixed')),
    ('S3 + beam broadening',               dict(model='gg',  bb=1, alpha='fixed')),
    ('S4 + optimised alpha',               dict(model='gg',  bb=1, alpha='opt')),
    ('S5 + finite decoy',                  dict(model='gg',  bb=1, alpha='opt', decoy=True)),
    ('S6 + no CSI',                        dict(model='gg',  bb=1, alpha='opt', decoy=True, conv='nocsi')),
]

def cfg_of(over): c = dict(REF); c.update(over); return c

# ---------------------------------------------------------------- caches
def fb2(cn2, L): return float(beam_broadening_factor(cn2, LAM, 0.5 * L * 1e3, W0, RX)) ** 2
_NODES = {}
def base_nodes(model, arms, cn2, L, n):
    key = (model, arms, cn2, L, n)
    if key in _NODES: return _NODES[key]
    name = {'gg': 'gamma_gamma', 'ln': 'lognormal'}[model]
    if arms == 'indep':
        ch = build(name, cn2, L); e, w = nodes(ch, n)
    elif arms == 'single':
        ch = build(name, cn2, L, two_link=False); e, w = nodes(ch, N_ONE)
    elif arms == 'corr':          # same fading realisation on both arms: eta = eta_arm^2
        ch = build(name, cn2, L); eA, w = ch.link_A.quadrature_nodes(N_ONE); e = np.clip(eA ** 2, 1e-300, 1.0)
    else: raise ValueError(arms)
    _NODES[key] = (e, w); return e, w

def get_ew(c, cn2, L):
    s = fb2(cn2, L) if c['bb'] else 1.0
    if c['model'] == 'det': return np.array([eta_nom(L) * s]), np.array([1.0])
    e, w = base_nodes(c['model'], c['arms'], cn2, L, c['n'])
    return e * s, w

_TAB = {}
def tab3():
    if 'T' not in _TAB: _TAB['T'] = YieldTable(DEC3, n=300); log("finite-decoy yield table built")
    return _TAB['T']

_INST = {}
def inst_table(finite):
    """Rmax(eta): alpha optimised per eta (exact yields, or 7 LP yields), tri residual, Nmax=4."""
    if finite in _INST: return _INST[finite]
    lg = np.linspace(-10.5, 0, 260); Rm = np.zeros_like(lg)
    sets = SETS_7 if finite else SETS_TRI; yf = tab3() if finite else None
    for i, l in enumerate(lg):
        eta = np.array([10 ** l])
        f = (lambda a: float(R_exact(a, eta, sets=sets, mode='tri', yfun=yf)[0])) if finite else (lambda a: float(R_exact(a, eta, sets=sets, mode='tri')[0]))
        Rm[i] = opt_alpha(f)[1]
    _INST[finite] = (lg, Rm); log("per-shot table built, finite =", finite); return _INST[finite]

# ---------------------------------------------------------------- rate of one configuration at one (class, L)
def rate(c, cls, L):
    cn2 = CLS[cls]; e, w = get_ew(c, cn2, L)
    decoy = DEC3 if c['decoy'] else None
    sets = SETS_7 if c['decoy'] else {j: S_TRI(j, c['nmax']) for j in (0, 1)}
    table = tab3() if c['decoy'] else None
    if c['alpha'] == 'inst':
        assert c['conv'] == 'csi' and c['nmax'] == 4 and c['resid'] == 'tri'
        lg, Rm = inst_table(bool(c['decoy']))
        return float(np.sum(w * np.interp(np.log10(e), lg, Rm, left=0.0)))
    yb = prep_nocsi(e, w, decoy) if c['conv'] == 'nocsi' else None
    f = lambda a: R_point(a, e, w, c['conv'], decoy, sets, c['resid'], table, yb)
    if c['alpha'] == 'fixed': return f(0.2)
    return opt_alpha(f)[1]

def max_range_km(c, cls, step=10.0, Lmax=340.0, iters=12):
    """Largest total distance with R > 1e-9 bit/pulse: step outwards until the first failure, then bisect."""
    L = step
    if rate(c, cls, L) <= THR: return None
    while L + step <= Lmax and rate(c, cls, L + step) > THR: L += step
    if L + step > Lmax: return float(L)
    lo, hi = L, L + step
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if rate(c, cls, mid) > THR: lo = mid
        else: hi = mid
    return 0.5 * (lo + hi)

def write(name, rows):
    keys = list(rows[0].keys())
    with open(os.path.join(OUT, name), 'w', newline='') as f:
        wr = csv.DictWriter(f, fieldnames=keys); wr.writeheader(); wr.writerows(rows)

# ---------------------------------------------------------------- stages
def stage_points():
    rows = []
    for cls in CLS:
        for L in POINT_L:
            Rref = rate(cfg_of({}), cls, L)
            for name, grp, over in VARIANTS:
                R = Rref if name == 'Reference' else rate(cfg_of(over), cls, L)
                rows.append(dict(variant=name, group=grp, cls=cls, L_km=L, R=R, R_ref=Rref,
                                 rel_change_pct=(100 * (R - Rref) / Rref) if Rref > 1e-15 else float('nan')))
            log("points", cls, L)
    write('ablation_points.csv', rows)

def classes():
    """All classes, or the comma-separated subset in the environment variable ABLATION_CLASSES (for partial runs)."""
    sel = os.environ.get('ABLATION_CLASSES')
    return [c for c in CLS if (not sel or c in sel.split(','))]

def stage_ranges():
    rows = []; ref = {}
    for cls in classes():
        ref[cls] = max_range_km(cfg_of({}), cls); log("range ref", cls, ref[cls])
        for name, grp, over in VARIANTS:
            r = ref[cls] if name == 'Reference' else max_range_km(cfg_of(over), cls)
            rows.append(dict(variant=name, group=grp, cls=cls, range_km=r, range_ref_km=ref[cls],
                             delta_km=(r - ref[cls]) if (r is not None and ref[cls] is not None) else None))
            log("range", cls, name, r)
        write('ablation_ranges.csv', rows)

def stage_ladder():
    rows = []
    for cls in classes():
        prev = None
        for name, over in LADDER:
            c = cfg_of(over); r = max_range_km(c, cls)
            R = {L: rate(c, cls, L) for L in POINT_L}
            rows.append(dict(step=name, cls=cls, range_km=r, step_delta_km=(r - prev) if (r is not None and prev is not None) else None,
                             **{f'R_{L}km': R[L] for L in POINT_L}))
            prev = r; log("ladder", cls, name, r)
    write('ablation_ladder.csv', rows)

def stage_sweep():
    """R(L) curves for the moderate class and the variants that are plotted in figure F2."""
    names = ['Reference', 'No beam broadening', 'No turbulence (deterministic)', 'Log-normal fading',
             'No CSI (averaged statistics)', 'Fixed alpha = 0.2', 'Finite decoy (3 intensities, LP)']
    sel = [(n, o) for n, g, o in VARIANTS if n in names]
    Ls = np.arange(10, 330, 10.0); rows = []
    for cls in ('moderate',):
        for n, o in sel:
            c = cfg_of(o)
            for L in Ls: rows.append(dict(variant=n, cls=cls, L_km=float(L), R=rate(c, cls, float(L))))
            log("sweep", n)
    write('ablation_sweep.csv', rows)

def stage_numerics():
    rows = []
    for cls, L in (('moderate', 190), ('strong', 70), ('weak', 270)):   # all with R > 0 at alpha = 0.2
        ref = None
        for n in (20, 40, 70, 100, 150, 250):
            c = cfg_of(dict(alpha='fixed', n=n)); R = rate(c, cls, L)
            if n == 250: ref = R
            rows.append(dict(cls=cls, L_km=L, n_per_arm=n, nodes_total=n * n, R=R))
        for r in rows:
            if r['cls'] == cls and r['L_km'] == L: r['err_vs_250_pct'] = (100 * (r['R'] - ref) / ref) if ref > 0 else float('nan')
        log("numerics", cls, L)
    write('ablation_numerics.csv', rows)

def stage_smoke():
    global OUT
    OUT = os.path.join(HERE, 'results', 'smoke'); os.makedirs(OUT, exist_ok=True)
    pick = ['Reference', 'No beam broadening', 'Fixed alpha = 0.2', 'Nmax = 6']
    rows = []
    for name, grp, over in VARIANTS:
        if name not in pick: continue
        c = cfg_of(over)
        rows.append(dict(variant=name, R_200km=rate(c, 'moderate', 200.0), range_km=max_range_km(c, 'moderate', step=20.0, iters=6)))
        log("smoke", rows[-1])
    write('smoke.csv', rows)
    ref = rows[0]; assert ref['range_km'] is not None and 150 < ref['range_km'] < 300, ref
    print("smoke OK ->", os.path.join(OUT, 'smoke.csv'))

if __name__ == '__main__':
    st = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if st == 'smoke': stage_smoke(); sys.exit(0)
    for s, f in (('points', stage_points), ('ranges', stage_ranges), ('ladder', stage_ladder), ('sweep', stage_sweep), ('numerics', stage_numerics)):
        if st in (s, 'all'): f()
    log("DONE", st)
