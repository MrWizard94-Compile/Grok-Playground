# CLAIMS REGISTRY — Iteration 001
**Status:** [LIVING DOCUMENT]  
**Last Updated:** 2026-07-01  
**Rule:** Every claim must have an explicit classification, supporting evidence link, falsification criteria, and scope.

## Classification Legend
- **[ESTABLISHED]** — Directly observable property of the simulator on the listed runs. Reproducible.
- **[SUPPORTED INFERENCE]** — Logical conclusion from data, but scoped to the exact tasks + baselines used.
- **[WORKING HYPOTHESIS]** — Core research claim still under active testing/falsification.
- **[SPECULATION]** — Not yet connected to runnable experiments.
- **[NEGATIVE / FALSIFIED IN THIS SCOPE]** — Attempted and did not hold under the conditions.

---

## Claim H1-BOUNDED-FOCUS-001
**Statement:** The EP-GRM reference implementation maintains a small, bounded active focus (executive state) while operating on graphs significantly larger than the focus size.

**Classification:** [SUPPORTED INFERENCE - Narrow]

**Scope:** Synthetic graphs 25–100 nodes, linear chain tasks, various branching/density/cycle/edit parameters. Max configured focus = 8 or 10.

**Evidence:**
- Linear n=25: peak_focus = 3
- Stress sweep 96 runs (results/epgrm_stress_sweep_20260701_015355.csv):
  - 25 nodes: mean peak 4.0, max 4
  - 50 nodes: mean peak 5.1, max 7
  - 100 nodes: mean peak 5.2, max 7
- Live 100-node dense cyclic run: peak_focus = 5 (max allowed 8)

**Falsification Criteria (current):**
- Any run where peak_focus > configured max_focus.
- Trend where mean peak_focus grows linearly with node count beyond small constant factor.

**Current Status:** Not falsified on tested instances. Focus growth is sub-linear and stays low.

**Related Code:** `src/core.py:FocusSet`, `src/epgrm_sim.py` (focus update logic)

---

## Claim H1-BOUNDED-FOCUS-002
**Statement:** Introducing cycles, higher branching (5), higher density (0.08), and random edits does not cause focus size to explode.

**Classification:** [SUPPORTED INFERENCE - Narrow]

**Evidence:** Breakdown in `results/stress_sweep_summary.md` and sweep CSV.
- Cycles on vs off: mean peak 4.7 vs 4.8
- Branching 5 vs 2: almost identical means

**Falsification:** Significant increase in peak when any of those factors are enabled.

**Status:** Supported on current data.

---

## Claim MOVEMENT-001
**Statement:** EP-GRM cumulative movement (node size proxy) is low and does not grow proportionally with total graph size or steps taken, relative to full-reload baselines.

**Classification:** [SUPPORTED INFERENCE - Baseline dependent]

**Scope:** Compared to NaiveContextAgent and FullStateReloadPlanner in the same harness.

**Evidence:**
- Linear chain: EP-GRM ~98 vs baselines ~200k
- Stress sweep avg movement: 83

**Warning Label:** [BASELINE DEPENDENT] — These baselines deliberately reload large state every step. Not equivalent to optimized conventional systems.

**Falsification:** When using better baselines, movement advantage disappears.

---

## Claim IMPLEMENTATION-001 (Established)
**Statement:** The simulator correctly enforces the configured focus bound at all times.

**Classification:** [ESTABLISHED]

**Evidence:** 
- `FocusSet.add()` returns False when full.
- Tests in `tests/test_epgrm_core.py` pass.
- All 96+ runs never exceeded configured max.

**Falsification Criteria:** Any execution where len(focus) > max_size after a step.

---

## Claim DETERMINISM-001 (Established)
**Statement:** For identical initial graph, rules, seed (where used), and max_steps, execution trace and final focus size are identical.

**Classification:** [ESTABLISHED]

**Evidence:** Multiple repeated seeds in sweep produced consistent results. Code is pure (no global random without seed).

---

## Claim STRESS-ROBUSTNESS-001
**Statement:** EP-GRM can run for hundreds of steps on 100-node graphs containing cycles and noise without focus size violating the bound.

**Classification:** [SUPPORTED INFERENCE]

**Evidence:** 200-step live run on 100-node + cycles + edits: peak=5.

**Next Falsification Target:** Add conflicting constraints generator + measure same property.

---

## Open Hypotheses (from Phase 4)
H1, H2, H3, H4, H5, H6 (EP-GRM specific), H7 (self-mod) — see `iterations/001/phase4-hypotheses.md`

Each will be updated with new evidence IDs as experiments complete.

---

## Negative Results Recorded
- Current stress rules make insufficient progress on complex graphs (success rate 0% in sweep). This is [NEGATIVE for rule quality] but [POSITIVE for focus boundedness] because focus stayed small even when not solving.

**This is valuable.**

## How Claims Are Updated
- New experiment run → new row in this registry.
- Every update must reference the exact CSV / commit / seed.
- Old claims are never deleted; they are versioned or marked superseded.

**End of Registry**
