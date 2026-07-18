"""Tests for Event Bus Foundation."""

import pytest

from app.events.models import (
    Event,
    EventResult,
    EventContext,
    EventMetadata,
    EventHandler,
)
from app.events.bus import EventBus
from app.events.dispatcher import EventDispatcher
from app.events.registry import EventRegistry
from app.events.validator import EventValidator, EventValidationError


# ============================================
# Event Models Tests
# ============================================

class TestEventMetadata:
    def test_create_metadata(self):
        metadata = EventMetadata(correlation_id="corr-1", priority=5)
        assert metadata.correlation_id == "corr-1"
        assert metadata.priority == 5

    def test_default_metadata(self):
        metadata = EventMetadata()
        assert metadata.correlation_id is None
        assert metadata.priority == 0


class TestEvent:
    def test_create_event(self):
        event = Event(event_id="evt-1", event_type="user_action", source="api")
        assert event.event_id == "evt-1"
        assert event.event_type == "user_action"
        assert event.source == "api"
        assert event.payload == {}

    def test_event_with_payload(self):
        event = Event(
            event_id="evt-1",
            event_type="user_action",
            source="api",
            payload={"action": "click", "target": "button"},
        )
        assert event.payload["action"] == "click"

    def test_event_with_metadata(self):
        metadata = EventMetadata(correlation_id="corr-1")
        event = Event(event_id="evt-1", event_type="user_action", source="api", metadata=metadata)
        assert event.metadata.correlation_id == "corr-1"


class TestEventResult:
    def test_create_success_result(self):
        result = EventResult(event_id="evt-1", success=True)
        assert result.success is True
        assert result.error is None

    def test_create_failure_result(self):
        result = EventResult(event_id="evt-1", success=False, error="Handler failed")
        assert result.success is False
        assert result.error == "Handler failed"


class TestEventContext:
    def test_create_context(self):
        event = Event(event_id="evt-1", event_type="test", source="test")
        context = EventContext(event=event)
        assert context.event.event_id == "evt-1"
        assert context.is_handled is False


class TestEventHandler:
    def test_create_handler(self):
        def handler(event):
            return {"ok": True}
        eh = EventHandler(name="test_handler", handler=handler, event_types=["user_action"])
        assert eh.name == "test_handler"
        assert eh.can_handle("user_action") is True
        assert eh.can_handle("other") is False

    def test_handler_no_event_types(self):
        def handler(event):
            return {"ok": True}
        eh = EventHandler(name="catch_all", handler=handler)
        assert eh.can_handle("any_type") is True


# ============================================
# EventRegistry Tests
# ============================================

class TestEventRegistry:
    def test_register_and_get(self):
        registry = EventRegistry()
        def handler(event):
            return {"ok": True}
        eh = EventHandler(name="test", handler=handler, event_types=["user_action"])
        registry.register(eh)
        assert registry.get("test") is eh

    def test_get_handlers_for_type(self):
        registry = EventRegistry()
        def handler1(event):
            return {"ok": True}
        def handler2(event):
            return {"ok": True}
        eh1 = EventHandler(name="h1", handler=handler1, event_types=["user_action"])
        eh2 = EventHandler(name="h2", handler=handler2, event_types=["user_action", "system"])
        registry.register(eh1)
        registry.register(eh2)
        handlers = registry.get_handlers_for_type("user_action")
        assert len(handlers) == 2

    def test_unregister(self):
        registry = EventRegistry()
        def handler(event):
            return {"ok": True}
        eh = EventHandler(name="test", handler=handler, event_types=["user_action"])
        registry.register(eh)
        assert registry.unregister("test") is True
        assert registry.get("test") is None

    def test_list_handlers(self):
        registry = EventRegistry()
        def handler(event):
            return {"ok": True}
        eh = EventHandler(name="test", handler=handler, event_types=["user_action"])
        registry.register(eh)
        assert "test" in registry.list_handlers()

    def test_has_handler(self):
        registry = EventRegistry()
        def handler(event):
            return {"ok": True}
        eh = EventHandler(name="test", handler=handler, event_types=["user_action"])
        registry.register(eh)
        assert registry.has_handler("user_action") is True
        assert registry.has_handler("unknown") is False


# ============================================
# EventDispatcher Tests
# ============================================

class TestEventDispatcher:
    def test_dispatch_to_handler(self):
        registry = EventRegistry()
        def handler(event):
            return {"processed": event.event_id}
        eh = EventHandler(name="processor", handler=handler, event_types=["user_action"])
        registry.register(eh)
        dispatcher = EventDispatcher(registry)
        event = Event(event_id="evt-1", event_type="user_action", source="api")
        result = dispatcher.dispatch(event)
        assert result.success is True
        assert result.handler_name == "processor"
        assert result.result["processed"] == "evt-1"

    def test_dispatch_unknown_handler(self):
        dispatcher = EventDispatcher()
        event = Event(event_id="evt-1", event_type="unknown", source="api")
        result = dispatcher.dispatch(event)
        assert result.success is False
        assert "No handler registered" in result.error

    def test_dispatch_all(self):
        registry = EventRegistry()
        calls = []
        def handler1(event):
            calls.append("h1")
            return "result1"
        def handler2(event):
            calls.append("h2")
            return "result2"
        eh1 = EventHandler(name="h1", handler=handler1, event_types=["user_action"])
        eh2 = EventHandler(name="h2", handler=handler2, event_types=["user_action"])
        registry.register(eh1)
        registry.register(eh2)
        dispatcher = EventDispatcher(registry)
        event = Event(event_id="evt-1", event_type="user_action", source="api")
        results = dispatcher.dispatch_all(event)
        assert len(results) == 2
        assert all(r.success for r in results)


# ============================================
# EventValidator Tests
# ============================================

class TestEventValidator:
    def test_validate_event_success(self):
        validator = EventValidator()
        event = Event(event_id="evt-1", event_type="user_action", source="api")
        valid, error = validator.validate_event(event)
        assert valid is True
        assert error is None

    def test_validate_event_missing_id(self):
        validator = EventValidator()
        event = Event(event_id="", event_type="user_action", source="api")
        valid, error = validator.validate_event(event)
        assert valid is False
        assert "event_id" in error

    def test_validate_event_missing_type(self):
        validator = EventValidator()
        event = Event(event_id="evt-1", event_type="", source="api")
        valid, error = validator.validate_event(event)
        assert valid is False
        assert "event_type" in error

    def test_validate_payload(self):
        validator = EventValidator()
        event = Event(event_id="evt-1", event_type="user_action", source="api", payload={"key": "value"})
        schema = {"key": str}
        valid, error = validator.validate_payload(event, schema)
        assert valid is True

    def test_validate_payload_missing_key(self):
        validator = EventValidator()
        event = Event(event_id="evt-1", event_type="user_action", source="api", payload={})
        schema = {"key": str}
        valid, error = validator.validate_payload(event, schema)
        assert valid is False
        assert "Missing required payload key" in error

    def test_validate_handler(self):
        validator = EventValidator()
        def handler(event):
            return {"ok": True}
        eh = EventHandler(name="test", handler=handler, event_types=["user_action"])
        valid, error = validator.validate_handler_registration(eh)
        assert valid is True

    def test_validate_or_raise(self):
        validator = EventValidator()
        event = Event(event_id="evt-1", event_type="user_action", source="api")
        validator.validate_or_raise(event=event)  # Should not raise

    def test_validate_or_raise_raises(self):
        validator = EventValidator()
        event = Event(event_id="", event_type="user_action", source="api")
        with pytest.raises(EventValidationError):
            validator.validate_or_raise(event=event)


# ============================================
# EventBus Tests
# ============================================

class TestEventBus:
    def test_register_handler(self):
        bus = EventBus()
        def handler(event):
            return {"ok": True}
        eh = EventHandler(name="processor", handler=handler, event_types=["user_action"])
        bus.register_handler(eh)
        assert "processor" in bus.get_handlers("user_action")

    def test_publish(self):
        bus = EventBus()
        def handler(event):
            return {"processed": event.event_id}
        eh = EventHandler(name="processor", handler=handler, event_types=["user_action"])
        bus.register_handler(eh)
        event = Event(event_id="evt-1", event_type="user_action", source="api")
        results = bus.publish(event)
        assert len(results) == 1
        assert results[0]["processed"] == "evt-1"

    def test_emit(self):
        bus = EventBus()
        def handler(event):
            return {"processed": event.event_id}
        eh = EventHandler(name="processor", handler=handler, event_types=["user_action"])
        bus.register_handler(eh)
        event = Event(event_id="evt-1", event_type="user_action", source="api")
        result = bus.emit(event)
        assert result["processed"] == "evt-1"

    def test_subscribe(self):
        bus = EventBus()
        def handler(event):
            return {"ok": True}
        eh = EventHandler(name="processor", handler=handler)
        bus.subscribe("user_action", eh)
        assert "processor" in bus.get_handlers("user_action")

    def test_unpublish_handler(self):
        bus = EventBus()
        def handler(event):
            return {"ok": True}
        eh = EventHandler(name="processor", handler=handler, event_types=["user_action"])
        bus.register_handler(eh)
        bus.unregister_handler("processor")
        assert "processor" not in bus.get_handlers("user_action")

    def test_get_published_events(self):
        bus = EventBus()
        def handler(event):
            return {"ok": True}
        eh = EventHandler(name="processor", handler=handler, event_types=["user_action"])
        bus.register_handler(eh)
        event = Event(event_id="evt-1", event_type="user_action", source="api")
        bus.publish(event)
        events = bus.get_published_events()
        assert len(events) == 1
        assert events[0].event_id == "evt-1"


# ============================================
# Integration Tests
# ============================================

class TestEventBusIntegration:
    def test_full_flow(self):
        bus = EventBus()
        results = []

        def handler1(event):
            results.append("h1")
            return "r1"

        def handler2(event):
            results.append("h2")
            return "r2"

        eh1 = EventHandler(name="h1", handler=handler1, event_types=["user_action"])
        eh2 = EventHandler(name="h2", handler=handler2, event_types=["user_action"])

        bus.register_handler(eh1)
        bus.register_handler(eh2)

        event = Event(event_id="evt-1", event_type="user_action", source="api")
        bus.publish(event)

        assert len(results) == 2
        assert "h1" in results
        assert "h2" in results

    def test_multiple_event_types(self):
        bus = EventBus()
        results = []

        def system_handler(event):
            results.append("system")
            return "sys"

        def user_handler(event):
            results.append("user")
            return "usr"

        bus.register_handler(EventHandler(name="sys_h", handler=system_handler, event_types=["system_event"]))
        bus.register_handler(EventHandler(name="user_h", handler=user_handler, event_types=["user_action"]))

        bus.publish(Event(event_id="e1", event_type="system_event", source="sys"))
        bus.publish(Event(event_id="e2", event_type="user_action", source="usr"))

        assert "system" in results
        assert "user" in results

    def test_unknown_handler_returns_failure(self):
        bus = EventBus()
        event = Event(event_id="evt-1", event_type="unknown", source="api")
        results = bus.publish(event)
        # No handlers - results will be empty
        assert results == []

    def test_validation_failure(self):
        bus = EventBus()
        with pytest.raises(EventValidationError):
            bus.publish(Event(event_id="", event_type="user_action", source="api"))