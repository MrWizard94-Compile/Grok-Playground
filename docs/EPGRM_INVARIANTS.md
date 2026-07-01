# EP-GRM ARCHITECTURE INVARIANTS
**File:** [ARCHITECTURE - ESTABLISHED + SPEC]  
**Version:** 2026-07-01  
**Purpose:** Explicitly list what must always be true for this architecture. Violations are bugs or falsifying results.

## Core Model Invariants (Must Hold)

1. **Bounded Executive State** [IMPLEMENTED + TESTED]
   - At no point may |active_focus| exceed the configured max_focus after a step.
   - Enforcement: `FocusSet.add()` + eviction logic.
   - Verified in every run via instrumentation + tests.

2. **All Progress Via Local Rewrites** [CORE PRINCIPLE]
   - No global activation or full-graph scan is required for forward progress.
   - Only nodes in focus or directly matched from focus can cause changes.
   - Data movement is only counted on nodes brought into attention.

3. **Persistent Versioned Graph is the Single Source of Truth**
   - Both long-term knowledge and current working state live in the versioned graph.
   - Executive focus contains only references (IDs) + small metadata.
   - Old versions are retained for justification and rollback.

4. **Verification is Co-located with Rewrite** [INTRINSIC]
   - Every accepted rewrite produces a justification record.
   - Light verification (guard re-evaluation) happens before commit.
   - [FUTURE] Heavy sampled re-derivation.

5. **Deterministic State Transitions**
   - Same (graph heads + focus + rule ordering) → same next state.
   - No hidden mutable global state.

## Implementation Invariants (Current Simulator)

- FocusSet.max_size is respected on every add.
- Movement is only charged on first "load" of a node into `_loaded`.
- All rule applications are atomic (new versions or nothing).
- Instrumentation captures before/after every step.

## Design Assumptions (Labeled)

**[ENGINEERING ASSUMPTION]** Matching cost can be kept reasonable via focus locality + future indexing.
**[WORKING HYPOTHESIS]** Goal-directed priority scheduling will allow useful work without needing large focus.
**[SPECULATION]** This model can eventually support self-modification of rules while preserving invariants.

## What Would Constitute a Fundamental Failure

- Focus size required grows linearly with problem size on multiple task families.
- Data movement (properly measured) becomes comparable to full-state reload.
- Adding cycles or conflicting constraints forces either focus explosion or deadlock/starvation.
- Verification overhead makes the system slower than non-verified baselines by >10x without corresponding reliability gain.

## Current Status vs Invariants

As of latest stress sweep + live runs:
- Invariant 1 held across all 96+ runs + live tests.
- Invariant 2 held by construction.
- Others held in the tested scope.

**Any future run that breaks an invariant must be prominently logged as [NEGATIVE RESULT] in RESEARCH_LOG.md and CLAIMS_REGISTRY.md**

---
*This document is the contract the implementation must satisfy.*
