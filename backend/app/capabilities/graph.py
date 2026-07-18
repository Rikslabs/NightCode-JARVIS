"""Capability Graph - represents relationships between capabilities."""

from typing import Any, Dict, List, Optional

from .models import Capability, CapabilityEdge, CapabilityNode, EdgeType


class CapabilityGraph:
    """
    Graph representation of capabilities and their relationships.

    Supports parent/child relationships and arbitrary capability connections.
    """

    def __init__(self):
        self._nodes: Dict[str, CapabilityNode] = {}
        self._edges: List[CapabilityEdge] = []

    def add_capability(self, capability: Capability) -> None:
        """Add a capability to the graph as a node."""
        self._nodes[capability.id] = CapabilityNode(
            capability_id=capability.id, capability=capability
        )

    def add_edge(self, edge: CapabilityEdge) -> None:
        """Add an edge between two capabilities."""
        self._edges.append(edge)

    def get_capability(self, capability_id: str) -> Optional[Capability]:
        """Get a capability by its ID."""
        node = self._nodes.get(capability_id)
        return node.capability if node else None

    def get_node(self, capability_id: str) -> Optional[CapabilityNode]:
        """Get a node by capability ID."""
        return self._nodes.get(capability_id)

    def get_dependencies(self, capability_id: str) -> List[Capability]:
        """Get all capabilities that this capability depends on."""
        dependencies = []
        for edge in self._edges:
            if edge.source_id == capability_id and edge.edge_type in (
                EdgeType.DEPENDS_ON,
                EdgeType.REQUIRES,
            ):
                dep = self.get_capability(edge.target_id)
                if dep:
                    dependencies.append(dep)
        return dependencies

    def get_dependents(self, capability_id: str) -> List[Capability]:
        """Get all capabilities that depend on this one."""
        dependents = []
        for edge in self._edges:
            if edge.target_id == capability_id and edge.edge_type in (
                EdgeType.DEPENDS_ON,
                EdgeType.REQUIRES,
            ):
                dep = self.get_capability(edge.source_id)
                if dep:
                    dependents.append(dep)
        return dependents

    def get_related(self, capability_id: str) -> List[Capability]:
        """Get all capabilities related to this one."""
        related = []
        for edge in self._edges:
            if edge.source_id == capability_id and edge.edge_type == EdgeType.RELATED_TO:
                sibling = self.get_capability(edge.target_id)
                if sibling:
                    related.append(sibling)
        return related

    def get_all_capabilities(self) -> List[Capability]:
        """Get all capabilities in the graph."""
        return [node.capability for node in self._nodes.values()]

    def get_capabilities_by_category(self, category: str) -> List[Capability]:
        """Get all capabilities in a category."""
        return [
            node.capability
            for node in self._nodes.values()
            if node.capability.metadata.category == category
            or node.capability.metadata.category.startswith(category + "/")
        ]

    def to_dict(self) -> Dict[str, Any]:
        """Convert graph to dictionary representation."""
        return {
            "nodes": {k: v.to_dict() for k, v in self._nodes.items()},
            "edges": [e.to_dict() for e in self._edges],
        }

    def get_execution_path(self, capability_id: str) -> List[str]:
        """
        Get the execution path through dependencies for a capability.

        Returns ordered list of capability IDs to execute.
        """
        visited = set()
        path = []

        def visit(node_id: str) -> None:
            if node_id in visited:
                return
            visited.add(node_id)
            # Visit dependencies first
            for edge in self._edges:
                if edge.source_id == node_id and edge.edge_type in (
                    EdgeType.DEPENDS_ON,
                    EdgeType.REQUIRES,
                ):
                    visit(edge.target_id)
            path.append(node_id)

        visit(capability_id)
        return path