"""Event dispatcher."""

from typing import Any, List, Optional

from .models import Event, EventResult, EventContext
from .registry import EventRegistry


class EventDispatcher:
    """Dispatches events to registered handlers."""

    def __init__(self, registry: Optional[EventRegistry] = None):
        self._registry = registry or EventRegistry()

    def dispatch(self, event: Event) -> EventResult:
        """Dispatch event to a single handler."""
        handlers = self._registry.get_handlers_for_type(event.event_type)
        if not handlers:
            return EventResult(
                event_id=event.event_id,
                success=False,
                error=f"No handler registered for event type: {event.event_type}",
            )

        handler = handlers[0]
        try:
            result = handler.handler(event)
            return EventResult(
                event_id=event.event_id,
                success=True,
                handler_name=handler.name,
                result=result,
            )
        except Exception as exc:
            return EventResult(
                event_id=event.event_id,
                success=False,
                handler_name=handler.name,
                error=str(exc),
            )

    def dispatch_all(self, event: Event) -> List[EventResult]:
        """Dispatch event to all matching handlers."""
        handlers = self._registry.get_handlers_for_type(event.event_type)
        if not handlers:
            return [
                EventResult(
                    event_id=event.event_id,
                    success=False,
                    error=f"No handler registered for event type: {event.event_type}",
                )
            ]

        results = []
        for handler in handlers:
            try:
                result = handler.handler(event)
                results.append(
                    EventResult(
                        event_id=event.event_id,
                        success=True,
                        handler_name=handler.name,
                        result=result,
                    )
                )
            except Exception as exc:
                results.append(
                    EventResult(
                        event_id=event.event_id,
                        success=False,
                        handler_name=handler.name,
                        error=str(exc),
                    )
                )
        return results

    def get_registry(self) -> EventRegistry:
        """Get the underlying registry."""
        return self._registry