"""Policy Engine - validates strategies against policies."""

from typing import Any, Dict, List, Optional
from .models import Strategy, RiskLevel


class PolicyEngine:
    """
    Validates strategies against policies.

    Checks for:
    - Missing tools
    - Policy violations
    - Unsafe actions
    - Approval-required actions
    """

    # Tools that require approval
    APPROVAL_REQUIRED_TOOLS = {"delete", "remove", "drop", "destroy"}

    def validate(self, strategy: Strategy, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Validate a strategy against policies.

        Args:
            strategy: Strategy to validate.
            context: Additional context (optional).

        Returns:
            Dictionary with 'valid' boolean and any violations.
        """
        violations = []

        # Check for missing tools
        if not self._tool_available(strategy.tool, context):
            violations.append(f"Tool unavailable: {strategy.tool}")

        # Check for approval-required tools
        if self._requires_approval(strategy.tool):
            violations.append(f"Approval required for tool: {strategy.tool}")

        # Check for unsafe actions
        if self._is_unsafe_action(strategy, context):
            violations.append(f"Unsafe action detected")

        return {
            "valid": len(violations) == 0,
            "violations": violations,
        }

    def filter_valid(self, strategies: List[Strategy], context: Optional[Dict] = None) -> List[Strategy]:
        """
        Filter out invalid strategies.

        Args:
            strategies: List of strategies to filter.
            context: Additional context (optional).

        Returns:
            List of valid strategies.
        """
        return [s for s in strategies if self.validate(s, context)["valid"]]

    def _tool_available(self, tool: str, context: Optional[Dict]) -> bool:
        """Check if tool is available."""
        # For now, assume all tools are available unless explicitly denied
        if context and "available_tools" in context:
            return tool in context["available_tools"]
        return True

    def _requires_approval(self, tool: str) -> bool:
        """Check if tool requires approval."""
        tool_lower = tool.lower()
        return any(req in tool_lower for req in self.APPROVAL_REQUIRED_TOOLS)

    def _is_unsafe_action(self, strategy: Strategy, context: Optional[Dict]) -> bool:
        """Check if action is potentially unsafe."""
        safe_tools = {"review", "analyze", "plan", "code", "knowledge"}
        if strategy.tool.lower() not in safe_tools:
            # Check if parameters indicate destructive action
            params = strategy.parameters or {}
            if params.get("force", False) or params.get("delete", False):
                return True
        return False