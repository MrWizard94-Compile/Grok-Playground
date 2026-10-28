"""
Rich instrumentation for EP-GRM experiments.

[MODULE STATUS: ESTABLISHED + INSTRUMENTATION LAYER]
[DESIGN GOAL]: Obsessive data collection so that later analysis can answer "exactly how did focus behave under stress?"

Per research feedback:
- Record far more than pass/fail.
- Enable plotting: peak focus vs graph size, rewrites vs size, verification work vs size, etc.
- Support stress dimension analysis.

[WHAT IS CAPTURED]:
- rewrites_attempted / accepted / rejected
- verification_calls
- node_visits, edge_traversals
- focus dynamics (size, adds, evictions) per step
- movement proxy per step
- timing + sampled memory
- graph size evolution
- checkpoint accounting

This data is required for credible claims about scaling.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
import time
import tracemalloc
from contextlib import contextmanager


@dataclass
class StepMetrics:
    """Per-step detailed counters."""
    step: int = 0
    rewrites_attempted: int = 0
    rewrites_accepted: int = 0
    rewrites_rejected: int = 0
    verification_calls: int = 0
    node_visits: int = 0
    edge_traversals: int = 0
    focus_size: int = 0
    focus_adds: int = 0
    focus_evictions: int = 0
    movement_this_step: int = 0
    graph_nodes: int = 0
    graph_edges: int = 0
    duration_ms: float = 0.0
    memory_kb: float = 0.0  # approximate
    # [NEW METRICS per user feedback on locality and efficiency]
    focus_admissions_this_step: int = 0
    nodes_touched_this_step: int = 0  # newly brought into attention this step
    value_this_step: float = 0.0  # value delta from this rewrite (for quality metric)


@dataclass
class RunMetrics:
    """Aggregated + time series for a full run."""
    success: bool = False
    steps: int = 0
    final_focus_size: int = 0
    peak_focus_size: int = 0
    total_movement: int = 0
    total_verification_calls: int = 0
    total_rewrites_attempted: int = 0
    total_rewrites_accepted: int = 0
    total_rewrites_rejected: int = 0
    total_node_visits: int = 0
    total_edge_traversals: int = 0
    final_graph_nodes: int = 0
    final_graph_edges: int = 0
    total_duration_s: float = 0.0
    peak_memory_kb: float = 0.0
    checkpoint_count: int = 0
    total_checkpoint_size: int = 0

    # [NEW AGGREGATES for H1 efficiency + locality analysis per reviewer feedback]
    total_focus_admissions: int = 0
    unique_nodes_touched: int = 0   # Information Locality numerator
    final_graph_nodes: int = 0
    information_locality: float = 0.0  # unique_touched / final_graph_nodes  (lower = better locality)

    # Usefulness / efficiency metrics
    average_focus_size: float = 0.0
    rewrites_per_admission: float = 0.0  # total_rewrites / total_admissions (higher = better scheduler efficiency)
    efficiency_score: float = 0.0  # rewrites / (average_focus * steps)  (work per unit executive state per step)

    # [NEW for diagnosing no-progress]
    impasse_steps: int = 0  # number of steps with no candidates found

    # Value of work (per reviewer feedback: not just quantity, but value/quality)
    total_value: float = 0.0  # cumulative "value" from rewrites (e.g., progress deltas)
    value_per_rewrite: float = 0.0  # average value per rewrite (convergence indicator)

    # [TIER 1 HIGHER FIDELITY] Memory model stats
    hf_total_bytes_moved: int = 0
    hf_page_faults: int = 0
    hf_write_backs: int = 0
    hf_persistence_log_entries: int = 0

    # Time series (list of StepMetrics or lightweight dicts)
    per_step: List[Dict[str, Any]] = field(default_factory=list)

    def to_summary_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d.pop('per_step', None)
        return d

    def compute_locality(self):
        if self.final_graph_nodes > 0 and self.final_graph_nodes > 0:
            self.information_locality = self.unique_nodes_touched / self.final_graph_nodes
        else:
            self.information_locality = 0.0

    def compute_efficiency(self):
        if self.steps > 0:
            # Compute average focus from per_step if available
            if self.per_step:
                focuses = [p.get('focus_size', 0) for p in self.per_step]
                self.average_focus_size = sum(focuses) / len(focuses) if focuses else 0
            else:
                self.average_focus_size = (self.peak_focus_size + self.final_focus_size) / 2
            if self.total_focus_admissions > 0:
                self.rewrites_per_admission = self.total_rewrites_accepted / self.total_focus_admissions
            if self.average_focus_size > 0:
                self.efficiency_score = self.total_rewrites_accepted / (self.average_focus_size * self.steps)
            if self.total_rewrites_accepted > 0:
                self.value_per_rewrite = self.total_value / self.total_rewrites_accepted


class Instrumentation:
    """
    Central collector. Call methods from the simulator at key points.
    Keeps both cumulative and per-step records.
    """

    def __init__(self, enable_memory: bool = True):
        self.current = StepMetrics()
        self.run = RunMetrics()
        self._step_start_time: float = 0.0
        self.enable_memory = enable_memory
        self._memory_started = False
        if enable_memory:
            try:
                tracemalloc.start()
                self._memory_started = True
            except Exception:
                self.enable_memory = False

    def reset(self):
        self.current = StepMetrics()
        self.run = RunMetrics()
        self._step_start_time = 0.0

    def start_step(self, step_num: int, current_graph_nodes: int, current_graph_edges: int):
        self.current = StepMetrics(step=step_num)
        self.current.graph_nodes = current_graph_nodes
        self.current.graph_edges = current_graph_edges
        self._step_start_time = time.perf_counter()

    def end_step(self):
        duration = (time.perf_counter() - self._step_start_time) * 1000
        self.current.duration_ms = duration

        if self.enable_memory and self._memory_started:
            try:
                current, peak = tracemalloc.get_traced_memory()
                self.current.memory_kb = current / 1024.0
                if self.current.memory_kb > self.run.peak_memory_kb:
                    self.run.peak_memory_kb = self.current.memory_kb
            except Exception:
                pass

        # Aggregate
        self.run.steps = max(self.run.steps, self.current.step)
        self.run.per_step.append(asdict(self.current))

        self.run.total_movement += self.current.movement_this_step
        self.run.total_verification_calls += self.current.verification_calls
        self.run.total_node_visits += self.current.node_visits
        self.run.total_edge_traversals += self.current.edge_traversals
        self.run.total_rewrites_attempted += self.current.rewrites_attempted
        self.run.total_rewrites_accepted += self.current.rewrites_accepted
        self.run.total_rewrites_rejected += self.current.rewrites_rejected

        if self.current.focus_size > self.run.peak_focus_size:
            self.run.peak_focus_size = self.current.focus_size

        # Aggregate value
        self.run.total_value += getattr(self.current, 'value_this_step', 0)

        # Aggregate new metrics
        self.run.total_focus_admissions += self.current.focus_admissions_this_step
        # For unique touched, we rely on sim's _unique_touched for run level, but accumulate per step for series
        self.run.unique_nodes_touched = max(self.run.unique_nodes_touched, self.current.nodes_touched_this_step)  # temp, actual set in sim

    def record_rewrite_attempt(self):
        self.current.rewrites_attempted += 1
        self.run.total_rewrites_attempted += 1  # incremental safety

    def record_rewrite_accepted(self):
        self.current.rewrites_accepted += 1

    def record_rewrite_rejected(self):
        self.current.rewrites_rejected += 1

    def record_verification(self):
        self.current.verification_calls += 1

    def record_node_visit(self, count: int = 1):
        self.current.node_visits += count

    def record_edge_traversal(self, count: int = 1):
        self.current.edge_traversals += count

    def record_movement(self, bytes_moved: int):
        self.current.movement_this_step += bytes_moved

    def record_focus_size(self, size: int):
        self.current.focus_size = size

    def record_focus_add(self):
        self.current.focus_adds += 1

    def record_focus_eviction(self):
        self.current.focus_evictions += 1

    def record_graph_size(self, nodes: int, edges: int):
        self.current.graph_nodes = nodes
        self.current.graph_edges = edges

    def finalize_run(self, success: bool, final_focus: int, final_nodes: int, final_edges: int):
        self.run.success = success
        self.run.final_focus_size = final_focus
        self.run.final_graph_nodes = final_nodes
        self.run.final_graph_edges = final_edges

        # sum totals from per_step if not already aggregated perfectly
        if self.run.total_duration_s == 0:
            self.run.total_duration_s = sum(p.get('duration_ms', 0) for p in self.run.per_step) / 1000.0

        self.run.compute_locality()
        self.run.compute_efficiency()

    def get_run_metrics(self) -> RunMetrics:
        return self.run

    @contextmanager
    def measure_checkpoint(self, size_estimate: int):
        self.run.checkpoint_count += 1
        self.run.total_checkpoint_size += size_estimate
        yield
