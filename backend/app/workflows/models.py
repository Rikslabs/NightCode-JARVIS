"""Workflow data models."""
from dataclasses import dataclass, field
from typing import Any, Optional
from datetime import datetime, timezone

from .states import WorkflowState


@dataclass
class WorkflowStep:
    """Represents a single step within a workflow."""
    id: str
    name: str
    description: str
    order: int
    status: WorkflowState = WorkflowState.PENDING
    result: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert step to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'order': self.order,
            'status': self.status.value,
            'result': self.result,
            'error': self.error,
            'metadata': self.metadata,
        }


@dataclass
class Workflow:
    """Represents a workflow with its steps and state."""
    id: str
    name: str
    description: str
    steps: list[WorkflowStep] = field(default_factory=list)
    current_step: Optional[int] = None
    state: WorkflowState = WorkflowState.PENDING
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert workflow to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'steps': [s.to_dict() for s in self.steps],
            'current_step': self.current_step,
            'state': self.state.value,
            'created_at': self.created_at,
            'completed_at': self.completed_at,
        }


@dataclass
class WorkflowContext:
    """Context for a workflow execution."""
    workflow_id: str
    project_path: str
    user_request: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert context to dictionary representation."""
        return {
            'workflow_id': self.workflow_id,
            'project_path': self.project_path,
            'user_request': self.user_request,
            'metadata': dict(self.metadata),
        }


@dataclass
class WorkflowResult:
    """Result of workflow execution."""
    success: bool
    workflow_id: str
    state: WorkflowState
    summary: str
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary representation."""
        return {
            'success': self.success,
            'workflow_id': self.workflow_id,
            'state': self.state.value,
            'summary': self.summary,
            'errors': list(self.errors),
        }