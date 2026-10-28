# CURRENT RESEARCH STATE SNAPSHOT
**Timestamp:** 2026-07-01  
**Iteration:** 001  
**Focus:** EP-GRM only (per strategy)

## Obsessive Documentation Completed This Session
- `docs/RESEARCH_MANIFEST.md` — Central index with labels
- `docs/CLAIMS_REGISTRY.md` — Every major claim explicitly classified + evidence links
- `docs/EPGRM_INVARIANTS.md` — What must always hold
- `docs/EXPERIMENT_REGISTRY.md` — All experiments tracked with IDs
- `docs/STATE_SNAPSHOT.md` (this file)
- Heavy [CLASSIFICATION] headers added to all core .py modules
- All results files cross-referenced

## Latest Quantitative Evidence (as of this snapshot)

**From EXP-005-SCALING-CLEAN (new, 18 runs, up to 120 nodes):**
- 20 nodes → mean peak focus 4.0
- 120 nodes → mean peak focus 5.3 (max 6)
- Extremely flat scaling even with cycles enabled

**Previous Stress Sweep (96 runs):**
- Max peak focus ever observed: 7 (max allowed 10)
- Insensitive to branching, cycles, density, edits

**Live example:**
- 100 nodes / 895 edges + cycles + edits: peak focus = 5

## Files You Should Look At (in order)
1. `docs/CLAIMS_REGISTRY.md`
2. `results/stress_sweep_summary.md`
3. `docs/EPGRM_INVARIANTS.md`
4. plots/*.png (the three generated)
5. `results/bounded_focus_scaling_20260701_031734.csv`
6. `logs/RESEARCH_LOG.md` (for full history)

## Next Actions (Best Judgement)
- [IN PROGRESS] Run additional batch at 250 nodes + disconnected for more stats.
- Analyze focus-over-time series for stability (low variance when bounded).
- Generate verification cost vs size/reviews plots.
- Add more property tests (nogood determinism, scheduler priority monotonicity).
- Update all registries with EXP-007 evidence (completed for this cycle).
- Prepare consolidated evidence summary if pattern holds.

**No new architectures will be introduced until EP-GRM has been thoroughly attacked along all stress dimensions.**

**This snapshot updated 2026-07-01 post-EXP-007 [ESTABLISHED].**
- Key new data: In 10 full-stress runs (150/200 nodes), peak focus 5-8 typical, max 10 (respected). Strong support for H1.
