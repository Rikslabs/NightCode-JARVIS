"""Subscriber registration."""

from typing import Iterable, List

from ..bus import EventBus
from .base import Subscriber, SubscriberError


class SubscriberRegistry:
    """Attach injected subscribers to an injected EventBus."""

    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus
        self._subscribers: List[Subscriber] = []

    def register(self, subscriber: Subscriber) -> None:
        if any(item.name == subscriber.name for item in self._subscribers):
            raise SubscriberError(f"subscriber already registered: {subscriber.name}")
        self._event_bus.register_handler(subscriber.as_event_handler())
        self._subscribers.append(subscriber)

    def register_all(self, subscribers: Iterable[Subscriber]) -> None:
        for subscriber in subscribers:
            self.register(subscriber)

    def unregister(self, name: str) -> bool:
        removed = self._event_bus.unregister_handler(name)
        if removed:
            self._subscribers = [item for item in self._subscribers if item.name != name]
        return removed

    def list_subscribers(self) -> List[str]:
        return [subscriber.name for subscriber in self._subscribers]
