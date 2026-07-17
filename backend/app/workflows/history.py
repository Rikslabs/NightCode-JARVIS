"""Workflow history management for tracking events."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

from .events import WorkflowEvent, WorkflowEventType


@dataclass
class WorkflowHistory:
    """Manages workflow event history in memory."""
    _events: dict[str, list[WorkflowEvent]] = field(default_factory=dict)

    def append_event(self, event: WorkflowEvent) -> None:
        """Add an event to the history for a workflow."""
        workflow_id = event.workflow_id
        if workflow_id not in self._events:
            self._events[workflow_id] = []
        self._events[workflow_id].append(event)

    def list_events(self, workflow_id: str) -> list[WorkflowEvent]:
        """Get all events for a workflow in chronological order."""
        events = self._events.get(workflow_id, [])
        return sorted(events, key=lambda e: e.timestamp)

    def get_events(
        self,
        workflow_id: str,
        event_type: Optional[WorkflowEventType] = None,
        step: Optional[str] = None,
    ) -> list[WorkflowEvent]:
        """Get filtered events for a workflow."""
        events = self.list_events(workflow_id)
        if event_type is not None:
            events = [e for e in events if e.event_type == event_type]
        if step is not None:
            events = [e for e in events if e.step == step]
        return events

    def workflow_duration(self, workflow_id: str) -> Optional[float]:
        """Calculate workflow duration in seconds from events."""
        events = self.list_events(workflow_id)
        if len(events) < 2:
            return None

        # Find creation and completion/failure/rollback events
        sorted_events = sorted(events, key=lambda e: e.timestamp)
        start_time: Optional[datetime] = None
        end_time: Optional[datetime] = None

        for event in sorted_events:
            if event.event_type == WorkflowEventType.WORKFLOW_STARTED:
                start_time = event.timestamp
            elif event.event_type in (
                WorkflowEventType.WORKFLOW_COMPLETED,
                WorkflowEventType.WORKFLOW_FAILED,
                WorkflowEventType.WORKFLOW_ROLLED_BACK,
            ):
                end_time = event.timestamp
                break  # Take first terminal state

        if start_time is None or end_time is None:
            return None

        return (end_time - start_time).total_seconds()

    def summary(self, workflow_id: str) -> dict[str, Any]:
        """Get a summary of workflow events."""
        events = self.list_events(workflow_id)
        if not events:
            return {
                'workflow_id': workflow_id,
                'total_events': 0,
                'duration_seconds': None,
                'event_counts': {},
            }

        event_counts: dict[str, int] = {}
        for event in events:
            event_type = event.event_type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

        return {
            'workflow_id': workflow_id,
            'total_events': len(events),
            'duration_seconds': self.workflow_duration(workflow_id),
            'event_counts': event_counts,
            'first_event': events[0].to_dict() if events else None,
            'last_event': events[-1].to_dict() if events else None,
        }

    def clear(self) -> None:
        """Clear all history."""
        self._events.clear()

    def to_dict(self, workflow_id: Optional[str] = None) -> dict[str, Any]:
        """Serialize history to dictionary."""
        if workflow_id is not None:
            return {workflow_id: [e.to_dict() for e in self.list_events(workflow_id)]}

        result = {}
        for wf_id, events in self._events.items():
            result[wf_id] = [e.to_dict() for e in self.list_events(wf_id)]
        return result