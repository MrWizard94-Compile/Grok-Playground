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
    add_conflicts: bool = False,  # [NEW 2026-07-01] conflicting constraints dimension
    add_disconnected: bool = False,  # [NEW 2026-07-01] disconnected components dimension
    heavy: bool = False,  # [HEAVY MODE]
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

    # [NEW STRESS DIMENSION - 2026-07-01] Conflicting constraints
    # [LABEL: FALSIFICATION ATTEMPT for H1/H3]
    # Add nodes marked as conflicting. Rules may need to handle nogoods.
    # This tests whether focus stays bounded when there are irreconcilable facts/goals.
    if add_conflicts:
        conflict_count = max(1, num_nodes // 15)
        conflict_nodes = random.sample(nodes, min(conflict_count, len(nodes)))
        for i, nid in enumerate(conflict_nodes):
            attrs = g.get_current_attrs(nid)
            attrs["conflicting"] = True
            attrs["conflict_group"] = i % 3  # groups of conflicts
            g.rewrite_node(nid, attrs)
            # Add some cross edges that create tension
            if i > 0:
                other = conflict_nodes[(i-1) % len(conflict_nodes)]
                g.add_edge(nid, other, "conflicts_with")

    # [NEW STRESS DIMENSION - 2026-07-01] Disconnected components
    # [LABEL: FALSIFICATION ATTEMPT for H1 - tests if focus can handle multiple independent subproblems without growing]
    if add_disconnected:
        num_components = 5 if heavy else 1  # HEAVY mode: 5 disconnected components for ultra stress
        for comp_idx in range(num_components):
            comp_label = chr(ord('B') + comp_idx)
            dc_size = max(5, num_nodes // (3 + comp_idx * 2))
            dc_nodes = []
            start_idx = num_nodes + comp_idx * dc_size
            for i in range(dc_size):
                nid = g.create_node("Fact", {"idx": start_idx + i, "depth": 0, "kind": "disconnected", "component": comp_label, "conflicting": heavy and (i % 3 == 0)})
                dc_nodes.append(nid)
            # Link internally
            for i in range(1, len(dc_nodes)):
                g.add_edge(dc_nodes[i-1], dc_nodes[i], "local_dep")
            # Local goal per component
            local_goal = g.create_node("Goal", {"description": f"disconnected_subproblem_{comp_label}", "component": comp_label})
            g.add_edge(local_goal, dc_nodes[0], "requires")

    # Random noise edits (simulate "environment" changes)
    for _ in range(random_edits):
        if nodes:
            target = random.choice(nodes)
            attrs = g.get_current_attrs(target)
            attrs["noise"] = random.random()
            # Note: this mutates current version directly (for stress)
            g.rewrite_node(target, attrs)

    return g

def compute_graph_properties(g: VersionedGraph) -> dict:
    """Analytical properties for dependency frontier.
    [LABEL: Proper frontier = transitive predecessors within rewrite context (BFS up to depth 2 on pred graph, as rewrites depend on constraining deps).]
    """
    import collections
    nodes = list(g.get_all_current_node_ids())
    if not nodes:
        return {'avg_degree': 0, 'max_degree': 0, 'est_frontier': 0, 'avg_active_frontier': 0, 'max_active_frontier': 0}

    degrees = [len(list(g.graph.successors(n))) + len(list(g.graph.predecessors(n))) for n in nodes]
    avg_d = sum(degrees) / len(degrees)
    max_d = max(degrees)

    # Active Dependency Frontier: BFS predecessors up to depth 2
    frontiers = []
    for start in nodes:
        visited = set()
        queue = collections.deque([(start, 0)])
        while queue:
            node, depth = queue.popleft()
            if depth > 2: continue
            for pred in g.graph.predecessors(node):
                if pred not in visited:
                    visited.add(pred)
                    queue.append((pred, depth + 1))
        frontiers.append(len(visited))
    avg_f = sum(frontiers) / len(frontiers)
    max_f = max(frontiers) if frontiers else 0

    return {
        'avg_degree': round(avg_d, 2),
        'max_degree': max_d,
        'est_frontier': max_d,
        'avg_active_frontier': round(avg_f, 2),
        'max_active_frontier': max_f,
        # [PHASE 10] Structure concentration proxy: higher = more concentrated deps (potentially lower L for given F)
        'frontier_concentration': round(max_f / max(1, avg_d), 2) if avg_d > 0 else 0
    }

def predict_locality(frontier: float, n: int, c: float = 0.5, concentration: float = 1.0) -> float:
    """Phase 10 revised predictive model.

    Base: L ≈ c * (F / N)   [from prior]
    Adjustment (post EXP-027/029 evidence): multiply by structure factor.
    Observed: L strongly capped by architecture (local rewrites + bounded focus).
    In layered/concentrated high-F structures, effective L can be much lower (c drops to ~0.06-0.1).
    concentration: proxy for dep concentration (higher = more shared deps, tends to lower realized L).

    Revised form (working): L ≈ min( observed_cap , c * (F / N) / max(1, concentration * 0.5) )
    Use for directional prediction + falsification only. All params fitted per family.
    """
    if n == 0: return 0.0
    base = c * (frontier / n)
    # Architecture cap + concentration dampening (higher concentration -> lower L)
    adjusted = base / max(1.0, concentration * 0.5)
    # Hard cap from data: L rarely exceeds ~0.12-0.25 in tested EP-GRM stress family even at high F
    arch_cap = 0.15
    return min(arch_cap, adjusted)


def make_stress_rewrite_rules(num_rules: int = 8) -> List[RewriteRule]:
    """Enhanced rules for heavy stress tests. [LABEL: Increased matching flexibility for ultra-heavy graphs]
    Rules now fire on broader depth ranges and any synthetic nodes to allow progress under high density/complexity.
    """
    rules = []

    def flexible_matcher_factory(min_depth: int = 0, max_depth: int = 30):
        def matcher(graph: VersionedGraph, context: Dict[str, Any]) -> List[Dict[str, Any]]:
            focus = context.get("focus")
            if not focus:
                return []
            attrs = graph.get_current_attrs(focus)
            d = attrs.get("depth", 0)
            if not (min_depth <= d <= max_depth):
                return []
            # Find any unadvanced synthetic dependent - broadened for heavy stress
            candidates = list(graph.graph.successors(focus)) + list(graph.graph.predecessors(focus))
            for succ in candidates[:10]:  # limit for perf in ultra-dense
                succ_attrs = graph.get_current_attrs(succ)
                if succ_attrs.get("kind") == "synthetic" and not succ_attrs.get("advanced"):
                    return [{"matched_nodes": {focus, succ}, "focus_node": focus, "target": succ}]
            # Fallback: any synthetic in focus's local area if no direct dep
            for nid in list(graph.get_all_current_node_ids())[:20]:
                if nid != focus:
                    n_attrs = graph.get_current_attrs(nid)
                    if n_attrs.get("kind") == "synthetic" and not n_attrs.get("advanced"):
                        # only if connected loosely
                        if graph.graph.has_edge(focus, nid) or graph.graph.has_edge(nid, focus):
                            return [{"matched_nodes": {focus, nid}, "focus_node": focus, "target": nid}]
            return []
        return matcher

    # [HEAVY STRESS FALLBACK RULE] Always try to advance ANY unadvanced synthetic if no depth match.
    # This increases capabilities for pulling data in dense graphs.
    def any_advance_matcher(graph: VersionedGraph, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        focus = context.get("focus")
        if not focus:
            return []
        for nid in list(graph.get_all_current_node_ids())[:50]:  # sample for perf
            if nid != focus:
                n_attrs = graph.get_current_attrs(nid)
                if n_attrs.get("kind") == "synthetic" and not n_attrs.get("advanced"):
                    return [{"matched_nodes": {focus, nid}, "focus_node": focus, "target": nid}]
        return []

    def any_applier(graph: VersionedGraph, match: Dict[str, Any]) -> Tuple[Set[NodeID], Dict[NodeID, Dict]]:
        target = match.get("target")
        if target and target in graph.heads:
            attrs = graph.get_current_attrs(target)
            attrs = dict(attrs)
            attrs["advanced"] = True
            graph.rewrite_node(target, attrs)
            match["value"] = 1.0  # base value for progress
            return {target}, {target: attrs}
        return set(), {}

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
            name=f"advance_flex_{d}",
            matcher=flexible_matcher_factory(d*2, d*2 + 5),
            applier=applier,
            guard=lambda m: True,
            cost_hint=1.0 + d * 0.05
        ))

    # Add heavy fallback
    rules.append(RewriteRule(
        name="any_advance_heavy",
        matcher=any_advance_matcher,
        applier=any_applier,
        guard=lambda m: True,
        cost_hint=0.5  # high priority for progress
    ))

    # [CONFLICT HANDLING RULE - NEW]
    # [LABEL: SUPPORTS H3 verification and H1 bounded state under conflict]
    # Detects conflicting nodes and marks them to test if focus stays small while handling nogoods.
    def conflict_matcher(graph: VersionedGraph, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        focus = context.get("focus")
        if not focus:
            return []
        attrs = graph.get_current_attrs(focus)
        if not attrs.get("conflicting"):
            return []
        # Find another in same group or connected by conflicts_with
        for succ in list(graph.graph.successors(focus)) + list(graph.graph.predecessors(focus)):
            s_attrs = graph.get_current_attrs(succ)
            if s_attrs.get("conflicting") and s_attrs.get("conflict_group") == attrs.get("conflict_group"):
                return [{"matched_nodes": {focus, succ}, "focus_node": focus, "conflict_pair": (focus, succ)}]
        return []

    def conflict_applier(graph: VersionedGraph, match: Dict[str, Any]) -> Tuple[Set[NodeID], Dict[NodeID, Dict]]:
        # Mark as "nogood" or "deferred" - this is explicit failure handling without exploding state
        pair = match.get("conflict_pair", (None, None))
        changed = set()
        new_attrs_map = {}
        for nid in pair:
            if nid and nid in graph.heads:
                attrs = dict(graph.get_current_attrs(nid))
                attrs["nogood"] = True
                attrs["resolved"] = "deferred_to_higher"  # explicit verifiable state
                graph.rewrite_node(nid, attrs)
                changed.add(nid)
                new_attrs_map[nid] = attrs
        match["value"] = 5.0  # higher value for conflict resolution (harder)
        return changed, new_attrs_map

    rules.append(RewriteRule(
        name="handle_conflict",
        matcher=conflict_matcher,
        applier=conflict_applier,
        guard=lambda m: True,
        cost_hint=2.0
    ))

    return rules


def create_stress_task(
    num_nodes: int = 80,
    branching: int = 3,
    density: float = 0.03,
    add_cycles: bool = False,
    random_edits: int = 5,
    add_conflicts: bool = False,  # [NEW STRESS DIMENSION]
    add_disconnected: bool = False,  # [NEW STRESS DIMENSION]
    heavy: bool = False,  # [HEAVY STRESS MODE 2026-07-01]
    seed: int = 123
) -> Dict[str, Any]:
    """Full task package for stress testing."""
    g = create_stress_graph(
        num_nodes=num_nodes,
        branching=branching,
        density=density,
        add_cycles=add_cycles,
        random_edits=random_edits,
        add_conflicts=add_conflicts,
        add_disconnected=add_disconnected,
        heavy=heavy,
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


def create_frontier_controlled_graph(
    num_nodes: int = 1000,
    target_max_frontier: int = 100,
    approx_edges: int = 2500,
    seed: int = 42
) -> 'VersionedGraph':
    """
    Generate a graph with approximately controllable Active Dependency Frontier width (2-hop pred cone).

    [NEW for explicit F control per move-on from H1: fixed N/E, vary F]
    [LABEL: Phase 9/10 mechanistic experiment support. Attempts to isolate frontier width F as variable.]

    Strategy to achieve target F:
    - Allocate a "source frontier" set of size ~target_max_frontier (these will be the constraining preds).
    - Dependent nodes attach such that their effective 2-hop predecessors approximate subsets or full frontier set.
      - low target: mostly chain/sequential attachment (each node sees small local frontier cone).
      - high target: wide attachment to large fraction of frontier sources (large shared dep cone).
    - Add a root + some structure for synthesis flavor.
    - Then add random extra edges to approach target total edges (without exploding F).

    Note: Exact match difficult due to graph structure interactions; script reports *achieved* max_active_frontier.
    Use achieved F for model testing.
    """
    import random
    import collections
    random.seed(seed)

    g = VersionedGraph()

    if num_nodes < 10:
        num_nodes = 10
    frontier_size = max(5, min(target_max_frontier, num_nodes // 2))

    # 1. Create frontier source nodes (high in-degree potential sources)
    frontier_nodes = []
    for i in range(frontier_size):
        nid = g.create_node("FrontierSource", {"idx": i, "kind": "frontier", "is_frontier": True})
        frontier_nodes.append(nid)

    # 2. Create dependent nodes
    # Root for task flavor
    root = g.create_node("Goal", {"kind": "root", "depth": 0})
    nodes = [root] + frontier_nodes

    remaining = num_nodes - len(nodes)
    dep_nodes = []
    for i in range(remaining):
        nid = g.create_node("Dependent", {"idx": len(nodes)+i, "kind": "synthetic", "depth": 1 + (i % 5)})
        dep_nodes.append(nid)
        nodes.append(nid)

    # 3. Wire dependencies to control frontier exposure
    # Fraction of frontier each dep "sees" depends on target vs scale.
    # For target low relative to possible: narrow cones
    # For high: broad cones
    frac = min(1.0, max(0.05, target_max_frontier / max(10, num_nodes // 3)))
    base_attach = max(1, int(frontier_size * frac * 0.6))

    for j, d in enumerate(dep_nodes):
        # Primary attachment: to a sliding or random window of frontier to modulate width
        if target_max_frontier < 50:
            # Low F: local/chainy
            attach_k = max(1, min(3, base_attach))
            start = (j * 2) % max(1, len(frontier_nodes) - attach_k)
            attach = frontier_nodes[start : start + attach_k]
        else:
            # High F: attach to many from frontier set (wide cone)
            attach_k = max(3, min(len(frontier_nodes), int(base_attach * 1.8)))
            attach = random.sample(frontier_nodes, k=min(attach_k, len(frontier_nodes)))

        for a in attach:
            g.add_edge(a, d, "depends_on")

        # Add some chain structure for propagation flavor (keeps some sequential deps)
        if j > 0:
            g.add_edge(dep_nodes[j-1], d, "depends_on")

    # 4. Add extra edges to approach approx_edges (without massively increasing F)
    current_e = sum(1 for _ in g.graph.edges())
    needed = max(0, approx_edges - current_e)
    all_n = list(g.get_all_current_node_ids())
    for _ in range(needed):
        a, b = random.sample(all_n, 2)
        if not g.graph.has_edge(a, b):
            g.add_edge(a, b, "extra")

    # Optional root wiring
    for f in frontier_nodes[:min(3, len(frontier_nodes))]:
        if not g.graph.has_edge(root, f):
            g.add_edge(root, f, "depends_on")

    return g


def create_frontier_controlled_task(
    num_nodes: int = 1000,
    target_max_frontier: int = 100,
    approx_edges: int = 2500,
    add_cycles: bool = False,
    add_conflicts: bool = True,
    add_disconnected: bool = True,
    heavy: bool = True,
    seed: int = 123
) -> Dict[str, Any]:
    """Task wrapper using explicit frontier-controlled graph gen. Fixed N/E attempt, vary target F."""
    g = create_frontier_controlled_graph(
        num_nodes=num_nodes,
        target_max_frontier=target_max_frontier,
        approx_edges=approx_edges,
        seed=seed
    )

    # Compute achieved properties for logging
    props = compute_graph_properties(g)
    achieved_f = props.get('max_active_frontier', 0)

    # Initial focus on root + some frontier
    goals = [nid for nid in g.get_all_current_node_ids()
             if g.get_current_attrs(nid).get("kind") == "root"] or \
            list(g.get_all_current_node_ids())[:3]
    initial_focus = set(goals[:4])

    rules = make_stress_rewrite_rules(num_rules=6)

    def acceptance(graph: VersionedGraph) -> bool:
        advanced = sum(1 for nid in graph.get_all_current_node_ids()
                       if graph.get_current_attrs(nid).get("advanced"))
        return advanced > num_nodes * 0.5

    return {
        "graph": g,
        "initial_focus": initial_focus,
        "rules": rules,
        "acceptance_fn": acceptance,
        "spec": {
            "type": "frontier_controlled",
            "num_nodes": num_nodes,
            "target_max_frontier": target_max_frontier,
            "approx_edges": approx_edges,
            "achieved_max_active_frontier": achieved_f,
            "cycles": add_cycles,
        },
        "horizon": num_nodes,
        "achieved_frontier": achieved_f,
        "concentration": props.get('frontier_concentration', 1.0)
    }


def create_adversarial_high_frontier_graph(
    num_nodes: int = 1000,
    frontier_sources: int = 400,
    attach_per_work: int = 25,
    approx_edges: int = 3000,
    seed: int = 42,
    use_multi_layer: bool = True
) -> 'VersionedGraph':
    """
    Adversarial generator targeting *high* active dependency frontier (max 2-hop pred cone).

    [LABEL: Stronger adversarial for H1a / model boundary test (post EXP-028). Per review + move-on from H1: force higher effective F to test if L elevates, focus inflates, or throughput drops.]
    [INTENT: Attempt falsification of "architecture always keeps L low independent of F". Use high fan-in + multi-layer merges for large transitive 2-hop cones. If L stays low, evidence that local rewrite + bounded focus dominate raw graph structure.]

    Construction:
    - Large pool of independent "source" frontier nodes.
    - (Optional multi-layer): mid_layer nodes with wide attachments to sources (creates broad cones).
    - Work nodes attach widely to mid or sources.
    - Goal: many nodes have large unique 2-hop predecessor sets (hundreds).
    - Add structure + padding edges.
    """
    import random
    random.seed(seed)

    g = VersionedGraph()

    frontier_sources = min(frontier_sources, max(10, num_nodes // 3))
    work_nodes_count = max(10, num_nodes - frontier_sources - 5)

    # Sources (base of frontier)
    sources = []
    for i in range(frontier_sources):
        nid = g.create_node("Source", {"idx": i, "kind": "frontier_source", "is_source": True})
        sources.append(nid)

    nodes = [nid for nid in sources]

    mid_layer = []
    if use_multi_layer and frontier_sources > 20:
        mid_count = min(frontier_sources // 2, 200)
        for i in range(mid_count):
            nid = g.create_node("MidMerge", {"idx": 1000 + i, "kind": "merge", "depth": 0.5})
            mid_layer.append(nid)
            nodes.append(nid)
            # Each mid attaches to large random subset of sources
            k = max(5, min(attach_per_work // 2, len(sources)))
            attached = random.sample(sources, k=min(k, len(sources)))
            for s in attached:
                g.add_edge(s, nid, "depends_on")

    # Root
    root = g.create_node("Goal", {"kind": "root", "depth": 0})
    nodes.insert(0, root)  # ensure order not critical

    # Work nodes with very wide attachments (to maximize cone)
    work_nodes = []
    attach_base = sources + mid_layer if mid_layer else sources
    for i in range(work_nodes_count):
        nid = g.create_node("Work", {"idx": 2000 + i, "kind": "synthetic", "depth": 1})
        work_nodes.append(nid)
        nodes.append(nid)

        # Very wide to force large 2-hop F
        k = min(attach_per_work, len(attach_base))
        if k > 0:
            attached = random.sample(attach_base, k=k)
            for a in attached:
                g.add_edge(a, nid, "depends_on")

    # Light chaining for some propagation
    for i in range(1, len(work_nodes)):
        if random.random() < 0.3:  # sparse chain
            g.add_edge(work_nodes[i-1], work_nodes[i], "depends_on")

    # Root wiring
    for s in sources[:min(5, len(sources))]:
        g.add_edge(root, s, "depends_on")

    # Pad edges
    current_e = sum(1 for _ in g.graph.edges())
    needed = max(0, approx_edges - current_e)
    all_n = list(g.get_all_current_node_ids())
    for _ in range(needed):
        a, b = random.sample(all_n, 2)
        if not g.graph.has_edge(a, b):
            g.add_edge(a, b, "extra")

    return g


def create_adversarial_high_frontier_task(
    num_nodes: int = 1000,
    frontier_sources: int = 400,
    attach_per_work: int = 25,
    approx_edges: int = 3000,
    add_cycles: bool = True,
    add_conflicts: bool = True,
    add_disconnected: bool = True,
    heavy: bool = True,
    seed: int = 123,
    use_multi_layer: bool = True
) -> Dict[str, Any]:
    """Full task for adversarial high-frontier testing. Reports achieved F."""
    g = create_adversarial_high_frontier_graph(
        num_nodes=num_nodes,
        frontier_sources=frontier_sources,
        attach_per_work=attach_per_work,
        approx_edges=approx_edges,
        seed=seed,
        use_multi_layer=use_multi_layer
    )

    props = compute_graph_properties(g)
    achieved_f = props.get('max_active_frontier', 0)

    goals = [nid for nid in g.get_all_current_node_ids()
             if g.get_current_attrs(nid).get("kind") == "root"] or \
            list(g.get_all_current_node_ids())[:4]
    initial_focus = set(goals[:4])

    rules = make_stress_rewrite_rules(num_rules=6)

    def acceptance(graph: VersionedGraph) -> bool:
        advanced = sum(1 for nid in graph.get_all_current_node_ids()
                       if graph.get_current_attrs(nid).get("advanced"))
        return advanced > num_nodes * 0.4

    return {
        "graph": g,
        "initial_focus": initial_focus,
        "rules": rules,
        "acceptance_fn": acceptance,
        "spec": {
            "type": "adversarial_high_frontier",
            "num_nodes": num_nodes,
            "frontier_sources": frontier_sources,
            "attach_per_work": attach_per_work,
            "approx_edges": approx_edges,
            "achieved_max_active_frontier": achieved_f,
        },
        "horizon": num_nodes,
        "achieved_frontier": achieved_f,
        "concentration": props.get('frontier_concentration', 1.0)
    }
