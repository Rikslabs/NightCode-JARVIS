"""Strategy Selector - selects best strategy from alternatives."""

from typing import Dict, List, Optional
from .models import Strategy, Decision, ExecutionDecision, RiskAssessment, RiskLevel, DecisionFactor


class StrategySelector:
    """
    Selects the best strategy from scored alternatives.

    Must be deterministic - always picks highest score.
    """

    def select(self, decisions: List[Decision]) -> Optional[Decision]:
        """
        Select the best decision from scored alternatives.

        Args:
            decisions: List of scored decisions.

        Returns:
            The decision with highest score, or None if empty.
        """
        if not decisions:
            return None

        return max(decisions, key=lambda d: d.total_score)

    def to_execution_decision(
        self,
        decision: Decision,
        rejected: Optional[List[Dict]] = None
    ) -> ExecutionDecision:
        """
        Convert a decision to execution decision format.

        Args:
            decision: The chosen decision.
            rejected: List of rejected alternatives.

        Returns:
            ExecutionDecision with full output.
        """
        # Assess risk based on factor scores
        risk_score = decision.factor_scores.get(DecisionFactor.RISK.value, 0.5) if hasattr(DecisionFactor, 'RISK') else 0.5
        risk_level = self._assess_risk(risk_score)

        return ExecutionDecision(
            chosen_strategy=decision.strategy,
            confidence=decision.strategy.confidence,
            explanation=f"Selected based on highest score: {decision.total_score:.2f}",
            rejected_alternatives=rejected or [],
            risk_assessment=risk_level,
            estimated_duration=decision.strategy.estimated_duration,
            estimated_cost=decision.factor_scores.get("execution_cost", 1.0),
        )

    def _assess_risk(self, score: float) -> RiskAssessment:
        """Assess risk level from score."""
        if score < 0.3:
            return RiskAssessment(level=RiskLevel.HIGH, score=score, factors=["high_risk_score"])
        elif score < 0.5:
            return RiskAssessment(level=RiskLevel.MEDIUM, score=score, factors=["medium_risk_score"])
        else:
            return RiskAssessment(level=RiskLevel.LOW, score=score)