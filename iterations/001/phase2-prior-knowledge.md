# Iteration 001 — Phase 2: Prior Knowledge Review

**Date:** 2026-07-01  
**Status:** In Progress (Draft)

**Protocol:** Literature and prior art treated **strictly as reference material**, not design constraints. Existing approaches inform what has been tried and where they fell short, but we are free to reject any or all of their fundamental assumptions.

## Summary of Categories Reviewed

### 1. Processing-in-Memory (PIM), Near-Memory Compute, Compute-in-Memory (CIM)

**Key References:** Surveys on DRAM PIM [web:0][web:1][web:5], Near-memory in 2026 context [web:3], IBM NorthPole example [web:6].

**Core Idea:** Move computation (ALU/logic or specialized units) physically close to or inside memory arrays (DRAM, HBM, SRAM) to eliminate or reduce round-trips over the memory bus.

**Strengths:**
- Dramatic reduction in energy and latency for data-movement-heavy kernels (vector ops, reductions, ML inference, DB scans).
- IBM NorthPole: extreme near-memory (local SRAM per core) demonstrated large efficiency gains (47x speed, 73x energy vs GPUs on specific LLM inference).

**Weaknesses / Limitations:**
- Coherence, consistency, and synchronization across PIM units and host remain difficult.
- Programming model transparency and compatibility challenges; requires new compilers, runtimes, or explicit offload.
- Not general-purpose for arbitrary control flow or complex cognition. Best for regular, data-parallel bulk ops.
- Simulation accuracy and hardware realization lag (many academic PIMs).
- Data placement and orchestration overhead can offset gains if not perfectly matched to workload.
- Still fundamentally "accelerator-like" additions rather than a replacement architecture for long-horizon reasoning.

**Unresolved Problems:**
- Full-system integration with OS, virtual memory, and general software.
- Handling irregular, pointer-chasing, or decision-heavy workloads (exactly the kind needed for autonomous synthesis).

**Challenged Assumptions:**
- The assumption that compute and memory must be strictly separated is being relaxed, but the "compute near memory" still assumes conventional instruction or data-parallel execution models. We may challenge the need for any von Neumann-style instruction dispatch at all.

**Classification:** Established Fact (memory movement dominates many workloads). Supported Inference (PIM helps specific cases). Working Hypothesis (PIM alone insufficient for general intelligent control).

### 2. Cognitive Architectures (SOAR, ACT-R, Sigma, related)

**Key References:** Laird's comparison of ACT-R and Soar [web:17][web:19], Soar descriptions [web:22][web:16].

**Core Idea:** Separate **working memory** (explicit, current situation as graph or buffered chunks), **procedural memory** (productions/rules/operators), **declarative/long-term memory**. Cycle of elaboration → decision → application. Impasses/substates for deliberation and meta-reasoning. Chunking for learning.

**Strengths:**
- **Explicit, inspectable, queryable state.** Working memory elements are first-class and linkable.
- Strong support for goal-directed behavior, subgoaling, and handling incomplete knowledge.
- Explainable decisions (traceable operator selection).
- Bounded or controllable breadth of active WM in practice (ACT-R uses limited buffers; Soar links to state).
- Chunking provides a path from slow deliberate reasoning to fast compiled knowledge.
- Substate mechanism provides natural structure for handling complexity and failure.

**Weaknesses / Limitations:**
- Historically knowledge-engineered; scaling to open-ended perception or vast knowledge difficult without hybrid learning.
- Limited native support for massive parallel statistical pattern matching (the strength of modern nets).
- Working memory can grow; control of complexity relies on careful design or learning.
- Integration with continuous/low-level perceptual data or probabilistic uncertainty historically weak.
- Performance on raw throughput for simple ops inferior to specialized hardware.

**Unresolved Problems:**
- How to maintain explicit state benefits while incorporating learned, high-dimensional representations at scale.
- Automatic management of WM "focus" or relevance without hand-crafted rules or heuristics that explode.
- Long-horizon persistence and versioning of WM across sessions or failures.

**Challenged Assumptions:**
- "Working memory" does not have to be a flat buffer or small fixed set. It can be a versioned, persistent graph with explicit links.
- Deliberation need not be only impasse-driven; richer verification and scheduling models are possible.
- The production cycle is one possible execution model; others may compose better with verification or hardware.

**Classification:** Established Fact (these architectures demonstrate value of explicit WM + operators). Supported Inference (explicit state aids explainability and control). Engineering Assumption (they show bounded-control is viable in principle).

### 3. Persistent Memory / Non-Volatile Main Memory (NVM, PM) & Single-Level Store Concepts

**Key References:** Surveys on NVM [web:13][web:12], persistent memory properties [web:9][web:10].

**Core Idea:** Byte-addressable storage that retains state across power loss (PCM, ReRAM, etc.). Enables load/store access to durable data; blurs or eliminates traditional memory/storage boundary (single-level store ideas).

**Strengths:**
- Instant persistence; no explicit serialization/flush for "save state".
- Potential for much larger effective "RAM" with persistence.
- Fast recovery; new programming models for durable data structures.
- Reduced data copying for checkpointing.

**Weaknesses / Limitations:**
- Asymmetric performance (writes often slower, limited endurance).
- Requires new consistency primitives (persistence fences, transactions) — software complexity high.
- Hybrid DRAM+NVM management needed in practice.
- OS/filesystem/allocator overhauls required; legacy code doesn't benefit automatically.
- Not a computational model by itself — still sits under conventional execution.

**Unresolved Problems:**
- Efficient, safe, concurrent access to persistent structures at scale.
- Wear-leveling + reliability for long-running autonomous systems.

**Challenged Assumptions:**
- Distinction between "working memory" (volatile, fast) and "persistent store" (slow, durable) is technological, not fundamental. We can explore architectures where persistent structures are the primary substrate for both.

**Classification:** Established Fact (NVM tech exists and offers persistence via load/store). Supported Inference (single-level store simplifies state). Speculation (can become the foundation for working cognition itself).

### 4. Dataflow and Graph Reduction Architectures

**Key References:** MIT Tagged-Token Dataflow [web:29][web:30], graph reduction discussions [web:23][web:28][web:25].

**Core Ideas:**
- **Dataflow:** Operations fire when all input tokens (data + tags) arrive. No program counter; implicit parallelism.
- **Graph Reduction:** Programs/data as graphs; computation = repeated rewriting of reducible expressions (redexes) until normal form. Sharing avoids duplication.

**Strengths:**
- Excellent natural parallelism and avoidance of unnecessary work (sharing/laziness).
- No sequential instruction stream in the classic sense.
- Clean semantics for functional/declarative computation.
- Potential for very fine-grained concurrency.

**Weaknesses / Limitations:**
- High overhead from token matching or pointer/graph manipulation (ironically memory and indirection heavy).
- Difficulty with side effects, I/O, mutable state, and irregular control.
- Load balancing and resource management in large/distributed implementations hard.
- Historical research machines (80s/90s) largely did not displace von Neumann for general use; many workloads favor optimized sequential + cache.
- Implementation complexity.

**Unresolved Problems:**
- Efficient realization on modern memory hierarchies and interconnects.
- Combining fine-grained data-driven execution with coarse-grained verified control and persistence.

**Challenged Assumptions:**
- "Control" must come from explicit sequencing or massive activation vectors. Token/graph-driven may be viable.
- All state must be "in memory" as mutable locations or activations. Immutable graph fragments with rewrite can suffice.

**Classification:** Established Fact (alternative models exist with different scaling properties). Supported Inference (they excel in certain parallel declarative workloads). Working Hypothesis (hybridized with explicit verification they may suit autonomous synthesis better).

### 5. Contemporary LLM/Transformer Agent Scaffolds (Reference for Contrast Only)

Not a computational architecture in the hardware/OS sense, but the dominant substrate for current "autonomous" synthesis attempts (ReAct, tool-use agents, etc.).

**Known Limitations (widely observed):**
- Context window fundamentally limits horizon and state fidelity.
- All "memory" is either in-context (quadratic cost) or external RAG/tools (lossy, slow, no native integration).
- Probabilistic generation leads to compounding errors without external guardrails.
- No first-class representation of "current goals + working state" that is small, versioned, and verifiable.
- Resource use grows with model size + context, not problem structure.

These are engineering reference points that inherit von Neumann + attention scaling issues.

## Cross-Cutting Observations

**Common Unresolved / Weak Areas Across Priors:**
- No dominant architecture provides **small bounded executive state + first-class verifiable long-horizon persistence + native program synthesis**.
- Most alternatives either:
  - Solve data movement for regular kernels (PIM) but leave control flow conventional.
  - Provide explicit state (cognitive arch) but struggle with scale, learning, and low-level efficiency.
  - Offer persistence (NVM) but no new execution model.
  - Enable parallelism (dataflow/reduction) but suffer practicality and side-effect issues.
- Verification is almost always layered on top rather than intrinsic.
- Scheduling/resource management rarely designed around "cognition" as primary workload.

**Assumptions We Explicitly Do Not Adopt as Constraints:**
- Compute must be imperative instructions or large tensor ops.
- State must be either tiny buffers or huge context activations.
- Persistence requires separate I/O or filesystem layer.
- "Intelligence" requires either massive parallelism of simple units or hand-crafted symbolic rules.
- Architecture must be general-purpose CPU-like or accelerator-like.

**What We Carry Forward (as useful mechanisms to possibly reuse or improve):**
- Explicit linked state elements (from cognitive arch).
- Operator / production / rewrite driven progress.
- Subgoaling / impasse for handling complexity.
- Data-driven firing or reduction (selectively).
- Hardware proximity of compute and data (selectively, or abstract it).
- Persistence as a core property of the primary state representation.

## Synthesis and Transition to Phase 3

Prior art demonstrates partial solutions to individual bottlenecks. No existing system solves the combination of **bounded executive + explicit verification + minimal movement + persistent cognition + autonomous synthesis** at practical scale.

Therefore, Phase 3 will deliberately generate **multiple fundamentally different approaches**, including some that depart more radically from all of the above.

**Classification Note:** All summaries above are Supported Inferences drawn from the referenced literature and established knowledge of the field. No claims of completeness.

---

**Next per protocol:** Phase 3 — Design Space Exploration.
