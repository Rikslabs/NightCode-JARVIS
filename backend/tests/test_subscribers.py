"""Focused tests for passive event subscribers."""

from unittest.mock import Mock

from app.events import Event, EventBus, EventHandler
from app.events.subscribers import (
    AnalyticsSubscriber, ExperienceSubscriber, LearningSubscriber,
    RuntimeMonitor, SubscriberRegistry,
)
from app.runtime import RuntimeTelemetry


def event(kind, **payload):
    return Event(event_id="event-1", event_type=kind, source="runtime", payload=payload)


def test_registry_wires_subscribers_and_failures_are_isolated():
    bus = EventBus()
    learning = Mock()
    registry = SubscriberRegistry(bus)
    registry.register(LearningSubscriber(learning))
    bus.register_handler(EventHandler("broken", Mock(side_effect=RuntimeError("boom")), ["execution.completed"]))
    metrics = Mock()
    registry.register(AnalyticsSubscriber(metrics))

    bus.publish(event("execution.completed", tool_name="review", intent="review"))

    learning.record_execution.assert_called_once()
    metrics.record_metric.assert_called_once()


def test_runtime_monitor_records_lifecycle():
    telemetry = RuntimeTelemetry()
    monitor = RuntimeMonitor(telemetry)
    monitor.handle(event("runtime.started", execution_id="exec-1", module_name="browser"))
    monitor.handle(event("runtime.completed", execution_id="exec-1"))
    assert telemetry.get_record("exec-1").status == "completed"


def test_experience_uses_injected_factory_and_public_add():
    experience = Mock()
    record = object()
    subscriber = ExperienceSubscriber(experience, lambda observed: record)
    subscriber.handle(event("execution.failed"))
    experience.add.assert_called_once_with(record)


def test_analytics_only_records_metric():
    metrics = Mock()
    AnalyticsSubscriber(metrics).handle(event("task.completed", task_id="task-1"))
    metrics.record_metric.assert_called_once_with("task.completed", 1, {"source": "runtime"})
