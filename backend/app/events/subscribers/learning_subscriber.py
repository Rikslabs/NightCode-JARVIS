"""Learning event subscriber."""

from typing import Any

from ..models import Event
from .base import Subscriber


class LearningSubscriber(Subscriber):
    """Pass completed execution observations to an injected learning service."""

    def __init__(self, learning: Any):
        super().__init__(
            "learning_subscriber",
            ("execution.completed", "execution.failed"),
        )
        self._learning = learning

    def handle(self, event: Event) -> None:
        payload = event.payload
        self._learning.record_execution(
            tool_name=str(payload.get("tool_name", payload.get("module_name", "runtime"))),
            intent=str(payload.get("intent", payload.get("action", event.event_type))),
            success=event.event_type == "execution.completed",
            duration=float(payload.get("duration", payload.get("duration_ms", 0.0))),
            confidence=float(payload.get("confidence", 0.0)),
            risk=payload.get("risk"),
        )
