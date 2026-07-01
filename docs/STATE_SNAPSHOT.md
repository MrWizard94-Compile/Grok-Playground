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
- Improve rule quality / scheduler further so more runs drive actual synthesis progress on stressed graphs.
- Add "conflicting constraints" stress generator.
- Run the new scaling experiment with even larger graphs (200+) if time/memory allows.
- Add property tests that assert focus bound is never violated.
- Update CLAIMS_REGISTRY with new EXP-005 data.
- Keep obsessively labeling every new artifact.

**No new architectures will be introduced until EP-GRM has been thoroughly attacked along all stress dimensions.**

This snapshot is itself labeled [ESTABLISHED] for the state at the moment of writing.
