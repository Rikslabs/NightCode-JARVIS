"""Event bus implementation."""

from typing import Any, Dict, List, Optional

from .dispatcher import EventDispatcher
from .models import Event, EventHandler
from .registry import EventRegistry
from .validator import EventValidator


class EventBus:
    """Unified event bus for system communication."""

    def __init__(
        self,
        registry: Optional[EventRegistry] = None,
        dispatcher: Optional[EventDispatcher] = None,
        validator: Optional[EventValidator] = None,
    ):
        self._registry = registry or EventRegistry()
        self._dispatcher = dispatcher or EventDispatcher(self._registry)
        self._validator = validator or EventValidator()
        self._published_events: List[Event] = []

    def register_handler(self, handler: EventHandler) -> None:
        """Register an event handler."""
        self._validator.validate_or_raise(handler=handler)
        self._registry.register(handler)

    def unregister_handler(self, name: str) -> bool:
        """Remove a handler by name."""
        return self._registry.unregister(name)

    def publish(self, event: Event) -> List[Any]:
        """Publish event to all matching handlers."""
        self._validator.validate_or_raise(event=event)
        self._published_events.append(event)
        results = self._dispatcher.dispatch_all(event)
        return [r.result for r in results if r.success]

    def emit(self, event: Event) -> Any:
        """Emit event to single handler (returns first result)."""
        self._validator.validate_or_raise(event=event)
        self._published_events.append(event)
        result = self._dispatcher.dispatch(event)
        return result.result

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Subscribe handler to event type."""
        if event_type not in handler.event_types:
            handler.event_types.append(event_type)
        self._registry.register(handler)

    def get_handlers(self, event_type: str) -> List[str]:
        """Get handler names for event type."""
        return [h.name for h in self._registry.get_handlers_for_type(event_type)]

    def get_published_events(self) -> List[Event]:
        """Get all published events."""
        return list(self._published_events)

    def clear_history(self) -> None:
        """Clear published events history."""
        self._published_events.clear()

    def get_registry(self) -> EventRegistry:
        """Get the underlying registry."""
        return self._registry

    def get_dispatcher(self) -> EventDispatcher:
        """Get the underlying dispatcher."""
        return self._dispatcher