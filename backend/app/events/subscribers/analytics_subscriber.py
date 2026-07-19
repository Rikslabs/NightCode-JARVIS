"""Metrics-only event subscriber."""

from typing import Any

from ..models import Event
from .base import Subscriber


class AnalyticsSubscriber(Subscriber):
    """Record one metric for each observed runtime event."""

    EVENT_TYPES = (
        "runtime.started", "runtime.completed", "runtime.failed",
        "execution.started", "execution.completed", "execution.failed",
        "task.scheduled", "task.started", "task.completed", "task.failed",
    )

    def __init__(self, metrics: Any):
        super().__init__("analytics_subscriber", self.EVENT_TYPES)
        self._metrics = metrics

    def handle(self, event: Event) -> None:
        self._metrics.record_metric(
            event.event_type,
            1,
            {"source": event.source},
        )
