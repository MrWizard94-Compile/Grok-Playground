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
from src.metrics import Instrumentation, RunMetrics
from contextlib import nullcontext


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

    Extensively instrumented per research guidance (node visits, rewrites attempted/accepted,
    verification, focus dynamics, graph size over time, timing, memory).
    """

    def __init__(self, max_focus: int = 32, instrument: bool = True):
        self.graph: VersionedGraph = VersionedGraph()
        self.focus = FocusSet(max_size=max_focus)
        self.rules: List[RewriteRule] = []
        self.task_spec: Optional[Dict[str, Any]] = None
        self.acceptance_fn: Optional[Callable[[VersionedGraph], bool]] = None

        # Rich instrumentation
        self.instr = Instrumentation(enable_memory=True) if instrument else None
        self.trace: List[Dict[str, Any]] = []  # kept for backward compat / detailed log

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

        if self.instr:
            self.instr.reset()
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
        if self.instr:
            self.instr.record_verification()
        # legacy support removed; use instr
        if rule.guard is not None:
            try:
                return bool(rule.guard(match))
            except Exception:
                return False
        return True

    def step(self) -> StepResult:
        """Perform one rewrite cycle or no-op. Fully instrumented."""
        step_num = (self.instr.run.steps + 1) if self.instr else (getattr(self, '_step_count', 0) + 1)
        if not hasattr(self, '_step_count'):
            self._step_count = 0
        self._step_count += 1

        nodes_now = self.graph.graph.number_of_nodes()
        edges_now = self.graph.graph.number_of_edges()

        if self.instr:
            self.instr.start_step(self._step_count, nodes_now, edges_now)
            self.instr.record_focus_size(len(self.focus))
            self.instr.record_graph_size(nodes_now, edges_now)

        if self.acceptance_fn and self.acceptance_fn(self.graph):
            if self.instr:
                self.instr.end_step()
                self.instr.finalize_run(True, len(self.focus), nodes_now, edges_now)
            return StepResult(
                applied=False, rule_name=None, movement=0,
                focus_size=len(self.focus), verified=True,
                notes="Goal already satisfied"
            )

        # 1. Consider candidates (instrument visits)
        candidates: List[Tuple[RewriteRule, Dict[str, Any]]] = []
        for rule in self.rules:
            self.instr.record_rewrite_attempt() if self.instr else None
            for focus_node in list(self.focus.members):
                self.instr.record_node_visit() if self.instr else None
                try:
                    matches = rule.matches(self.graph, {"focus": focus_node})
                    for m in matches:
                        self.instr.record_node_visit(len(m.get("matched_nodes", []))) if self.instr else None
                        m = dict(m)
                        m["focus_node"] = focus_node
                        m["rule"] = rule.name
                        candidates.append((rule, m))
                except Exception as e:
                    self.trace.append({"step": self._step_count, "error": str(e)})

        if not candidates:
            res = StepResult(
                applied=False, rule_name=None, movement=0,
                focus_size=len(self.focus), verified=True,
                notes="No candidates found (possible impasse)"
            )
            if self.instr:
                self.instr.record_rewrite_rejected()
                self.instr.end_step()
            return res

        # 2. Pick
        candidates.sort(key=lambda rc: rc[0].cost_hint)
        rule, match = candidates[0]
        self.instr.record_rewrite_attempt() if self.instr else None

        # 3. Verify
        verified = self._light_verify(rule, match)
        if self.instr:
            self.instr.record_verification()

        if not verified:
            self.trace.append({"step": self._step_count, "rule": rule.name, "verified": False})
            if self.instr:
                self.instr.record_rewrite_rejected()
                self.instr.end_step()
            return StepResult(applied=False, rule_name=rule.name, movement=0,
                              focus_size=len(self.focus), verified=False,
                              notes="Light verification failed")

        # 4. Apply
        try:
            changed_nodes, new_attrs_map = rule.apply(self.graph, match)
        except Exception as e:
            self.trace.append({"step": self._step_count, "apply_error": str(e)})
            if self.instr:
                self.instr.record_rewrite_rejected()
                self.instr.end_step()
            return StepResult(applied=False, rule_name=rule.name, movement=0,
                              focus_size=len(self.focus), verified=True,
                              notes=f"Apply error: {e}")

        # 5. Movement
        accessed = set(match.get("matched_nodes", [])) | {match.get("focus_node", None)} - {None}
        accessed |= changed_nodes
        movement = self._account_movement(accessed)
        if self.instr:
            self.instr.record_movement(movement)

        # Perform rewrites
        for nid, attrs in new_attrs_map.items():
            if nid in self.graph.heads:
                self.graph.rewrite_node(nid, attrs)

        # 6. Update focus + instrument changes
        for nid in changed_nodes:
            if nid not in self.focus.members:
                if not self.focus.add(nid):
                    if self.instr:
                        self.instr.record_focus_eviction()
                    self.focus.evict_lowest_priority()
                    self.focus.add(nid)
                else:
                    if self.instr:
                        self.instr.record_focus_add()

        if self.instr:
            self.instr.record_focus_size(len(self.focus))
            self.instr.record_rewrite_accepted()

        # Trace (richer)
        trace_entry = {
            "step": self._step_count,
            "rule": rule.name,
            "applied": True,
            "movement": movement,
            "focus_size": len(self.focus),
            "changed": list(changed_nodes)
        }
        self.trace.append(trace_entry)

        if self.instr:
            self.instr.end_step()

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
        """Run until acceptance or max_steps or impasse. Uses rich metrics when enabled."""
        trace = []
        for s in range(max_steps):
            res = self.step()
            trace.append({
                "step": getattr(self, '_step_count', s+1),
                "applied": res.applied,
                "rule": res.rule_name,
                "movement": res.movement,
                "focus": res.focus_size,
                "notes": res.notes
            })
            if self.acceptance_fn and self.acceptance_fn(self.graph):
                if self.instr:
                    nodes = self.graph.graph.number_of_nodes()
                    edges = self.graph.graph.number_of_edges()
                    self.instr.finalize_run(True, len(self.focus), nodes, edges)
                return RunResult(
                    success=True,
                    steps=getattr(self, '_step_count', 0),
                    final_focus_size=len(self.focus),
                    total_movement=self.instr.run.total_movement if self.instr else 0,
                    verifications=self.instr.run.total_verification_calls if self.instr else 0,
                    trace=trace
                )
            if not res.applied and "No candidates" in res.notes:
                break

        success = bool(self.acceptance_fn and self.acceptance_fn(self.graph))
        if self.instr:
            nodes = self.graph.graph.number_of_nodes()
            edges = self.graph.graph.number_of_edges()
            self.instr.finalize_run(success, len(self.focus), nodes, edges)

        return RunResult(
            success=success,
            steps=getattr(self, '_step_count', 0),
            final_focus_size=len(self.focus),
            total_movement=self.instr.run.total_movement if self.instr else 0,
            verifications=self.instr.run.total_verification_calls if self.instr else 0,
            trace=trace,
            error=None if success else "Did not reach acceptance or impasse"
        )

    def get_exec_state_size(self) -> int:
        """Primary metric for H1: size of bounded executive."""
        return len(self.focus)

    def get_run_metrics(self) -> Optional[RunMetrics]:
        """Return the rich instrumentation data."""
        return self.instr.get_run_metrics() if self.instr else None

    def checkpoint(self) -> Dict[str, Any]:
        """Minimal bootstrap checkpoint (for H4 persistence test)."""
        size_est = len(str(self.focus.members)) + len(self.graph.heads) * 20
        with (self.instr.measure_checkpoint(size_est) if self.instr else nullcontext()):
            return {
                "focus": list(self.focus.members),
                "top_goals": [nid for nid in self.focus.members
                              if self.graph.get_current_attrs(nid).get("type") == "Goal"],
                "heads": self.graph.heads.copy(),
            }
