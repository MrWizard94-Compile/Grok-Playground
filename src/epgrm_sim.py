"""
EP-GRM Simulator (Explicit Persistent Graph Rewrite Machine)

Implements the architecture described in Phase 6 plan.

This is the primary first artifact for testing H1-H5, H7.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
import copy

from src.core import (
    VersionedGraph, FocusSet, RewriteRule, NodeID, RuleName
)


@dataclass
class StepResult:
    applied: bool
    rule_name: Optional[RuleName]
    movement: int
    focus_size: int
    verified: bool
    notes: str = ""


@dataclass
class RunResult:
    success: bool
    steps: int
    final_focus_size: int
    total_movement: int
    verifications: int
    trace: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None


class EPGRMSimulator:
    """
    High-fidelity but simple simulator of EP-GRM.

    Key invariants (from plan):
    - Executive state = FocusSet (bounded) + Candidate consideration
    - All progress via verified rewrites on VersionedGraph
    - Movement counted on access to nodes not currently "loaded"
    - Deterministic by default
    """

    def __init__(self, max_focus: int = 32):
        self.graph: VersionedGraph = VersionedGraph()
        self.focus = FocusSet(max_size=max_focus)
        self.rules: List[RewriteRule] = []
        self.task_spec: Optional[Dict[str, Any]] = None
        self.acceptance_fn: Optional[Callable[[VersionedGraph], bool]] = None

        # Instrumentation (public)
        self.cumulative_movement: int = 0
        self.verification_count: int = 0
        self.step_count: int = 0
        self.trace: List[Dict[str, Any]] = []

        # "Loaded" set for movement accounting (nodes whose attrs we have recently touched)
        self._loaded: Set[NodeID] = set()

    def reset(self,
              initial_graph: VersionedGraph,
              initial_focus: Set[NodeID],
              rules: List[RewriteRule],
              task_spec: Dict[str, Any],
              acceptance_fn: Callable[[VersionedGraph], bool]) -> None:
        """Reset to a clean initial state (used by experiments)."""
        self.graph = initial_graph.clone() if hasattr(initial_graph, 'clone') else copy.deepcopy(initial_graph)
        self.focus = FocusSet(max_size=self.focus.max_size)
        for nid in initial_focus:
            self.focus.add(nid)
            self._loaded.add(nid)
        self.rules = list(rules)
        self.task_spec = task_spec
        self.acceptance_fn = acceptance_fn

        self.cumulative_movement = 0
        self.verification_count = 0
        self.step_count = 0
        self.trace = []
        self._loaded = set(initial_focus)

    def _account_movement(self, node_ids: Set[NodeID]) -> int:
        """Count bytes for nodes brought into executive attention."""
        moved = 0
        for nid in node_ids:
            if nid not in self._loaded:
                size = self.graph.size_estimate(nid)
                moved += size
                self._loaded.add(nid)
        return moved

    def _light_verify(self, rule: RewriteRule, match: Dict[str, Any]) -> bool:
        """Lightweight verification: re-evaluate guard if present."""
        self.verification_count += 1
        if rule.guard is not None:
            try:
                return bool(rule.guard(match))
            except Exception:
                return False
        return True

    def step(self) -> StepResult:
        """Perform one rewrite cycle or no-op."""
        self.step_count += 1

        if self.acceptance_fn and self.acceptance_fn(self.graph):
            return StepResult(
                applied=False, rule_name=None, movement=0,
                focus_size=len(self.focus), verified=True,
                notes="Goal already satisfied"
            )

        # 1. Consider candidates (MVP: scan focus neighborhood + rules)
        candidates: List[Tuple[RewriteRule, Dict[str, Any]]] = []
        for rule in self.rules:
            for focus_node in list(self.focus.members):
                try:
                    matches = rule.matches(self.graph, {"focus": focus_node})
                    for m in matches:
                        m = dict(m)
                        m["focus_node"] = focus_node
                        m["rule"] = rule.name
                        candidates.append((rule, m))
                except Exception as e:
                    # Record but continue (robustness)
                    self.trace.append({"step": self.step_count, "error": str(e)})

        if not candidates:
            return StepResult(
                applied=False, rule_name=None, movement=0,
                focus_size=len(self.focus), verified=True,
                notes="No candidates found (possible impasse)"
            )

        # 2. Pick highest priority (MVP: first with cost, stable order)
        # In real: use scheduler with goal distance etc.
        candidates.sort(key=lambda rc: rc[0].cost_hint)
        rule, match = candidates[0]

        # 3. Verify
        verified = self._light_verify(rule, match)
        if not verified:
            self.trace.append({"step": self.step_count, "rule": rule.name, "verified": False})
            return StepResult(applied=False, rule_name=rule.name, movement=0,
                              focus_size=len(self.focus), verified=False,
                              notes="Light verification failed")

        # 4. Apply (atomic)
        try:
            changed_nodes, new_attrs_map = rule.apply(self.graph, match)
        except Exception as e:
            self.trace.append({"step": self.step_count, "apply_error": str(e)})
            return StepResult(applied=False, rule_name=rule.name, movement=0,
                              focus_size=len(self.focus), verified=True,
                              notes=f"Apply error: {e}")

        # 5. Movement accounting for accessed + changed nodes
        accessed = set(match.get("matched_nodes", [])) | {match.get("focus_node")}
        accessed |= changed_nodes
        movement = self._account_movement(accessed)

        # Perform the rewrites (update versions)
        for nid, attrs in new_attrs_map.items():
            if nid in self.graph.heads:
                self.graph.rewrite_node(nid, attrs)

        # 6. Update focus (add any new nodes mentioned, respect bound)
        for nid in changed_nodes:
            if nid not in self.focus.members:
                if not self.focus.add(nid):
                    # Bound hit — evict
                    self.focus.evict_lowest_priority()
                    self.focus.add(nid)

        # Record trace entry
        trace_entry = {
            "step": self.step_count,
            "rule": rule.name,
            "applied": True,
            "movement": movement,
            "focus_size": len(self.focus),
            "changed": list(changed_nodes)
        }
        self.trace.append(trace_entry)
        self.cumulative_movement += movement

        return StepResult(
            applied=True,
            rule_name=rule.name,
            movement=movement,
            focus_size=len(self.focus),
            verified=True,
            notes=""
        )

    def run_until(self, max_steps: int = 1000,
                  check_every: int = 1) -> RunResult:
        """Run until acceptance or max_steps or impasse."""
        trace = []
        for s in range(max_steps):
            res = self.step()
            trace.append({
                "step": self.step_count,
                "applied": res.applied,
                "rule": res.rule_name,
                "movement": res.movement,
                "focus": res.focus_size,
                "notes": res.notes
            })
            if self.acceptance_fn and self.acceptance_fn(self.graph):
                return RunResult(
                    success=True,
                    steps=self.step_count,
                    final_focus_size=len(self.focus),
                    total_movement=self.cumulative_movement,
                    verifications=self.verification_count,
                    trace=trace
                )
            if not res.applied and "No candidates" in res.notes:
                # Impasse
                break

        success = bool(self.acceptance_fn and self.acceptance_fn(self.graph))
        return RunResult(
            success=success,
            steps=self.step_count,
            final_focus_size=len(self.focus),
            total_movement=self.cumulative_movement,
            verifications=self.verification_count,
            trace=trace,
            error=None if success else "Did not reach acceptance or impasse"
        )

    def get_exec_state_size(self) -> int:
        """Primary metric for H1: size of bounded executive."""
        return len(self.focus)

    def checkpoint(self) -> Dict[str, Any]:
        """Minimal bootstrap checkpoint (for H4 persistence test)."""
        return {
            "focus": list(self.focus.members),
            "top_goals": [nid for nid in self.focus.members
                          if self.graph.get_current_attrs(nid).get("type") == "Goal"],
            "heads": self.graph.heads.copy(),
            # In real persistent system the graph would live on durable storage
        }
