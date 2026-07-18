"""Main orchestrator for the Intelligence layer."""

from typing import Any, Optional

from .models import (
    ExecutionDecision,
    ExecutionPlan,
    IntentAnalysis,
    ReasoningContext,
    ReasoningResult,
)
from .reasoner import IntentReasoner
from .planner import ExecutionPlanner
from .selector import ToolSelector
from .validator import ExecutionValidator
from .context import IntelligenceContext


class IntelligenceOrchestrator:
    """
    The thinking process between the Brain and the existing Workflow/Tool system.

    Implements the flow:
    Understand -> Reason -> Plan -> Select Tool -> Execute -> Verify
    """

    def __init__(
        self,
        reasoner: Optional[IntentReasoner] = None,
        planner: Optional[ExecutionPlanner] = None,
        selector: Optional[ToolSelector] = None,
        validator: Optional[ExecutionValidator] = None,
    ):
        """
        Initialize the orchestrator with optional dependency injection.

        Args:
            reasoner: Intent reasoner component.
            planner: Execution planner component.
            selector: Tool selector component.
            validator: Execution validator component.
        """
        self._reasoner = reasoner or IntentReasoner()
        self._planner = planner or ExecutionPlanner()
        self._selector = selector or ToolSelector()
        self._validator = validator or ExecutionValidator()

    def process(self, request: str, context: Optional[IntelligenceContext] = None) -> ReasoningResult:
        """
        Process a request through the intelligence pipeline.

        Args:
            request: The natural language request.
            context: Optional intelligence context.

        Returns:
            ReasoningResult with the complete analysis and plan.
        """
        # Create context if not provided
        if context is None:
            context = IntelligenceContext()

        # Create reasoning context
        reasoning_context = ReasoningContext(
            request=request,
            project_path=context.project_path,
            user_id=context.user_id,
            session_id=context.session_id,
            metadata=context.metadata,
        )

        # Step 1: Understand - Analyze intent
        intent_analysis = self._reasoner.analyze(reasoning_context)
        context.add_to_history("intent_analyzed", intent_analysis.to_dict())

        # Step 2: Plan - Create execution plan
        execution_plan = self._planner.create_plan(intent_analysis, reasoning_context)
        context.add_to_history("plan_created", execution_plan.to_dict())

        # Step 3: Select - Choose tool
        execution_decision = self._selector.select(execution_plan, context)
        context.add_to_history("tool_selected", execution_decision.to_dict())

        return ReasoningResult(
            intent_analysis=intent_analysis,
            execution_plan=execution_plan,
            execution_decision=execution_decision,
        )