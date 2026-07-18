"""Verification layer for the Intelligence Orchestrator."""

from typing import Any, Dict, Optional

from .models import ExecutionDecision, ExecutionPlan, VerificationResult


class ExecutionValidator:
    """
    Verifies execution results after tool execution.

    Checks for success, missing outputs, failures, and partial completion.
    """

    def verify(
        self,
        decision: ExecutionDecision,
        result: Any,
        plan: ExecutionPlan,
    ) -> VerificationResult:
        """
        Verify the result of tool execution.

        Args:
            decision: The execution decision.
            result: The result from tool execution.
            plan: The original execution plan.

        Returns:
            VerificationResult indicating success/failure and recommendations.
        """
        errors = []
        missing_outputs = []
        failures = []
        partial = False

        # Check if result is None or indicates failure
        if result is None:
            failures.append(f"No result returned from tool: {decision.tool_name}")
            partial = False
        elif isinstance(result, dict):
            # Check for success flag
            success = result.get("success", True)
            if not success:
                failures.append(f"Tool {decision.tool_name} reported failure")
                error_msg = result.get("error", "Unknown error")
                if error_msg:
                    errors.append(str(error_msg))

            # Check for expected outputs
            data = result.get("data", {})
            if not data:
                missing_outputs.append("No data returned in result")

        # Determine if retry is recommended
        retry_recommended = self._should_retry(decision, result, errors, failures)

        # Check for partial completion
        if len(plan.steps) > 1 and decision.requires_multiple_steps:
            partial = result is not None

        return VerificationResult(
            success=len(errors) == 0 and len(failures) == 0,
            validation_errors=errors,
            missing_outputs=missing_outputs,
            tool_failures=failures,
            partial_completion=partial,
            retry_recommended=retry_recommended,
        )

    def _should_retry(self, decision: ExecutionDecision, result: Any, errors: list, failures: list) -> bool:
        """
        Determine if retry is recommended.

        Based on failure patterns and confidence level.
        """
        if not failures and not errors:
            return False

        # Retry if confidence was high enough
        if decision.confidence > 0.5:
            return True

        return False