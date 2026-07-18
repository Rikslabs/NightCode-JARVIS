"""Capability Analyzer - generates reports about capabilities."""

from typing import Any, Dict, List, Optional

from .graph import CapabilityGraph
from .models import RiskLevel
from .registry import CapabilityRegistry


class CapabilityAnalyzer:
    """
    Analyzes capability coverage and relationships.
    """

    def __init__(self, graph: Optional[CapabilityGraph] = None, registry: Optional[CapabilityRegistry] = None):
        """Initialize with graph and registry for DI."""
        self._graph = graph or CapabilityGraph()
        self._registry = registry or CapabilityRegistry()

    def generate_coverage_report(self) -> Dict[str, Any]:
        """
        Generate a coverage report of all capabilities.

        Returns:
            Dictionary with coverage statistics.
        """
        capabilities = self._registry.get_all_capabilities()

        by_category: Dict[str, int] = {}
        by_provider: Dict[str, int] = {}
        by_risk: Dict[str, int] = {}

        for cap in capabilities.values():
            cat = cap.metadata.category
            by_category[cat] = by_category.get(cat, 0) + 1

            provider = cap.metadata.provider
            by_provider[provider] = by_provider.get(provider, 0) + 1

            risk = cap.metadata.risk_level.value
            by_risk[risk] = by_risk.get(risk, 0) + 1

        return {
            "total_capabilities": len(capabilities),
            "by_category": by_category,
            "by_provider": by_provider,
            "by_risk_level": by_risk,
            "categories_without_capabilities": self._find_empty_categories(by_category),
        }

    def _find_empty_categories(self, by_category: Dict[str, int]) -> List[str]:
        """Find categories that have no capabilities."""
        from .taxonomy import CapabilityCategory

        all_categories = CapabilityCategory.get_all_categories()
        empty = []
        for cat in all_categories:
            has_subcat = any(sc.startswith(cat + "/") for sc in by_category)
            has_direct = cat in by_category
            if not has_direct and not has_subcat:
                empty.append(cat)
        return empty

    def find_duplicates(self) -> List[Dict[str, Any]]:
        """
        Find duplicate or overlapping capabilities.

        Returns:
            List of duplicate capability info.
        """
        capabilities = self._registry.get_all_capabilities()
        duplicates = []

        seen_names = {}
        for cap_id, cap in capabilities.items():
            name = cap.metadata.name
            if name in seen_names:
                duplicates.append({
                    "name": name,
                    "first_id": seen_names[name],
                    "duplicate_id": cap_id,
                })
            else:
                seen_names[name] = cap_id

        return duplicates

    def find_missing_providers(self) -> List[str]:
        """
        Find capabilities with missing provider tools.

        Returns:
            List of capability IDs with missing providers.
        """
        # This would require access to the actual tool registry
        # For now, return empty list
        return []

    def analyze_graph(self) -> Dict[str, Any]:
        """
        Analyze graph structure.

        Returns:
            Dictionary with graph analysis.
        """
        total_nodes = len(self._graph._nodes)
        total_edges = len(self._graph._edges)

        # Count edges by type
        edge_types: Dict[str, int] = {}
        for edge in self._graph._edges:
            et = edge.edge_type.value
            edge_types[et] = edge_types.get(et, 0) + 1

        # Find orphaned capabilities
        orphaned = []
        for node_id in self._graph._nodes:
            has_deps = any(e.source_id == node_id or e.target_id == node_id for e in self._graph._edges)
            if not has_deps:
                orphaned.append(node_id)

        return {
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "edge_types": edge_types,
            "orphaned_capabilities": orphaned,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert analyzer results to dictionary."""
        return {
            "coverage": self.generate_coverage_report(),
            "duplicates": self.find_duplicates(),
            "graph_analysis": self.analyze_graph(),
        }