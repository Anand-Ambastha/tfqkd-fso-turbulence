# ablation

Ablation study of the Gamma-Gamma TF-QKD key-rate model. Each variant changes **one** component of the reference
configuration; a cumulative ladder adds components one at a time to the deterministic baseline. It imports `src/` and
`gamma_gamma/lib.py` unchanged and is fully deterministic (quadrature, no random seeds).

**Reference:** Gamma-Gamma fading + long-term beam broadening, independent fading per arm, CSI averaging, ergodic-optimal
alpha, infinite decoy, corrected residual (v2.4.1), Nmax = 4, pd = 1e-7, 150 quadrature nodes per arm. Classes are
Cn2 = 1e-17 / 1e-15 / 1e-13 (weak / moderate / strong); range = largest distance with R > 1e-9 bit/pulse.

| group | variants |
|---|---|
| channel | no beam broadening; no fading (BB loss kept); no turbulence; log-normal fading; one link at full length; perfectly correlated arms |
| receiver | no CSI; fixed alpha = 0.2; per-shot optimal alpha (oracle upper bound) |
| security | finite decoy (3 intensities, LP); residual before v2.4.1; Nmax = 2, 6, 8 |
| numerics | quadrature nodes per arm 20 to 250 (convergence table) |
| ladder | S0 deterministic -> +log-normal -> Gamma-Gamma -> +beam broadening -> +alpha optimisation -> +finite decoy -> +no CSI |

## Run

```bash
python paper_analysis/ablation/ablation.py smoke   # ~1 min, 4 variants, writes results/smoke/ only
sh paper_analysis/ablation/run_all.sh              # full study, ~35 min on one CPU, then figures and LaTeX table
python -m pytest tests/test_ablation_reference.py tests/test_ablation_components.py
```

Stages can also be run alone: `ablation.py points|ranges|ladder|sweep|numerics`. Outputs: `results/tables/ablation_*.csv`,
`ablation_table.tex` (booktabs, ready to `\input`), and `results/figures/abl_F1..F3` (range change per variant, R(L)
curves, ladder).

## Reading the results

- Odd Nmax adds no photon-number pairs to the triangular sets (n_A + n_B <= Nmax), so Nmax = 3 equals 2 and 5 equals 4.
  Only even values are listed. The key rate is non-decreasing in Nmax, so Nmax = 4 is a conservative truncation, not a
  converged one; check the Nmax rows before quoting absolute ranges.
- "One link at full length" keeps the beam-broadening factor of the reference and replaces only the fading law.
- "Perfectly correlated arms" (eta = eta_arm^2) is a what-if bound, not a physical claim: the arms cross different air columns.
- "Per-shot optimal alpha" needs the instantaneous eta at the transmitter and is an oracle upper bound.
- Protocol parameters (pd, theta) are not ablated here: they are parameter sweeps rather than model components.
- The analytic-expansion truncation (naive / 2nd / 4th order) is already tabulated in `gamma_gamma/results/tables/master_points.csv`.
- Ranges use 150 quadrature nodes per arm. The `numerics` stage (convergence table) is not part of the shipped results; run
  `ablation.py numerics` before interpreting range differences of a km or less.
