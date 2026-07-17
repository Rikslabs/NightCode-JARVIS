"""Workflow storage management for in-memory persistence."""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

from .models import Workflow
from .states import WorkflowState
from .events import WorkflowEvent, WorkflowEventType


@dataclass
class WorkflowStorageStatistics:
    """Statistics about workflow storage."""
    total_workflows: int = 0
    completed: int = 0
    failed: int = 0
    running: int = 0
    pending: int = 0
    rolled_back: int = 0

    def to_dict(self) -> dict[str, int]:
        """Convert statistics to dictionary."""
        return {
            'total_workflows': self.total_workflows,
            'completed': self.completed,
            'failed': self.failed,
            'running': self.running,
            'pending': self.pending,
            'rolled_back': self.rolled_back,
        }

    @classmethod
    def from_workflows(cls, workflows: dict[str, Workflow]) -> 'WorkflowStorageStatistics':
        """Create statistics from workflow dictionary."""
        stats = cls()
        stats.total_workflows = len(workflows)

        for workflow in workflows.values():
            if workflow.state == WorkflowState.COMPLETED:
                stats.completed += 1
            elif workflow.state == WorkflowState.FAILED:
                stats.failed += 1
            elif workflow.state == WorkflowState.RUNNING:
                stats.running += 1
            elif workflow.state == WorkflowState.PENDING:
                stats.pending += 1
            elif workflow.state == WorkflowState.ROLLED_BACK:
                stats.rolled_back += 1

        return stats


class WorkflowStorage:
    """In-memory storage for workflows."""

    def __init__(self):
        self._workflows: dict[str, Workflow] = {}

    def save_workflow(self, workflow: Workflow) -> None:
        """Save a workflow to storage."""
        self._workflows[workflow.id] = workflow

    def update_workflow(self, workflow: Workflow) -> bool:
        """Update an existing workflow in storage."""
        if workflow.id not in self._workflows:
            return False
        self._workflows[workflow.id] = workflow
        return True

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get a workflow by ID."""
        return self._workflows.get(workflow_id)

    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow from storage."""
        if workflow_id in self._workflows:
            del self._workflows[workflow_id]
            return True
        return False

    def list_workflows(self) -> list[Workflow]:
        """Get all workflows in deterministic order (by id)."""
        return [self._workflows[wf_id] for wf_id in sorted(self._workflows.keys())]

    def workflow_exists(self, workflow_id: str) -> bool:
        """Check if a workflow exists."""
        return workflow_id in self._workflows

    def clear(self) -> None:
        """Clear all workflows from storage."""
        self._workflows.clear()

    def statistics(self) -> WorkflowStorageStatistics:
        """Get statistics about stored workflows."""
        return WorkflowStorageStatistics.from_workflows(self._workflows)

    def to_dict(self) -> dict[str, Any]:
        """Serialize storage to dictionary."""
        return {wf_id: wf.to_dict() for wf_id, wf in self._workflows.items()}