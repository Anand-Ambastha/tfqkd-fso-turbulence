# paper_analysis

Scripts, tables, figures and LaTeX sources behind the manuscript on turbulence-averaged TF-QKD key rates. Everything here imports
`src/` and `analytical_validation/` unchanged.

| folder | content |
|---|---|
| `gamma_gamma/` | Gamma-Gamma key-rate analysis with independent fading on each arm: CSI and no-CSI averaging, amplitude optimisation, finite decoy (`docs/FINITE_DECOY.md`), beam broadening, analytic expansion against quadrature (`gamma_gamma/README.md`) |
| `ablation/` | Ablation study of that model: one component changed at a time, plus a cumulative ladder (`ablation/README.md`, `docs/ABLATION.md`) |
| `scripts/` | Per-arm tables and errors of the analytic expansion (log-normal and Gamma-Gamma), the controlled sigma_X^2 sensitivity study, and the builders of the LaTeX tables |
| `latex/` | `paper_content/` (result tables and derivation) and `sensitivity_study/`; sources only, build with `pdflatex` |
| `results/` | Tables (`tables/`), figures (`figures/`) and run logs (`logs/`) written by `scripts/` |

## Regenerate

From the repository root, in this order:

```bash
python analytical_validation/run_all.py                 # about 30 s, writes analytical_validation/results/
for f in beam_wander_table ln_error_vs_distance ln_vs_gg_per_arm perarm_analytic_errors \
         sensitivity_study sensitivity_thresholds sensitivity_figures; do python paper_analysis/scripts/$f.py; done
python paper_analysis/scripts/sensitivity_make_tex.py
python paper_analysis/scripts/paper_make_tables.py
python paper_analysis/scripts/paper_assemble_tex.py
sh paper_analysis/gamma_gamma/run_all.sh                # about 35 min
python paper_analysis/ablation/ablation.py all          # about 35 min, then plot_ablation.py
```

`results/tables/perarm_analytic_errors.csv` covers 20 to 300 km. Rows where the exact key rate is essentially zero (moderate
turbulence with beam broadening beyond about 200 km) have meaningless relative errors and are reported as `nan` or very large values.
