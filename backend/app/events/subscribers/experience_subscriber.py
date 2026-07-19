"""Experience event subscriber."""

from typing import Any, Callable

from ..models import Event
from .base import Subscriber


class ExperienceSubscriber(Subscriber):
    """Store completed execution observations using an injected public API."""

    def __init__(self, experience: Any, record_factory: Callable[[Event], Any]):
        super().__init__(
            "experience_subscriber",
            ("execution.completed", "execution.failed"),
        )
        self._experience = experience
        self._record_factory = record_factory

    def handle(self, event: Event) -> None:
        self._experience.add(self._record_factory(event))
