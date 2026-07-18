"""Additional tests for Capability Graph system."""

from app.capabilities.models import (
    CapabilityMetadata, RiskLevel, EdgeType,
    CapabilityMatch, CapabilityResult, CapabilityNode, CapabilityGroup,
    Capability, CapabilityEdge
)
from app.capabilities.taxonomy import CapabilityCategory, CapabilityTaxonomy
from app.capabilities.graph import CapabilityGraph
from app.capabilities.registry import CapabilityRegistry
from app.capabilities.matcher import CapabilityMatcher
from app.capabilities.resolver import CapabilityResolver
from app.capabilities.builder import CapabilityBuilder
from app.capabilities.analyzer import CapabilityAnalyzer


# ============================================
# Additional Coverage Tests
# ============================================

class TestCapabilityMetadataSerialization:
    def test_to_dict_risk_level(self):
        metadata = CapabilityMetadata(
            name="test", description="test", category="cat", provider="prov", priority=5
        )
        result = metadata.to_dict()
        assert result["risk_level"] == "low"
        assert result["priority"] == 5


class TestCapabilityMatchToDict:
    def test_to_dict(self):
        metadata = CapabilityMetadata(name="test", description="test", category="cat", provider="prov")
        cap = Capability(id="test_id", metadata=metadata)
        match = CapabilityMatch(capability=cap, confidence=0.95, match_reason="test match")

        result = match.to_dict()
        assert result["confidence"] == 0.95


class TestCapabilityResultToDict:
    def test_to_dict(self):
        metadata = CapabilityMetadata(name="test", description="test", category="cat", provider="prov")
        cap = Capability(id="test_id", metadata=metadata)
        match = CapabilityMatch(capability=cap, confidence=0.9)
        result = CapabilityResult(
            capability_match=match,
            tool_name="test_tool",
            execution_path=["step1", "step2"],
        )

        d = result.to_dict()
        assert d["tool_name"] == "test_tool"
        assert len(d["execution_path"]) == 2


class TestCapabilityNodeToDict:
    def test_to_dict(self):
        metadata = CapabilityMetadata(name="test", description="test", category="cat", provider="prov")
        cap = Capability(id="test_id", metadata=metadata)
        node = CapabilityNode(capability_id="test_id", capability=cap)

        result = node.to_dict()
        assert result["capability_id"] == "test_id"


class TestCapabilityGroupToDict:
    def test_to_dict(self):
        metadata = CapabilityMetadata(name="test", description="test", category="planning", provider="prov")
        cap = Capability(id="test_id", metadata=metadata)
        group = CapabilityGroup(category="planning", capabilities=[cap])

        result = group.to_dict()
        assert result["category"] == "planning"
        assert len(result["capabilities"]) == 1


class TestCapabilityAnalyzerGraph:
    def test_analyze_graph(self):
        graph = CapabilityGraph()
        metadata = CapabilityMetadata(name="n1", description="d1", category="cat", provider="p1")
        cap1 = Capability(id="cap1", metadata=metadata)
        cap2 = Capability(id="cap2", metadata=metadata)
        graph.add_capability(cap1)
        graph.add_capability(cap2)

        analyzer = CapabilityAnalyzer(graph=graph)
        result = analyzer.analyze_graph()

        assert result["total_nodes"] == 2


class TestEdgeTypeEnum:
    def test_edge_types_exist(self):
        assert EdgeType.DEPENDS_ON.value == "depends_on"
        assert EdgeType.REQUIRES.value == "requires"
        assert EdgeType.EXTENDS.value == "extends"
        assert EdgeType.RELATED_TO.value == "related_to"


class TestRiskLevelEnum:
    def test_risk_levels_exist(self):
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.HIGH.value == "high"
        assert RiskLevel.CRITICAL.value == "critical"


class TestCapabilityGroup:
    def test_empty_group(self):
        group = CapabilityGroup(category="empty", capabilities=[])
        assert len(group.capabilities) == 0


class TestCapabilityMatcherRanking:
    def test_match_ranking(self):
        registry = CapabilityRegistry()
        m1 = CapabilityMetadata(name="review", description="full review", category="engineering/code_review", provider="review")
        m2 = CapabilityMetadata(name="analyze", description="partial review", category="engineering/architecture_review", provider="analyze")
        registry.register("review_cap", m1)
        registry.register("analyze_cap", m2)

        matcher = CapabilityMatcher(registry)
        matches = matcher.match("review", top_n=5)

        assert matches[0].capability.metadata.name == "review"

    def test_match_no_matches(self):
        registry = CapabilityRegistry()
        m = CapabilityMetadata(name="kb", description="knowledge base", category="knowledge", provider="kb")
        registry.register("kb_cap", m)

        matcher = CapabilityMatcher(registry)
        matches = matcher.match("xyz nonexistent query")
        assert len(matches) == 0


class TestCapabilityResolverAlternatives:
    def test_resolve_multiple(self):
        registry = CapabilityRegistry()
        m1 = CapabilityMetadata(name="review", description="full", category="engineering/code_review", provider="review")
        m2 = CapabilityMetadata(name="analyze", description="code analysis", category="engineering/architecture_review", provider="analyze")
        registry.register("review_cap", m1)
        registry.register("analyze_cap", m2)

        matcher = CapabilityMatcher(registry)
        resolver = CapabilityResolver(matcher=matcher)
        results = resolver.resolve_with_alternatives("review code", top_n=3)

        assert len(results) >= 1


class TestCapabilityRegistryByProvider:
    def test_get_by_provider(self):
        registry = CapabilityRegistry()
        m1 = CapabilityMetadata(name="n1", description="d1", category="cat", provider="tool_a")
        m2 = CapabilityMetadata(name="n2", description="d2", category="cat", provider="tool_a")
        m3 = CapabilityMetadata(name="n3", description="d3", category="cat", provider="tool_b")

        registry.register("c1", m1)
        registry.register("c2", m2)
        registry.register("c3", m3)

        results = registry.get_by_provider("tool_a")
        assert len(results) == 2


class TestCapabilityRegistryByRisk:
    def test_get_by_risk_level(self):
        registry = CapabilityRegistry()
        m1 = CapabilityMetadata(name="n1", description="d1", category="cat", provider="p1", risk_level=RiskLevel.HIGH)
        m2 = CapabilityMetadata(name="n2", description="d2", category="cat", provider="p2", risk_level=RiskLevel.LOW)

        registry.register("c1", m1)
        registry.register("c2", m2)

        high = registry.get_by_risk_level(RiskLevel.HIGH)
        assert len(high) == 1


class TestCapabilityRegistryRemove:
    def test_remove_existing(self):
        registry = CapabilityRegistry()
        m = CapabilityMetadata(name="test", description="test", category="cat", provider="prov")
        registry.register("test_id", m)

        result = registry.remove("test_id")
        assert result is True
        assert registry.get("test_id") is None

    def test_remove_nonexistent(self):
        registry = CapabilityRegistry()
        result = registry.remove("nonexistent")
        assert result is False


class TestCapabilityGraphRelationships:
    def test_get_dependencies(self):
        graph = CapabilityGraph()
        metadata = CapabilityMetadata(name="test", description="test", category="cat", provider="prov")
        cap1 = Capability(id="cap1", metadata=metadata)
        cap2 = Capability(id="cap2", metadata=metadata)
        graph.add_capability(cap1)
        graph.add_capability(cap2)

        edge = CapabilityEdge(source_id="cap1", target_id="cap2", edge_type=EdgeType.DEPENDS_ON)
        graph.add_edge(edge)

        deps = graph.get_dependencies("cap1")
        assert len(deps) == 1

    def test_get_dependents(self):
        graph = CapabilityGraph()
        metadata = CapabilityMetadata(name="test", description="test", category="cat", provider="prov")
        cap1 = Capability(id="cap1", metadata=metadata)
        cap2 = Capability(id="cap2", metadata=metadata)
        graph.add_capability(cap1)
        graph.add_capability(cap2)

        edge = CapabilityEdge(source_id="cap1", target_id="cap2", edge_type=EdgeType.DEPENDS_ON)
        graph.add_edge(edge)

        dependents = graph.get_dependents("cap2")
        assert len(dependents) == 1


class TestCapabilityTaxonomyDetails:
    def test_to_dict(self):
        taxonomy = CapabilityTaxonomy()
        result = taxonomy.to_dict()
        assert "engineering" in result

    def test_get_all_subcategories(self):
        taxonomy = CapabilityTaxonomy()
        subcats = taxonomy.get_all_subcategories()
        assert len(subcats) > 0


class TestCapabilityAnalyzerToDict:
    def test_to_dict(self):
        registry = CapabilityRegistry()
        m = CapabilityMetadata(name="test", description="test", category="planning", provider="prov")
        registry.register("c1", m)

        analyzer = CapabilityAnalyzer(registry=registry)
        result = analyzer.to_dict()
        assert "coverage" in result
        assert "duplicates" in result


class TestCapabilityCategoryMethods:
    def test_parent_category(self):
        parent = CapabilityCategory.get_parent_category("engineering/code_review")
        assert parent == "engineering"

    def test_parent_category_top_level(self):
        parent = CapabilityCategory.get_parent_category("planning")
        assert parent == "planning"


# ============================================
# Performance & Edge Cases
# ============================================

class TestCapabilityGraphGetAll:
    def test_get_all_capabilities(self):
        graph = CapabilityGraph()
        metadata = CapabilityMetadata(name="n1", description="d1", category="cat", provider="p1")

        for i in range(10):
            cap = Capability(id=f"cap{i}", metadata=metadata)
            graph.add_capability(cap)

        all_caps = graph.get_all_capabilities()
        assert len(all_caps) == 10


class TestCapabilityGraphToDict:
    def test_to_dict(self):
        graph = CapabilityGraph()
        metadata = CapabilityMetadata(name="n1", description="d1", category="cat", provider="p1")
        cap1 = Capability(id="cap1", metadata=metadata)
        cap2 = Capability(id="cap2", metadata=metadata)
        graph.add_capability(cap1)
        graph.add_capability(cap2)

        edge = CapabilityEdge(source_id="cap1", target_id="cap2", edge_type=EdgeType.REQUIRES)
        graph.add_edge(edge)

        result = graph.to_dict()
        assert "nodes" in result
        assert "edges" in result


class TestCapabilityRegistryCount:
    def test_count(self):
        registry = CapabilityRegistry()
        assert registry.count() == 0

        m = CapabilityMetadata(name="n1", description="d1", category="cat", provider="p1")
        registry.register("c1", m)

        assert registry.count() == 1


class TestCapabilityRegistryListAll:
    def test_list_all(self):
        registry = CapabilityRegistry()
        m = CapabilityMetadata(name="n1", description="d1", category="cat", provider="p1")
        registry.register("c1", m)

        all_caps = registry.list_all()
        assert "c1" in all_caps


class TestCapabilityRegistryToDict:
    def test_to_dict(self):
        registry = CapabilityRegistry()
        m = CapabilityMetadata(name="n1", description="d1", category="cat", provider="p1")
        registry.register("c1", m)

        result = registry.to_dict()
        assert "count" in result
        assert result["count"] == 1


class TestCapabilityGraphExecutionPath:
    def test_execution_path_simple(self):
        graph = CapabilityGraph()
        metadata = CapabilityMetadata(name="test", description="test", category="cat", provider="prov")
        cap = Capability(id="cap1", metadata=metadata)
        graph.add_capability(cap)

        path = graph.get_execution_path("cap1")
        assert path == ["cap1"]


class TestCapabilityBuilderBuild:
    def test_build_with_mock_tools(self):
        builder = CapabilityBuilder()

        # Mock tool structure
        tools = {
            "review": type("MockTool", (), {"description": "Review tool", "parameters": {"path": "str"}})(),
            "planning": type("MockTool", (), {"description": "Planning tool", "parameters": {"goal": "str"}})(),
        }

        graph = builder.build(tools)

        # Should have extracted capabilities from both tools
        assert len(graph._nodes) >= 2


class TestCapabilityAnalyzerMissingProviders:
    def test_find_missing_providers(self):
        registry = CapabilityRegistry()
        m = CapabilityMetadata(name="n1", description="d1", category="cat", provider="p1")
        registry.register("c1", m)

        analyzer = CapabilityAnalyzer(registry=registry)
        missing = analyzer.find_missing_providers()
        assert isinstance(missing, list)


class TestCapabilityMatcherScore:
    def test_match_score_boundaries(self):
        registry = CapabilityRegistry()
        # Capability with exact name match
        m = CapabilityMetadata(name="review", description="test test test", category="engineering/code_review", provider="prov")
        registry.register("cap1", m)

        matcher = CapabilityMatcher(registry)
        matches = matcher.match("review")

        # Confidence should be capped at 1.0
        assert matches[0].confidence <= 1.0


class TestCapabilityResolverNoMatch:
    def test_resolve_no_match(self):
        resolver = CapabilityResolver()
        result = resolver.resolve("nonexistent goal xyz")

        assert result.success is False
        assert result.tool_name == ""


# ============================================
# More Edge Cases
# ============================================

class TestCapabilityMetadataWithAllFields:
    def test_with_all_fields(self):
        metadata = CapabilityMetadata(
            name="full",
            description="full description",
            category="planning/roadmap",
            provider="roadmap_tool",
            required_inputs=["start", "end"],
            outputs=["milestones", "timeline"],
            risk_level=RiskLevel.MEDIUM,
            priority=10,
            dependencies=["cap1", "cap2"],
        )
        assert metadata.priority == 10
        assert len(metadata.dependencies) == 2


class TestCapabilityWithTags:
    def test_tags_preserved(self):
        metadata = CapabilityMetadata(name="t", description="d", category="c", provider="p")
        cap = Capability(id="id", metadata=metadata, tags=["python", "review", "code"])
        assert len(cap.tags) == 3


class TestCapabilityGraphGetRelated:
    def test_get_related(self):
        graph = CapabilityGraph()
        metadata = CapabilityMetadata(name="test", description="test", category="cat", provider="prov")
        cap1 = Capability(id="cap1", metadata=metadata)
        cap2 = Capability(id="cap2", metadata=metadata)
        graph.add_capability(cap1)
        graph.add_capability(cap2)

        edge = CapabilityEdge(source_id="cap1", target_id="cap2", edge_type=EdgeType.RELATED_TO)
        graph.add_edge(edge)

        related = graph.get_related("cap1")
        assert len(related) == 1


class TestCapabilityGraphGetByCategory:
    def test_get_by_category(self):
        graph = CapabilityGraph()
        m1 = CapabilityMetadata(name="n1", description="d1", category="planning", provider="p1")
        m2 = CapabilityMetadata(name="n2", description="d2", category="knowledge", provider="p2")
        cap1 = Capability(id="cap1", metadata=m1)
        cap2 = Capability(id="cap2", metadata=m2)
        graph.add_capability(cap1)
        graph.add_capability(cap2)

        planning_caps = graph.get_capabilities_by_category("planning")
        assert len(planning_caps) == 1


class TestCapabilityMatcherDescriptionOverlap:
    def test_description_word_overlap(self):
        registry = CapabilityRegistry()
        m = CapabilityMetadata(name="analyze", description="analyze code quality and patterns", category="engineering/architecture_review", provider="analyze")
        registry.register("cap1", m)

        matcher = CapabilityMatcher(registry)
        matches = matcher.match("analyze code")
        assert len(matches) > 0


class TestCapabilityAnalyzerCoverageReport:
    def test_full_coverage_report(self):
        registry = CapabilityRegistry()
        m1 = CapabilityMetadata(name="n1", description="d1", category="planning", provider="p1", risk_level=RiskLevel.HIGH)
        m2 = CapabilityMetadata(name="n2", description="d2", category="knowledge", provider="p2", risk_level=RiskLevel.LOW)
        registry.register("c1", m1)
        registry.register("c2", m2)

        analyzer = CapabilityAnalyzer(registry=registry)
        report = analyzer.generate_coverage_report()

        assert "by_risk_level" in report
        assert "high" in report["by_risk_level"]


class TestCapabilityAnalyzerEmptyCoverage:
    def test_empty_coverage_report(self):
        registry = CapabilityRegistry()
        analyzer = CapabilityAnalyzer(registry=registry)
        report = analyzer.generate_coverage_report()

        assert report["total_capabilities"] == 0
