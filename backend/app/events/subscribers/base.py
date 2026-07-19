"""Common subscriber adapter."""

from abc import ABC, abstractmethod
from typing import Iterable, Tuple

from ..models import Event, EventHandler


class SubscriberError(Exception):
    """Raised when a subscriber cannot be registered."""


class Subscriber(ABC):
    """A passive event consumer that can be attached to an EventBus."""

    def __init__(self, name: str, event_types: Iterable[str]):
        types = tuple(event_types)
        if not name or not types:
            raise SubscriberError("subscriber name and event types are required")
        self._name = name
        self._event_types = types

    @property
    def name(self) -> str:
        return self._name

    @property
    def event_types(self) -> Tuple[str, ...]:
        return self._event_types

    @abstractmethod
    def handle(self, event: Event) -> None:
        """Observe an event without affecting execution."""

    def as_event_handler(self) -> EventHandler:
        """Expose this subscriber through the existing EventBus API."""
        return EventHandler(
            name=self.name,
            handler=self.handle,
            event_types=list(self.event_types),
        )
