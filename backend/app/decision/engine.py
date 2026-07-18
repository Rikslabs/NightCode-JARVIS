"""Decision Engine - main orchestrator for choosing execution strategies."""

from typing import Any, Dict, List, Optional
from .models import Strategy, ExecutionDecision, DecisionFactor
from .scorer import DecisionScorer
from .selector import StrategySelector
from .policy import PolicyEngine
from .validator import DecisionValidator


class DecisionEngine:
    """
    Main decision engine that chooses optimal execution strategy.

    Deterministic selection based on weighted scoring.
    """

    def __init__(
        self,
        scorer: Optional[DecisionScorer] = None,
        selector: Optional[StrategySelector] = None,
        policy: Optional[PolicyEngine] = None,
        validator: Optional[DecisionValidator] = None,
    ):
        """Initialize with optional components (DI pattern)."""
        self._scorer = scorer or DecisionScorer()
        self._selector = selector or StrategySelector()
        self._policy = policy or PolicyEngine()
        self._validator = validator or DecisionValidator()

    def decide(
        self,
        strategies: List[Strategy],
        context: Optional[Dict] = None
    ) -> Optional[ExecutionDecision]:
        """
        Choose the best strategy from alternatives.

        Args:
            strategies: List of possible strategies.
            context: Additional context (capability matches, experience, risk level, etc.)

        Returns:
            ExecutionDecision with chosen strategy, or None if no valid strategy.
        """
        if not strategies:
            return None

        # Filter by policy
        valid_strategies = self._policy.filter_valid(strategies, context)
        if not valid_strategies:
            return None

        # Score all strategies
        decisions = self._scorer.score_multiple(valid_strategies, context)

        # Select best
        best = self._selector.select(decisions)
        if not best:
            return None

        # Build rejected alternatives list
        rejected = [
            {"strategy": d.strategy.to_dict(), "score": d.total_score}
            for d in decisions
            if d.strategy.id != best.strategy.id
        ]

        # Create execution decision
        return self._selector.to_execution_decision(best, rejected)