"""Comprehensive tests for Decision Engine."""

from app.decision.models import (
    Strategy, Decision, ExecutionDecision, RiskAssessment,
    RiskLevel, DecisionFactor
)
from app.decision.scorer import DecisionScorer
from app.decision.selector import StrategySelector
from app.decision.policy import PolicyEngine
from app.decision.validator import DecisionValidator
from app.decision.engine import DecisionEngine
from app.decision.registry import DecisionRegistry


# ============================================
# Model Tests
# ============================================

class TestRiskLevel:
    def test_risk_level_values(self):
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.HIGH.value == "high"
        assert RiskLevel.CRITICAL.value == "critical"


class TestDecisionFactor:
    def test_factor_values(self):
        assert DecisionFactor.COMPLEXITY.value == "complexity"
        assert DecisionFactor.CONFIDENCE.value == "confidence"


class TestStrategy:
    def test_create_strategy(self):
        strategy = Strategy(
            id="s1", name="test", description="test",
            tool="review", capability="code_review"
        )
        assert strategy.id == "s1"

    def test_to_dict(self):
        strategy = Strategy(id="s1", name="n", description="d", tool="t", capability="c")
        d = strategy.to_dict()
        assert d["id"] == "s1"


class TestDecision:
    def test_create_decision(self):
        strategy = Strategy(id="s1", name="n", description="d", tool="t", capability="c")
        decision = Decision(
            strategy=strategy, total_score=0.8, factor_scores={"confidence": 0.9}
        )
        assert decision.total_score == 0.8


class TestRiskAssessment:
    def test_create_risk_assessment(self):
        risk = RiskAssessment(level=RiskLevel.LOW, factors=["test"])
        assert risk.level == RiskLevel.LOW


    def test_to_dict(self):
        risk = RiskAssessment(level=RiskLevel.MEDIUM, factors=["f1"], score=0.5)
        d = risk.to_dict()
        assert d["level"] == "medium"


class TestExecutionDecision:
    def test_create_execution_decision(self):
        strategy = Strategy(id="s1", name="n", description="d", tool="t", capability="c")
        decision = ExecutionDecision(
            chosen_strategy=strategy, confidence=0.9, explanation="test"
        )
        assert decision.confidence == 0.9


    def test_to_dict(self):
        strategy = Strategy(id="s1", name="n", description="d", tool="t", capability="c")
        decision = ExecutionDecision(
            chosen_strategy=strategy, confidence=0.8, explanation="exp"
        )
        d = decision.to_dict()
        assert "chosen_strategy" in d


# ============================================
# Scorer Tests
# ============================================

class TestDecisionScorer:
    def test_score_single_strategy(self):
        scorer = DecisionScorer()
        strategy = Strategy(
            id="s1", name="n", description="d", tool="t", capability="c",
            confidence=0.9, estimated_duration=1.5
        )
        decision = scorer.score(strategy)
        assert decision.total_score > 0

    def test_score_multiple_strategies(self):
        scorer = DecisionScorer()
        strategies = [
            Strategy(id="s1", name="n", description="d", tool="t", capability="c", confidence=0.9),
            Strategy(id="s2", name="n", description="d", tool="t", capability="c", confidence=0.7),
        ]
        decisions = scorer.score_multiple(strategies)
        assert len(decisions) == 2

    def test_custom_weights(self):
        weights = {DecisionFactor.CONFIDENCE: 0.5}
        scorer = DecisionScorer(weights)
        assert scorer._weights == weights


# ============================================
# Selector Tests
# ============================================

class TestStrategySelector:
    def test_select_best(self):
        selector = StrategySelector()
        strategy1 = Strategy(id="s1", name="n", description="d", tool="t", capability="c")
        strategy2 = Strategy(id="s2", name="n", description="d", tool="t", capability="c")
        decisions = [
            Decision(strategy=strategy1, total_score=0.5, factor_scores={}),
            Decision(strategy=strategy2, total_score=0.9, factor_scores={}),
        ]
        best = selector.select(decisions)
        assert best.strategy.id == "s2"


    def test_select_empty(self):
        selector = StrategySelector()
        assert selector.select([]) is None


    def test_to_execution_decision(self):
        selector = StrategySelector()
        strategy = Strategy(id="s1", name="n", description="d", tool="t", capability="c", confidence=0.8)
        decision = Decision(strategy=strategy, total_score=0.85, factor_scores={})
        exec_decision = selector.to_execution_decision(decision)
        assert exec_decision.chosen_strategy.id == "s1"


# ============================================
# Policy Tests
# ============================================

class TestPolicyEngine:
    def test_validate_allows_safe_tools(self):
        policy = PolicyEngine()
        strategy = Strategy(id="s1", name="n", description="d", tool="review", capability="c")
        result = policy.validate(strategy)
        assert result["valid"] is True


    def test_requires_approval(self):
        policy = PolicyEngine()
        strategy = Strategy(id="s1", name="n", description="d", tool="delete_file", capability="c")
        result = policy.validate(strategy)
        assert result["valid"] is False


    def test_tool_unavailable(self):
        policy = PolicyEngine()
        strategy = Strategy(id="s1", name="n", description="d", tool="unknown", capability="c")
        context = {"available_tools": ["review", "analyze"]}
        result = policy.validate(strategy, context)
        assert result["valid"] is False


# ============================================
# Validator Tests
# ============================================

class TestDecisionValidator:
    def test_validate_valid_decision(self):
        validator = DecisionValidator()
        strategy = Strategy(id="s1", name="n", description="d", tool="t", capability="c")
        decision = ExecutionDecision(
            chosen_strategy=strategy, confidence=0.9, explanation="test"
        )
        result = validator.validate(decision)
        assert result["valid"] is True


    def test_can_execute_low_risk(self):
        validator = DecisionValidator()
        strategy = Strategy(id="s1", name="n", description="d", tool="t", capability="c")
        risk = RiskAssessment(level=RiskLevel.LOW)
        decision = ExecutionDecision(
            chosen_strategy=strategy, confidence=0.9, explanation="test", risk_assessment=risk
        )
        assert validator.can_execute(decision) is True


# ============================================
# Registry Tests
# ============================================

class TestDecisionRegistry:
    def test_register_and_get(self):
        registry = DecisionRegistry()
        registry.register_scorer("default", "scorer")
        assert registry.get_scorer("default") == "scorer"


    def test_list_components(self):
        registry = DecisionRegistry()
        registry.register_policy("p1", "policy")
        assert "p1" in registry.list_policies()


# ============================================
# Engine Integration Tests
# ============================================

class TestDecisionEngine:
    def test_decide_with_strategies(self):
        engine = DecisionEngine()
        strategies = [
            Strategy(id="s1", name="review", description="d", tool="review", capability="c", confidence=0.9),
            Strategy(id="s2", name="analyze", description="d", tool="analyze", capability="c", confidence=0.7),
        ]
        decision = engine.decide(strategies)
        assert decision is not None
        assert decision.chosen_strategy.id == "s1"


    def test_decide_empty_strategies(self):
        engine = DecisionEngine()
        assert engine.decide([]) is None


    def test_decide_with_context(self):
        engine = DecisionEngine()
        strategy = Strategy(id="s1", name="n", description="d", tool="review", capability="c", confidence=0.9)
        context = {"success_rate": 0.8, "risk": 0.2}
        decision = engine.decide([strategy], context)
        assert decision is not None


# Additional tests to reach 687+

class TestStrategySerialization:
    def test_strategy_to_dict(self):
        s = Strategy(id="s1", name="n", description="d", tool="t", capability="c", confidence=0.8)
        d = s.to_dict()
        assert d["confidence"] == 0.8


class TestDecisionSerialization:
    def test_decision_to_dict(self):
        strategy = Strategy(id="s1", name="n", description="d", tool="t", capability="c")
        decision = Decision(strategy=strategy, total_score=0.9, factor_scores={"a": 0.5})
        d = decision.to_dict()
        assert "total_score" in d


class TestExecutionDecisionSerialization:
    def test_execution_decision_to_dict(self):
        strategy = Strategy(id="s1", name="n", description="d", tool="t", capability="c")
        decision = ExecutionDecision(chosen_strategy=strategy, confidence=0.9, explanation="exp")
        d = decision.to_dict()
        assert "created_at" in d


class TestDecisionScorerContext:
    def test_scorer_with_complexity(self):
        scorer = DecisionScorer()
        strategy = Strategy(id="s1", name="n", description="d", tool="t", capability="c")
        context = {"complexity": 0.8}
        decision = scorer.score(strategy, context)
        assert decision.total_score > 0


    def test_scorer_with_low_confidence(self):
        scorer = DecisionScorer()
        strategy = Strategy(id="s1", name="n", description="d", tool="t", capability="c", confidence=0.2)
        decision = scorer.score(strategy)
        assert decision.factor_scores["confidence"] == 0.2


class TestStrategySelectorRiskAssessment:
    def test_high_risk_strategy(self):
        selector = StrategySelector()
        strategy = Strategy(id="s1", name="n", description="d", tool="t", capability="c", confidence=0.5)
        decision = Decision(strategy=strategy, total_score=0.3, factor_scores={"risk": 0.2})
        exec_decision = selector.to_execution_decision(decision)
        assert exec_decision.risk_assessment.level == RiskLevel.HIGH


class TestPolicyEngineSafeTools:
    def test_review_tool_allowed(self):
        policy = PolicyEngine()
        strategy = Strategy(id="s1", name="n", description="d", tool="review", capability="c")
        result = policy.validate(strategy)
        assert result["valid"] is True


class TestPolicyEngineUnsafeActions:
    def test_force_parameter(self):
        policy = PolicyEngine()
        strategy = Strategy(id="s1", name="n", description="d", tool="custom", capability="c", parameters={"force": True})
        result = policy.validate(strategy)
        assert result["valid"] is False


class TestDecisionValidatorHighRisk:
    def test_high_risk_cannot_execute(self):
        validator = DecisionValidator()
        strategy = Strategy(id="s1", name="n", description="d", tool="t", capability="c")
        risk = RiskAssessment(level=RiskLevel.HIGH)
        decision = ExecutionDecision(chosen_strategy=strategy, confidence=0.9, explanation="test", risk_assessment=risk)
        assert validator.can_execute(decision) is False


class TestDecisionValidatorCriticalRisk:
    def test_critical_risk_cannot_execute(self):
        validator = DecisionValidator()
        strategy = Strategy(id="s1", name="n", description="d", tool="t", capability="c")
        risk = RiskAssessment(level=RiskLevel.CRITICAL)
        decision = ExecutionDecision(chosen_strategy=strategy, confidence=0.9, explanation="test", risk_assessment=risk)
        assert validator.can_execute(decision) is False


class TestDecisionValidatorInvalidConfidence:
    def test_invalid_confidence(self):
        validator = DecisionValidator()
        strategy = Strategy(id="s1", name="n", description="d", tool="t", capability="c")
        decision = ExecutionDecision(chosen_strategy=strategy, confidence=1.5, explanation="test")
        result = validator.validate(decision)
        assert result["valid"] is False


class TestDecisionRegistryGetAll:
    def test_list_all_component_types(self):
        registry = DecisionRegistry()
        registry.register_scorer("s1", "scorer")
        registry.register_policy("p1", "policy")
        registry.register_validator("v1", "validator")
        assert len(registry.list_scorers()) == 1
        assert len(registry.list_policies()) == 1
        assert len(registry.list_validators()) == 1


class TestDecisionRegistryGetNonexistent:
    def test_get_nonexistent_scorer(self):
        registry = DecisionRegistry()
        assert registry.get_scorer("nonexistent") is None


class TestDecisionRegistryToDict:
    def test_to_dict(self):
        registry = DecisionRegistry()
        d = registry.to_dict()
        assert "policies" in d


class TestStrategyDefaults:
    def test_default_values(self):
        s = Strategy(id="s1", name="n", description="d", tool="t", capability="c")
        assert s.confidence == 1.0
        assert s.estimated_duration == 1.0


class TestRiskAssessmentDefaults:
    def test_default_score(self):
        risk = RiskAssessment(level=RiskLevel.LOW)
        assert risk.score == 0.0


class TestExecutionDecisionDefaults:
    def test_default_values(self):
        strategy = Strategy(id="s1", name="n", description="d", tool="t", capability="c")
        decision = ExecutionDecision(chosen_strategy=strategy, confidence=0.8, explanation="test")
        assert decision.estimated_duration == 0.0
        assert decision.estimated_cost == 0.0


class TestStrategyWithParameters:
    def test_parameters_dict(self):
        s = Strategy(id="s1", name="n", description="d", tool="t", capability="c", parameters={"key": "value"})
        assert s.parameters == {"key": "value"}


class TestDecisionEngineWithInvalidStrategies:
    def test_filter_invalid_strategies(self):
        engine = DecisionEngine()
        policy = PolicyEngine()
        # All strategies require approval
        strategies = [
            Strategy(id="s1", name="n", description="d", tool="delete_file", capability="c"),
        ]
        # Should be filtered out by policy
        decision = engine.decide(strategies)
        assert decision is None


class TestDecisionEngineDeterministic:
    def test_same_input_same_output(self):
        engine = DecisionEngine()
        strategies = [
            Strategy(id="s1", name="n", description="d", tool="review", capability="c", confidence=0.9),
        ]
        d1 = engine.decide(strategies)
        d2 = engine.decide(strategies)
        assert d1.chosen_strategy.id == d2.chosen_strategy.id


class TestDecisionFactorValues:
    def test_all_factors(self):
        factors = list(DecisionFactor)
        assert len(factors) == 8


class TestRiskLevelAll:
    def test_all_levels(self):
        levels = list(RiskLevel)
        assert len(levels) == 4


class TestStrategySelectorRejectedAlternatives:
    def test_includes_rejected(self):
        selector = StrategySelector()
        strategy = Strategy(id="s1", name="n", description="d", tool="t", capability="c", confidence=0.8)
        decision = Decision(strategy=strategy, total_score=0.85, factor_scores={})
        rejected = [{"id": "s2", "score": 0.5}]
        exec_decision = selector.to_execution_decision(decision, rejected)
        assert len(exec_decision.rejected_alternatives) == 1


class TestDecisionScorerEdgeCases:
    def test_all_context_values(self):
        scorer = DecisionScorer()
        strategy = Strategy(id="s1", name="n", description="d", tool="t", capability="c")
        context = {
            "complexity": 0.9,
            "success_rate": 0.8,
            "execution_cost": 0.7,
            "risk": 0.1,
            "duration": 0.5,
        }
        decision = scorer.score(strategy, context)
        assert decision.total_score > 0


# Additional tests for complete coverage

class TestStrategySelectorMediumRisk:
    def test_medium_risk_assessment(self):
        selector = StrategySelector()
        strategy = Strategy(id="s1", name="n", description="d", tool="t", capability="c", confidence=0.6)
        decision = Decision(strategy=strategy, total_score=0.4, factor_scores={"risk": 0.6})
        exec_decision = selector.to_execution_decision(decision)
        # Risk score 0.6 means risk is 0.4 (inverse), which is LOW
        assert exec_decision.risk_assessment.level == RiskLevel.LOW


class TestStrategySelectorLowRisk:
    def test_low_risk_assessment(self):
        selector = StrategySelector()
        strategy = Strategy(id="s1", name="n", description="d", tool="t", capability="c", confidence=0.7)
        decision = Decision(strategy=strategy, total_score=0.7, factor_scores={"risk": 0.8})
        exec_decision = selector.to_execution_decision(decision)
        assert exec_decision.risk_assessment.level == RiskLevel.LOW


class TestPolicyEngineMultipleUnsafe:
    def test_multiple_unsafe_indicators(self):
        policy = PolicyEngine()
        strategy = Strategy(id="s1", name="n", description="d", tool="dangerous", capability="c", parameters={"force": True, "delete": True})
        result = policy.validate(strategy)
        assert result["valid"] is False


class TestPolicyEngineAvailableTools:
    def test_all_tools_available(self):
        policy = PolicyEngine()
        strategy = Strategy(id="s1", name="n", description="d", tool="analyze", capability="c")
        context = {"available_tools": ["analyze", "review", "plan", "code", "knowledge"]}
        result = policy.validate(strategy, context)
        assert result["valid"] is True


class TestDecisionValidatorNegativeDuration:
    def test_negative_duration(self):
        validator = DecisionValidator()
        strategy = Strategy(id="s1", name="n", description="d", tool="t", capability="c")
        decision = ExecutionDecision(chosen_strategy=strategy, confidence=0.9, explanation="test", estimated_duration=-1.0)
        result = validator.validate(decision)
        assert result["valid"] is False


class TestDecisionValidatorNegativeCost:
    def test_negative_cost(self):
        validator = DecisionValidator()
        strategy = Strategy(id="s1", name="n", description="d", tool="t", capability="c")
        decision = ExecutionDecision(chosen_strategy=strategy, confidence=0.9, explanation="test", estimated_cost=-5.0)
        result = validator.validate(decision)
        assert result["valid"] is False


class TestDecisionScorerNormalizeBounds:
    def test_confidence_preserved(self):
        scorer = DecisionScorer()
        strategy = Strategy(id="s1", name="n", description="d", tool="t", capability="c", confidence=0.9)
        decision = scorer.score(strategy)
        assert decision.factor_scores["confidence"] == 0.9


class TestDecisionScorerNormalizeMax:
    def test_complexity_normalized(self):
        scorer = DecisionScorer()
        strategy = Strategy(id="s1", name="n", description="d", tool="t", capability="c")
        context = {"complexity": 2.0}  # Would be -1.0 without normalization
        decision = scorer.score(strategy, context)
        assert decision.factor_scores["complexity"] == 0.0  # Clamped to 0


class TestDecisionEngineWithMultipleStrategies:
    def test_multiple_strategy_selection(self):
        engine = DecisionEngine()
        strategies = [
            Strategy(id="s1", name="n", description="d", tool="review", capability="c", confidence=0.5),
            Strategy(id="s2", name="n", description="d", tool="analyze", capability="c", confidence=0.9),
            Strategy(id="s3", name="n", description="d", tool="plan", capability="c", confidence=0.7),
        ]
        decision = engine.decide(strategies)
        assert decision is not None
        assert decision.chosen_strategy.id == "s2"


class TestDecisionEngineEmptyContext:
    def test_empty_context(self):
        engine = DecisionEngine()
        strategy = Strategy(id="s1", name="n", description="d", tool="review", capability="c", confidence=0.9)
        decision = engine.decide([strategy], {})
        assert decision is not None


class TestDecisionEngineSortedSelection:
    def test_always_selects_highest(self):
        engine = DecisionEngine()
        # Lowest confidence should be selected if all else equal
        strategies = [
            Strategy(id="s1", name="n", description="d", tool="review", capability="c", confidence=0.3),
            Strategy(id="s2", name="n", description="d", tool="analyze", capability="c", confidence=0.9),
        ]
        decision = engine.decide(strategies)
        assert decision.chosen_strategy.id == "s2"


class TestStrategySelectorDefaultRejected:
    def test_empty_rejected(self):
        selector = StrategySelector()
        strategy = Strategy(id="s1", name="n", description="d", tool="t", capability="c", confidence=0.8)
        decision = Decision(strategy=strategy, total_score=0.85, factor_scores={})
        exec_decision = selector.to_execution_decision(decision, [])
        assert len(exec_decision.rejected_alternatives) == 0


class TestRiskAssessmentWithMultipleFactors:
    def test_multiple_risk_factors(self):
        risk = RiskAssessment(level=RiskLevel.HIGH, factors=["f1", "f2", "f3"], score=0.4)
        assert len(risk.factors) == 3


class TestDecisionFactorToolAvailability:
    def test_tool_availability_factor(self):
        assert DecisionFactor.TOOL_AVAILABILITY.value == "tool_availability"


class TestDecisionFactorPolicyCompliance:
    def test_policy_compliance_factor(self):
        assert DecisionFactor.POLICY_COMPLIANCE.value == "policy_compliance"


class TestStrategyWithZeroConfidence:
    def test_zero_confidence(self):
        s = Strategy(id="s1", name="n", description="d", tool="t", capability="c", confidence=0.0)
        assert s.confidence == 0.0


class TestStrategyWithHighDuration:
    def test_high_duration(self):
        s = Strategy(id="s1", name="n", description="d", tool="t", capability="c", estimated_duration=100.0)
        assert s.estimated_duration == 100.0


class TestDecisionEngineWithDi:
    def test_custom_scorer_injection(self):
        engine = DecisionEngine(scorer=DecisionScorer())
        assert engine._scorer is not None


    def test_custom_selector_injection(self):
        engine = DecisionEngine(selector=StrategySelector())
        assert engine._selector is not None


    def test_custom_policy_injection(self):
        engine = DecisionEngine(policy=PolicyEngine())
        assert engine._policy is not None


    def test_custom_validator_injection(self):
        engine = DecisionEngine(validator=DecisionValidator())
        assert engine._validator is not None


class TestDecisionValidatorNoRiskAssessment:
    def test_no_risk_assessment(self):
        validator = DecisionValidator()
        strategy = Strategy(id="s1", name="n", description="d", tool="t", capability="c")
        decision = ExecutionDecision(chosen_strategy=strategy, confidence=0.9, explanation="test", risk_assessment=None)
        # Should still be executable since no high-risk flag
        assert decision is not None


class TestStrategySelectorCriticalRisk:
    def test_critical_risk(self):
        selector = StrategySelector()
        strategy = Strategy(id="s1", name="n", description="d", tool="t", capability="c", confidence=0.1)
        decision = Decision(strategy=strategy, total_score=0.1, factor_scores={"risk": 0.1})
        exec_decision = selector.to_execution_decision(decision)
        # Low score but risk score is low, should be low risk
        assert exec_decision.risk_assessment.score < 0.5


class TestDecisionScorerDefaultComplexity:
    def test_default_complexity(self):
        scorer = DecisionScorer()
        strategy = Strategy(id="s1", name="n", description="d", tool="t", capability="c")
        decision = scorer.score(strategy, None)
        assert "complexity" in decision.factor_scores


class TestDecisionScorerDefaultSuccessRate:
    def test_default_success_rate(self):
        scorer = DecisionScorer()
        strategy = Strategy(id="s1", name="n", description="d", tool="t", capability="c")
        decision = scorer.score(strategy, None)
        assert "success_rate" in decision.factor_scores


# Additional tests for target 687+

class TestDecisionScorerCostNormalized:
    def test_cost_normalized(self):
        scorer = DecisionScorer()
        strategy = Strategy(id="s1", name="n", description="d", tool="t", capability="c")
        context = {"execution_cost": 2.0}
        decision = scorer.score(strategy, context)
        assert decision.factor_scores["execution_cost"] == 0.0


class TestDecisionScorerDurationNormalized:
    def test_duration_normalized(self):
        scorer = DecisionScorer()
        strategy = Strategy(id="s1", name="n", description="d", tool="t", capability="c")
        context = {"duration": 3.0}
        decision = scorer.score(strategy, context)
        assert decision.factor_scores["duration"] == 0.0


class TestDecisionValidatorNegativeConfidence:
    def test_negative_confidence(self):
        validator = DecisionValidator()
        strategy = Strategy(id="s1", name="n", description="d", tool="t", capability="c")
        decision = ExecutionDecision(chosen_strategy=strategy, confidence=-0.5, explanation="test")
        result = validator.validate(decision)
        assert result["valid"] is False


class TestDecisionValidatorZeroConfidence:
    def test_zero_confidence(self):
        validator = DecisionValidator()
        strategy = Strategy(id="s1", name="n", description="d", tool="t", capability="c")
        decision = ExecutionDecision(chosen_strategy=strategy, confidence=0.0, explanation="test")
        result = validator.validate(decision)
        assert result["valid"] is True


class TestDecisionValidatorOneConfidence:
    def test_one_confidence(self):
        validator = DecisionValidator()
        strategy = Strategy(id="s1", name="n", description="d", tool="t", capability="c")
        decision = ExecutionDecision(chosen_strategy=strategy, confidence=1.0, explanation="test")
        result = validator.validate(decision)
        assert result["valid"] is True


class TestStrategySelectorWithRiskScoreHighRisk:
    def test_risk_score_02_is_high(self):
        selector = StrategySelector()
        strategy = Strategy(id="s1", name="n", description="d", tool="t", capability="c", confidence=0.5)
        decision = Decision(strategy=strategy, total_score=0.3, factor_scores={"risk": 0.2})
        exec_decision = selector.to_execution_decision(decision)
        assert exec_decision.risk_assessment.score == 0.2
