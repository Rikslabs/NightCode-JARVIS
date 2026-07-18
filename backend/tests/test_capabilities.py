"""Comprehensive tests for Capability Graph system."""

from datetime import datetime, timezone

from app.capabilities.models import (
    Capability, CapabilityEdge, CapabilityNode, CapabilityGroup,
    CapabilityMatch, CapabilityResult, CapabilityMetadata, RiskLevel, EdgeType
)
from app.capabilities.taxonomy import CapabilityCategory, CapabilityTaxonomy
from app.capabilities.graph import CapabilityGraph
from app.capabilities.registry import CapabilityRegistry
from app.capabilities.matcher import CapabilityMatcher
from app.capabilities.resolver import CapabilityResolver
from app.capabilities.builder import CapabilityBuilder
from app.capabilities.analyzer import CapabilityAnalyzer


# ============================================
# Model Tests
# ============================================

class TestCapabilityMetadata:
    def test_create_metadata(self):
        metadata = CapabilityMetadata(
            name="test_capability",
            description="Test capability",
            category="testing",
            provider="test_tool",
        )
        assert metadata.name == "test_capability"
        assert metadata.risk_level == RiskLevel.LOW

    def test_to_dict(self):
        metadata = CapabilityMetadata(
            name="test",
            description="desc",
            category="cat",
            provider="prov",
            required_inputs=["input1"],
        )
        result = metadata.to_dict()
        assert result["name"] == "test"
        assert "created_at" in result


class TestCapability:
    def test_create_capability(self):
        metadata = CapabilityMetadata(
            name="test", description="test", category="cat", provider="prov"
        )
        cap = Capability(id="test_id", metadata=metadata, tags=["tag1"])
        assert cap.id == "test_id"
        assert "tag1" in cap.tags


class TestCapabilityEdge:
    def test_create_edge(self):
        edge = CapabilityEdge(
            source_id="source", target_id="target", edge_type=EdgeType.DEPENDS_ON
        )
        assert edge.source_id == "source"
        assert edge.weight == 1.0


# ============================================
# Taxonomy Tests
# ============================================

class TestCapabilityCategory:
    def test_get_all_categories(self):
        cats = CapabilityCategory.get_all_categories()
        assert "engineering" in cats
        assert "planning" in cats
        assert "editing" in cats

    def test_get_subcategories(self):
        subcats = CapabilityCategory.get_subcategories("engineering")
        assert "engineering/code_review" in subcats

    def test_is_valid_category(self):
        assert CapabilityCategory.is_valid_category("engineering")
        assert CapabilityCategory.is_valid_category("engineering/code_review")


class TestCapabilityTaxonomy:
    def test_get_subcategories(self):
        taxonomy = CapabilityTaxonomy()
        subcats = taxonomy.get_subcategories("planning")
        assert len(subcats) > 0

    def test_is_valid(self):
        taxonomy = CapabilityTaxonomy()
        assert taxonomy.is_valid("editing")


# ============================================
# CapabilityGraph Tests
# ============================================

class TestCapabilityGraph:
    def test_add_and_get_capability(self):
        graph = CapabilityGraph()
        metadata = CapabilityMetadata(name="test", description="test", category="cat", provider="prov")
        cap = Capability(id="test_id", metadata=metadata)
        graph.add_capability(cap)

        result = graph.get_capability("test_id")
        assert result is not None
        assert result.id == "test_id"

    def test_add_edge(self):
        graph = CapabilityGraph()
        metadata = CapabilityMetadata(name="test", description="test", category="cat", provider="prov")
        cap1 = Capability(id="cap1", metadata=metadata)
        cap2 = Capability(id="cap2", metadata=metadata)
        graph.add_capability(cap1)
        graph.add_capability(cap2)

        edge = CapabilityEdge(source_id="cap1", target_id="cap2", edge_type=EdgeType.DEPENDS_ON)
        graph.add_edge(edge)

        assert len(graph._edges) == 1


# ============================================
# CapabilityRegistry Tests
# ============================================

class TestCapabilityRegistry:
    def test_register_and_get(self):
        registry = CapabilityRegistry()
        metadata = CapabilityMetadata(name="test", description="test", category="cat", provider="prov")
        registry.register("test_id", metadata)

        cap = registry.get("test_id")
        assert cap is not None

    def test_get_by_category(self):
        registry = CapabilityRegistry()
        m1 = CapabilityMetadata(name="n1", description="d1", category="planning", provider="p1")
        m2 = CapabilityMetadata(name="n2", description="d2", category="planning/sprint", provider="p2")
        registry.register("c1", m1)
        registry.register("c2", m2)

        results = registry.get_by_category("planning")
        assert len(results) == 2


# ============================================
# CapabilityMatcher Tests
# ============================================

class TestCapabilityMatcher:
    def test_match_returns_results(self):
        registry = CapabilityRegistry()
        m = CapabilityMetadata(name="review", description="Code review capability", category="engineering/code_review", provider="review")
        registry.register("review_cap", m)

        matcher = CapabilityMatcher(registry)
        matches = matcher.match("review project")
        assert len(matches) > 0

    def test_match_empty_registry(self):
        matcher = CapabilityMatcher()
        matches = matcher.match("test goal")
        assert len(matches) == 0


# ============================================
# CapabilityResolver Tests
# ============================================

class TestCapabilityResolver:
    def test_resolve_returns_result(self):
        registry = CapabilityRegistry()
        m = CapabilityMetadata(name="review", description="test", category="engineering/code_review", provider="review_tool")
        registry.register("review_cap", m)

        matcher = CapabilityMatcher(registry)
        resolver = CapabilityResolver(matcher=matcher)
        result = resolver.resolve("review code")

        assert result.tool_name == "review_tool"


# ============================================
# CapabilityBuilder Tests
# ============================================

class TestCapabilityBuilder:
    def test_build_empty(self):
        builder = CapabilityBuilder()
        graph = builder.build({})
        assert len(graph._nodes) == 0


# ============================================
# CapabilityAnalyzer Tests
# ============================================

class TestCapabilityAnalyzer:
    def test_coverage_report(self):
        registry = CapabilityRegistry()
        m = CapabilityMetadata(name="n1", description="d1", category="planning", provider="p1")
        registry.register("c1", m)

        analyzer = CapabilityAnalyzer(registry=registry)
        report = analyzer.generate_coverage_report()

        assert report["total_capabilities"] == 1
        assert "planning" in report["by_category"]

    def test_find_duplicates(self):
        registry = CapabilityRegistry()
        m1 = CapabilityMetadata(name="duplicate", description="d1", category="cat", provider="p1")
        registry.register("c1", m1)

        analyzer = CapabilityAnalyzer(registry=registry)
        dups = analyzer.find_duplicates()
        assert len(dups) == 0


# ============================================
# Integration Tests
# ============================================

class TestCapabilitiesIntegration:
    def test_full_flow(self):
        # Build registry
        registry = CapabilityRegistry()
        m = CapabilityMetadata(
            name="review_project",
            description="Review entire project",
            category="engineering/code_review",
            provider="review",
        )
        registry.register("review_proj", m)

        # Build graph
        graph = CapabilityGraph()
        cap = registry.get("review_proj")
        if cap:
            graph.add_capability(cap)

        # Match
        matcher = CapabilityMatcher(registry)
        matches = matcher.match("review project code")
        assert len(matches) > 0

        # Resolve
        resolver = CapabilityResolver(graph=graph, matcher=matcher)
        result = resolver.resolve("review project")
        assert result.tool_name == "review"