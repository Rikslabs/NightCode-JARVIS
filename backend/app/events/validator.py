"""Event validation."""

from typing import Any, Dict, List, Optional, Tuple

from .models import Event, EventMetadata, EventHandler


class EventValidationError(Exception):
    """Event validation error."""
    pass


class EventValidator:
    """Validates events and handlers."""

    def __init__(self):
        self._errors: List[str] = []

    def validate_event(self, event: Event) -> Tuple[bool, Optional[str]]:
        """Validate an event. Returns (is_valid, error_message)."""
        if not event.event_id:
            return False, "event_id is required"
        if not event.event_type:
            return False, "event_type is required"
        if not event.source:
            return False, "source is required"
        return True, None

    def validate_payload(self, event: Event, schema: Optional[Dict[str, Any]] = None) -> Tuple[bool, Optional[str]]:
        """Validate event payload against optional schema."""
        if schema is None:
            return True, None
        for key, expected_type in schema.items():
            if key not in event.payload:
                return False, f"Missing required payload key: {key}"
            if not isinstance(event.payload[key], expected_type):
                return False, f"Invalid type for {key}, expected {expected_type}"
        return True, None

    def validate_metadata(self, metadata: Optional[EventMetadata]) -> Tuple[bool, Optional[str]]:
        """Validate event metadata."""
        if metadata is None:
            return True, None
        return True, None

    def validate_handler_registration(self, handler: EventHandler) -> Tuple[bool, Optional[str]]:
        """Validate handler for registration."""
        if not handler.name:
            return False, "handler name is required"
        if handler.handler is None:
            return False, "handler callable is required"
        return True, None

    def validate_or_raise(
        self,
        event: Optional[Event] = None,
        payload_schema: Optional[Dict[str, Any]] = None,
        handler: Optional[EventHandler] = None,
    ) -> None:
        """Validate and raise EventValidationError on failure."""
        if event is not None:
            valid, error = self.validate_event(event)
            if not valid:
                raise EventValidationError(f"Invalid event: {error}")
            valid, error = self.validate_payload(event, payload_schema)
            if not valid:
                raise EventValidationError(f"Invalid payload: {error}")

        if handler is not None:
            valid, error = self.validate_handler_registration(handler)
            if not valid:
                raise EventValidationError(f"Invalid handler: {error}")