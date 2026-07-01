"""
Baselines for comparison (Phase 5).

B1: Naive Context Agent (NCA) — grows "loaded context".
B2: Full-State Reload (FSR) — reloads everything each step.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Set
import copy

from src.core import VersionedGraph


@dataclass
class BaselineRunResult:
    success: bool
    steps: int
    peak_context_size: int
    total_movement: int
    trace: List[Dict[str, Any]]


class NaiveContextAgent:
    """
    B1: Simulates an agent that keeps growing context.
    "Movement" is the size of everything it decides is relevant each step.
    """

    def __init__(self):
        self.graph: VersionedGraph = VersionedGraph()
        self.context: Dict[str, Any] = {}
        self.cumulative_movement = 0
        self.steps = 0

    def reset(self, initial_graph: VersionedGraph, task_spec: Dict[str, Any],
              acceptance_fn: Callable[[Any], bool], progress_fn: Callable[[Any], bool]):
        self.graph = initial_graph.clone() if hasattr(initial_graph, 'clone') else copy.deepcopy(initial_graph)
        # Naive: dump a lot of state into "context"
        self.context = {
            "all_nodes": {nid: initial_graph.get_current_attrs(nid)
                          for nid in initial_graph.get_all_current_node_ids()},
            "task": task_spec,
            "history": []
        }
        self.acceptance = acceptance_fn
        self.progress_fn = progress_fn
        self.cumulative_movement = 0
        self.steps = 0

    def step(self) -> Dict[str, Any]:
        self.steps += 1
        # "Load" everything — simulates full relevant context materialization
        loaded_size = sum(self.graph.size_estimate(n) for n in self.graph.get_all_current_node_ids())
        self.cumulative_movement += loaded_size

        progressed = self.progress_fn(self.context)
        if self.acceptance(self.graph):
            return {"applied": True, "movement": loaded_size, "done": True}

        return {"applied": progressed, "movement": loaded_size, "done": False}

    def run_until(self, max_steps: int = 1000) -> BaselineRunResult:
        trace = []
        peak = 0
        for _ in range(max_steps):
            res = self.step()
            size = len(str(self.context))
            peak = max(peak, size)
            trace.append(res)
            if res.get("done"):
                break
        success = self.acceptance(self.graph)
        return BaselineRunResult(
            success=success,
            steps=self.steps,
            peak_context_size=peak,
            total_movement=self.cumulative_movement,
            trace=trace
        )


class FullStateReloadPlanner:
    """
    B2: Every step explicitly reloads full relevant state.
    Even more pessimistic movement.
    """

    def __init__(self):
        self.graph: VersionedGraph = VersionedGraph()
        self.cumulative_movement = 0
        self.steps = 0

    def reset(self, g: VersionedGraph, acceptance: Callable, progress: Callable):
        self.graph = g.clone() if hasattr(g, 'clone') else copy.deepcopy(g)
        self.acceptance = acceptance
        self.progress = progress
        self.cumulative_movement = 0
        self.steps = 0

    def step(self):
        self.steps += 1
        # Reload everything every step
        moved = sum(self.graph.size_estimate(n) for n in self.graph.get_all_current_node_ids())
        self.cumulative_movement += moved

        self.progress(self.graph)

        return {"applied": True, "movement": moved}

    def run_until(self, max_steps=1000):
        trace = []
        peak = 0
        for _ in range(max_steps):
            r = self.step()
            peak = max(peak, r["movement"])
            trace.append(r)
            if self.acceptance(self.graph):
                break
        return BaselineRunResult(
            success=self.acceptance(self.graph),
            steps=self.steps,
            peak_context_size=peak,
            total_movement=self.cumulative_movement,
            trace=trace
        )
