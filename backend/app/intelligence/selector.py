"""Tool selector for the Intelligence Orchestrator."""

from typing import Any, Dict, Optional

from .models import ExecutionDecision, ExecutionPlan, IntentAnalysis, IntentType
from .context import IntelligenceContext


class ToolSelector:
    """
    Selects appropriate tools based on execution plan.

    Uses the existing Tool Registry to look up tools and match capabilities.
    """

    def __init__(self, tool_registry: Optional[Dict[str, Any]] = None):
        """
        Initialize the tool selector.

        Args:
            tool_registry: Optional tool registry for dependency injection.
        """
        self._tool_registry = tool_registry

    def select(self, plan: ExecutionPlan, context: IntelligenceContext) -> ExecutionDecision:
        """
        Select a tool to execute based on the plan.

        Args:
            plan: The execution plan.
            context: The intelligence context.

        Returns:
            ExecutionDecision with selected tool and parameters.
        """
        if not plan.steps:
            return ExecutionDecision(
                tool_name="knowledge",
                parameters={"query": "How can I help you?"},
                confidence=0.1,
                requires_multiple_steps=False,
            )

        first_step = plan.steps[0]
        tool_name = first_step.get("tool", "knowledge")
        parameters = first_step.get("parameters", {})

        # Check if there are multiple steps
        has_next_step = len(plan.steps) > 1

        next_step_tool = plan.steps[1].get("tool") if has_next_step else None

        # Calculate confidence based on intent and tool availability
        confidence = self._calculate_confidence(plan.intent, tool_name, context)

        return ExecutionDecision(
            tool_name=tool_name,
            parameters=parameters,
            confidence=confidence,
            requires_multiple_steps=has_next_step,
            next_step_tool=next_step_tool,
        )

    def _calculate_confidence(self, intent: IntentType, tool_name: str, context: IntelligenceContext) -> float:
        """
        Calculate confidence score for tool selection.

        Based on intent reliability and tool availability.
        """
        base_confidence = 0.7

        # Boost confidence if tool exists in registry
        if self._tool_registry and tool_name in self._tool_registry:
            base_confidence += 0.2

        # Adjust based on intent type
        if intent == IntentType.UNKNOWN:
            base_confidence = 0.3

        return min(1.0, base_confidence)