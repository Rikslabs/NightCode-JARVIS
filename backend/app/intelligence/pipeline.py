"""Intelligence pipeline - the complete thinking process."""

from typing import Any, Optional

from .models import ReasoningResult, VerificationResult, ReasoningContext
from .orchestrator import IntelligenceOrchestrator
from .context import IntelligenceContext
from .validator import ExecutionValidator
from .selector import ToolSelector


class IntelligencePipeline:
    """
    Complete pipeline for the Intelligence Orchestrator.

    Implements the full flow:
    Understand -> Reason -> Plan -> Select Tool -> Execute -> Verify -> Respond
    """

    def __init__(
        self,
        orchestrator: Optional[IntelligenceOrchestrator] = None,
        validator: Optional[ExecutionValidator] = None,
        tool_executor: Optional[Any] = None,
    ):
        """
        Initialize the pipeline.

        Args:
            orchestrator: The intelligence orchestrator.
            validator: The execution validator.
            tool_executor: Optional tool executor function for dependency injection.
        """
        self._orchestrator = orchestrator or IntelligenceOrchestrator()
        self._validator = validator or ExecutionValidator()
        self._tool_executor = tool_executor

    def execute(
        self,
        request: str,
        context: Optional[IntelligenceContext] = None,
    ) -> tuple[ReasoningResult, Optional[VerificationResult]]:
        """
        Execute a request through the full pipeline.

        Args:
            request: The natural language request.
            context: Optional intelligence context.

        Returns:
            Tuple of ReasoningResult and optional VerificationResult.
        """
        # Step 1-3: Reason and plan (via orchestrator)
        result = self._orchestrator.process(request, context)

        # Step 4-6: Execute and verify
        if self._tool_executor is not None:
            execution_result = self._execute_tool(result)
            verification = self._verify_execution(result, execution_result)
        else:
            verification = None

        return result, verification

    def _execute_tool(self, reasoning_result: ReasoningResult) -> Any:
        """
        Execute the selected tool.

        Args:
            reasoning_result: The reasoning result containing the execution decision.

        Returns:
            The result from the tool execution.
        """
        if self._tool_executor is None:
            return None

        decision = reasoning_result.execution_decision
        return self._tool_executor(decision.tool_name, **decision.parameters)

    def _verify_execution(
        self,
        reasoning_result: ReasoningResult,
        execution_result: Any,
    ) -> VerificationResult:
        """
        Verify the execution result.

        Args:
            reasoning_result: The reasoning result.
            execution_result: The result from tool execution.

        Returns:
            VerificationResult with verification status.
        """
        return self._validator.verify(
            decision=reasoning_result.execution_decision,
            result=execution_result,
            plan=reasoning_result.execution_plan,
        )