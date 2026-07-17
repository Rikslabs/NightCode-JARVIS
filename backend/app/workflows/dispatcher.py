"""Workflow dispatcher - bridges scheduler to executor."""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

from .models import Workflow, WorkflowContext, WorkflowResult
from .executor import WorkflowExecutor
from .events import WorkflowEventType
from .history import WorkflowHistory


@dataclass
class DispatchResult:
    """Result of a dispatch operation."""
    success: bool
    workflow_id: str
    message: str
    retry_count: int = 0


class WorkflowDispatcher:
    """Bridge between scheduler and executor."""

    def __init__(self, executor: WorkflowExecutor, history: Optional[WorkflowHistory] = None):
        self._executor = executor
        self._history = history
        self._retry_counts: dict[str, int] = {}

    def dispatch(
        self,
        workflow: Workflow,
        context: WorkflowContext,
        max_retries: int = 3,
    ) -> DispatchResult:
        """Dispatch a workflow for execution."""
        workflow_id = workflow.id

        # Initialize retry count if not present
        if workflow_id not in self._retry_counts:
            self._retry_counts[workflow_id] = 0

        result = self._executor.execute(workflow, context)

        if result is None:
            return DispatchResult(
                success=False,
                workflow_id=workflow_id,
                message='Execution returned no result',
                retry_count=self._retry_counts[workflow_id],
            )

        return DispatchResult(
            success=result.success,
            workflow_id=workflow_id,
            message=result.summary,
            retry_count=self._retry_counts[workflow_id],
        )

    def dispatch_next(self) -> Optional[DispatchResult]:
        """Dispatch the next queued workflow (to be called by scheduler)."""
        # This is a placeholder - actual queue handling is in scheduler
        return None

    def retry(
        self,
        workflow: Workflow,
        context: WorkflowContext,
        max_retries: int = 3,
    ) -> DispatchResult:
        """Retry a failed workflow."""
        workflow_id = workflow.id

        # Increment retry count
        current_retries = self._retry_counts.get(workflow_id, 0)

        if current_retries >= max_retries:
            return DispatchResult(
                success=False,
                workflow_id=workflow_id,
                message=f'Max retries ({max_retries}) exceeded',
                retry_count=current_retries,
            )

        self._retry_counts[workflow_id] = current_retries + 1

        result = self._executor.execute(workflow, context)

        if result is None:
            return DispatchResult(
                success=False,
                workflow_id=workflow_id,
                message='Execution returned no result',
                retry_count=self._retry_counts[workflow_id],
            )

        return DispatchResult(
            success=result.success,
            workflow_id=workflow_id,
            message=result.summary,
            retry_count=self._retry_counts[workflow_id],
        )

    def abort(self, workflow_id: str) -> bool:
        """Abort a workflow dispatch."""
        if workflow_id in self._retry_counts:
            del self._retry_counts[workflow_id]
            return True
        return False

    def dispatch_status(self, workflow_id: str) -> Optional[dict[str, Any]]:
        """Get the dispatch status for a workflow."""
        # Get execution status from executor
        status = self._executor.get_execution_status(workflow_id)
        if status is not None:
            status['retry_count'] = self._retry_counts.get(workflow_id, 0)
        return status

    def to_dict(self) -> dict[str, Any]:
        """Serialize dispatcher state to dictionary."""
        return {
            'retry_counts': dict(self._retry_counts),
        }