"""Workflow metrics tracking for runtime statistics."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4


@dataclass
class DispatchResult:
    """Result of a dispatch operation."""
    success: bool
    workflow_id: str
    message: str
    retry_count: int = 0


@dataclass
class WorkflowMetrics:
    """Tracks workflow execution metrics."""
    submitted: int = 0
    completed: int = 0
    failed: int = 0
    cancelled: int = 0
    retried: int = 0
    total_execution_time: float = 0.0
    total_queue_wait: float = 0.0
    approval_count: int = 0
    total_approval_wait: float = 0.0
    _executions: list[dict[str, Any]] = field(default_factory=list)

    def record(
        self,
        event_type: str,
        execution_time: Optional[float] = None,
        queue_wait: Optional[float] = None,
        approval_wait: Optional[float] = None,
        retry_count: int = 0,
    ) -> None:
        """Record a workflow event."""
        if event_type == 'submitted':
            self.submitted += 1
        elif event_type == 'completed':
            self.completed += 1
            if execution_time is not None:
                self.total_execution_time += execution_time
        elif event_type == 'failed':
            self.failed += 1
        elif event_type == 'cancelled':
            self.cancelled += 1
        elif event_type == 'retried':
            self.retried += retry_count if retry_count > 0 else 1

        if queue_wait is not None:
            self.total_queue_wait += queue_wait
        if approval_wait is not None:
            self.total_approval_wait += approval_wait
            self.approval_count += 1

        self._executions.append({
            'event': event_type,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'execution_time': execution_time,
            'queue_wait': queue_wait,
            'approval_wait': approval_wait,
        })

    def record_approval(self, approval_wait: float) -> None:
        """Record an approval event."""
        self.approval_count += 1
        self.total_approval_wait += approval_wait

    def average_execution_time(self) -> Optional[float]:
        """Calculate average execution time."""
        if self.completed == 0:
            return None
        return self.total_execution_time / self.completed

    def average_queue_wait(self) -> Optional[float]:
        """Calculate average queue wait time."""
        total_submitted = self.submitted - self.cancelled
        if total_submitted <= 0:
            return None
        return self.total_queue_wait / total_submitted

    def average_approval_wait(self) -> Optional[float]:
        """Calculate average approval wait time."""
        if self.approval_count == 0:
            return None
        return self.total_approval_wait / self.approval_count

    def success_rate(self) -> float:
        """Calculate success rate as a percentage."""
        if self.submitted == 0:
            return 0.0
        return (self.completed / self.submitted) * 100.0

    def summary(self) -> dict[str, Any]:
        """Get a summary of all metrics."""
        return {
            'submitted': self.submitted,
            'completed': self.completed,
            'failed': self.failed,
            'cancelled': self.cancelled,
            'retried': self.retried,
            'success_rate': self.success_rate(),
            'average_execution_time': self.average_execution_time(),
            'average_queue_wait': self.average_queue_wait(),
            'average_approval_wait': self.average_approval_wait(),
            'total_approvals': self.approval_count,
        }

    def reset(self) -> None:
        """Reset all metrics to initial values."""
        self.submitted = 0
        self.completed = 0
        self.failed = 0
        self.cancelled = 0
        self.retried = 0
        self.total_execution_time = 0.0
        self.total_queue_wait = 0.0
        self.approval_count = 0
        self.total_approval_wait = 0.0
        self._executions.clear()

    def to_dict(self) -> dict[str, Any]:
        """Serialize metrics to dictionary."""
        return {
            'submitted': self.submitted,
            'completed': self.completed,
            'failed': self.failed,
            'cancelled': self.cancelled,
            'retried': self.retried,
            'average_execution_time': self.average_execution_time(),
            'average_queue_wait': self.average_queue_wait(),
            'average_approval_wait': self.average_approval_wait(),
            'success_rate': self.success_rate(),
            'approval_count': self.approval_count,
        }