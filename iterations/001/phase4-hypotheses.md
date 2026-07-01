# Iteration 001 — Phase 4: Hypothesis Formation

**Date:** 2026-07-01  
**Status:** Draft — Hypotheses extracted from Phase 3

**Protocol:** Every significant design decision is expressed as a falsifiable hypothesis. Includes statement, rationale, expected observations, measurable outcomes, and **explicit falsification criteria**.

Hypotheses are architecture-agnostic where possible, or tied to specific candidate approaches (EP-GRM, HB-AE, CT-DFV, CSPS primarily; RD-MC noted as higher-risk).

## Core Cross-Cutting Hypotheses

### H1: Bounded Executive State Sufficiency
**Statement:** It is possible to organize autonomous multi-step program synthesis using an explicitly bounded executive/working state (≤ K elements or frontier size, where K is small and independent of horizon length H) while achieving successful completion of synthesis tasks whose natural description length or required reasoning steps greatly exceed K.

**Rationale:** Current transformer agents require growing context because all relevant state lives in the activation/context. Cognitive architectures and control systems demonstrate that focused attention + external memory (here persistent graph) suffices for long tasks. Bounded frontier + good indexing/scheduling should suffice.

**Expected Observations:**
- Task success rate remains high as horizon increases while max active executive elements stays flat or grows very slowly.
- System can "remember" and correctly reference prior decisions without re-materializing full history in executive state.

**Measurable Outcomes:**
- Success rate on benchmark synthesis tasks of increasing horizon (measured in number of required atomic synthesis actions or dependency depth).
- Peak active executive state size (count of live focus nodes / actors / propagators / tokens) as function of horizon.
- Total bytes of "executive state" materialized at any time.

**Explicit Falsification Criteria:**
- For any fixed K, there exists a task family with horizon H > f(K) where success rate drops below a pre-defined threshold (e.g., 50% relative to unbounded reference) **and** the drop cannot be attributed to rule/constraint coverage.
- Peak executive size grows linearly or worse with H in all attempted schedulers.

**Classification:** Working Hypothesis (strongest claim of the program). Directly targets "fixed context windows" and "limited persistence of working cognition".

### H2: Data Movement Reduction via Persistent Local Rewrite/Propagation
**Statement:** Architectures where computation (rewrites, firings, propagations, actor steps) operates locally on or near persistent state representations, with only frontier/summary data loaded into fast executive structures, will exhibit substantially lower total data movement (bytes read/written between compute logic and backing store) per unit of useful synthesis progress than an equivalent-horizon transformer agent or conventional von Neumann program that materializes full relevant context.

**Rationale:** von Neumann + context windows force repeated transfer of large state for each reasoning step. Local mutation on versioned persistent structures + lazy loading of only relevant subgraphs should change the scaling.

**Expected Observations:**
- Measured movement (instrumented reads/writes or simulated cache-line equivalents) is dominated by "delta" size of rewrites rather than full state reloads.
- As task length grows, movement per step stays relatively flat or sub-linear vs baselines.

**Measurable Outcomes:**
- Cumulative bytes transferred (or cache misses / page loads in simulation) normalized by number of successful synthesis steps.
- Comparison against two baselines: (1) naive context-growing LLM agent simulation, (2) a conventional symbolic planner that loads full state each step.
- Memory bandwidth utilization and working set size.

**Explicit Falsification Criteria:**
- In controlled simulation/implementation, no architecture variant achieves > 3-5× reduction in movement per synthesis step (relative to baselines) on tasks longer than 20-30 steps, after tuning.
- Working set size grows proportionally to horizon despite locality mechanisms.

**Classification:** Working Hypothesis. Directly targets "excessive data movement" and "memory wall".

### H3: Intrinsic Verification Overhead is Acceptable
**Statement:** Adding intrinsic or co-equal verification (justification recording, re-derivation sampling, contract checking) to the core execution loop increases per-step cost by a bounded factor (< 4× in CPU time / memory in simulation) while enabling detection and recovery from errors that would otherwise require expensive external guardrails or full re-runs in probabilistic systems.

**Rationale:** Current agents pay hidden costs in retries, human oversight, or larger models for reliability. Explicit justifications may have upfront cost but enable cheap local checks and targeted rollback.

**Expected Observations:**
- Most verification is cheap local re-check or hash/signature validation.
- On injected faults, system detects and recovers without full restart.
- Overall wall-clock or simulated time for verified synthesis is competitive with unverified probabilistic agent on same task (due to fewer wasted paths).

**Measurable Outcomes:**
- Overhead ratio: time/memory with verification enabled vs disabled, on successful tasks.
- Fault injection recovery rate and cost.
- Fraction of steps where verification work dominates.

**Explicit Falsification Criteria:**
- Overhead consistently > 5× on representative tasks even after optimization of justification structures.
- Recovery from faults is more expensive than simply restarting a non-verified run.
- Verification itself introduces new classes of errors (e.g., justification bloat) that negate benefits.

**Classification:** Working Hypothesis. Targets "probabilistic instability".

### H4: Persistent Graph/Store as Primary Working Cognition
**Statement:** Representing both long-term knowledge and current working cognition in the **same** versioned persistent structure (graph, event log + slices, or membrane) allows an architecture to maintain continuity across sessions, power cycles, or context resets with negligible reload cost, while still supporting selective focus.

**Rationale:** Current systems lose "mind" on context clear or restart. Single-level persistent substrate + small focus pointers/indexes should provide instant continuity.

**Expected Observations:**
- After simulated "restart", system resumes with correct prior goals and partial results using only a small bootstrap state (pointers + top goals).
- Selective queries or loading of subgraphs succeed without full deserialization.

**Measurable Outcomes:**
- Time and data loaded to restore a mid-task state after "power cycle".
- Correctness of resumed synthesis vs fresh run.
- Size of bootstrap state vs full task state.

**Explicit Falsification Criteria:**
- Restoration cost scales with total work done (no savings vs re-computing).
- Selective loading is not possible; system must deserialize large portions to be correct.

**Classification:** Supported Inference from NVM + cognitive arch priors; Working Hypothesis for synthesis workload.

## Approach-Specific Hypotheses (Selected for Further Work)

We will prioritize EP-GRM and HB-AE for initial deeper exploration and simulation/implementation because they map most directly to implementable artifacts on current hardware within resource limits. CT-DFV and CSPS are secondary. RD-MC is exploratory/speculative only.

### H5 (EP-GRM): Efficient Incremental Matching on Versioned Graphs
**Statement:** Using incremental pattern matching (or indexed retrieval) over only changed portions of a versioned persistent graph, the cost of discovering applicable rewrites can be kept sub-linear in total graph size for typical synthesis workloads.

**Expected Measurable:** Rewrite discovery time vs graph size (nodes + edges). Compare naive scan vs incremental.

**Falsification:** Discovery time grows linearly or worse with graph size even on incremental implementation for realistic synthesis graphs (> few thousand nodes).

### H6 (HB-AE): Hierarchical Decomposition with Bounded Actors Scales
**Statement:** A hierarchical actor ensemble where each actor is limited to M state elements and L mailbox items can solve synthesis problems whose complexity requires > M state by dynamically spawning/activating sub-actors, without the top-level executive state ever exceeding its bound.

**Measurable:** Max top-level state size; total actors used; success on increasing complexity tasks.

**Falsification:** To solve harder tasks the system is forced to either (a) increase per-actor bounds or (b) inflate the director actor's state beyond bound.

### H7 (Cross): Composability and Self-Modification
**Statement:** The proposed architectures support first-class representation and verified modification of their own synthesis rules / actor definitions / constraints as part of normal operation, without requiring a separate meta-level or external code generation step that breaks the bounded-state or verification guarantees.

**Falsification:** Self-modification either violates bounds, cannot be verified within the model, or requires falling back to conventional code editing outside the architecture.

## Notes on Hypothesis Management
- Hypotheses will be tested in Phase 5/8 primarily via simulation first (cheaper, allows rapid falsification), then minimal implementation.
- Hypotheses can be refined, split, or retired as evidence arrives.
- Negative results will be recorded prominently.

**Classification of All Hypotheses:** Working Hypotheses unless otherwise noted. They are designed to be testable within the resource envelope (simulation on desktop + small targeted impls).

---

**Phase 4 Sign-off:** Hypotheses formalized.

**Next per workflow:** Phase 5 — Experimental Design.
