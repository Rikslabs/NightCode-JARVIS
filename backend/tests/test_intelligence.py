"""Comprehensive tests for the Intelligence Orchestrator."""

import pytest
from datetime import datetime, timezone

from app.intelligence.models import (
    ReasoningContext,
    IntentAnalysis,
    ExecutionPlan,
    ExecutionDecision,
    ReasoningResult,
    VerificationResult,
    IntentType,
    ComplexityLevel,
    RiskLevel,
)
from app.intelligence.context import IntelligenceContext
from app.intelligence.reasoner import IntentReasoner
from app.intelligence.planner import ExecutionPlanner
from app.intelligence.selector import ToolSelector
from app.intelligence.validator import ExecutionValidator
from app.intelligence.orchestrator import IntelligenceOrchestrator
from app.intelligence.pipeline import IntelligencePipeline
from app.intelligence.registry import (
    IntelligenceRegistry,
    get_registry,
    register_reasoner,
    register_planner,
    register_selector,
    register_validator,
)


# ============================================
# Model Tests
# ============================================

class TestReasoningContext:
    def test_create_reasoning_context(self):
        context = ReasoningContext(request="review the project")
        assert context.request == "review the project"
        assert context.project_path is None

    def test_create_with_all_fields(self):
        context = ReasoningContext(
            request="analyze code",
            project_path="/path/to/project",
            user_id="user123",
            session_id="session456",
        )
        assert context.project_path == "/path/to/project"
        assert context.user_id == "user123"

    def test_to_dict(self):
        context = ReasoningContext(request="test request")
        result = context.to_dict()
        assert result["request"] == "test request"
        assert "timestamp" in result

    def test_serializable(self):
        context = ReasoningContext(request="test")
        data = context.to_dict()
        assert isinstance(data, dict)


class TestIntentAnalysis:
    def test_create_intent_analysis(self):
        analysis = IntentAnalysis(
            intent=IntentType.REVIEW_PROJECT,
            confidence=0.97,
            entities=["project1"],
            complexity=ComplexityLevel.COMPLEX,
            risk=RiskLevel.LOW,
            reasoning="Test reasoning",
        )
        assert analysis.intent == IntentType.REVIEW_PROJECT
        assert analysis.confidence == 0.97

    def test_to_dict(self):
        analysis = IntentAnalysis(
            intent=IntentType.QUERY_KNOWLEDGE,
            confidence=0.85,
            entities=[],
            complexity=ComplexityLevel.SIMPLE,
            risk=RiskLevel.LOW,
            reasoning="Test",
        )
        result = analysis.to_dict()
        assert result["intent"] == "query_knowledge"
        assert result["complexity"] == "simple"

    def test_from_dict(self):
        data = {
            "intent": "review_project",
            "confidence": 0.9,
            "entities": ["test"],
            "complexity": "complex",
            "risk": "low",
            "reasoning": "Test reasoning",
        }
        analysis = IntentAnalysis.from_dict(data)
        assert analysis.intent == IntentType.REVIEW_PROJECT
        assert analysis.confidence == 0.9


class TestExecutionPlan:
    def test_create_execution_plan(self):
        plan = ExecutionPlan(
            goal="Review project",
            intent=IntentType.REVIEW_PROJECT,
            steps=[{"step": 1}],
            estimated_steps=1,
            requires_workflow=False,
            requires_planning=False,
        )
        assert plan.goal == "Review project"
        assert plan.estimated_steps == 1

    def test_to_dict(self):
        plan = ExecutionPlan(
            goal="test",
            intent=IntentType.PLAN_FEATURE,
            steps=[],
            estimated_steps=0,
            requires_workflow=False,
            requires_planning=True,
        )
        result = plan.to_dict()
        assert result["intent"] == "plan_feature"
        assert result["requires_planning"] is True


class TestExecutionDecision:
    def test_create_decision(self):
        decision = ExecutionDecision(
            tool_name="review",
            parameters={"path": "."},
            confidence=0.9,
            requires_multiple_steps=False,
        )
        assert decision.tool_name == "review"
        assert decision.parameters == {"path": "."}

    def test_to_dict(self):
        decision = ExecutionDecision(
            tool_name="planning",
            parameters={"goal": "test"},
            confidence=0.85,
            requires_multiple_steps=True,
            next_step_tool="review",
        )
        result = decision.to_dict()
        assert result["tool_name"] == "planning"
        assert result["next_step_tool"] == "review"


class TestReasoningResult:
    def test_create_result(self):
        analysis = IntentAnalysis(
            intent=IntentType.UNKNOWN,
            confidence=0.5,
            entities=[],
            complexity=ComplexityLevel.SIMPLE,
            risk=RiskLevel.LOW,
            reasoning="Test",
        )
        plan = ExecutionPlan(
            goal="test",
            intent=IntentType.UNKNOWN,
            steps=[],
            estimated_steps=0,
            requires_workflow=False,
            requires_planning=False,
        )
        decision = ExecutionDecision(
            tool_name="knowledge",
            parameters={},
            confidence=0.5,
            requires_multiple_steps=False,
        )
        result = ReasoningResult(
            intent_analysis=analysis,
            execution_plan=plan,
            execution_decision=decision,
        )
        assert result.success is True


class TestVerificationResult:
    def test_create_success_result(self):
        result = VerificationResult(success=True)
        assert result.success is True
        assert result.retry_recommended is False

    def test_create_failure_result(self):
        result = VerificationResult(
            success=False,
            validation_errors=["Error 1"],
            tool_failures=["Tool failed"],
            retry_recommended=True,
        )
        assert result.success is False
        assert len(result.tool_failures) == 1

    def test_to_dict(self):
        result = VerificationResult(success=False, validation_errors=["err"])
        data = result.to_dict()
        assert data["success"] is False


# ============================================
# IntentReasoner Tests
# ============================================

class TestIntentReasoner:
    def test_analyze_review_project(self):
        reasoner = IntentReasoner()
        context = ReasoningContext(request="review project")
        result = reasoner.analyze(context)

        assert result.intent == IntentType.REVIEW_PROJECT
        assert result.confidence > 0.5
        assert result.risk == RiskLevel.LOW

    def test_analyze_plan_feature(self):
        reasoner = IntentReasoner()
        context = ReasoningContext(request="plan feature for user authentication")
        result = reasoner.analyze(context)

        assert result.intent == IntentType.PLAN_FEATURE
        assert result.risk in (RiskLevel.MEDIUM, RiskLevel.HIGH)

    def test_analyze_plan_bugfix(self):
        reasoner = IntentReasoner()
        context = ReasoningContext(request="fix bug in login module")
        result = reasoner.analyze(context)

        assert result.intent == IntentType.PLAN_BUGFIX

    def test_analyze_refactor(self):
        reasoner = IntentReasoner()
        context = ReasoningContext(request="refactor the codebase")
        result = reasoner.analyze(context)

        assert result.intent == IntentType.PLAN_REFACTOR

    def test_analyze_analyze_code(self):
        reasoner = IntentReasoner()
        context = ReasoningContext(request="analyze the main.py file")
        result = reasoner.analyze(context)

        assert result.intent == IntentType.ANALYZE_CODE

    def test_analyze_query_knowledge(self):
        reasoner = IntentReasoner()
        context = ReasoningContext(request="what is Python?")
        result = reasoner.analyze(context)

        assert result.intent == IntentType.QUERY_KNOWLEDGE

    def test_extract_entities_file_path(self):
        reasoner = IntentReasoner()
        entities = reasoner._extract_entities("analyze app/main.py")
        assert "app/main.py" in entities or any(".py" in e for e in entities)

    def test_assess_complexity_simple(self):
        reasoner = IntentReasoner()
        complexity = reasoner._assess_complexity(IntentType.QUERY_KNOWLEDGE, [])
        assert complexity == ComplexityLevel.SIMPLE

    def test_assess_complexity_complex(self):
        reasoner = IntentReasoner()
        complexity = reasoner._assess_complexity(IntentType.REVIEW_PROJECT, ["a", "b", "c"])
        assert complexity == ComplexityLevel.COMPLEX


# ============================================
# ExecutionPlanner Tests
# ============================================

class TestExecutionPlanner:
    def test_create_plan_review(self):
        planner = ExecutionPlanner()
        analysis = IntentAnalysis(
            intent=IntentType.REVIEW_PROJECT,
            confidence=0.9,
            entities=[],
            complexity=ComplexityLevel.COMPLEX,
            risk=RiskLevel.LOW,
            reasoning="Test",
        )
        context = ReasoningContext(request="review project")
        plan = planner.create_plan(analysis, context)

        assert plan.intent == IntentType.REVIEW_PROJECT
        assert len(plan.steps) == 1
        assert plan.steps[0]["tool"] == "review"

    def test_create_plan_feature(self):
        planner = ExecutionPlanner()
        analysis = IntentAnalysis(
            intent=IntentType.PLAN_FEATURE,
            confidence=0.85,
            entities=[],
            complexity=ComplexityLevel.COMPLEX,
            risk=RiskLevel.HIGH,
            reasoning="Test",
        )
        context = ReasoningContext(request="plan feature")
        plan = planner.create_plan(analysis, context)

        assert plan.intent == IntentType.PLAN_FEATURE
        assert len(plan.steps) == 2
        assert plan.requires_planning is True

    def test_create_plan_analyze(self):
        planner = ExecutionPlanner()
        analysis = IntentAnalysis(
            intent=IntentType.ANALYZE_CODE,
            confidence=0.9,
            entities=["test.py"],
            complexity=ComplexityLevel.SIMPLE,
            risk=RiskLevel.LOW,
            reasoning="Test",
        )
        context = ReasoningContext(request="analyze test.py")
        plan = planner.create_plan(analysis, context)

        assert plan.intent == IntentType.ANALYZE_CODE
        assert plan.steps[0]["tool"] == "coding"

    def test_create_plan_unknown(self):
        planner = ExecutionPlanner()
        analysis = IntentAnalysis(
            intent=IntentType.UNKNOWN,
            confidence=0.5,
            entities=[],
            complexity=ComplexityLevel.MODERATE,
            risk=RiskLevel.LOW,
            reasoning="Test",
        )
        context = ReasoningContext(request="unknown request")
        plan = planner.create_plan(analysis, context)

        assert plan.intent == IntentType.UNKNOWN
        assert plan.steps[0]["tool"] == "knowledge"


# ============================================
# ToolSelector Tests
# ============================================

class TestToolSelector:
    def test_select_tool_review(self):
        selector = ToolSelector()
        plan = ExecutionPlan(
            goal="review",
            intent=IntentType.REVIEW_PROJECT,
            steps=[{"tool": "review", "parameters": {"path": "."}}],
            estimated_steps=1,
            requires_workflow=False,
            requires_planning=False,
        )
        context = IntelligenceContext()
        decision = selector.select(plan, context)

        assert decision.tool_name == "review"
        assert decision.requires_multiple_steps is False

    def test_select_tool_multiple_steps(self):
        selector = ToolSelector()
        plan = ExecutionPlan(
            goal="plan feature",
            intent=IntentType.PLAN_FEATURE,
            steps=[
                {"tool": "planning", "parameters": {"goal": "test"}},
                {"tool": "review", "parameters": {"path": "."}},
            ],
            estimated_steps=2,
            requires_workflow=False,
            requires_planning=True,
        )
        context = IntelligenceContext()
        decision = selector.select(plan, context)

        assert decision.requires_multiple_steps is True
        assert decision.next_step_tool == "review"

    def test_select_empty_plan(self):
        selector = ToolSelector()
        plan = ExecutionPlan(
            goal="test",
            intent=IntentType.UNKNOWN,
            steps=[],
            estimated_steps=0,
            requires_workflow=False,
            requires_planning=False,
        )
        context = IntelligenceContext()
        decision = selector.select(plan, context)

        assert decision.tool_name == "knowledge"


# ============================================
# ExecutionValidator Tests
# ============================================

class TestExecutionValidator:
    def test_verify_success(self):
        validator = ExecutionValidator()
        decision = ExecutionDecision(
            tool_name="review",
            parameters={"path": "."},
            confidence=0.9,
            requires_multiple_steps=False,
        )
        plan = ExecutionPlan(
            goal="test",
            intent=IntentType.REVIEW_PROJECT,
            steps=[],
            estimated_steps=1,
            requires_workflow=False,
            requires_planning=False,
        )
        result = {"success": True, "data": "output"}
        verification = validator.verify(decision, result, plan)

        assert verification.success is True
        assert verification.retry_recommended is False

    def test_verify_failure(self):
        validator = ExecutionValidator()
        decision = ExecutionDecision(
            tool_name="review",
            parameters={"path": "."},
            confidence=0.9,
            requires_multiple_steps=False,
        )
        plan = ExecutionPlan(
            goal="test",
            intent=IntentType.REVIEW_PROJECT,
            steps=[],
            estimated_steps=1,
            requires_workflow=False,
            requires_planning=False,
        )
        result = {"success": False, "error": "Tool failed"}
        verification = validator.verify(decision, result, plan)

        assert verification.success is False

    def test_verify_none_result(self):
        validator = ExecutionValidator()
        decision = ExecutionDecision(
            tool_name="review",
            parameters={},
            confidence=0.9,
            requires_multiple_steps=False,
        )
        plan = ExecutionPlan(
            goal="test",
            intent=IntentType.REVIEW_PROJECT,
            steps=[],
            estimated_steps=1,
            requires_workflow=False,
            requires_planning=False,
        )
        verification = validator.verify(decision, None, plan)

        assert verification.success is False


# ============================================
# IntelligenceContext Tests
# ============================================

class TestIntelligenceContext:
    def test_create_context(self):
        context = IntelligenceContext(project_path="/test/path")
        assert context.project_path == "/test/path"

    def test_add_to_history(self):
        context = IntelligenceContext()
        context.add_to_history("test_event", {"key": "value"})

        history = context.get_history()
        assert len(history) == 1
        assert history[0]["event"] == "test_event"

    def test_to_dict(self):
        context = IntelligenceContext(user_id="user123")
        data = context.to_dict()
        assert data["user_id"] == "user123"

    def test_from_dict(self):
        data = {"project_path": "/path", "user_id": "user"}
        context = IntelligenceContext.from_dict(data)
        assert context.project_path == "/path"


# ============================================
# IntelligenceOrchestrator Tests
# ============================================

class TestIntelligenceOrchestrator:
    def test_process_simple_request(self):
        orchestrator = IntelligenceOrchestrator()
        result = orchestrator.process("review the project")

        assert result.intent_analysis.intent == IntentType.REVIEW_PROJECT
        assert result.execution_plan.steps[0]["tool"] == "review"

    def test_process_with_context(self):
        orchestrator = IntelligenceOrchestrator()
        context = IntelligenceContext(project_path="/my/project")
        result = orchestrator.process("analyze code", context)

        assert result.intent_analysis is not None
        assert result.execution_plan is not None

    def test_process_unknown_request(self):
        orchestrator = IntelligenceOrchestrator()
        result = orchestrator.process("what is the meaning of life?")

        assert result.intent_analysis.intent == IntentType.QUERY_KNOWLEDGE


# ============================================
# IntelligencePipeline Tests
# ============================================

class TestIntelligencePipeline:
    def test_execute_without_tool_executor(self):
        pipeline = IntelligencePipeline()
        result, verification = pipeline.execute("review project")

        assert result is not None
        assert result.intent_analysis.intent == IntentType.REVIEW_PROJECT
        assert verification is None

    def test_execute_with_tool_executor(self):
        def mock_executor(tool_name, **kwargs):
            return {"success": True, "data": "result"}

        pipeline = IntelligencePipeline(tool_executor=mock_executor)
        result, verification = pipeline.execute("review project")

        assert result is not None
        assert verification is not None
        assert verification.success is True

    def test_execute_multiple_steps(self):
        def mock_executor(tool_name, **kwargs):
            return {"success": True, "data": {}}

        pipeline = IntelligencePipeline(tool_executor=mock_executor)
        result, verification = pipeline.execute("plan feature implementation")

        assert result.execution_decision.requires_multiple_steps is True


# ============================================
# IntelligenceRegistry Tests
# ============================================

class TestIntelligenceRegistry:
    def test_get_default_reasoner(self):
        registry = IntelligenceRegistry()
        reasoner = registry.get_reasoner()
        assert isinstance(reasoner, IntentReasoner)

    def test_register_and_get_reasoner(self):
        registry = IntelligenceRegistry()
        custom_reasoner = IntentReasoner()
        registry.register_reasoner("custom", custom_reasoner)

        reasoner = registry.get_reasoner("custom")
        assert reasoner is custom_reasoner

    def test_register_and_get_planner(self):
        registry = IntelligenceRegistry()
        custom_planner = ExecutionPlanner()
        registry.register_planner("custom", custom_planner)

        planner = registry.get_planner("custom")
        assert planner is custom_planner

    def test_register_and_get_selector(self):
        registry = IntelligenceRegistry()
        custom_selector = ToolSelector()
        registry.register_selector("custom", custom_selector)

        selector = registry.get_selector("custom")
        assert selector is custom_selector

    def test_register_and_get_validator(self):
        registry = IntelligenceRegistry()
        custom_validator = ExecutionValidator()
        registry.register_validator("custom", custom_validator)

        validator = registry.get_validator("custom")
        assert validator is custom_validator

    def test_clear_registry(self):
        registry = IntelligenceRegistry()
        registry.register_reasoner("test", IntentReasoner())
        registry.clear()

        assert registry.get_reasoner("test") is None
        assert registry.get_planner("test") is None

    def test_list_components(self):
        registry = IntelligenceRegistry()
        registry.register_reasoner("r1", IntentReasoner())
        registry.register_planner("p1", ExecutionPlanner())

        assert "r1" in registry.list_reasoners()
        assert "p1" in registry.list_planners()


# ============================================
# Edge Cases Tests
# ============================================

class TestEdgeCases:
    def test_empty_request(self):
        reasoner = IntentReasoner()
        context = ReasoningContext(request="")
        result = reasoner.analyze(context)

        assert result.intent == IntentType.UNKNOWN

    def test_confidence_bounds(self):
        selector = ToolSelector()
        analysis = IntentAnalysis(
            intent=IntentType.UNKNOWN,
            confidence=0.1,
            entities=[],
            complexity=ComplexityLevel.SIMPLE,
            risk=RiskLevel.LOW,
            reasoning="Test",
        )
        decision = ExecutionDecision(
            tool_name="test",
            parameters={},
            confidence=0.3,
            requires_multiple_steps=False,
        )
        should_retry = (decision.confidence, 0.3)  # Low confidence
        assert decision.confidence < 0.5

    def test_serialization_roundtrip(self):
        original = IntentAnalysis(
            intent=IntentType.PLAN_FEATURE,
            confidence=0.88,
            entities=["entity1", "entity2"],
            complexity=ComplexityLevel.COMPLEX,
            risk=RiskLevel.MEDIUM,
            reasoning="Detailed reasoning trace",
        )

        data = original.to_dict()
        restored = IntentAnalysis.from_dict(data)

        assert restored.intent == original.intent
        assert restored.confidence == original.confidence
        assert restored.entities == original.entities

    def test_timezone_aware_timestamp(self):
        context = ReasoningContext(request="test")
        timestamp = context.timestamp

        # Should be valid ISO format with timezone
        parsed = datetime.fromisoformat(timestamp)
        assert parsed.tzinfo is not None

    def test_multiple_entities_extraction(self):
        reasoner = IntentReasoner()
        entities = reasoner._extract_entities("review app/main.py for project /src")
        assert isinstance(entities, list)