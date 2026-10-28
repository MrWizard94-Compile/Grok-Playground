# EXP-008 HEAVY STRESS TEST REPORT
**Experiment ID:** EXP-008-HEAVY-STRESS-TEST
**Date:** 2026-07-01
**Classification:** [AGGRESSIVE FALSIFICATION ATTEMPT + TEST OF INCREASED CAPABILITIES]

## Configuration (Maximum Stress)
- Nodes: 300
- Branching: 6
- Density: 0.08 (resulting in 5574 edges)
- add_cycles: True
- random_edits: 8
- add_conflicts: True (multiple groups)
- add_disconnected: True (3 components via heavy=True)
- max_focus: 12
- max_steps: 400

## Results [CLASSIFIED]
- **Peak Focus:** 12
- **Final Focus:** 12
- **Final Graph Size:** ~300 nodes, 5574 edges
- **Total Movement:** 1380
- **Rewrites Accepted:** 400
- **Verifications:** 800
- **Node Visits:** (from series)
- **Duration:** 2.76 seconds
- **Acceptance:** False (expected for stress)

## Interpretation
[ESTABLISHED]: The focus bound was respected throughout. No exceedance occurred.

[SUPPORTED INFERENCE]: Under this extreme combined stress (far beyond previous tests), the EP-GRM implementation was able to sustain 400 rewrites while keeping executive state at the configured maximum.

[WORKING HYPOTHESIS update]: The architecture demonstrates "increased capabilities" to operate without collapse at 300-node / 5.5k-edge scale with conflicts and disconnected subproblems. However, it fully utilizes the allowed focus budget.

[NEGATIVE / EDGE DATA]: Hit the max focus. This is not a failure of the bound (it held), but indicates the current focus management policy saturates here. Useful for future scheduler refinements.

## Plots
- plots/exp008_heavy_focus_over_time_20260701_034039.png (focus climbs to 12 and holds while work continues)

## Artifacts
- results/exp008_heavy_stress_20260701_034039.csv
- results/exp008_heavy_series_20260701_034039.csv

## Relation to Hypotheses
- Strongly supports H1 on this heavy instance (bounded state held).
- H2: Movement of 1380 for 5574-edge graph over 400 steps is still relatively contained given the density.
- Provides data point where "increased capabilities" (sustained work under heavy load) were tested.

All claims narrowly scoped. See CLAIMS_REGISTRY.md for updated H1-005.

**End of Report** [DOCUMENT - SUPPORTED INFERENCE]