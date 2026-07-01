"""
T1: Linear Chain Assembly task.

Synthesize a pipeline: start -> A -> B -> ... -> N -> result
Each step applies a "link" primitive by rewriting a pending "next" goal.

This is the simplest controllable-horizon synthesis task.
"""
from __future__ import annotations
from typing import Any, Dict, List, Set
from src.core import VersionedGraph, RewriteRule, NodeID


def create_linear_chain_task(n: int) -> Dict[str, Any]:
    """
    Returns dict with:
      - graph: initial VersionedGraph
      - initial_focus
      - rules
      - acceptance_fn
      - spec (for documentation)
    Horizon roughly = n (n links to create).
    """
    g = VersionedGraph()

    # Library primitives (immutable reference nodes)
    lib_start = g.create_node("LibraryPrimitive", {"name": "start", "arity": 0})
    lib_end = g.create_node("LibraryPrimitive", {"name": "end", "arity": 1})

    primitives = []
    for i in range(n):
        pid = g.create_node("LibraryPrimitive", {"name": f"step_{i}", "arity": 1})
        primitives.append(pid)

    # Top goal
    goal = g.create_node("Goal", {"description": f"build linear chain of length {n}", "target_length": n})

    # Initial "pending link" marker (the thing we will progressively rewrite)
    pending = g.create_node("PendingLink", {"position": 0, "target": n})

    # Current partial result head
    current = g.create_node("PartialResult", {"value": "start", "length": 0})

    # Connect
    g.add_edge(goal, pending, "requires")
    g.add_edge(pending, current, "at")

    # Initial focus: goal + pending
    initial_focus = {goal, pending}

    # Rules
    def make_link_rule(idx: int, prev_prim: str, this_prim_id: NodeID) -> RewriteRule:
        """Rule that advances the chain by one step when at the right position."""
        def matcher(graph: VersionedGraph, context: Dict[str, Any]) -> List[Dict[str, Any]]:
            focus = context.get("focus")
            if not focus:
                return []
            attrs = graph.get_current_attrs(focus)
            if attrs.get("type") != "PendingLink":
                return []
            if attrs.get("position") != idx:
                return []
            # Find current partial
            # In MVP we scan a little
            for nid in graph.get_all_current_node_ids():
                a = graph.get_current_attrs(nid)
                if a.get("type") == "PartialResult" and a.get("length") == idx:
                    return [{"pending": focus, "partial": nid, "matched_nodes": {focus, nid}}]
            return []

        def applier(graph: VersionedGraph, match: Dict[str, Any]) -> tuple[Set[NodeID], Dict[NodeID, Dict]]:
            pending_n = match["pending"]
            partial_n = match["partial"]

            p_attrs = graph.get_current_attrs(pending_n)
            new_pos = p_attrs["position"] + 1

            # Advance pending
            graph.rewrite_node(pending_n, {"position": new_pos, "target": p_attrs["target"]})

            # Advance partial result (symbolic concatenation for verification)
            old_val = graph.get_current_attrs(partial_n)["value"]
            new_val = f"{old_val} -> step_{idx}"
            graph.rewrite_node(partial_n, {"value": new_val, "length": new_pos})

            changed = {pending_n, partial_n}
            new_attrs = {
                pending_n: graph.get_current_attrs(pending_n),
                partial_n: graph.get_current_attrs(partial_n),
            }
            return changed, new_attrs

        return RewriteRule(
            name=f"link_{idx}",
            matcher=matcher,
            applier=applier,
            guard=lambda m: True,
            cost_hint=1.0 + (idx * 0.01)  # slight bias to do in order
        )

    rules: List[RewriteRule] = []
    for i in range(n):
        prim = primitives[i]
        rules.append(make_link_rule(i, f"step_{i}", prim))

    def acceptance(graph: VersionedGraph) -> bool:
        # Find the PartialResult and check length == n
        for nid in graph.get_all_current_node_ids():
            a = graph.get_current_attrs(nid)
            if a.get("type") == "PartialResult" and a.get("length") == n:
                return True
        return False

    return {
        "graph": g,
        "initial_focus": initial_focus,
        "rules": rules,
        "acceptance_fn": acceptance,
        "spec": {"type": "linear_chain", "n": n, "description": f"Assemble chain of {n} steps"},
        "horizon": n,
    }
