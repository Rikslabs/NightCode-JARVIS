"""Event models."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional


@dataclass
class EventMetadata:
    """Event metadata."""

    correlation_id: Optional[str] = None
    priority: int = 0
    ttl_seconds: Optional[int] = None
    headers: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Event:
    """Base event class."""

    event_id: str
    event_type: str
    source: str
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Optional[EventMetadata] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class EventResult:
    """Event handling result."""

    event_id: str
    success: bool
    handler_name: Optional[str] = None
    error: Optional[str] = None
    result: Any = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class EventContext:
    """Context for event handling."""

    event: Event
    handler_names: List[str] = field(default_factory=list)
    is_handled: bool = False


@dataclass
class EventHandler:
    """Event handler registration."""

    name: str
    handler: Callable[[Event], Any]
    event_types: List[str] = field(default_factory=list)

    def can_handle(self, event_type: str) -> bool:
        """Check if handler can process this event type."""
        return event_type in self.event_types or not self.event_types