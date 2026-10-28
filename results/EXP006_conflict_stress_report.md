# EXP-006 + Related Progress Report
**Date:** 2026-07-01  
**Classification:** [SUPPORTED INFERENCE + ESTABLISHED IMPLEMENTATION UPDATES]

## New Stress Dimension: Conflicting Constraints
- Added to `src/tasks/stress.py`
- Graphs now include nodes with "conflicting": True and "conflict_group"
- New rule "handle_conflict" that marks "nogood" + "resolved": "deferred_to_higher"
- This provides **explicit verifiable state transition** for irreconcilable elements (supports H3).

## Key Run: 200 Node Full Stress (EXP-006)
**Parameters:**
- num_nodes=200
- branching=4
- density=0.05
- add_cycles=True
- random_edits=3
- add_conflicts=True
- max_focus=10
- steps=250

**Results [LABELED]:**
- Peak focus: 5
- Final focus: 5
- Graph size: 200 nodes / 1851 edges (dense)
- Movement: 118 (very low)
- Rewrites accepted: 250 (including conflict handling)
- Verifications: 500
- Duration: 0.75s

**Interpretation:**
The system performed useful rewrites (advances + nogood marking) while keeping executive state at 5 out of 10 allowed, even with explicit conflicts.

This is [SUPPORTED INFERENCE] that the EP-GRM mechanisms (bounded focus + local verified rewrites + explicit nogood state) handle competing constraints without focus explosion.

## Plots Generated
- plots/peak_focus_full_stress_scaling_20260701.png : Combined view 25-200 nodes across experiments.

## Code Changes [LABELED]
- Scheduler priority now accounts for conflicts (penalize but allow resolution).
- All changes have [CLASSIFICATION] comments.

## Impact on Hypotheses
- H1 (bounded focus): Stronger support. 200 nodes + conflicts still ~5 focus.
- H2 (movement): Continues to look favorable (118 for large dense graph).
- H3 (verification + explicit handling): Conflict rule provides first-class nogood state.

**Next per best judgement:** Batch multiple runs with conflicts + improved scheduler for statistical distributions. Then consider Phase 10 revision if patterns hold.

All data and claims cross-linked in docs/CLAIMS_REGISTRY.md and EXPERIMENT_REGISTRY.md.
