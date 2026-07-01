"""
Stress dimension generators for EP-GRM.

[MODULE STATUS: FALSIFICATION TOOL]
[INTENT]: "Try to break it" — per explicit research strategy.

Goal: deliberately try to break the architecture along the dimensions recommended:
- graph depth / width / branching factor
- density (many edges per node)
- dependency overlap
- cycles
- conflicting / competing constraints [PLANNED]
- random edits / noise
- disconnected components [PLANNED]

These are used to generate harder instances of synthesis-like graphs and measure
whether focus size stays bounded, movement stays flat, verification work scales reasonably,
as graph size grows.

[CLASSIFICATION]:
- The generator itself is a tool [ESTABLISHED].
- Results from using it update [WORKING HYPOTHESIS] status in CLAIMS_REGISTRY.md.
"""
from __future__ import annotations
from typing import Any, Dict, List, Set, Tuple
import random
import uuid

from src.core import VersionedGraph, RewriteRule, NodeID


def _new_id(prefix: str = "n") -> NodeID:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def create_stress_graph(
    num_nodes: int = 100,
    branching: int = 2,
    density: float = 0.05,
    add_cycles: bool = False,
    overlap: float = 0.3,
    random_edits: int = 0,
    seed: int = 42
) -> VersionedGraph:
    """
    Generate a synthetic graph with controllable stress parameters.
    Nodes are mostly "Goal" / "Fact" / "Partial" style for synthesis flavor.
    """
    random.seed(seed)
    g = VersionedGraph()

    # Core chain / tree backbone
    nodes: List[NodeID] = []
    root = g.create_node("Goal", {"kind": "root", "depth": 0})
    nodes.append(root)

    for i in range(1, num_nodes):
        depth = min(i // max(1, num_nodes // 10), 20)
        ntype = random.choice(["Fact", "Goal", "PartialResult", "Constraint"])
        nid = g.create_node(ntype, {"idx": i, "depth": depth, "kind": "synthetic"})
        nodes.append(nid)

        # Connect to previous with branching
        parent_count = max(1, min(branching, i))
        parents = random.sample(nodes[:-1], k=min(parent_count, len(nodes)-1))
        for p in parents:
            g.add_edge(p, nid, "depends_on")

        # Add some overlap (shared substructure)
        if random.random() < overlap and len(nodes) > 5:
            shared = random.choice(nodes[:-2])
            g.add_edge(shared, nid, "overlaps")

    # Add extra density edges
    extra = int(num_nodes * num_nodes * density / 2)
    for _ in range(extra):
        a, b = random.sample(nodes, 2)
        if not g.graph.has_edge(a, b):
            g.add_edge(a, b, "extra")

    # Introduce cycles (stress for matching / focus)
    if add_cycles:
        for _ in range(max(1, num_nodes // 20)):
            a, b, c = random.sample(nodes, 3)
            g.add_edge(b, a, "cycle")
            g.add_edge(c, b, "cycle")

    # Random noise edits (simulate "environment" changes)
    for _ in range(random_edits):
        if nodes:
            target = random.choice(nodes)
            attrs = g.get_current_attrs(target)
            attrs["noise"] = random.random()
            # Note: this mutates current version directly (for stress)
            g.rewrite_node(target, attrs)

    return g


def make_stress_rewrite_rules(num_rules: int = 5) -> List[RewriteRule]:
    """Simple family of rules that can fire on the stress graphs (advance partials etc.)."""
    rules = []

    def base_matcher_factory(target_depth: int):
        def matcher(graph: VersionedGraph, context: Dict[str, Any]) -> List[Dict[str, Any]]:
            focus = context.get("focus")
            if not focus:
                return []
            attrs = graph.get_current_attrs(focus)
            if attrs.get("depth", 0) != target_depth:
                return []
            # Find a dependent that can be "advanced"
            for succ in graph.graph.successors(focus):
                succ_attrs = graph.get_current_attrs(succ)
                if succ_attrs.get("kind") == "synthetic":
                    return [{"matched_nodes": {focus, succ}, "focus_node": focus, "target": succ}]
            return []
        return matcher

    def applier(graph: VersionedGraph, match: Dict[str, Any]) -> Tuple[Set[NodeID], Dict[NodeID, Dict]]:
        target = match.get("target")
        if target and target in graph.heads:
            attrs = graph.get_current_attrs(target)
            attrs = dict(attrs)
            attrs["advanced"] = True
            graph.rewrite_node(target, attrs)
            return {target}, {target: attrs}
        return set(), {}

    for d in range(num_rules):
        rules.append(RewriteRule(
            name=f"advance_d{d}",
            matcher=base_matcher_factory(d),
            applier=applier,
            guard=lambda m: True,
            cost_hint=1.0 + d * 0.1
        ))

    return rules


def create_stress_task(
    num_nodes: int = 80,
    branching: int = 3,
    density: float = 0.03,
    add_cycles: bool = False,
    random_edits: int = 5,
    seed: int = 123
) -> Dict[str, Any]:
    """Full task package for stress testing."""
    g = create_stress_graph(
        num_nodes=num_nodes,
        branching=branching,
        density=density,
        add_cycles=add_cycles,
        random_edits=random_edits,
        seed=seed
    )

    # Pick some "top level" goals as focus
    goals = [nid for nid in g.get_all_current_node_ids()
             if g.get_current_attrs(nid).get("kind") == "root" or
             g.get_current_attrs(nid).get("depth", 0) < 2]
    if not goals:
        goals = list(g.get_all_current_node_ids())[:3]

    initial_focus = set(goals[:4])

    rules = make_stress_rewrite_rules(num_rules=max(3, branching))

    def acceptance(graph: VersionedGraph) -> bool:
        # Trivial acceptance for stress: after many steps or when many nodes "advanced"
        advanced = sum(1 for nid in graph.get_all_current_node_ids()
                       if graph.get_current_attrs(nid).get("advanced"))
        return advanced > num_nodes * 0.6   # partial progress goal

    return {
        "graph": g,
        "initial_focus": initial_focus,
        "rules": rules,
        "acceptance_fn": acceptance,
        "spec": {
            "type": "stress",
            "num_nodes": num_nodes,
            "branching": branching,
            "density": density,
            "cycles": add_cycles,
            "edits": random_edits
        },
        "horizon": num_nodes
    }
