# Iteration 001 — Phase 5: Experimental Design

**Date:** 2026-07-01  
**Status:** Draft

**Protocol:** Experiments designed to validate **or falsify** every hypothesis from Phase 4. Preference for simulation first (fast iteration, controlled measurement, runs on target hardware). Minimal real implementation only after simulation provides supporting evidence or clear refinement.

## Overall Experimental Strategy

1. **Simulation Tier (Primary for Iteration 001)**
   - Python + networkx (graphs) + pure Python objects.
   - Abstract "cost model": count nodes/edges loaded, "bytes" approximated by serialized size or node count × avg size.
   - Deterministic by default; optional seeded stochastic elements.
   - Instrumented at every step: executive state size, bytes "moved"/loaded, verification work, progress metrics.
   - Runs entirely in < 6 GB (Python overhead manageable).

2. **Targeted Micro-Implementation Tier (Conditional)**
   - If simulation supports key hypotheses, implement core loop of one or two architectures (EP-GRM first) in efficient Python or small native module.
   - Same instrumentation.

3. **Baselines (for all comparative experiments)**
   - **B1: Naive Context Agent (NCA)** — Simulated agent with growing "context" dict. Each step, relevant history + current goal + library is "loaded". Oracle or simple rule applier makes progress. Models context-window style.
   - **B2: Full-State Reload Planner (FSR)** — Symbolic planner that explicitly re-materializes all known relevant facts/goals every decision step (classic von Neumann style for cognition).
   - **B3 (optional later):** Small real LLM agent scaffold using available tools (langgraph) as real-world reference. **Not primary**; expensive and noisy.

4. **Task Families (Synthesized, controllable horizon)**
   All tasks are program synthesis or planning problems with explicit, measurable "horizon" (number of atomic synthesis actions or dependency depth).
   - **T1: Linear Chain Assembly** — Synthesize a pipeline of N functions from library primitives. Each step adds one link. Horizon ≈ N. Dependencies linear.
   - **T2: Tree/Branching Construction** — Build an expression tree or nested structure of depth/width D. Horizon = number of nodes.
   - **T3: Planning with Backtracking (e.g., constrained synthesis)** — Tasks requiring trial, verification failure, and revision (inject "bugs" that must be detected).
   - **T4: Multi-Goal with Shared Substructure** — Several goals sharing sub-components (tests reuse, compaction, persistence value).
   - Horizon control: Parameterized by N or D. Target: 10 → 50 → 200+ steps where feasible.

   All tasks have:
   - Formal spec (what the synthesized artifact must satisfy).
   - Library of primitives (functions, combinators).
   - Verifiable acceptance test (executable checker).

5. **Measurement & Instrumentation (common)**
   - Executive state size over time (live elements, active frontier).
   - Cumulative "data movement" proxy: sum of sizes of nodes/structures brought into fast/executive structures per step.
   - Verification cost (justifications generated/checked, re-derivations).
   - Progress: steps to completion, success/failure, recovery from injected faults.
   - Resource: peak memory (Python process), wall time per step (simulated "cost").
   - Reproducibility: same seed + initial state → identical trace.

6. **Statistical / Repeatability**
   - Multiple runs per (task, architecture, param).
   - Report mean + variance where non-deterministic.
   - All random seeds logged.

## Experiment Designs Mapped to Hypotheses

### Exp1: Bounded Executive Sufficiency (H1, H6)
**Purpose:** Test whether bounded frontier suffices.

**Design:**
- Run EP-GRM and HB-AE (with hard K bounds: e.g. K=20, 50, 100 frontier elements) on T1–T4 with increasing horizon N=10,25,50,100,200.
- Measure success rate vs horizon.
- Compare to NCA and FSR (unbounded or full-state).
- For HB-AE: enforce per-actor and director bounds.

**Metrics:**
- Success @ horizon H for given K.
- Peak measured executive size vs H.
- If success holds while size flat → support.

**Falsification Path:** If success drops sharply for H >> K and gap cannot be closed by better scheduling/indexing (within reasonable tuning budget), H1 weakened.

**Cost:** Low (simulation). 5 horizons × 4 tasks × 3 bounds × repeats.

### Exp2: Data Movement Scaling (H2)
**Purpose:** Quantify movement reduction.

**Design:**
- Instrument all architectures + baselines identically.
- On same task instances, compute:
  - Movement per synthesis step (bytes proxy).
  - Total movement to completion.
  - Movement / progress ratio.
- Plot vs horizon.

**Expected (to support H2):** EP-GRM / HB-AE / CSPS show movement dominated by delta size; baselines grow with loaded context.

**Falsification:** Movement curves statistically indistinguishable or worse after normalization.

**Additional:** Break down movement into "frontier load", "rewrite application", "verification".

**Cost:** Low.

### Exp3: Verification Overhead & Recovery (H3)
**Purpose:** Measure cost/benefit of intrinsic verification.

**Design:**
- For EP-GRM and HB-AE: two variants — full justification recording + sampling verifier vs "verification disabled" (assume correct).
- On clean tasks: overhead ratio.
- On tasks with injected faults (bad rewrite proposed at random points): detection rate, recovery cost (rollback via version + re-plan), vs baseline that has no native detection and must restart or use external checker.

**Metrics:**
- Overhead = (time_with_verif / time_without) on success.
- Fault detection latency and recovery steps.
- End-to-end time including faults.

**Falsification:** Overhead >5× consistently + recovery worse than restart.

**Cost:** Medium (more variants).

### Exp4: Persistence & Continuity (H4)
**Purpose:** Test restart / continuity cost.

**Design:**
- Run architecture to mid-task checkpoint.
- Simulate full "process death": save only minimal bootstrap (top goals, focus pointers, persistent root).
- Restart simulator, load from persistent store using bootstrap.
- Measure:
  - Data loaded to resume.
  - Time to first useful action post-restart.
  - Correctness: continues to same solution path as uninterrupted run.
- Compare to NCA (which would need to reload full prior context or lose state).

**Falsification:** Resume cost ≈ re-running from start or scales with work done.

**Cost:** Low. Powerful demonstration if successful.

### Exp5: Incremental Matching / Discovery Cost (H5)
**Purpose:** EP-GRM specific.

**Design:**
- Implement two EP-GRM variants in sim:
  - Naive: full scan of graph for pattern matches each cycle.
  - Incremental: index or delta-based (e.g., networkx + custom reverse index on types/attributes, only re-match changed neighborhoods).
- Run on growing graphs (T2, T4) while measuring discovery time (or simulated work) as |V|+|E| grows.

**Metrics:** Time or work vs graph size; ratio naive/incremental.

**Falsification:** Incremental still linear or super-linear in practice for synthesis graphs.

**Cost:** Medium (indexing impl).

### Exp6: Hierarchical Actor Scaling (H6 detailed)
**Design:**
- HB-AE on T3/T4 (tasks needing decomposition).
- Track: director state size (must stay ≤ bound), total sub-actors spawned, communication volume.
- Vary task complexity.
- Measure whether director stays bounded while total work scales.

**Falsification:** Director state must grow with complexity or sub-actor communication explodes.

### Exp7: Self-Modification Viability (H7) — Lightweight
**Design:**
- In EP-GRM: include a small set of "meta-rewrite" rules that can add or modify ordinary rewrite rules (under strict verification that new rule preserves invariants or passes test suite).
- Demonstrate at least one successful self-extension during a task (e.g., learn a useful composite operator from repeated pattern).
- Verify the new rule is used subsequently and system remains sound (acceptance tests pass).
- Measure any growth in executive state or verification cost.

**Falsification:** Cannot add verified useful rule without external intervention or bound violation.

**Note:** This is a "existence" experiment; full learning is future work.

## Simulation Architecture (High-Level Plan)
- Core: `ArchitectureSimulator` base with step(), get_exec_state_size(), get_movement(), etc.
- EP-GRM sim: NetworkX MultiDiGraph for versioned nodes (each node has versions list or immutable copies on write). Small `FocusSet`, `RewriteRule` objects, `Scheduler`.
- HB-AE sim: Dict of Actor objects. Actor has tiny local dict/graph + persistent log reference (simulated by dict of committed slices).
- Instrumentation hooks everywhere.
- Task generator: pure functions that emit specs + initial graph/actors + oracle acceptance.
- CLI or pytest for running suites.

## Formal / Analytical Elements
- **Complexity sketches** (pre-impl):
  - EP-GRM rewrite discovery with good index: O(degree of changed nodes) per step expected.
  - Movement: O(size of rewrite delta) per step.
  - HB-AE: per-actor O(1) expected if bounds enforced.
- **Property-based testing / small model checking:** Use hypothesis or simple exhaustive check on tiny instances of rewrite soundness.
- **Reproducibility:** Full trace logging (list of applied rewrites + states) for deterministic replay.

## Success / Stopping Criteria for Experiments
- Run until clear support, clear falsification, or resource/time budget exhausted for the iteration.
- Any hypothesis that survives initial experiments advances; falsified ones are revised or discarded (Phase 10).
- Document all parameter choices and tuning performed.

## Resource Expectations
- All simulation runs targeted to complete in minutes to low hours on i7 + 6GB GPU (GPU unused for pure sim).
- Peak Python RAM < 4 GB for graphs up to 10k nodes.
- If successful, move to Phase 6 planning for a reference implementation of the simulator itself as first artifact.

## Risks & Mitigations
- Task design too easy/hard → start with T1 linear, scale parameters iteratively.
- Instrumentation inaccurate → cross-validate movement counts with multiple proxies.
- Overfitting to one architecture → always run multiple + baselines.

---

**Phase 5 Sign-off (when experiments executed):** Experiments will be documented with results in future Phase 9/ logs.

**Immediate Next:** Phase 6 — Implementation Planning (for the simulator and core of prioritized architectures).
