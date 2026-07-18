"""Runtime event types."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def _make_event_id(prefix: str) -> str:
    return f"evt-{prefix}-{datetime.now(timezone.utc).isoformat()}"


@dataclass
class RuntimeStarted:
    """Event emitted when runtime starts."""
    event_id: str = field(default_factory=lambda: _make_event_id("runtime-started"))
    event_type: str = "runtime.started"
    source: str = "runtime"
    payload: Dict[str, Any] = field(default_factory=lambda: {})
    execution_id: str = ""
    module_name: str = ""


@dataclass
class RuntimeCompleted:
    """Event emitted when runtime completes successfully."""
    event_id: str = field(default_factory=lambda: _make_event_id("runtime-completed"))
    event_type: str = "runtime.completed"
    source: str = "runtime"
    payload: Dict[str, Any] = field(default_factory=lambda: {})
    execution_id: str = ""
    result: Any = None


@dataclass
class RuntimeFailed:
    """Event emitted when runtime fails."""
    event_id: str = field(default_factory=lambda: _make_event_id("runtime-failed"))
    event_type: str = "runtime.failed"
    source: str = "runtime"
    payload: Dict[str, Any] = field(default_factory=lambda: {})
    execution_id: str = ""
    error: str = ""


@dataclass
class ExecutionStarted:
    """Event emitted when execution starts."""
    event_id: str = field(default_factory=lambda: _make_event_id("execution-started"))
    event_type: str = "execution.started"
    source: str = "runtime"
    payload: Dict[str, Any] = field(default_factory=lambda: {})
    execution_id: str = ""
    request_id: str = ""


@dataclass
class ExecutionCompleted:
    """Event emitted when execution completes."""
    event_id: str = field(default_factory=lambda: _make_event_id("execution-completed"))
    event_type: str = "execution.completed"
    source: str = "runtime"
    payload: Dict[str, Any] = field(default_factory=lambda: {})
    execution_id: str = ""
    result: Any = None


@dataclass
class ExecutionFailed:
    """Event emitted when execution fails."""
    event_id: str = field(default_factory=lambda: _make_event_id("execution-failed"))
    event_type: str = "execution.failed"
    source: str = "runtime"
    payload: Dict[str, Any] = field(default_factory=lambda: {})
    execution_id: str = ""
    error: str = ""


@dataclass
class TaskScheduled:
    """Event emitted when a task is scheduled."""
    event_id: str = field(default_factory=lambda: _make_event_id("task-scheduled"))
    event_type: str = "task.scheduled"
    source: str = "runtime"
    payload: Dict[str, Any] = field(default_factory=lambda: {})
    execution_id: str = ""
    task_id: str = ""


@dataclass
class TaskStarted:
    """Event emitted when a task starts."""
    event_id: str = field(default_factory=lambda: _make_event_id("task-started"))
    event_type: str = "task.started"
    source: str = "runtime"
    payload: Dict[str, Any] = field(default_factory=lambda: {})
    execution_id: str = ""
    task_id: str = ""


@dataclass
class TaskCompleted:
    """Event emitted when a task completes."""
    event_id: str = field(default_factory=lambda: _make_event_id("task-completed"))
    event_type: str = "task.completed"
    source: str = "runtime"
    payload: Dict[str, Any] = field(default_factory=lambda: {})
    execution_id: str = ""
    task_id: str = ""
    result: Any = None


@dataclass
class TaskFailed:
    """Event emitted when a task fails."""
    event_id: str = field(default_factory=lambda: _make_event_id("task-failed"))
    event_type: str = "task.failed"
    source: str = "runtime"
    payload: Dict[str, Any] = field(default_factory=lambda: {})
    execution_id: str = ""
    task_id: str = ""
    error: str = ""