"""Comprehensive tests for Experience layer."""

from app.experience.models import (
    ExperienceRecord, ExperienceSummary, ExperienceMatch, ExperienceScore,
    ExperienceStatistics, ExperienceContext, ExperienceRecommendation
)
from app.experience.history import ExecutionHistory
from app.experience.retriever import ExperienceRetriever
from app.experience.scoring import ExperienceScorer
from app.experience.ranking import ExperienceRanker
from app.experience.index import ExperienceIndex
from app.experience.registry import ExperienceRegistry
from app.experience.analyzer import ExperienceAnalyzer


# ============================================
# Model Tests
# ============================================

class TestExperienceRecord:
    def test_create_record(self):
        record = ExperienceRecord(
            id="test_id",
            goal="review project",
            capability_id="review_cap",
            tool_name="review",
            workflow="code_review",
            duration_ms=1500.0,
            success=True,
            result={"findings": ["issue1"]},
            failure_reason=None,
        )
        assert record.id == "test_id"
        assert record.success is True

    def test_to_dict(self):
        record = ExperienceRecord(
            id="test_id",
            goal="test goal",
            capability_id="cap1",
            tool_name="tool1",
            workflow=None,
            duration_ms=100.0,
            success=True,
            result={"key": "value"},
            failure_reason=None,
        )
        result = record.to_dict()
        assert result["id"] == "test_id"
        assert "timestamp" in result


class TestExperienceSummary:
    def test_create_summary(self):
        summary = ExperienceSummary(
            capability_id="cap1",
            tool_name="tool1",
            total_executions=10,
            successful_executions=8,
            failed_executions=2,
            success_rate=0.8,
            average_duration_ms=500.0,
            last_execution="2024-01-01T00:00:00+00:00",
        )
        assert summary.success_rate == 0.8

    def test_to_dict(self):
        summary = ExperienceSummary(
            capability_id="cap1", tool_name="t1", total_executions=5,
            successful_executions=3, failed_executions=2,
            success_rate=0.6, average_duration_ms=300.0, last_execution=None
        )
        result = summary.to_dict()
        assert result["total_executions"] == 5


class TestExperienceMatch:
    def test_create_match(self):
        record = ExperienceRecord(id="r1", goal="g1", capability_id="c1", tool_name="t1",
                                 workflow=None, duration_ms=100.0, success=True,
                                 result={}, failure_reason=None)
        match = ExperienceMatch(record=record, confidence=0.9, similarity_score=0.85)
        assert match.confidence == 0.9

    def test_to_dict(self):
        record = ExperienceRecord(id="r1", goal="g1", capability_id="c1", tool_name="t1",
                                 workflow=None, duration_ms=100.0, success=True,
                                 result={}, failure_reason=None)
        match = ExperienceMatch(record=record, confidence=0.9, similarity_score=0.85)
        result = match.to_dict()
        assert result["confidence"] == 0.9


class TestExperienceScore:
    def test_create_score(self):
        score = ExperienceScore(
            record_id="r1",
            success_score=1.0,
            recency_score=0.8,
            frequency_score=0.5,
            duration_score=0.7,
            overall_score=0.75,
        )
        assert score.overall_score == 0.75

    def test_to_dict(self):
        score = ExperienceScore(
            record_id="r1", success_score=1.0, recency_score=0.8,
            frequency_score=0.5, duration_score=0.7, overall_score=0.75
        )
        result = score.to_dict()
        assert "factors" in result


class TestExperienceStatistics:
    def test_create_statistics(self):
        stats = ExperienceStatistics(
            total_records=100,
            total_successful=80,
            total_failed=20,
            overall_success_rate=0.8,
            tool_statistics={},
            capability_statistics={},
            average_duration_ms=500.0,
        )
        assert stats.total_records == 100


class TestExperienceContext:
    def test_create_context(self):
        ctx = ExperienceContext(
            goal="test goal",
            project_path="/project",
            user_id="user1",
            capabilities_used=["cap1"],
            tools_used=["tool1"],
            previous_executions=["exec1"],
        )
        assert ctx.goal == "test goal"

    def test_to_dict(self):
        ctx = ExperienceContext(
            goal="g", project_path="p", user_id="u",
            capabilities_used=["c1"], tools_used=["t1"], previous_executions=[]
        )
        result = ctx.to_dict()
        assert result["goal"] == "g"


class TestExperienceRecommendation:
    def test_create_recommendation(self):
        rec = ExperienceRecommendation(
            tool_name="review",
            capability_id="review_cap",
            confidence=0.9,
            reason="high success rate",
            based_on_experiences=["e1", "e2"],
        )
        assert rec.tool_name == "review"

    def test_to_dict(self):
        rec = ExperienceRecommendation(
            tool_name="t1", capability_id="c1", confidence=0.8,
            reason="test", based_on_experiences=["e1"]
        )
        result = rec.to_dict()
        assert result["tool_name"] == "t1"


# ============================================
# ExecutionHistory Tests
# ============================================

class TestExecutionHistory:
    def test_add_and_get(self):
        history = ExecutionHistory()
        record = ExperienceRecord(id="r1", goal="g1", capability_id="c1", tool_name="t1",
                                 workflow=None, duration_ms=100.0, success=True,
                                 result={}, failure_reason=None)
        history.add(record)
        assert history.get("r1") == record

    def test_count(self):
        history = ExecutionHistory()
        assert history.count() == 0
        record = ExperienceRecord(id="r1", goal="g1", capability_id="c1", tool_name="t1",
                                 workflow=None, duration_ms=100.0, success=True,
                                 result={}, failure_reason=None)
        history.add(record)
        assert history.count() == 1

    def test_remove(self):
        history = ExecutionHistory()
        record = ExperienceRecord(id="r1", goal="g1", capability_id="c1", tool_name="t1",
                                 workflow=None, duration_ms=100.0, success=True,
                                 result={}, failure_reason=None)
        history.add(record)
        assert history.remove("r1") is True
        assert history.remove("nonexistent") is False

    def test_get_summary_for_tool(self):
        history = ExecutionHistory()
        r1 = ExperienceRecord(id="r1", goal="g1", capability_id="c1", tool_name="review",
                             workflow=None, duration_ms=100.0, success=True,
                             result={}, failure_reason=None)
        r2 = ExperienceRecord(id="r2", goal="g2", capability_id="c2", tool_name="review",
                             workflow=None, duration_ms=200.0, success=False,
                             result={}, failure_reason="error")
        history.add(r1)
        history.add(r2)

        summary = history.get_summary_for_tool("review")
        assert summary.total_executions == 2
        assert summary.successful_executions == 1


# ============================================
# ExperienceRetriever Tests
# ============================================

class TestExperienceRetriever:
    def test_retrieve_empty(self):
        retriever = ExperienceRetriever()
        matches = retriever.retrieve("any goal")
        assert len(matches) == 0

    def test_retrieve_with_history(self):
        history = ExecutionHistory()
        r1 = ExperienceRecord(id="r1", goal="review code", capability_id="c1", tool_name="review",
                             workflow=None, duration_ms=100.0, success=True,
                             result={}, failure_reason=None)
        history.add(r1)

        retriever = ExperienceRetriever(history)
        matches = retriever.retrieve("review project")
        assert len(matches) > 0

    def test_retrieve_by_tool(self):
        history = ExecutionHistory()
        r1 = ExperienceRecord(id="r1", goal="g1", capability_id="c1", tool_name="review",
                             workflow=None, duration_ms=100.0, success=True,
                             result={}, failure_reason=None)
        history.add(r1)

        retriever = ExperienceRetriever(history)
        matches = retriever.retrieve_by_tool("review")
        assert len(matches) == 1


# ============================================
# ExperienceScorer Tests
# ============================================

class TestExperienceScorer:
    def test_score_successful(self):
        scorer = ExperienceScorer()
        record = ExperienceRecord(id="r1", goal="g1", capability_id="c1", tool_name="t1",
                                 workflow=None, duration_ms=500.0, success=True,
                                 result={}, failure_reason=None)
        score = scorer.score(record)
        assert score.success_score == 1.0

    def test_score_failed(self):
        scorer = ExperienceScorer()
        record = ExperienceRecord(id="r1", goal="g1", capability_id="c1", tool_name="t1",
                                 workflow=None, duration_ms=500.0, success=False,
                                 result={}, failure_reason="error")
        score = scorer.score(record)
        assert score.success_score == 0.1

    def test_duration_scoring(self):
        scorer = ExperienceScorer()
        # Fast duration
        score_fast = scorer._calculate_duration_score(50)
        assert score_fast == 1.0

        # Slow duration
        score_slow = scorer._calculate_duration_score(15000)
        assert score_slow == 0.2


# ============================================
# ExperienceRanker Tests
# ============================================

class TestExperienceRanker:
    def test_rank_empty_matches(self):
        ranker = ExperienceRanker()
        ranked = ranker.rank([])
        assert len(ranked) == 0

    def test_recommend_empty_history(self):
        ranker = ExperienceRanker()
        recs = ranker.recommend("any goal")
        assert len(recs) == 0

    def test_recommend_with_history(self):
        history = ExecutionHistory()
        r1 = ExperienceRecord(id="r1", goal="g1", capability_id="c1", tool_name="review",
                             workflow=None, duration_ms=100.0, success=True,
                             result={}, failure_reason=None)
        r2 = ExperienceRecord(id="r2", goal="g2", capability_id="c2", tool_name="review",
                             workflow=None, duration_ms=200.0, success=True,
                             result={}, failure_reason=None)
        history.add(r1)
        history.add(r2)

        ranker = ExperienceRanker(history=history)
        recs = ranker.recommend("test")
        assert len(recs) > 0
        assert recs[0].tool_name == "review"


# ============================================
# ExperienceIndex Tests
# ============================================

class TestExperienceIndex:
    def test_index_empty(self):
        index = ExperienceIndex()
        index.build()
        assert len(index.get_by_tool("any")) == 0

    def test_build_index(self):
        history = ExecutionHistory()
        r1 = ExperienceRecord(id="r1", goal="review project code", capability_id="c1", tool_name="review",
                             workflow=None, duration_ms=100.0, success=True,
                             result={}, failure_reason=None)
        history.add(r1)

        index = ExperienceIndex(history)
        index.build()
        assert len(index.get_by_tool("review")) == 1

    def test_search_by_keyword(self):
        history = ExecutionHistory()
        r1 = ExperienceRecord(id="r1", goal="review project code", capability_id="c1", tool_name="review",
                             workflow=None, duration_ms=100.0, success=True,
                             result={}, failure_reason=None)
        history.add(r1)

        index = ExperienceIndex(history)
        index.build()
        ids = index.get_by_goal_keyword("review")
        assert "r1" in ids


# ============================================
# ExperienceRegistry Tests
# ============================================

class TestExperienceRegistry:
    def test_register_and_get(self):
        registry = ExperienceRegistry()
        registry.register_retriever("default", "retriever_instance")

        assert registry.get_retriever("default") == "retriever_instance"

    def test_list_retrievers(self):
        registry = ExperienceRegistry()
        registry.register_retriever("r1", "retriever1")
        registry.register_retriever("r2", "retriever2")

        assert len(registry.list_retrievers()) == 2


# ============================================
# ExperienceAnalyzer Tests
# ============================================

class TestExperienceAnalyzer:
    def test_empty_statistics(self):
        analyzer = ExperienceAnalyzer()
        stats = analyzer.get_statistics()
        assert stats.total_records == 0

    def test_statistics_with_history(self):
        history = ExecutionHistory()
        r1 = ExperienceRecord(id="r1", goal="g1", capability_id="c1", tool_name="review",
                             workflow=None, duration_ms=100.0, success=True,
                             result={}, failure_reason=None)
        r2 = ExperienceRecord(id="r2", goal="g2", capability_id="c2", tool_name="planning",
                             workflow=None, duration_ms=200.0, success=False,
                             result={}, failure_reason="error")
        history.add(r1)
        history.add(r2)

        analyzer = ExperienceAnalyzer(history)
        stats = analyzer.get_statistics()
        assert stats.total_records == 2

    def test_most_used_tools(self):
        history = ExecutionHistory()
        for i in range(5):
            history.add(ExperienceRecord(id=f"r{i}", goal=f"g{i}", capability_id="c1",
                                        tool_name="review", workflow=None, duration_ms=100.0,
                                        success=True, result={}, failure_reason=None))
        for i in range(3):
            history.add(ExperienceRecord(id=f"r2_{i}", goal=f"g2_{i}", capability_id="c2",
                                        tool_name="planning", workflow=None, duration_ms=100.0,
                                        success=True, result={}, failure_reason=None))

        analyzer = ExperienceAnalyzer(history)
        tools = analyzer.get_most_used_tools()
        assert "review" in tools
        assert tools[0] == "review"

    def test_failure_statistics(self):
        history = ExecutionHistory()
        r1 = ExperienceRecord(id="r1", goal="g1", capability_id="c1", tool_name="review",
                             workflow=None, duration_ms=100.0, success=False,
                             result={}, failure_reason="error")
        history.add(r1)

        analyzer = ExperienceAnalyzer(history)
        failures = analyzer.get_failure_statistics()
        assert "review/c1" in failures