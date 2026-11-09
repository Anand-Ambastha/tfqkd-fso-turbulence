# results

Output of the examples in `examples/`, produced with the current code (see `CHANGELOG.md` for the version). Regenerate with
`python examples/example_NN_*.py` from the repository root; example 06 takes about 10 minutes and example 07 about 10 minutes
on one CPU.

| folder | content |
|---|---|
| `figures/` | PNG and PDF figures of examples 01 and 03 to 07 (`docs/FIGURES.md` lists them) |
| `reports/` | Text reports: `MAX_RANGE_REPORT.txt` (example 04), `INSTANTANEOUS_ADAPTIVE_ALL_GRAPHS_REPORT.txt` (example 05), `GAMMA_GAMMA_PER_ARM_REPORT.txt` (example 06), `BEAM_BROADENING_REPORT.txt` (example 07) |
| `logs/` | Console output of each example run, with exit codes and run times in `_progress.txt` |

Setup for all runs: wavelength 1550 nm, beam waist 5 cm, receiver radius 15 cm, 0.2 dB/km attenuation, Cn2 = 1e-17 / 1e-15 / 1e-13
m^(-2/3) for weak / moderate / strong, outage threshold 1e-9 bit/pulse.
