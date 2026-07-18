"""Tests for Learning Engine module."""

import pytest

from app.learning.models import (
    ExecutionHistory,
    LearningRecord,
    LearningSummary,
    OptimizationSuggestion,
    FailurePattern,
    SuccessPattern,
    Recommendation,
    LearningStatistics,
)
from app.learning.learner import LearningEngine
from app.learning.feedback import FeedbackCollector
from app.learning.optimizer import OptimizationEngine
from app.learning.history import LearningHistory
from app.learning.knowledge import LearningKnowledge
from app.learning.registry import LearningRegistry
from app.learning.analytics import LearningAnalytics
from app.core.enums import RiskLevel


class TestExecutionHistory:
    def test_create_history(self):
        h = ExecutionHistory(
            tool_name="review",
            intent="review_project",
            success=True,
            duration=1.5,
            confidence=0.9,
            risk=RiskLevel.LOW,
        )
        assert h.tool_name == "review"
        assert h.success is True


class TestLearningRecord:
    def test_create_record(self):
        r = LearningRecord(
            execution_id="exec_1",
            tool_name="review",
            success=True,
            duration=1.0,
            confidence=0.9,
        )
        assert r.execution_id == "exec_1"
        assert r.tool_name == "review"


class TestLearningSummary:
    def test_create_summary(self):
        s = LearningSummary(
            total_executions=10,
            successful_executions=8,
            failed_executions=2,
            average_duration=5.0,
            success_rate=0.8,
            most_reliable_tools=["review", "planning"],
        )
        assert s.total_executions == 10
        assert s.success_rate == 0.8


class TestOptimizationSuggestion:
    def test_create_suggestion(self):
        s = OptimizationSuggestion(
            tool_name="review",
            current_confidence=0.8,
            suggested_confidence=0.9,
            reason="High reliability",
            impact="positive",
        )
        assert s.tool_name == "review"
        assert s.suggested_confidence == 0.9


class TestFailurePattern:
    def test_create_pattern(self):
        p = FailurePattern(
            pattern_id="fail_timeout",
            tool_name="api",
            error_type="timeout",
            occurrence_count=5,
        )
        assert p.error_type == "timeout"


class TestSuccessPattern:
    def test_create_pattern(self):
        p = SuccessPattern(
            pattern_id="success_review",
            tool_name="review",
            confidence_level=0.95,
            occurrence_count=10,
        )
        assert p.confidence_level == 0.95


class TestRecommendation:
    def test_create_recommendation(self):
        r = Recommendation(
            tool_name="review",
            confidence=0.9,
            reasoning="Most reliable",
            based_on_pattern="success_rate",
        )
        assert r.tool_name == "review"


class TestLearningStatistics:
    def test_create_statistics(self):
        s = LearningStatistics(
            total_records=100,
            total_analyses=50,
            suggestions_generated=25,
            patterns_identified=10,
        )
        assert s.total_records == 100


# ============================================
# LearningEngine Tests
# ============================================

class TestLearningEngine:
    def test_record_execution(self):
        engine = LearningEngine()
        record = engine.record_execution(
            tool_name="review",
            intent="review_project",
            success=True,
            duration=1.0,
            confidence=0.9,
            risk=RiskLevel.LOW,
        )
        assert record.tool_name == "review"
        assert record.success is True

    def test_analyze(self):
        engine = LearningEngine()
        engine.record_execution(
            tool_name="review",
            intent="review_project",
            success=True,
            duration=1.0,
            confidence=0.9,
            risk=RiskLevel.LOW,
        )
        summary = engine.analyze()
        assert summary.total_executions == 1
        assert summary.success_rate == 1.0

    def test_get_statistics(self):
        engine = LearningEngine()
        engine.record_execution(
            tool_name="review",
            intent="review_project",
            success=True,
            duration=1.0,
            confidence=0.9,
            risk=RiskLevel.LOW,
        )
        stats = engine.get_statistics()
        assert stats.total_records == 1


# ============================================
# FeedbackCollector Tests
# ============================================

class TestFeedbackCollector:
    def test_collect_feedback(self):
        collector = FeedbackCollector()
        collector.collect("exec_1", True, "Good result")
        feedback = collector.get_all()
        assert len(feedback) == 1

    def test_get_failure_feedback(self):
        collector = FeedbackCollector()
        collector.collect("exec_1", False, "Failed")
        failures = collector.get_failure_feedback()
        assert len(failures) == 1

    def test_to_dict(self):
        collector = FeedbackCollector()
        collector.collect("exec_1", True)
        d = collector.to_dict()
        assert d["total"] == 1


# ============================================
# OptimizationEngine Tests
# ============================================

class TestOptimizationEngine:
    def test_suggest_improvement(self):
        opt = OptimizationEngine()
        suggestion = opt.suggest_improvement("review", 0.8)
        assert suggestion.tool_name == "review"
        assert suggestion.suggested_confidence == 0.9

    def test_identify_failure_patterns(self):
        opt = OptimizationEngine()
        patterns = opt.identify_failure_patterns([
            {"error_type": "timeout"},
            {"error_type": "timeout"},
        ])
        assert len(patterns) >= 1

    def test_identify_success_patterns(self):
        opt = OptimizationEngine()
        patterns = opt.identify_success_patterns([
            {"tool_name": "review", "confidence": 0.9},
            {"tool_name": "review", "confidence": 0.95},
        ])
        assert len(patterns) >= 1


# ============================================
# LearningHistory Tests
# ============================================

class TestLearningHistory:
    def test_add_record(self):
        history = LearningHistory()
        history.add_record({"tool": "review", "success": True})
        assert len(history.get_recent()) == 1

    def test_get_by_tool(self):
        history = LearningHistory()
        history.add_record({"tool_name": "review", "success": True})
        history.add_record({"tool_name": "planning", "success": False})
        review_records = history.get_by_tool("review")
        assert len(review_records) == 1

    def test_get_successful(self):
        history = LearningHistory()
        history.add_record({"success": True})
        history.add_record({"success": False})
        successes = history.get_successful()
        assert len(successes) == 1


# ============================================
# LearningKnowledge Tests
# ============================================

class TestLearningKnowledge:
    def test_update_tool_reliability(self):
        knowledge = LearningKnowledge()
        knowledge.update_tool_reliability("review", True)
        knowledge.update_tool_reliability("review", True)
        reliability = knowledge.get_tool_reliability("review")
        assert reliability > 0.5

    def test_get_most_reliable_tools(self):
        knowledge = LearningKnowledge()
        knowledge.update_tool_reliability("review", True)
        knowledge.update_tool_reliability("review", True)
        knowledge.update_tool_reliability("planning", False)
        tools = knowledge.get_most_reliable_tools()
        assert "review" in tools

    def test_to_dict(self):
        knowledge = LearningKnowledge()
        d = knowledge.to_dict()
        assert "tool_reliability" in d


# ============================================
# LearningRegistry Tests
# ============================================

class TestLearningRegistry:
    def test_get_instance(self):
        registry = LearningRegistry.get_instance()
        assert isinstance(registry, LearningRegistry)

    def test_register_and_get_engine(self):
        registry = LearningRegistry()
        engine = LearningEngine()
        registry.register_engine("test", engine)
        assert registry.get_engine("test") is engine

    def test_clear(self):
        registry = LearningRegistry()
        engine = LearningEngine()
        registry.register_engine("test", engine)
        registry.clear()
        assert registry.get_engine("test") is None


# ============================================
# LearningAnalytics Tests
# ============================================

class TestLearningAnalytics:
    def test_track_tool(self):
        analytics = LearningAnalytics()
        analytics.track_tool("review", 1.0, True)
        analytics.track_tool("review", 2.0, False)
        reliability = analytics.get_tool_reliability("review")
        assert reliability == 0.5

    def test_track_capability(self):
        analytics = LearningAnalytics()
        analytics.track_capability("code_review", 1.0, True)
        # Capability is stored in _capability_metrics, not _tool_metrics
        assert analytics._capability_metrics["code_review"]["successful"] == 1

    def test_track_capability_update(self):
        analytics = LearningAnalytics()
        analytics.track_capability("code_review", 1.0, True)
        analytics.track_capability("code_review", 1.0, True)
        assert analytics._capability_metrics["code_review"]["successful"] == 2

    def test_get_top_tools(self):
        analytics = LearningAnalytics()
        analytics.track_tool("review", 1.0, True)
        analytics.track_tool("planning", 2.0, False)
        top = analytics.get_top_tools(limit=1)
        assert "review" in top