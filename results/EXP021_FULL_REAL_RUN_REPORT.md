# EXP-021: Full Real Ultra-Heavy 2000 Node Run Report
**Date:** 2026-07-01
**Classification:** [SUPPORTED INFERENCE - Strong] "For shits and giggles"

## Config
- 2000 nodes base + heavy disconnected (~3759 total)
- Full stress: cycles, conflicts (internal), disconnected, edits, density, branching
- max_focus=15
- 200 steps

## Results (ALL data captured)
- Peak focus: 15 (saturated, respected)
- Rewrites: 200 (full, useful work)
- Locality: 0.054 (5.4%)
- Efficiency: 0.0681
- Value/rew: 2.0
- Focus over time: 5 -> 15 (saturates)
- Duration: 12s
- Trace: 200 entries
- Series: full (focus, movement, rewrites, touched, admissions, value per step)

## Interpretation [LABELED]
- At extreme scale (2000/3759 nodes, max stress), executive state bounded at configured max while full work sustained.
- Locality 5.4% - continues downward trend with scale.
- [SUPPORTED INFERENCE - Strong for H1]: Bound holds, useful work (rewrites + value) consistent, locality improves (shrinking fraction).
- All data captured for future analysis ("thank ourselves later").

## Artifacts
- results/exp021_full_heavy_20260701_full/full_series.csv
- results/exp021_full_heavy_20260701_full/master.csv
- plots/exp021_focus_over_time.png

**Consolidated with prior:** Locality drops with scale across 200-2000 nodes. Plateau/saturation at max_focus but work done. Frontier correlation holds.

This is the data haul. H1 robust. 

See EXPERIMENT_REGISTRY, CLAIMS for labels.