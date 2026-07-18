"""Event handler registry."""

from typing import Any, Dict, List, Optional

from .models import Event, EventHandler


class EventRegistry:
    """Maintains handler registry."""

    def __init__(self):
        self._handlers: Dict[str, EventHandler] = {}
        self._type_handlers: Dict[str, List[EventHandler]] = {}

    def register(self, handler: EventHandler) -> None:
        """Register an event handler."""
        self._handlers[handler.name] = handler
        for event_type in handler.event_types:
            if event_type not in self._type_handlers:
                self._type_handlers[event_type] = []
            self._type_handlers[event_type].append(handler)

    def unregister(self, name: str) -> bool:
        """Remove a handler by name."""
        handler = self._handlers.pop(name, None)
        if handler is None:
            return False
        for event_type in handler.event_types:
            if event_type in self._type_handlers:
                self._type_handlers[event_type] = [
                    h for h in self._type_handlers[event_type] if h.name != name
                ]
        return True

    def get(self, name: str) -> Optional[EventHandler]:
        """Get handler by name."""
        return self._handlers.get(name)

    def get_handlers_for_type(self, event_type: str) -> List[EventHandler]:
        """Get all handlers that can handle this event type."""
        return list(self._type_handlers.get(event_type, []))

    def list_handlers(self) -> List[str]:
        """List all registered handler names."""
        return list(self._handlers.keys())

    def clear(self) -> None:
        """Clear all handlers."""
        self._handlers.clear()
        self._type_handlers.clear()
        self._type_handlers = {}

    def has_handler(self, event_type: str) -> bool:
        """Check if any handler exists for event type."""
        return event_type in self._type_handlers and len(self._type_handlers[event_type]) > 0