"""Runtime telemetry subscriber."""

from app.runtime.telemetry import RuntimeTelemetry

from ..models import Event
from .base import Subscriber


class RuntimeMonitor(Subscriber):
    """Reflect runtime lifecycle events into injected runtime telemetry."""

    def __init__(self, telemetry: RuntimeTelemetry):
        super().__init__(
            "runtime_monitor",
            ("runtime.started", "runtime.completed", "runtime.failed"),
        )
        self._telemetry = telemetry

    def handle(self, event: Event) -> None:
        execution_id = str(event.payload.get("execution_id", ""))
        if not execution_id:
            return
        if event.event_type == "runtime.started":
            self._telemetry.start_execution(
                execution_id,
                module_name=str(event.payload.get("module_name", "")),
                metadata=dict(event.payload.get("metadata", {})),
            )
        elif event.event_type == "runtime.completed":
            self._telemetry.finish_execution(execution_id, "completed")
        elif event.event_type == "runtime.failed":
            self._telemetry.finish_execution(execution_id, "failed")
