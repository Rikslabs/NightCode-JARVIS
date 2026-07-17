"""Workflow queue for managing pending workflow execution."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from .models import Workflow, WorkflowContext


class WorkflowPriority:
    """Priority levels for workflow queue."""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


@dataclass
class QueuedWorkflow:
    """A workflow waiting to be executed."""
    id: str
    workflow: Workflow
    context: WorkflowContext
    priority: int
    queued_at: str


class WorkflowQueue:
    """FIFO priority queue for workflow execution."""

    def __init__(self):
        self._queue: list[tuple[int, QueuedWorkflow]] = []  # (insertion_order, queued_workflow)
        self._counter: int = 0

    def enqueue(
        self,
        workflow: Workflow,
        context: WorkflowContext,
        priority: int = WorkflowPriority.NORMAL,
    ) -> str:
        """Add a workflow to the queue."""
        queued = QueuedWorkflow(
            id=str(uuid4()),
            workflow=workflow,
            context=context,
            priority=priority,
            queued_at=datetime.now(timezone.utc).isoformat(),
        )
        self._counter += 1
        self._queue.append((self._counter, queued))
        # Sort by priority (ascending), then by insertion order (ascending)
        self._queue.sort(key=lambda x: (x[1].priority, x[0]))
        return queued.id

    def dequeue(self) -> Optional[tuple[Workflow, WorkflowContext]]:
        """Remove and return the next workflow from the queue."""
        if not self._queue:
            return None
        _, queued = self._queue.pop(0)
        return (queued.workflow, queued.context)

    def peek(self) -> Optional[tuple[Workflow, WorkflowContext]]:
        """Return the next workflow without removing it."""
        if not self._queue:
            return None
        return (self._queue[0][1].workflow, self._queue[0][1].context)

    def cancel(self, queue_id: str) -> bool:
        """Remove a workflow from the queue by ID."""
        for i, (_, queued) in enumerate(self._queue):
            if queued.id == queue_id:
                del self._queue[i]
                return True
        return False

    def clear(self) -> None:
        """Remove all workflows from the queue."""
        self._queue.clear()

    def size(self) -> int:
        """Return the number of workflows in the queue."""
        return len(self._queue)

    def list_pending(self) -> list[QueuedWorkflow]:
        """Return all pending workflows in priority order."""
        return [q for _, q in self._queue]

    def contains(self, workflow_id: str) -> bool:
        """Check if a workflow is in the queue."""
        return any(q.workflow.id == workflow_id for _, q in self._queue)

    def remove(self, workflow_id: str) -> bool:
        """Remove a workflow from the queue by workflow ID."""
        for i, (_, queued) in enumerate(self._queue):
            if queued.workflow.id == workflow_id:
                del self._queue[i]
                return True
        return False

    def to_dict(self) -> list[dict]:
        """Serialize queue to dictionary."""
        return [
            {
                'id': q.id,
                'workflow_id': q.workflow.id,
                'priority': q.priority,
                'queued_at': q.queued_at,
            }
            for _, q in self._queue
        ]