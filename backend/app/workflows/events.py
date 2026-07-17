"""Workflow event types and data structures."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import uuid4, UUID


class WorkflowEventType(Enum):
    """Enumeration of workflow event types for history tracking."""
    WORKFLOW_CREATED = 'workflow_created'
    WORKFLOW_STARTED = 'workflow_started'
    WORKFLOW_PAUSED = 'workflow_paused'
    WORKFLOW_RESUMED = 'workflow_resumed'
    STEP_STARTED = 'step_started'
    STEP_COMPLETED = 'step_completed'
    STEP_FAILED = 'step_failed'
    APPROVAL_REQUIRED = 'approval_required'
    APPROVAL_GRANTED = 'approval_granted'
    APPROVAL_DENIED = 'approval_denied'
    WORKFLOW_COMPLETED = 'workflow_completed'
    WORKFLOW_FAILED = 'workflow_failed'
    WORKFLOW_ROLLED_BACK = 'workflow_rolled_back'


@dataclass
class WorkflowEvent:
    """Represents an event in workflow history."""
    id: UUID
    workflow_id: str
    event_type: WorkflowEventType
    timestamp: datetime
    step: Optional[str] = None
    message: str = ''
    metadata: Optional[dict[str, Any]] = None

    def __post_init__(self):
        """Ensure timezone-aware timestamp."""
        if self.timestamp.tzinfo is None:
            self.timestamp = self.timestamp.replace(tzinfo=timezone.utc)

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary representation."""
        return {
            'id': str(self.id),
            'workflow_id': self.workflow_id,
            'event_type': self.event_type.value,
            'timestamp': self.timestamp.isoformat(),
            'step': self.step,
            'message': self.message,
            'metadata': dict(self.metadata) if self.metadata else None,
        }

    @classmethod
    def create(
        cls,
        workflow_id: str,
        event_type: WorkflowEventType,
        step: Optional[str] = None,
        message: str = '',
        metadata: Optional[dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
    ) -> 'WorkflowEvent':
        """Factory method to create a workflow event with auto-generated ID and timestamp."""
        return cls(
            id=uuid4(),
            workflow_id=workflow_id,
            event_type=event_type,
            timestamp=timestamp if timestamp else datetime.now(timezone.utc),
            step=step,
            message=message,
            metadata=metadata,
        )
