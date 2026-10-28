# EP-GRM Implementation Directory

**Status (2026-07-01):** Tier 1 done + envelope pushed in sim. Tier 2 skeleton started.

**Current Reality:** All validation has been performed inside the Python + NetworkX reference simulator (see root `SIMULATION_LIMITS_AND_PATH_TO_REALIZATION.md`).

**Tier 2 Starter:** `tier2_reference_skeleton.py` - pure dict-based VersionedGraph + FocusSet stub (no networkx). Expand for ref impl.

**Planned Contents (Tiers):**
- `spec/` — Formal interface and semantics definition (to be used by any real implementation).
- `reference/` — Full reference (expand skeleton).
- `fidelity/` — Comparison harness between simulator and real impl.
- `hardware/` — Sketches for PIM / accelerator mapping.

This directory will only contain artifacts that have left pure simulation.

See also:
- `SIMULATION_LIMITS_AND_PATH_TO_REALIZATION.md` (root)
- `results/PHASE10_REVISION.md`
- Phase 6/7 iteration documents
- simulations/high_fidelity/ for Tier 1

*Nothing in this directory has yet been executed or measured outside the simulator.*