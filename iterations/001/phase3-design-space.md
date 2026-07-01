# Iteration 001 — Phase 3: Design Space Exploration

**Date:** 2026-07-01  
**Status:** Complete (multiple approaches generated)

**Protocol:** Multiple fundamentally different approaches generated **before** convergence. Novelty encouraged; internal consistency required. No premature dismissal.

All approaches are described with:
- Intended purpose
- Proposed operating principle
- Expected advantages
- Expected disadvantages
- Anticipated failure modes

Approaches deliberately span a spectrum from "plausible evolution of good priors" to "more radical departures".

## Approach A: Explicit Persistent Graph Rewrite Machine (EP-GRM)

**Intended Purpose:** Provide a computational substrate where long-horizon autonomous program synthesis is performed by repeated, verifiable, local rewrites on an explicit, versioned, persistent knowledge/program graph. Executive control is a small, bounded "focus frontier" rather than full context.

**Proposed Operating Principle:**
- Primary data structure: Directed graph of typed nodes (Facts, Goals, Plans, CodeFragments, Verifications, Dependencies) with versioned edges.
- Computation = matching small patterns (productions or rewrite rules) against the graph and applying atomic, auditable rewrites that produce new versions.
- Persistent by default (inspired by NVM single-level ideas; all committed state durable).
- Working executive state: A small set of "focus" nodes + a priority queue of candidate rewrites (applicable rules) + current top-level goals. Size intentionally bounded by scheduler policy (e.g., beam or relevance decay).
- Scheduling: Data-driven + goal-directed priority. A rewrite fires only when preconditions verified and priority selected.
- Verification: Every rewrite records justification (rule + matched premises). Independent verifier can re-check.
- Program synthesis: Synthesizing code is literally adding/rewriting CodeFragment nodes via higher-order rules.

**Expected Advantages:**
- Executive state bounded or logarithmic (only frontier active).
- Minimal data movement: Rewrites are local graph mutations; no full context reload.
- Native persistence and versioning (time-travel debugging, rollback on failed verification).
- Strong explainability and verifiability.
- Composability: Subgraphs are reusable.
- Graceful degradation: Partial graph always remains consistent.

**Expected Disadvantages:**
- Graph traversal / matching cost if naive (need efficient indexing or incremental maintenance).
- Rule authoring or learning the rewrite set is non-trivial.
- May be slower than optimized matrix ops on regular numeric work (acceptable trade-off).

**Anticipated Failure Modes:**
- Rule set insufficient coverage → stagnation (impasse explosion or empty frontier).
- Matching becomes quadratic despite efforts.
- Versioning overhead grows unbounded without aggressive compaction/garbage collection of history.
- Difficulty expressing continuous or perceptual data efficiently.

**Classification of Description:** Working Hypothesis + Engineering Assumptions about implementability on consumer hardware.

## Approach B: Capability Token Dataflow with Explicit Verification (CT-DFV)

**Intended Purpose:** Replace instruction streams or activations with immutable data + verified capability tokens that enable operations. Computation and synthesis proceed by flowing verified "permission to act" alongside data. Target: eliminate shared mutable state and unnecessary movement.

**Proposed Operating Principle:**
- All values are immutable. State evolution happens by producing new values + tokens.
- A "capability token" is a signed/verified claim (e.g., "this value satisfies precondition P for operator O, version V").
- Execution model: Operators are pure functions guarded by token matching. When all required input tokens + data arrive at a "firing site", the operator executes (locally or near data) and emits result value + new verification tokens.
- Persistent substrate: Append-only history of values and tokens (log + merkle-like for verification).
- Executive "state": Small set of live token queues and active firing sites (bounded by resource policy).
- For synthesis: Program fragments are themselves values that can be flowed and combined under capability constraints.
- Failure handling: Invalid token → reject and propagate error token.

**Expected Advantages:**
- Strong determinism and reproducibility (immutable + tokens).
- Natural parallelism (data + capability availability).
- Reduced movement: Firing can happen "near" the data values (abstract PIM-like).
- Verification intrinsic (tokens carry proof obligations).
- No traditional von Neumann "load everything to compute".
- Bounded live state if old tokens/values are garbage-collected after consumption + persistence to log.

**Expected Disadvantages:**
- Token and history management complexity.
- Pure functional style may make I/O and external interaction cumbersome (requires capability modeling of effects).
- Matching overhead for tokens.

**Anticipated Failure Modes:**
- Token bloat or loss leading to deadlock/starvation.
- Inability to express efficient mutable algorithms without massive copying (mitigate with structure sharing).
- Verification token generation itself becomes bottleneck.

**Classification:** Working Hypothesis (dataflow + capabilities can be made practical). Speculation on boundedness for synthesis tasks.

## Approach C: Hierarchical Bounded-State Actor Ensemble (HB-AE)

**Intended Purpose:** Model cognition as a dynamic ensemble of small, independent actors. Each actor maintains only a tiny explicit state machine + local persistent store. Global synthesis emerges from structured message passing and contract-based verification between actors. Hierarchical decomposition for complexity.

**Proposed Operating Principle:**
- Actor = small finite-state machine + very small local working memory (dozens of elements) + reference to a private persistent object store slice.
- Top-level "Executive Director" actor decomposes goals into sub-actors (spawning or activating).
- Communication via typed, capability-protected asynchronous messages.
- Each message carries verification metadata (e.g., "this subgoal derived from parent via rule R").
- Scheduling: Cooperative or priority-based event loop per "node"; global scheduler has bounded view (only active actor descriptors).
- Persistence: Actor checkpoints + event sourcing to persistent log.
- Synthesis: Specialized "Coder" actors produce code; "Verifier" actors check; "Critic" actors propose alternatives.
- Boundedness: Hard limits on mailbox size, state size per actor, and max concurrent active actors. Overflow → delegation or suspension.

**Expected Advantages:**
- Extremely small per-actor executive state (easy to fit in cache / small memory).
- Excellent isolation and failure containment.
- Natural distribution and modularity.
- Graceful scaling by adding actors rather than growing state.
- Verification contracts can be checked locally or by dedicated verifiers.
- Persistence per slice reduces global movement.

**Expected Disadvantages:**
- Message-passing overhead and latency for tight coordination.
- Designing good decomposition heuristics or protocols.
- Potential for actor proliferation or deadlocks without careful design.
- Global visibility (for high-level planning) must be explicitly constructed.

**Anticipated Failure Modes:**
- Poor decomposition leads to too many tiny actors or communication explosion.
- Coordination protocols fail under uncertainty (incomplete contracts).
- Persistent slices become inconsistent without distributed transactions.

**Classification:** Supported Inference (actor models proven for concurrency). Working Hypothesis (can be specialized for bounded cognition + synthesis).

## Approach D: Constraint Satisfaction & Propagation Substrate (CSPS)

**Intended Purpose:** Represent both knowledge and goals as a network of constraints and facts over a persistent fact base. "Reasoning" and synthesis become propagation, relaxation, and search within the constraint network. Executive state is the current propagation frontier (work queue) + active constraints.

**Proposed Operating Principle:**
- Facts and variables live in a persistent, versioned store.
- Constraints are first-class (arithmetic, logical, type, dependency, synthesis rules).
- Propagation engine: When a fact changes, enqueue affected constraints. Constraints "fire" by inferring new facts or tightening domains (like AC-3 or more modern propagators).
- For program synthesis: Constraints can include "generate candidate fragments" + "must satisfy spec" + "cost bounds".
- Executive control: Priority queue of propagations (informed by goal relevance or contradiction risk). Bounded active propagators via resource budget.
- Verification: Every inferred fact carries a justification DAG. Full re-derivation or sampling for audit.
- Failure: Contradiction detected → record nogood, backtrack or relax (explicitly).
- No "forward pass" or token stream; computation converges or reaches quiescence.

**Expected Advantages:**
- Naturally handles partial information and inconsistency (core to real autonomy).
- Justification structures give excellent explainability and minimal change on revision.
- State is the current assignment + active constraints — can be kept small by focusing propagation.
- Persistence native.
- Good match for planning + verification (SAT/CP solvers already do parts of this).

**Expected Disadvantages:**
- Propagation can be expensive (worst-case exponential) without good heuristics and bounding.
- Less "step by step imperative" intuition; harder to map some algorithms.
- Learning new constraints dynamically is non-trivial.

**Anticipated Failure Modes:**
- Constraint network explodes (too many constraints activated).
- Weak heuristics lead to thrashing instead of progress.
- Difficulty integrating continuous perception or very high-dimensional data.

**Classification:** Working Hypothesis (constraint propagation as primary "compute" for synthesis). Supported Inference (solvers already succeed on verification/planning subproblems).

## Approach E: Radical — Reaction-Diffusion / Membrane-Inspired Persistent Chemistry (RD-MC)

**Intended Purpose:** Explore a non-symbolic, non-graph, non-actor model: computation as concentrations and reactions in a persistent "membrane" substrate. Inspired by membrane computing / P-systems and reaction-diffusion systems, but made verifiable and directed toward synthesis tasks.

**Proposed Operating Principle:**
- "Memory" = a set of persistent compartments (membranes) containing multisets of symbols (objects: facts, code atoms, goals, resources).
- "Compute" = reaction rules that consume and produce objects within or across membranes (with possible movement rules).
- Executive "state": Summary statistics or small set of high-priority membranes + a reaction scheduler (e.g., stochastic or priority-based selection of which rules to attempt).
- Versioning/Persistence: Every membrane state is versioned; reactions produce new versions with lineage.
- Verification: Reactions are guarded by "catalysts" or explicit validators that must also be present.
- Synthesis: Code fragments and programs are symbol multisets that can be "assembled" by reactions.
- Boundedness: Membrane count, object count per membrane, and reaction rate all under explicit budgets. Excess → diffusion out or decay.

**Expected Advantages:**
- Fundamentally different scaling: parallelism and robustness emerge from concentration and stochasticity rather than explicit enumeration.
- Natural handling of resource, uncertainty, and parallelism.
- Minimal "addressing" — locality via membranes.
- Potentially very hardware-efficient if mapped to chemical or analog-like substrates later.
- Graceful with noisy or partial objects.

**Expected Disadvantages:**
- Stochastic nature may reduce reproducibility (mitigate with seeded deterministic schedulers or counts instead of probs).
- Mapping high-level synthesis goals to chemical-like reactions is alien and difficult to design.
- Verification harder (probabilistic guarantees?).
- Debugging and introspection less direct than symbolic graphs.

**Anticipated Failure Modes:**
- Inability to encode precise algorithmic synthesis in reaction rules.
- State (object counts) grows uncontrollably or oscillates.
- Scheduler cannot focus computation usefully on long-horizon goals.

**Classification:** Speculation (most radical departure). High risk/high reward. May be useful as inspiration even if primary architecture is more conventional.

## Cross-Approach Comparison Axes (for later evaluation)

- Degree of explicitness vs implicitness of state
- Boundedness mechanism
- Verification integration (intrinsic vs layered)
- Data movement profile
- Persistence model
- Natural support for self-modification / synthesis
- Determinism / reproducibility
- Expected implementation complexity on current hardware
- Failure containment

## Observations from Exploration
- Common thread across promising approaches: explicit (or summary) state that is much smaller than full history or context, plus a mechanism for progress (rewrite, fire, propagate, react).
- Persistence is elevated from "storage" to primary representation.
- Verification moves from post-hoc to intrinsic or co-equal.
- No approach relies on large fixed context windows or massive undifferentiated activation.

**No approach has been selected yet.** Selection and refinement will occur via hypotheses in Phase 4.

---

**Phase 3 Complete.** Full details above and in this file.

**Next:** Phase 4 — Hypothesis Formation (take key design decisions from above and make them falsifiable).
