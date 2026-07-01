# Iteration 001 — Phase 6: Implementation Planning

**Date:** 2026-07-01  
**Status:** Draft

**Protocol:** Planning **precedes** any code. Architecture, interfaces, data structures, algorithms, state transitions, and verification strategy fully specified before implementation.

## Scope for First Implementation Artifact

**Primary Artifact (this iteration):** A high-fidelity **Architecture Simulator** capable of:
- Executing EP-GRM (prioritized).
- Executing a simplified HB-AE (for comparison).
- Running the defined experiments / task families.
- Producing all required instrumentation data.
- Being deterministic and reproducible.

Secondary: Skeleton for future CT-DFV / CSPS if time and evidence allow.

**Non-Goals for first cut:**
- High performance (simulation fidelity > speed).
- Full self-modification (H7 lightweight only).
- Real I/O or external tools.
- GPU acceleration (pure CPU simulation).

**Resource Target Adherence:** Simulator itself must run comfortably on the GTX 1660 Ti machine (target < 3-4 GB RAM for large experiments).

## Chosen Primary Architecture: EP-GRM (Detailed Design)

### Computational Model
- **Data:** Versioned directed attributed multigraph.
  - Nodes: Have unique ID, type (Fact, Goal, Plan, CodeFragment, Justification, LibraryPrimitive, ...), attributes (dict), and version history.
  - Edges: Labeled (e.g., "depends_on", "produces", "justifies", "part_of").
  - Versions: On rewrite, affected nodes get new versions. Old versions remain for audit/rollback. A "head" pointer per logical node.
- **Computation:** Pattern-directed rewrite.
  - A `RewriteRule` = (left-hand pattern, guard, right-hand replacement template, justification schema).
  - Pattern matching finds subgraphs satisfying the LHS + guard.
  - Application produces new node/edge versions and a Justification node linking old premises → new conclusions.

### Execution Model
- **Cycle:**
  1. Scheduler selects next focus or candidate rewrite (priority + fairness).
  2. Matching engine finds applicable rule instances on current heads (incremental where possible).
  3. Selected rewrite is verified (local guard + optional sampled full justification check).
  4. Atomic commit: new versions created, focus updated, justification recorded.
  5. Side effects on persistent store model (in sim: the graph itself is the store).
- No global program counter. Progress is rewrite application until goal satisfaction or quiescence.

### Memory Model
- **Persistent primary:** The full versioned graph (simulated as the networkx graph + version dicts).
- **Working / Executive:** 
  - `FocusSet`: small set of node IDs currently "in attention" (bounded by policy, e.g., max 64).
  - `CandidateQueue`: priority queue of (rule_instance, priority, estimated_cost).
  - Small caches for indexes (type → nodes, attribute indexes).
- **Loading:** Only nodes in Focus or directly referenced by current candidates are "loaded" into executive accounting. Others remain in the "backing" graph (movement cost counted on access).

### Persistent Knowledge Representation
- The versioned graph **is** both long-term and working knowledge.
- Goals are nodes. Plans and partial CodeFragments are subgraphs.
- Library primitives are immutable base nodes.

### Working Memory Representation
- FocusSet + CandidateQueue + small derivation stack (for backtracking if needed).
- Explicit links back into the persistent graph.

### Scheduling Model
- Multi-level priority:
  - Goal relevance (distance or dependency to top goals).
  - Rule specificity or historical success.
  - Fairness / age to prevent starvation.
- Hard cap: if Focus or queue exceeds bound → drop lowest priority or defer.
- Deterministic tie-breaking via node ID + rule ID.

### Communication Model
- Internal only in simulation: all via graph structure and focus.
- (Future) messages could be special "Message" nodes.

### Verification Model
- **Intrinsic:** Every rewrite produces a Justification node.
- **Lightweight check:** Structural pattern match + guard re-evaluation on apply.
- **Heavy check (sampling):** Occasionally fully re-derive a justification chain from original premises.
- **Acceptance:** External task checker (pure function) validates final CodeFragment against spec.
- Rollback: on failed heavy check or injected fault, revert heads to previous version using recorded parent pointers.

### Failure Handling
- Failed rewrite: record Failure node, possibly lower priority of similar rules.
- Contradiction: special "Nogood" nodes that block certain rewrites.
- Quiescence without goal satisfaction → impasse (create sub-goal or report).

### Resource Management
- Node/edge budget in simulation.
- History compaction policy (optional): keep only last M versions + all justification roots.
- Focus eviction policy: LRU + relevance.

### State Transitions (Explicit)
```
State = (GraphHeads, FocusSet, CandidateQueue, VersionLog, Metrics)
Transition(relevant_rule_instance):
  - Validate
  - Compute new_heads, new_justification
  - Update Focus and Queue
  - Append to VersionLog
  - Update Metrics (movement += size of touched nodes)
```

All transitions produce a new State deterministically.

## Data Structures (Python / networkx plan)

- `VersionedGraph`:
  - `nx.MultiDiGraph` for current heads (or separate structure).
  - `versions: dict[node_id, list[Version]]` where Version = {attrs, incoming, outgoing, parent_version}
  - Or simpler: immutable node snapshots; current heads point to latest snapshot id.

- `Node` (dataclass or dict): id, type, attrs, version
- `RewriteRule` (dataclass): name, lhs_pattern (networkx or custom matcher), guard (callable), rhs_template (callable or declarative), cost_hint
- `FocusSet`: set of node ids + metadata (priority, last_access)
- `Scheduler`: class with `select_next(...) -> Optional[RuleInstance]`
- `Justification`: node type with premises list + rule + timestamp
- `TaskSpec`: spec dict + acceptance_fn
- `SimulatorState`: frozen or immutable snapshot for reproducibility

For incremental matching: simple reverse index `type_to_nodes`, `attr_key_to_nodes`. On rewrite, only re-scan neighborhood of changed nodes.

## Interfaces (High-Level)

```python
class ArchitectureSimulator:
    def reset(self, initial_graph, focus, rules, task_spec): ...
    def step(self) -> StepResult: ...
    def run_until(self, predicate, max_steps) -> RunResult: ...
    def get_exec_state_size(self) -> int: ...
    def get_cumulative_movement(self) -> int: ...
    def get_justification_count(self) -> int: ...
    def checkpoint(self) -> Checkpoint: ...
    def restore(self, checkpoint) -> None: ...
    def get_current_goals(self) -> list: ...
```

`StepResult`: applied, new_focus_size, movement_this_step, verified, ...

## Algorithms (Sketches)

1. **Match & Apply (EP-GRM core)**
   - For candidates in queue or focus neighbors:
     - Attempt pattern match (networkx isomorphism or custom small-pattern matcher for speed).
     - If match + guard(): produce rhs nodes/edges.
   - To keep simple: start with exhaustive small patterns on focus neighborhood; add indexing later.

2. **Priority Calculation**
   - Base priority from goal distance (BFS from goal nodes in graph).
   - Bonus for high-specificity rules.
   - Decay for age.

3. **Versioning on Rewrite**
   - For every touched node: create new version snapshot.
   - Record parent.
   - Update heads.

4. **Instrumentation**
   - On every node/edge access outside current "loaded" set: add size to movement counter.
   - Size estimator: recursive or cached (len(attrs) + 1 per edge).

## HB-AE Sketch (for comparison sim)

- `Actor` dataclass: id, local_state (small dict or tiny nx graph), mailbox (bounded deque), persistent_slice_id, rule_set (subset of rewrites or local productions).
- Global: dict[actor_id, Actor], event_queue, director_actor.
- Step: pick actor (by priority), process one message or internal step, possibly spawn child.
- Movement: only when message payload crosses or actor loads its slice.
- Verification: message carries justification token; local checks.

Shared infrastructure: Task generator, metrics collector, result serializer.

## Verification Strategy for the Simulator Itself

- Property-based: Using pytest + hypothesis or manual generators, assert:
  - After any sequence of steps, all justifications are consistent with current heads (replayable).
  - Focus size never exceeds configured bound.
  - Acceptance test only passes on valid final artifacts.
  - Restore from checkpoint produces identical behavior.
- Determinism: full trace of applied rules + random seeds logged; replay must match.
- Small model checking: for T1 linear tasks with <10 steps, exhaustively explore all possible rewrite orders and assert only correct paths lead to success.
- Code correctness: type hints, small unit tests for core classes, integration tests per task family.

## Implementation Order (for Phase 7)

1. Core data structures: VersionedGraph (simple first), Node, basic matching.
2. RewriteRule + one or two hand-written rules for T1.
3. FocusSet + naive Scheduler.
4. Basic step loop + instrumentation.
5. Task generator for T1 + acceptance.
6. Naive Context Agent and FSR baselines as separate simulator classes implementing same interface.
7. Incremental improvements (indexing, better scheduler).
8. HB-AE basic implementation.
9. Checkpoint/restore.
10. Experiment runner script + CSV/JSON output.
11. Tests.

## Documentation Requirements
- Every module/class has docstring.
- Architecture invariants documented in code + markdown.
- Experiment configs versioned with results.

## Risks Identified in Planning
- Matching performance in Python may be slow for very large graphs → cap graph size in first experiments; profile early.
- Versioning memory bloat → implement simple pruning policy from start.
- Over-engineering → start minimal (one task type, naive matching) then add.

## Exit Criteria for Phase 7
- Simulator can run Exp1–Exp4 on T1 at least.
- Reproducible traces.
- Data collection sufficient to begin Phase 8/9 analysis.
- All code reviewed against this plan (self-review + simple diffs).

---

**Phase 6 Sign-off:** Architecture, data structures, algorithms, interfaces, verification strategy, and phased build plan documented.

**Next:** Phase 7 — Implementation (only what is planned above).
