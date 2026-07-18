"""Capability Builder - auto-builds capability graph from Tool Registry."""

from typing import Any, Dict, List, Optional

from .graph import CapabilityGraph
from .models import Capability, CapabilityEdge, CapabilityMetadata, RiskLevel
from .registry import CapabilityRegistry
from .taxonomy import CapabilityCategory


class CapabilityBuilder:
    """
    Builds capability graph from existing Tool Registry.

    Only reads from Tool Registry - does not modify it.
    """

    def __init__(
        self,
        tool_registry: Optional[Dict[str, Any]] = None,
        capability_registry: Optional[CapabilityRegistry] = None,
    ):
        """Initialize with tool registry and capability registry for DI."""
        self._tool_registry = tool_registry
        self._capability_registry = capability_registry or CapabilityRegistry()

    def build(self, tool_registry: Optional[Dict[str, Any]] = None) -> CapabilityGraph:
        """
        Build capability graph from tool registry.

        Args:
            tool_registry: Tool registry dict (optional, uses injected if not provided).

        Returns:
            CapabilityGraph populated with capabilities from tools.
        """
        registry = tool_registry or self._tool_registry
        graph = CapabilityGraph()

        if not registry:
            return graph

        for tool_name, tool in registry.items():
            capabilities = self._extract_capabilities_from_tool(tool_name, tool)
            for capability in capabilities:
                self._capability_registry.register(capability.id, capability.metadata)
                graph.add_capability(capability)

        # Build relationships between capabilities
        self._build_graph_relationships(graph)

        return graph

    def _extract_capabilities_from_tool(
        self, tool_name: str, tool: Any
    ) -> List[Capability]:
        """Extract capabilities from a tool."""
        capabilities = []

        # Map tool names to capability categories
        category_map = {
            "review": CapabilityCategory.CODE_REVIEW,
            "planning": CapabilityCategory.PLANNING,
            "coding": CapabilityCategory.ENGINEERING,
            "knowledge": CapabilityCategory.KNOWLEDGE,
            "workflow": CapabilityCategory.WORKFLOW,
            "memory": CapabilityCategory.MEMORY,
            "system": CapabilityCategory.SYSTEM,
        }

        category = category_map.get(tool_name, CapabilityCategory.FUTURE)

        # Create capability from tool
        metadata = CapabilityMetadata(
            name=tool_name,
            description=tool.description or f"{tool_name} tool capability",
            category=category,
            provider=tool_name,
            required_inputs=list(tool.parameters.keys()),
            outputs=["success", "data"],
            risk_level=RiskLevel.LOW,
        )

        capability = Capability(id=f"{tool_name}_capability", metadata=metadata)
        capabilities.append(capability)

        return capabilities

    def _build_graph_relationships(self, graph: CapabilityGraph) -> None:
        """Build dependency relationships between capabilities."""
        # Example relationships based on tool interactions
        relationships = [
            # Review might depend on project index
            ("review_capability", "coding_capability", "depends_on"),
            # Planning might depend on review
            ("planning_capability", "review_capability", "requires"),
            # Editing might depend on review
            ("editing_capability", "review_capability", "extends"),
        ]

        for source, target, edge_type in relationships:
            if source in graph._nodes and target in graph._nodes:
                edge = CapabilityEdge(
                    source_id=source,
                    target_id=target,
                    edge_type=edge_type,
                )
                graph.add_edge(edge)