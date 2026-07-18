"""Decision Validator - validates decisions before execution."""

from typing import Any, Dict, List, Optional
from .models import Strategy, ExecutionDecision


class DecisionValidator:
    """
    Validates execution decisions.

    Checks for:
    - Missing required fields
    - Invalid risk levels
    - Negative durations/costs
    """

    def validate(self, decision: ExecutionDecision) -> Dict[str, Any]:
        """
        Validate an execution decision.

        Args:
            decision: Decision to validate.

        Returns:
            Dictionary with 'valid' boolean and any errors/warnings.
        """
        errors = []
        warnings = []

        # Check required fields
        if not decision.chosen_strategy:
            errors.append("Missing chosen_strategy")

        if decision.confidence < 0 or decision.confidence > 1:
            errors.append(f"Invalid confidence: {decision.confidence}")

        if decision.estimated_duration < 0:
            errors.append(f"Negative duration: {decision.estimated_duration}")

        if decision.estimated_cost < 0:
            errors.append(f"Negative cost: {decision.estimated_cost}")

        # Check risk assessment
        if not decision.risk_assessment:
            warnings.append("Missing risk assessment")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }

    def can_execute(self, decision: ExecutionDecision) -> bool:
        """
        Check if decision can be executed.

        Args:
            decision: Decision to check.

        Returns:
            True if execution is allowed.
        """
        result = self.validate(decision)
        if result["errors"]:
            return False

        # Check risk level
        risk = decision.risk_assessment.level.value if decision.risk_assessment else "low"
        if risk in ("critical", "high"):
            return False

        return True