# EXP-009 ULTRA-HEAVY STRESS TEST REPORT
**Experiment ID:** EXP-009-ULTRA-HEAVY-STRESS-TEST
**Date:** 2026-07-01
**Classification:** [EXTREME FALSIFICATION ATTEMPT + INCREASED CAPABILITIES TEST]

## Configuration (Maximum Stress)
- Nodes: 500
- Branching: 8
- Density: 0.12 (→ 18,934 edges)
- add_cycles: True
- random_edits: 15
- add_conflicts: True
- add_disconnected: True (5+ components with internal conflicts, heavy=True)
- max_focus: 15
- max_steps: 500

## Results [CLASSIFIED]
- **Peak Focus:** 6
- **Final Focus:** 6
- **Final Graph:** ~500 nodes, 18,934 edges (extremely dense + complex)
- **Total Movement:** 235
- **Rewrites Accepted:** 500 (full horizon)
- **Verifications:** 1000
- **Duration:** 7.29s

## Interpretation
[ESTABLISHED]: Bound respected (6 << 15).

[SUPPORTED INFERENCE - Strong]: Despite dramatically increased scale and complexity (500 nodes, 19k edges, 5+ disconnected conflicting subproblems), executive focus remained small and stable. Movement stayed very low while performing full-horizon work.

[POSITIVE for "increased capabilities"]: Focus was *lower* (6) than in 300-node heavy test (which hit 12). The system handled ~2x nodes, ~3.4x edges with *better* relative boundedness and very low movement.

[NO FALSIFICATION]: H1 holds strongly on this extreme instance.

**Plot:** plots/exp009_ultra_heavy_focus_over_time_20260701_034357.png (labeled with classifications)

## Relation to Goals
- Bounded executive state: Strongly supported
- Low data movement: Strongly supported (235 for massive graph)
- Verifiable state transitions: 1000 verifs performed

All narrowly scoped. See updated claims in CLAIMS_REGISTRY.md.

**End of Report** [DOCUMENT - SUPPORTED INFERENCE]