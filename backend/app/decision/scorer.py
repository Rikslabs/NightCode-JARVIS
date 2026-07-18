"""Decision Scorer - deterministic weighted scoring."""

from typing import Dict, List, Optional
from .models import Strategy, Decision, DecisionFactor, RiskLevel


class DecisionScorer:
    """
    Deterministic weighted scoring for strategies.

    Uses weighted factors to score each strategy.
    """

    # Default weights for each factor
    DEFAULT_WEIGHTS = {
        DecisionFactor.COMPLEXITY: 0.15,
        DecisionFactor.CONFIDENCE: 0.25,
        DecisionFactor.SUCCESS_RATE: 0.20,
        DecisionFactor.EXECUTION_COST: 0.10,
        DecisionFactor.RISK: 0.20,
        DecisionFactor.DURATION: 0.10,
    }

    def __init__(self, weights: Optional[Dict[DecisionFactor, float]] = None):
        """Initialize with optional custom weights."""
        self._weights = weights or self.DEFAULT_WEIGHTS

    def score(self, strategy: Strategy, context: Optional[Dict] = None) -> Decision:
        """
        Score a strategy based on context.

        Args:
            strategy: Strategy to score.
            context: Additional context (optional).

        Returns:
            Decision with total score and factor scores.
        """
        factor_scores = {}

        # Complexity score (lower is better)
        complexity = context.get("complexity", 1.0) if context else 1.0
        factor_scores[DecisionFactor.COMPLEXITY.value] = self._normalize(1.0 - complexity)

        # Confidence score
        factor_scores[DecisionFactor.CONFIDENCE.value] = strategy.confidence

        # Success rate score
        success_rate = context.get("success_rate", 0.5) if context else 0.5
        factor_scores[DecisionFactor.SUCCESS_RATE.value] = success_rate

        # Execution cost score (lower is better)
        cost = context.get("execution_cost", 1.0) if context else 1.0
        factor_scores[DecisionFactor.EXECUTION_COST.value] = self._normalize(1.0 - cost)

        # Risk score (lower risk is better)
        risk = context.get("risk", 0.5) if context else 0.5
        factor_scores[DecisionFactor.RISK.value] = self._normalize(1.0 - risk)

        # Duration score (lower is better)
        duration = context.get("duration", 1.0) if context else 1.0
        factor_scores[DecisionFactor.DURATION.value] = self._normalize(1.0 - duration)

        # Calculate weighted total
        total_score = sum(
            factor_scores.get(f.value, 0.0) * w
            for f, w in self._weights.items()
        )

        return Decision(
            strategy=strategy,
            total_score=total_score,
            factor_scores=factor_scores,
        )

    def score_multiple(self, strategies: List[Strategy], context: Optional[Dict] = None) -> List[Decision]:
        """Score multiple strategies."""
        return [self.score(s, context) for s in strategies]

    def _normalize(self, value: float) -> float:
        """Normalize value to 0-1 range."""
        return max(0.0, min(1.0, value))