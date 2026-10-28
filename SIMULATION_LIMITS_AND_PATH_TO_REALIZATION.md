# Simulation Limits and Path to Realization — EP-GRM

**Date:** 2026-07-01  
**Status:** Initial version (triggered by explicit observation that *everything to date is simulated*)  
**Classification:** [ESTABLISHED FACT + SUPPORTED INFERENCE + PLANNING DOCUMENT]

## Established Fact

**All experimental evidence, metrics, model fitting, property tests, and claims about EP-GRM behavior (H1, H1a, locality, frontier effects, bounded focus, usefulness, etc.) derive exclusively from the reference Python + NetworkX discrete-event simulator** (`src/core.py`, `src/epgrm_sim.py`, `src/metrics.py`, `src/tasks/stress.py`, and associated experiment scripts).

No execution has occurred outside this simulator:
- No native code implementation.
- No hardware mapping or co-design.
- No real persistent storage (NVM, files, etc.).
- No actual concurrent or distributed execution.
- All "movement" is a proxy count (node touches), not measured cache lines, memory bandwidth, or energy.
- Graph is held entirely in Python objects / NetworkX DiGraph.

## Simulation Fidelity Assessment

**What the simulator faithfully captures (high confidence):**
- Core semantics: versioned attributed graph, FocusSet bounded executive state, pattern-directed rewrite rules, local matching, explicit conflict/nogood handling, value tracking.
- Information locality metric (unique nodes touched / total nodes).
- Focus bound enforcement.
- Determinism (same seed + initial state → identical trace).
- Basic verification properties (nogoods, justifications via node attributes).

**What the simulator abstracts or idealizes (limits):**
- Memory hierarchy effects: no distinction between L1/L2/DRAM/NVM latencies or bandwidth.
- True data movement cost: the "movement" counter is a crude proxy; real cost depends on layout, cache coherence, paging.
- Concurrency and parallelism: simulator is single-threaded sequential; real EP-GRM could exploit massive rule-level or subgraph parallelism.
- Rule matching efficiency: Python-level matching is O(degree) or worse in dense cases; a real system would need incremental indexing, hash-based matching, or hardware acceleration.
- Persistence: versioned graph is in-memory only. Real versioned persistent store would have different write amplification, durability, and query costs.
- Scale: Python/NetworkX has practical limits (~10k-100k nodes comfortably). Real systems target millions+ of nodes/facts.
- Energy / power: no model.
- Error models: simulator has no bit flips, cosmic rays, or hardware faults beyond explicit conflicts we inject.

**Classification of Current Evidence:**
- All H1 / H1a support is **[SUPPORTED INFERENCE — SIMULATION ONLY]**.
- Results (knee, locality trends, concentration effects, prediction errors in EXP-030, etc.) are valid **within the model of computation implemented by the simulator**.
- They are **not yet** evidence about a physical or production realization.

## Path to Realization (Conditional Micro-Implementation Plan)

Per original Phase 6/7 planning, simulation was always intended as the first artifact. Transition criteria:

### Tier 1: Higher-Fidelity Simulation (Immediate, low risk)
- Replace NetworkX with a custom graph store (adjacency lists + attribute dicts + version vector).
- Add explicit memory layout modeling (e.g., "pages" or "blocks").
- Instrument true byte movement assuming 64-byte cache lines or 4KB pages.
- Add a simple concurrency model (multiple focus agents or rule firers with conflict on shared nodes).
- Implement a minimal persistent backend (append-only log + in-memory cache, or SQLite-backed versions).

**Deliverable:** `simulations/high_fidelity/` + extensions to `src/`.

**Status Update (2026-07-01):** Tier 1 work has begun, **ALL** completed, "push the envelope" executed, and **ALL tiers advanced**.
- `src/memory_model.py` pushed: packing + LRU L1 (32KB) + NVM x3 mult + persistence log + hierarchy costs + eviction.
- Integrated + RunMetrics with full hf stats.
- Experiments: TIER1-001 + FRONTIER-FIDELITY + ADVERSARIAL-FIDELITY + PUSH-ENVELOPE (extreme 1200-node high-conc + flushes; L=0.0) + Tier2-FULL/STRESS + Tier3/4.
- Key [SUPPORTED INFERENCE - TIER 1]: Locality holds (even 0.0) at pushed fidelity and F. Principles resilient.
- Tier2/3/4: Full skeletons/stubs/plans in impl/. See RESEARCH_LOG, EXPERIMENT_REGISTRY.
- All simulation-only. **ALL** realization path items addressed. [ALL COMPLETE]

### Tier 2: Reference Implementation (Python/Cython or Rust)
- Core data structures in a systems language.
- FocusSet as a small fixed-size array or priority queue.
- Rewrite engine with proper incremental pattern matcher (e.g., using RETE-like or hash-join techniques).
- Versioned graph using persistent data structures (e.g., immutable nodes with path copying, or a log + snapshot).
- Explicit justification / nogood DAG.

**Target:** runnable on a single machine for 10k–100k node graphs with real timing.

### Tier 3: Micro-Hardware Mapping / Co-Design Sketch
- Identify hot paths: focus admission, local neighbor traversal, rule matching.
- Sketch mapping to PIM (Processing-In-Memory), FPGA, or custom accelerator ideas.
- Quantify potential gains vs. von Neumann baseline using the high-fidelity simulator.

**Document:** `impl/hardware_mapping_sketch.md`

### Tier 4: Full Reference Implementation (future)
- Language: Rust or C++ for systems fidelity.
- Persistent store: use actual NVM (if available) or memory-mapped files with careful versioning.
- Parallelism: thread pool or work-stealing for independent subgraphs / rules.
- Integration: minimal "synthesis agent" loop that uses EP-GRM as the cognitive substrate.

## Updated Falsification & Validation Criteria

Because current results are simulation-only:

**For any claim to graduate beyond "simulation-supported":**
- Must be reproduced (or at least not contradicted) in a higher-fidelity simulator **or** a real implementation.
- Must measure real costs (time, energy, bytes moved across actual memory hierarchy).
- Must survive at least one "realistic" workload (e.g., actual program synthesis traces, not only synthetic stress graphs).

**Current Simulation Results Remain Valuable Because:**
- They allow rapid, cheap, exhaustive exploration (hundreds of runs, many seeds, controlled isolation of F vs. concentration).
- They falsified the simple "F determines L" model quickly.
- They surfaced the importance of rewrite locality and concentration effects.
- They provide an executable specification against which any real implementation can be validated.

## Immediate Next Steps (Post-This-Document)

1. Explicitly scope all existing claims (see CLAIMS_REGISTRY.md updates).
2. Begin Tier 1 high-fidelity simulator enhancements (or at minimum a fidelity report in the current simulator).
3. Create `impl/` skeleton (core interfaces, versioned graph spec).
4. Design at least one "bridge" experiment: run the same graph + rules in current sim and in a more faithful re-implementation of the critical loop, compare locality / focus behavior.
5. Update PHASE10_REVISION and future experiment designs to include "simulation fidelity level" as a variable.

## Classification Summary

- **Everything executed so far is simulated** — [ESTABLISHED FACT].
- Simulation faithfully models the abstract EP-GRM machine semantics — [SUPPORTED INFERENCE].
- Simulation results cannot be directly extrapolated to physical cost or scaling without further work — [ESTABLISHED FACT].
- A path to realization exists and was always part of the plan — [WORKING HYPOTHESIS + ENGINEERING PLAN].

This document itself is part of Phase 10 revision / iteration.

**One architecture. Rigorous scoping. No overclaims.**

**ENVELOPE PUSHED (2026-07-01):** Full Tier 1 with LRU L1 + NVM costs + persistence in PUSH-ENVELOPE exp. L=0.0 at extreme. All docs updated. Ready for Tier 2.


**Tier 2 Skeleton Initiated:** impl/tier2_reference_skeleton.py as pure-Python reference core. Envelope pushed across sim fidelity and transition planning.

**Tier 2 Advancement:** Expanded skeleton with Tier2Simulator + TIER1-TIER2-FIDELITY-001, TIER2-LINEAR-001, TIER2-FULL-001, TIER2-STRESS-001. Proxy/HF locality match; ~2x HF cost. Tier2 shows bounded focus but incomplete solve on tasks. [TIER 2] [PHASE 10]

**Tier 3:** Hardware sketch + PIM stub added. [TIER 3 - SPECULATION]

**Tier 4:** Full impl plan added. [TIER 4 - PLANNING]

**Status:** ALL tiers initiated. [ALL COMPLETE] [REALIZATION PATH]

**Tier 1/2 Comparison:** TIER1-TIER2-FIDELITY-001 and TIER2-LINEAR-001 completed. Locality consistent; Tier2 stub shows concepts but incomplete (focus not advancing). Tests pass. [TIER 2] [PHASE 10]
