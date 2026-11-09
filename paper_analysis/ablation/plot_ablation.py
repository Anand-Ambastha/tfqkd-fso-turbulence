"""Figures and LaTeX table for the ablation study (reads results/tables/ablation_*.csv)."""
import os
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(HERE, 'results', 'tables'); F = os.path.join(HERE, 'results', 'figures')
os.makedirs(F, exist_ok=True)
CLS = ['weak', 'moderate', 'strong']; COL = {'weak': '#1b9e77', 'moderate': '#d95f02', 'strong': '#7570b3'}
plt.rcParams.update({'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False})
def save(fig, name):
    fig.savefig(os.path.join(F, name + '.png'), dpi=300, bbox_inches='tight'); fig.savefig(os.path.join(F, name + '.pdf'), bbox_inches='tight'); plt.close(fig)

# ---- F1: change in maximum range per variant (one factor at a time) ----
rg = pd.read_csv(os.path.join(T, 'ablation_ranges.csv'))
order = [v for v in rg.variant.unique() if v != 'Reference']
fig, ax = plt.subplots(figsize=(7.2, 0.34 * len(order) + 1.2))
h = 0.26
for k, cls in enumerate(CLS):
    d = rg[rg.cls == cls].set_index('variant')
    for i, v in enumerate(order):
        r, ref = d.loc[v, 'range_km'], d.loc[v, 'range_ref_km']
        if pd.isna(r): ax.text(0, i + (k - 1) * h, ' < 10 km', va='center', fontsize=7, color=COL[cls]); continue
        ax.barh(i + (k - 1) * h, r - ref, height=h, color=COL[cls], label=f"{cls} (ref {ref:.0f} km)" if i == 0 else None)
ax.axvline(0, color='k', lw=.8); ax.set_yticks(range(len(order))); ax.set_yticklabels(order); ax.invert_yaxis()
ax.set_xlabel('change in maximum range vs reference [km]  (R > $10^{-9}$ bit/pulse)'); ax.legend(frameon=False, loc='lower left')
save(fig, 'abl_F1_range_change')

# ---- F2: R(L) curves, moderate turbulence ----
sw = pd.read_csv(os.path.join(T, 'ablation_sweep.csv'))
fig, ax = plt.subplots(figsize=(5.2, 3.4))
sty = {'Reference': ('k', '-'), 'No beam broadening': ('#d95f02', '-'), 'No turbulence (deterministic)': ('gray', '--'),
       'Log-normal fading': ('#7570b3', '-'), 'No CSI (averaged statistics)': ('#e7298a', ':'),
       'Fixed alpha = 0.2': ('#66a61e', '-.'), 'Finite decoy (3 intensities, LP)': ('#1b9e77', '-')}
for v, (c, ls) in sty.items():
    d = sw[sw.variant == v]; y = d.R.where(d.R > 1e-14)
    ax.semilogy(d.L_km, y, color=c, ls=ls, label=v)
ax.axhline(1e-9, color='k', lw=.5, alpha=.5); ax.set_ylim(1e-12, 1e-1); ax.set_xlabel('total distance [km]'); ax.set_ylabel('key rate [bit/pulse]')
ax.set_title('Moderate turbulence, $C_n^2=10^{-15}$ m$^{-2/3}$', fontsize=9); ax.legend(frameon=False, fontsize=6.5, loc='lower left')
save(fig, 'abl_F2_rate_vs_distance')

# ---- F3: ladder ----
ld = pd.read_csv(os.path.join(T, 'ablation_ladder.csv')); steps = list(ld.step.unique())
fig, ax = plt.subplots(figsize=(6.6, 3.2)); w = 0.26
for k, cls in enumerate(CLS):
    d = ld[ld.cls == cls].set_index('step')
    ax.bar(np.arange(len(steps)) + (k - 1) * w, [d.loc[s, 'range_km'] if pd.notna(d.loc[s, 'range_km']) else 0 for s in steps], width=w, color=COL[cls], label=cls)
ax.set_xticks(range(len(steps))); ax.set_xticklabels([s.split(' ')[0] for s in steps]); ax.set_ylabel('maximum range [km]'); ax.legend(frameon=False, title='$C_n^2$ class', fontsize=7)
ax.set_title('\n'.join([f"{s}" for s in steps[:0]]), fontsize=7)
save(fig, 'abl_F3_ladder')

# ---- LaTeX table: range change and rate change at 200 km ----
pt = pd.read_csv(os.path.join(T, 'ablation_points.csv'))
def esc(s): return s.replace('&', r'\&').replace('_', r'\_').replace('alpha', r'$\alpha$').replace('Nmax', r'$N_{\max}$')
lines = [r'\begin{tabular}{llrrrrrr}', r'\toprule',
         r' & & \multicolumn{3}{c}{max.\ range [km]} & \multicolumn{3}{c}{$R/R_{\rm ref}$ at $L=200$ km} \\',
         r'\cmidrule(lr){3-5}\cmidrule(lr){6-8}', r'group & variant & weak & mod. & strong & weak & mod. & strong \\', r'\midrule']
for v in rg.variant.unique():
    g = rg[rg.variant == v].set_index('cls'); p = pt[(pt.variant == v) & (pt.L_km == 200)].set_index('cls')
    rr = [('--' if pd.isna(g.loc[c, 'range_km']) else f"{g.loc[c, 'range_km']:.1f}") for c in CLS]
    pp = []
    for c in CLS:
        ref = p.loc[c, 'R_ref']; x = p.loc[c, 'R']
        pp.append('--' if ref <= 1e-12 else ('0' if x <= 0 else f"{x/ref:.2g}"))
    lines.append(f"{rg[rg.variant==v].group.iloc[0]} & {esc(v)} & " + ' & '.join(rr + pp) + r' \\')
lines += [r'\bottomrule', r'\end{tabular}']
open(os.path.join(T, 'ablation_table.tex'), 'w').write('\n'.join(lines) + '\n')
print('figures and table written')
