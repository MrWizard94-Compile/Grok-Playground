"""
Core data structures for EP-GRM simulator.

Follows Phase 6 plan in iterations/001/phase6-implementation-planning.md

Computational Model:
- Versioned directed attributed multigraph.
- Nodes have id, type, attrs, version.
- Rewrites create new versions (immutable snapshots).

All state transitions must be explicit and deterministic.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
import networkx as nx
import copy
import time
import uuid


NodeID = str
VersionID = int
RuleName = str


@dataclass(frozen=True)
class NodeVersion:
    """Immutable snapshot of a node at a particular version."""
    version: VersionID
    node_type: str
    attrs: Dict[str, Any] = field(default_factory=dict)
    # For simplicity in sim: we don't duplicate full graph edges per version here.
    # Edges are managed at the VersionedGraph level with head tracking.


@dataclass
class VersionedGraph:
    """
    Primary persistent representation (the "backing store" in simulation).

    - Uses networkx.MultiDiGraph for current heads.
    - Maintains full version history per logical node.
    - Movement accounting is done by the Simulator when it "loads" nodes.
    """
    graph: nx.MultiDiGraph = field(default_factory=nx.MultiDiGraph)
    # logical_node_id -> list of NodeVersion (index = version)
    versions: Dict[NodeID, List[NodeVersion]] = field(default_factory=dict)
    # logical_node_id -> current head version number
    heads: Dict[NodeID, VersionID] = field(default_factory=dict)
    next_version: VersionID = 0

    def create_node(self, node_type: str, attrs: Optional[Dict[str, Any]] = None,
                    node_id: Optional[NodeID] = None) -> NodeID:
        """Create a new logical node. Returns its ID. Initial version 0."""
        if node_id is None:
            node_id = f"n_{uuid.uuid4().hex[:12]}"
        if node_id in self.heads:
            raise ValueError(f"Node {node_id} already exists")

        attrs = attrs or {}
        v0 = NodeVersion(version=0, node_type=node_type, attrs=copy.deepcopy(attrs))

        self.versions[node_id] = [v0]
        self.heads[node_id] = 0

        # Add to graph with current attrs for easy traversal
        self.graph.add_node(node_id, type=node_type, **attrs, _version=0)
        return node_id

    def add_edge(self, src: NodeID, dst: NodeID, label: str, **edge_attrs: Any) -> None:
        """Add a labeled edge between current heads."""
        if src not in self.heads or dst not in self.heads:
            raise ValueError("Both src and dst must exist")
        self.graph.add_edge(src, dst, key=label, label=label, **edge_attrs)

    def get_current_attrs(self, node_id: NodeID) -> Dict[str, Any]:
        """Return a copy of current head attrs (for matching / focus)."""
        if node_id not in self.heads:
            raise KeyError(node_id)
        data = self.graph.nodes[node_id]
        return {k: v for k, v in data.items() if not k.startswith('_')}

    def get_node_version(self, node_id: NodeID, version: Optional[VersionID] = None) -> NodeVersion:
        """Retrieve a specific (or head) version snapshot."""
        if node_id not in self.versions:
            raise KeyError(node_id)
        if version is None:
            version = self.heads[node_id]
        return self.versions[node_id][version]

    def _bump_version(self, node_id: NodeID, new_attrs: Dict[str, Any]) -> VersionID:
        """Internal: create new version for node and update head + graph node."""
        versions = self.versions[node_id]
        new_ver = len(versions)
        snapshot = NodeVersion(
            version=new_ver,
            node_type=versions[0].node_type,
            attrs=copy.deepcopy(new_attrs)
        )
        versions.append(snapshot)
        self.heads[node_id] = new_ver

        # Update live graph view
        for k in list(self.graph.nodes[node_id].keys()):
            if not k.startswith('_'):
                del self.graph.nodes[node_id][k]
        self.graph.nodes[node_id].update(new_attrs)
        self.graph.nodes[node_id]['_version'] = new_ver
        self.graph.nodes[node_id]['type'] = snapshot.node_type

        self.next_version = max(self.next_version, new_ver + 1)
        return new_ver

    def rewrite_node(self, node_id: NodeID, new_attrs: Dict[str, Any],
                     parent_version: Optional[VersionID] = None) -> VersionID:
        """
        Create a new version of the node with updated attrs.
        This models a local rewrite mutation.
        """
        if node_id not in self.heads:
            raise KeyError(node_id)
        current_ver = self.heads[node_id]
        if parent_version is not None and parent_version != current_ver:
            # In full system we might support branching; for MVP we require head
            pass
        return self._bump_version(node_id, new_attrs)

    def size_estimate(self, node_id: NodeID) -> int:
        """Crude byte proxy for movement accounting."""
        attrs = self.get_current_attrs(node_id)
        # Very rough: 1 byte per char in str(repr) + overhead
        return len(str(attrs)) + 32

    def get_all_current_node_ids(self) -> Set[NodeID]:
        return set(self.heads.keys())

    def clone(self) -> "VersionedGraph":
        """Deep copy for checkpointing (expensive; use sparingly)."""
        new_g = VersionedGraph()
        new_g.graph = self.graph.copy()
        new_g.versions = copy.deepcopy(self.versions)
        new_g.heads = self.heads.copy()
        new_g.next_version = self.next_version
        return new_g


@dataclass
class FocusSet:
    """Bounded executive focus. Explicitly size-limited."""
    members: Set[NodeID] = field(default_factory=set)
    max_size: int = 64
    metadata: Dict[NodeID, Dict[str, Any]] = field(default_factory=dict)

    def add(self, node_id: NodeID, meta: Optional[Dict[str, Any]] = None) -> bool:
        if len(self.members) >= self.max_size and node_id not in self.members:
            return False  # Bound would be violated
        self.members.add(node_id)
        if meta:
            self.metadata[node_id] = meta
        return True

    def remove(self, node_id: NodeID) -> None:
        self.members.discard(node_id)
        self.metadata.pop(node_id, None)

    def evict_lowest_priority(self) -> Optional[NodeID]:
        """Simple policy: arbitrary for MVP. Real impl would use scores."""
        if not self.members:
            return None
        victim = next(iter(self.members))  # Deterministic in insertion? Not guaranteed.
        self.remove(victim)
        return victim

    def __len__(self) -> int:
        return len(self.members)

    def is_full(self) -> bool:
        return len(self) >= self.max_size


@dataclass
class RewriteRule:
    """Declarative rewrite rule. LHS pattern is matched against graph neighborhood."""
    name: RuleName
    # For MVP: we use a simple predicate matcher (callable)
    # In later iteration: more declarative or networkx iso matcher
    matcher: Any  # callable(graph, focus_node, ...) -> list of matches
    applier: Any  # callable(graph, match) -> (changed_nodes, new_attrs_map)
    guard: Any = None  # optional callable(match) -> bool
    cost_hint: float = 1.0

    def matches(self, graph: VersionedGraph, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Return list of match dicts."""
        if callable(self.matcher):
            return self.matcher(graph, context)
        return []

    def apply(self, graph: VersionedGraph, match: Dict[str, Any]) -> Tuple[Set[NodeID], Dict[NodeID, Dict]]:
        if callable(self.applier):
            return self.applier(graph, match)
        return set(), {}


# Simple example rule matchers / appliers can be defined in task or experiment code.
