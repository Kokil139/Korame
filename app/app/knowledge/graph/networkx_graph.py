"""
Graph storage using NetworkX.

Default in-memory graph implementation. For production, consider Neo4j.
"""

from typing import Optional, Any, List, Dict
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class GraphNode:
    """A node in the knowledge graph."""
    node_id: str
    label: str
    properties: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class GraphEdge:
    """An edge (relationship) in the knowledge graph."""
    source: str
    target: str
    relationship_type: str
    properties: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


class NetworkXGraph:
    """In-memory knowledge graph using adjacency lists."""

    def __init__(self):
        """Initialize the graph."""
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: Dict[str, List[GraphEdge]] = {}  # source -> list of edges

    def add_node(
        self,
        node_id: str,
        label: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> GraphNode:
        """
        Add a node to the graph.

        Args:
            node_id: Unique node ID
            label: Node label (type)
            properties: Optional properties

        Returns:
            The created node
        """
        node = GraphNode(
            node_id=node_id,
            label=label,
            properties=properties or {}
        )
        self.nodes[node_id] = node
        if node_id not in self.edges:
            self.edges[node_id] = []
        return node

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get a node by ID."""
        return self.nodes.get(node_id)

    def update_node(self, node_id: str, properties: Dict[str, Any]) -> bool:
        """
        Update node properties.

        Args:
            node_id: Node ID
            properties: Properties to update/add

        Returns:
            True if updated, False if node not found
        """
        if node_id not in self.nodes:
            return False

        node = self.nodes[node_id]
        node.properties.update(properties)
        node.updated_at = datetime.utcnow()
        return True

    def delete_node(self, node_id: str) -> bool:
        """
        Delete a node and all its edges.

        Args:
            node_id: Node ID

        Returns:
            True if deleted, False if not found
        """
        if node_id not in self.nodes:
            return False

        # Delete outgoing edges
        if node_id in self.edges:
            del self.edges[node_id]

        # Delete incoming edges
        for source_id in list(self.edges.keys()):
            self.edges[source_id] = [
                e for e in self.edges[source_id]
                if e.target != node_id
            ]

        del self.nodes[node_id]
        return True

    def add_edge(
        self,
        source: str,
        target: str,
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add an edge (relationship) between two nodes.

        Args:
            source: Source node ID
            target: Target node ID
            relationship_type: Type of relationship
            properties: Optional properties

        Returns:
            True if added, False if source or target not found
        """
        if source not in self.nodes or target not in self.nodes:
            return False

        edge = GraphEdge(
            source=source,
            target=target,
            relationship_type=relationship_type,
            properties=properties or {}
        )

        if source not in self.edges:
            self.edges[source] = []

        self.edges[source].append(edge)
        return True

    def get_edges(self, source: str) -> List[GraphEdge]:
        """Get all outgoing edges from a node."""
        return self.edges.get(source, [])

    def get_incoming_edges(self, target: str) -> List[GraphEdge]:
        """Get all incoming edges to a node."""
        incoming = []
        for edges_list in self.edges.values():
            incoming.extend([e for e in edges_list if e.target == target])
        return incoming

    def get_related_nodes(
        self,
        node_id: str,
        relationship_type: Optional[str] = None,
        max_depth: int = 1
    ) -> List[GraphNode]:
        """
        Get related nodes within a certain depth.

        Args:
            node_id: Starting node ID
            relationship_type: Filter by relationship type (None = all)
            max_depth: Maximum traversal depth

        Returns:
            List of related nodes
        """
        visited = set()
        to_visit = [(node_id, 0)]
        related = []

        while to_visit:
            current_id, depth = to_visit.pop(0)

            if current_id in visited or depth > max_depth:
                continue

            visited.add(current_id)

            # Get related nodes
            for edge in self.get_edges(current_id):
                if relationship_type and edge.relationship_type != relationship_type:
                    continue

                if edge.target not in visited:
                    related.append(self.get_node(edge.target))
                    if depth < max_depth:
                        to_visit.append((edge.target, depth + 1))

        return [n for n in related if n is not None]

    def find_path(self, source: str, target: str) -> Optional[List[str]]:
        """
        Find a path between two nodes using BFS.

        Args:
            source: Source node ID
            target: Target node ID

        Returns:
            List of node IDs forming a path, or None if no path exists
        """
        if source not in self.nodes or target not in self.nodes:
            return None

        visited = {source}
        queue = [(source, [source])]

        while queue:
            current, path = queue.pop(0)

            if current == target:
                return path

            for edge in self.get_edges(current):
                if edge.target not in visited:
                    visited.add(edge.target)
                    queue.append((edge.target, path + [edge.target]))

        return None

    def get_stats(self) -> Dict[str, int]:
        """Get graph statistics."""
        total_edges = sum(len(edges) for edges in self.edges.values())
        return {
            "nodes": len(self.nodes),
            "edges": total_edges,
            "node_types": len(set(n.label for n in self.nodes.values()))
        }

    def export(self) -> Dict[str, Any]:
        """
        Export graph as dictionary.

        Returns:
            Dictionary representation of the graph
        """
        return {
            "nodes": {
                nid: {
                    "label": n.label,
                    "properties": n.properties,
                    "created_at": n.created_at.isoformat(),
                    "updated_at": n.updated_at.isoformat()
                }
                for nid, n in self.nodes.items()
            },
            "edges": {
                source: [
                    {
                        "target": e.target,
                        "type": e.relationship_type,
                        "properties": e.properties,
                        "created_at": e.created_at.isoformat()
                    }
                    for e in edges
                ]
                for source, edges in self.edges.items()
            }
        }

