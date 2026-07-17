"""Workflow scheduler - manages multiple workflow execution."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from .models import Workflow, WorkflowContext
from .queue import WorkflowQueue
from .executor import WorkflowExecutor
from .storage import WorkflowStorage
from .history import WorkflowHistory
from .metrics import WorkflowMetrics
from .dispatcher import WorkflowDispatcher, DispatchResult


@dataclass
class ScheduledWorkflow:
    """A scheduled workflow entry."""
    workflow: Workflow
    context: WorkflowContext
    queue_id: str


class WorkflowScheduler:
    """Manages workflow execution scheduling."""

    def __init__(
        self,
        executor: WorkflowExecutor,
        storage: WorkflowStorage,
        history: WorkflowHistory,
        metrics: Optional[WorkflowMetrics] = None,
    ):
        self._queue = WorkflowQueue()
        self._dispatcher = WorkflowDispatcher(executor, history)
        self._storage = storage
        self._metrics = metrics if metrics else WorkflowMetrics()
        self._executor = executor  # Store for pause/resume
        self._active_workflow: Optional[Workflow] = None
        self._active_context: Optional[WorkflowContext] = None
        self._completed: list[Workflow] = []
        self._failed: list[Workflow] = []
        self._last_execution_time: Optional[datetime] = None

    def submit(
        self,
        workflow: Workflow,
        context: WorkflowContext,
        priority: int = 2,  # NORMAL
    ) -> str:
        """Submit a workflow for scheduling."""
        self._metrics.record('submitted')
        self._storage.save_workflow(workflow)
        return self._queue.enqueue(workflow, context, priority)

    def start_next(self) -> Optional[DispatchResult]:
        """Start the next workflow in the queue."""
        if self._active_workflow is not None:
            return None  # Already running

        next_item = self._queue.dequeue()
        if next_item is None:
            return None

        workflow, context = next_item
        self._active_workflow = workflow
        self._active_context = context

        # Record queue wait time
        if self._last_execution_time is not None:
            wait_time = (datetime.now(timezone.utc) - self._last_execution_time).total_seconds()
            self._metrics.record('started', queue_wait=wait_time)

        result = self._dispatcher.dispatch(workflow, context)

        if result.success:
            self._completed.append(workflow)
            self._metrics.record('completed')
        else:
            self._failed.append(workflow)
            self._metrics.record('failed')

        self._active_workflow = None
        self._active_context = None
        self._last_execution_time = datetime.now(timezone.utc)

        return result

    def pause(self) -> bool:
        """Pause the current workflow."""
        if self._active_workflow is None:
            return False
        return self._executor.pause_for_approval(self._active_workflow.id)

    def resume(self) -> bool:
        """Resume a paused workflow."""
        if self._active_workflow is None:
            return False
        return self._executor.resume(self._active_workflow.id)

    def cancel(self, workflow_id: str) -> bool:
        """Cancel a workflow."""
        # Try to remove from queue first
        if self._queue.remove(workflow_id):
            self._metrics.record('cancelled')
            return True

        # Try to cancel active workflow
        if self._active_workflow is not None and self._active_workflow.id == workflow_id:
            self._active_workflow = None
            self._active_context = None
            self._metrics.record('cancelled')
            return True

        return False

    def shutdown(self) -> None:
        """Shutdown the scheduler, clearing all queues."""
        self._queue.clear()
        self._active_workflow = None
        self._active_context = None

    def restart(self) -> None:
        """Restart the scheduler."""
        self.shutdown()
        self._completed.clear()
        self._failed.clear()
        self._last_execution_time = None

    def active_workflow(self) -> Optional[Workflow]:
        """Return the currently active workflow."""
        return self._active_workflow

    def pending_workflows(self) -> list[Workflow]:
        """Return all pending workflows."""
        return [q.workflow for q in self._queue.list_pending()]

    def completed_workflows(self) -> list[Workflow]:
        """Return all completed workflows."""
        return list(self._completed)

    def failed_workflows(self) -> list[Workflow]:
        """Return all failed workflows."""
        return list(self._failed)

    def to_dict(self) -> dict[str, Any]:
        """Serialize scheduler state to dictionary."""
        return {
            'queue': self._queue.to_dict(),
            'active_workflow': self._active_workflow.to_dict() if self._active_workflow else None,
            'pending_count': len(self.pending_workflows()),
            'completed_count': len(self._completed),
            'failed_count': len(self._failed),
        }