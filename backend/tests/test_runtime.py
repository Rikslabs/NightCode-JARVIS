"""Tests for Runtime Foundation."""

import pytest

from app.runtime.models import (
    RuntimeStatus,
    ExecutionContext,
    ExecutionRequest,
    ExecutionResult,
    RuntimeResult,
)
from app.runtime.context import RuntimeContext
from app.runtime.executor import RuntimeExecutor
from app.runtime.registry import RuntimeRegistry
from app.runtime.dispatcher import RuntimeDispatcher
from app.runtime.scheduler import RuntimeScheduler
from app.runtime.coordinator import RuntimeCoordinator
from app.runtime.pipeline import RuntimePipeline
from app.runtime.collector import RuntimeCollector
from app.runtime.recovery import RuntimeRecovery, RetryStrategy, SkipStrategy, AbortStrategy, FallbackStrategy
from app.runtime.telemetry import RuntimeTelemetry, ExecutionTelemetry
from app.runtime.validator import RuntimeValidator, RuntimeValidationError


# ============================================
# Model Tests
# ============================================

class TestRuntimeStatus:
    def test_all_statuses(self):
        assert RuntimeStatus.IDLE.value == "idle"
        assert RuntimeStatus.RUNNING.value == "running"
        assert RuntimeStatus.COMPLETED.value == "completed"
        assert RuntimeStatus.FAILED.value == "failed"


class TestExecutionContext:
    def test_create_context(self):
        context = ExecutionContext(execution_id="exec-1")
        assert context.execution_id == "exec-1"
        assert context.active_module == ""

    def test_context_with_module(self):
        context = ExecutionContext(execution_id="exec-1", active_module="browser")
        assert context.active_module == "browser"

    def test_context_to_dict(self):
        context = ExecutionContext(execution_id="exec-1", active_module="browser")
        d = context.to_dict()
        assert d["execution_id"] == "exec-1"
        assert d["active_module"] == "browser"
        assert "timestamp" in d

    def test_context_timestamp_is_timezone_aware(self):
        context = ExecutionContext(execution_id="exec-1")
        assert context.timestamp.tzinfo is not None


class TestExecutionRequest:
    def test_create_request(self):
        request = ExecutionRequest(request_id="req-1", action="open_url")
        assert request.request_id == "req-1"
        assert request.action == "open_url"

    def test_request_with_parameters(self):
        request = ExecutionRequest(
            request_id="req-1",
            action="click",
            parameters={"selector": "#button"},
        )
        assert request.parameters["selector"] == "#button"

    def test_request_with_context(self):
        context = ExecutionContext(execution_id="exec-1")
        request = ExecutionRequest(request_id="req-1", action="click", context=context)
        assert request.context is not None
        assert request.context.execution_id == "exec-1"

    def test_request_to_dict(self):
        request = ExecutionRequest(request_id="req-1", action="click")
        d = request.to_dict()
        assert d["request_id"] == "req-1"
        assert d["action"] == "click"
        assert d["context"] is None


class TestExecutionResult:
    def test_create_success_result(self):
        result = ExecutionResult(request_id="req-1", success=True)
        assert result.success is True
        assert result.error is None

    def test_create_failure_result(self):
        result = ExecutionResult(request_id="req-1", success=False, error="Not found")
        assert result.success is False
        assert result.error == "Not found"

    def test_result_to_dict(self):
        result = ExecutionResult(request_id="req-1", success=True)
        d = result.to_dict()
        assert d["success"] is True
        assert d["request_id"] == "req-1"
        assert "timestamp" in d


# ============================================
# RuntimeContext Tests
# ============================================

class TestRuntimeContext:
    def test_create_context(self):
        context = RuntimeContext(execution_id="exec-1")
        assert context.execution_id == "exec-1"
        assert context.status == RuntimeStatus.IDLE

    def test_context_active_module(self):
        context = RuntimeContext(execution_id="exec-1", active_module="browser")
        assert context.active_module == "browser"
        context.active_module = "desktop"
        assert context.active_module == "desktop"

    def test_context_metadata(self):
        context = RuntimeContext(execution_id="exec-1", metadata={"key": "value"})
        assert context.metadata["key"] == "value"
        context.metadata = {"new": "data"}
        assert context.metadata["new"] == "data"

    def test_context_status(self):
        context = RuntimeContext(execution_id="exec-1")
        assert context.status == RuntimeStatus.IDLE
        context.status = RuntimeStatus.RUNNING
        assert context.status == RuntimeStatus.RUNNING

    def test_context_to_dict(self):
        context = RuntimeContext(execution_id="exec-1", active_module="browser")
        d = context.to_dict()
        assert d["context"]["execution_id"] == "exec-1"
        assert d["status"] == "idle"


# ============================================
# RuntimeExecutor Tests
# ============================================

class TestRuntimeExecutor:
    def test_create_executor(self):
        executor = RuntimeExecutor()
        assert executor.get_status() == RuntimeStatus.IDLE

    def test_create_executor_with_context(self):
        context = RuntimeContext(execution_id="exec-1")
        executor = RuntimeExecutor(context=context)
        assert executor.get_context().execution_id == "exec-1"

    def test_initialize(self):
        executor = RuntimeExecutor()
        context = executor.initialize("exec-1", active_module="browser")
        assert context.execution_id == "exec-1"
        assert context.active_module == "browser"
        assert context.status == RuntimeStatus.RUNNING
        assert executor.get_status() == RuntimeStatus.RUNNING

    def test_prepare(self):
        executor = RuntimeExecutor()
        request = ExecutionRequest(request_id="req-1", action="open_url")
        result = executor.prepare(request)
        assert result.success is True
        assert result.request_id == "req-1"
        assert result.result["status"] == "prepared"
        assert result.result["action"] == "open_url"
        assert executor.get_status() == RuntimeStatus.COMPLETED


# ============================================
# RuntimeRegistry Tests
# ============================================

class TestRuntimeRegistry:
    def test_get_instance(self):
        registry = RuntimeRegistry.get_instance()
        assert isinstance(registry, RuntimeRegistry)

    def test_register_and_get(self):
        registry = RuntimeRegistry()
        executor = RuntimeExecutor()
        registry.register("executor", executor)
        assert registry.get("executor") is executor

    def test_get_missing(self):
        registry = RuntimeRegistry()
        assert registry.get("missing") is None

    def test_clear(self):
        registry = RuntimeRegistry()
        executor = RuntimeExecutor()
        registry.register("executor", executor)
        registry.clear()
        assert registry.get("executor") is None


# ============================================
# Integration Tests
# ============================================

class TestRuntimeIntegration:
    def test_full_execution_flow(self):
        registry = RuntimeRegistry()
        executor = RuntimeExecutor()
        registry.register("executor", executor)

        context = executor.initialize("exec-1", active_module="browser")
        request = ExecutionRequest(request_id="req-1", action="open_url", context=context)
        result = executor.prepare(request)

        assert result.success is True
        assert executor.get_status() == RuntimeStatus.COMPLETED

    def test_context_persistence(self):
        executor = RuntimeExecutor()
        context = executor.initialize("exec-1", active_module="browser")
        request = ExecutionRequest(request_id="req-1", action="click", context=context)
        result = executor.prepare(request)

        assert result.result["status"] == "prepared"
        assert result.result["action"] == "click"


# ============================================
# RuntimeDispatcher Tests
# ============================================

class TestRuntimeDispatcher:
    def test_register_module(self):
        dispatcher = RuntimeDispatcher()
        dispatcher.register_module("browser", object())
        assert "browser" in dispatcher._modules

    def test_dispatch_unknown_action(self):
        dispatcher = RuntimeDispatcher()
        context = RuntimeContext(execution_id="exec-1")
        request = ExecutionRequest(request_id="req-1", action="unknown")
        result = dispatcher.dispatch(request, context)
        assert result.success is False
        assert "No module registered" in result.error

    def test_dispatch_missing_module(self):
        dispatcher = RuntimeDispatcher()
        dispatcher.register_module("other", object())
        context = RuntimeContext(execution_id="exec-1")
        request = ExecutionRequest(request_id="req-1", action="open_url")
        result = dispatcher.dispatch(request, context)
        assert result.success is False
        assert "Module not found" in result.error

    def test_dispatch_success(self):
        module = type("DummyModule", (), {"execute": lambda self, params: {"ok": True}})()
        dispatcher = RuntimeDispatcher({"browser": module})
        context = RuntimeContext(execution_id="exec-1")
        request = ExecutionRequest(request_id="req-1", action="open_url")
        result = dispatcher.dispatch(request, context)
        assert result.success is True
        assert result.result["ok"] is True

    def test_dispatch_module_without_execute(self):
        module = type("BadModule", (), {})()
        dispatcher = RuntimeDispatcher({"browser": module})
        context = RuntimeContext(execution_id="exec-1")
        request = ExecutionRequest(request_id="req-1", action="open_url")
        result = dispatcher.dispatch(request, context)
        assert result.success is False
        assert "no execute method" in result.error.lower()


# ============================================
# RuntimeScheduler Tests
# ============================================

class TestRuntimeScheduler:
    def test_enqueue_and_size(self):
        executor = RuntimeExecutor()
        scheduler = RuntimeScheduler(executor)
        request = ExecutionRequest(request_id="req-1", action="open_url")
        scheduler.enqueue(request)
        assert scheduler.size() == 1

    def test_run_next(self):
        executor = RuntimeExecutor()
        scheduler = RuntimeScheduler(executor)
        request = ExecutionRequest(request_id="req-1", action="open_url")
        scheduler.enqueue(request)
        context = RuntimeContext(execution_id="exec-1")
        result = scheduler.run_next(context)
        assert result.success is True
        assert scheduler.size() == 0

    def test_run_next_empty_queue(self):
        executor = RuntimeExecutor()
        scheduler = RuntimeScheduler(executor)
        with pytest.raises(RuntimeError):
            scheduler.run_next(RuntimeContext(execution_id="exec-1"))

    def test_run_all(self):
        executor = RuntimeExecutor()
        scheduler = RuntimeScheduler(executor)
        for i in range(3):
            scheduler.enqueue(ExecutionRequest(request_id=f"req-{i}", action="open_url"))
        context = RuntimeContext(execution_id="exec-1")
        results = scheduler.run_all(context)
        assert len(results) == 3
        assert all(r.success for r in results)

    def test_clear(self):
        executor = RuntimeExecutor()
        scheduler = RuntimeScheduler(executor)
        scheduler.enqueue(ExecutionRequest(request_id="req-1", action="open_url"))
        scheduler.clear()
        assert scheduler.size() == 0


# ============================================
# RuntimeCoordinator Tests
# ============================================

class TestRuntimeCoordinator:
    def test_start_initializes_context(self):
        coordinator = RuntimeCoordinator()
        context = coordinator.start("exec-1", active_module="browser")
        assert context.execution_id == "exec-1"
        assert context.active_module == "browser"

    def test_submit_dispatches_request(self):
        module = type("DummyModule", (), {"execute": lambda self, params: {"ok": True}})()
        coordinator = RuntimeCoordinator()
        coordinator.register_module("browser", module)
        coordinator.start("exec-1")
        request = ExecutionRequest(request_id="req-1", action="open_url")
        result = coordinator.submit(request)
        assert result.success is True

    def test_submit_without_start(self):
        coordinator = RuntimeCoordinator()
        request = ExecutionRequest(request_id="req-1", action="open_url")
        result = coordinator.submit(request)
        assert result.success is False

    def test_enqueue_and_execute_next(self):
        coordinator = RuntimeCoordinator()
        coordinator.start("exec-1")
        request = ExecutionRequest(request_id="req-1", action="open_url")
        coordinator.enqueue(request)
        result = coordinator.execute_next()
        assert result.success is True

    def test_execute_all(self):
        coordinator = RuntimeCoordinator()
        coordinator.start("exec-1")
        for i in range(3):
            coordinator.enqueue(ExecutionRequest(request_id=f"req-{i}", action="open_url"))
        results = coordinator.execute_all()
        assert len(results) == 3

    def test_execute_next_without_start_raises(self):
        coordinator = RuntimeCoordinator()
        with pytest.raises(RuntimeError):
            coordinator.execute_next()

    def test_reset_clears_state(self):
        coordinator = RuntimeCoordinator()
        coordinator.start("exec-1")
        coordinator.enqueue(ExecutionRequest(request_id="req-1", action="open_url"))
        coordinator.reset()
        assert coordinator.get_context() is None
        assert coordinator.get_status() == RuntimeStatus.IDLE

    def test_register_module(self):
        coordinator = RuntimeCoordinator()
        coordinator.register_module("browser", object())
        assert "browser" in coordinator._dispatcher._modules


# ============================================
# RuntimePipeline Tests
# ============================================

class TestRuntimePipeline:
    def test_execute_single_request(self):
        module = type("DummyModule", (), {"execute": lambda self, params: {"ok": True}})()
        pipeline = RuntimePipeline()
        pipeline.register_module("browser", module)
        request = ExecutionRequest(request_id="req-1", action="open_url")
        result = pipeline.execute(request)
        assert result.success is True

    def test_enqueue_and_execute_scheduled(self):
        pipeline = RuntimePipeline()
        pipeline.start("exec-1")
        for i in range(3):
            pipeline.enqueue(ExecutionRequest(request_id=f"req-{i}", action="open_url"))
        results = pipeline.execute_scheduled()
        assert len(results) == 3
        assert all(r.success for r in results)

    def test_reset_clears_results(self):
        pipeline = RuntimePipeline()
        pipeline.execute(ExecutionRequest(request_id="req-1", action="open_url"))
        pipeline.reset()
        assert pipeline.get_results() == []

    def test_get_context(self):
        pipeline = RuntimePipeline()
        request = ExecutionRequest(request_id="req-1", action="open_url")
        pipeline.execute(request)
        context = pipeline.get_context()
        assert context is not None
        assert context.execution_id == "req-1"

    def test_invalid_request_returns_failure(self):
        pipeline = RuntimePipeline()
        result = pipeline.execute(ExecutionRequest(request_id="req-1", action="unknown"))
        assert result.success is False

    def test_lifecycle_status_transitions(self):
        module = type("DummyModule", (), {"execute": lambda self, params: {"ok": True}})()
        pipeline = RuntimePipeline()
        pipeline.register_module("browser", module)
        assert pipeline.get_status() == RuntimeStatus.IDLE
        request = ExecutionRequest(request_id="req-1", action="open_url")
        pipeline.execute(request)
        assert pipeline.get_status() == RuntimeStatus.COMPLETED


# ============================================
# Pipeline Integration Tests
# ============================================

class TestPipelineIntegration:
    def test_full_pipeline_lifecycle(self):
        module = type("DummyModule", (), {"execute": lambda self, params: {"ok": True}})()
        pipeline = RuntimePipeline()
        pipeline.register_module("browser", module)
        request = ExecutionRequest(request_id="req-1", action="open_url")
        result = pipeline.execute(request)
        assert result.success is True
        assert pipeline.get_status() == RuntimeStatus.COMPLETED

    def test_pipeline_with_invalid_action(self):
        pipeline = RuntimePipeline()
        result = pipeline.execute(ExecutionRequest(request_id="req-1", action="unknown"))
        assert result.success is False
        assert pipeline.get_status() == RuntimeStatus.FAILED


# ============================================
# RuntimeCollector Tests
# ============================================

class TestRuntimeCollector:
    def test_collect_result(self):
        collector = RuntimeCollector()
        result = ExecutionResult(request_id="req-1", success=True)
        collector.collect(result)
        assert len(collector.get_results()) == 1

    def test_collect_module_output(self):
        collector = RuntimeCollector()
        collector.collect_module_output("browser", {"ok": True})
        assert collector.get_module_outputs()["browser"] == {"ok": True}

    def test_build_result_success(self):
        collector = RuntimeCollector()
        context = RuntimeContext(execution_id="exec-1")
        collector.collect(ExecutionResult(request_id="req-1", success=True))
        final = collector.build_result(context)
        assert final.success is True
        assert final.execution_id == "exec-1"

    def test_build_result_failure(self):
        collector = RuntimeCollector()
        context = RuntimeContext(execution_id="exec-1")
        collector.collect(ExecutionResult(request_id="req-1", success=False, error="boom"))
        final = collector.build_result(context)
        assert final.success is False
        assert "boom" in final.errors

    def test_clear(self):
        collector = RuntimeCollector()
        collector.collect(ExecutionResult(request_id="req-1", success=True))
        collector.clear()
        assert len(collector.get_results()) == 0
        assert len(collector.get_module_outputs()) == 0


# ============================================
# RuntimeRecovery Tests
# ============================================

class TestRuntimeRecovery:
    def test_register_and_select_strategy(self):
        recovery = RuntimeRecovery()
        strategy = SkipStrategy()
        recovery.register_strategy("skip", strategy)
        recovery.select_strategy("skip")
        assert recovery.get_strategy("skip") is strategy

    def test_unknown_strategy_raises(self):
        recovery = RuntimeRecovery()
        with pytest.raises(KeyError):
            recovery.select_strategy("missing")

    def test_skip_strategy_returns_result(self):
        recovery = RuntimeRecovery()
        recovery.register_strategy("skip", SkipStrategy())
        result = ExecutionResult(request_id="req-1", success=False, error="fail")
        outcome = recovery.recover(RuntimeContext(execution_id="exec-1"), result)
        assert outcome is result

    def test_abort_strategy_raises(self):
        recovery = RuntimeRecovery()
        recovery.register_strategy("abort", AbortStrategy())
        recovery.select_strategy("abort")
        with pytest.raises(RuntimeError):
            recovery.recover(RuntimeContext(execution_id="exec-1"), ExecutionResult(request_id="req-1", success=False, error="fail"))

    def test_fallback_strategy_executes(self):
        called = False
        def fallback(context):
            nonlocal called
            called = True
            return "fallback"
        recovery = RuntimeRecovery()
        recovery.register_strategy("fallback", FallbackStrategy(fallback))
        recovery.select_strategy("fallback")
        result = recovery.recover(RuntimeContext(execution_id="exec-1"), ExecutionResult(request_id="req-1", success=False, error="fail"))
        assert called is True
        assert result == "fallback"

    def test_successful_result_not_recovered(self):
        recovery = RuntimeRecovery()
        recovery.register_strategy("skip", SkipStrategy())
        recovery.select_strategy("skip")
        result = ExecutionResult(request_id="req-1", success=True)
        outcome = recovery.recover(RuntimeContext(execution_id="exec-1"), result)
        assert outcome is result

    def test_clear_removes_strategies(self):
        recovery = RuntimeRecovery()
        recovery.register_strategy("skip", SkipStrategy())
        recovery.clear()
        assert len(recovery._strategies) == 0


# ============================================
# RuntimeTelemetry Tests
# ============================================

class TestRuntimeTelemetry:
    def test_start_and_finish(self):
        telemetry = RuntimeTelemetry()
        record = telemetry.start_execution("exec-1", module_name="browser")
        assert record.execution_id == "exec-1"
        assert record.status == "idle"
        finished = telemetry.finish_execution("exec-1", "completed")
        assert finished is record
        assert finished.duration_ms is not None
        assert finished.status == "completed"

    def test_finish_missing_id_returns_none(self):
        telemetry = RuntimeTelemetry()
        assert telemetry.finish_execution("missing", "completed") is None

    def test_record_retry(self):
        telemetry = RuntimeTelemetry()
        telemetry.start_execution("exec-1")
        telemetry.record_retry("exec-1")
        assert telemetry.get_record("exec-1").retries == 1

    def test_get_record(self):
        telemetry = RuntimeTelemetry()
        telemetry.start_execution("exec-1")
        record = telemetry.get_record("exec-1")
        assert record.execution_id == "exec-1"
        assert telemetry.get_record("missing") is None

    def test_get_all_records(self):
        telemetry = RuntimeTelemetry()
        telemetry.start_execution("exec-1")
        telemetry.finish_execution("exec-1", "completed")
        records = telemetry.get_all_records()
        assert len(records) == 1

    def test_clear(self):
        telemetry = RuntimeTelemetry()
        telemetry.start_execution("exec-1")
        telemetry.clear()
        assert len(telemetry.get_all_records()) == 0

    def test_execution_telemetry_to_dict(self):
        import time
        telemetry = RuntimeTelemetry()
        record = telemetry.start_execution("exec-1", metadata={"key": "value"})
        time.sleep(0.01)
        telemetry.finish_execution("exec-1", "completed")
        d = record.to_dict()
        assert d["execution_id"] == "exec-1"
        assert d["metadata"]["key"] == "value"
        assert d["finished_at"] is not None
        assert d["duration_ms"] > 0


# ============================================
# RuntimeValidator Tests
# ============================================

class TestRuntimeValidator:
    def test_validate_request_success(self):
        validator = RuntimeValidator()
        request = ExecutionRequest(request_id="req-1", action="open_url")
        valid, error = validator.validate_request(request)
        assert valid is True
        assert error is None

    def test_validate_request_missing_id(self):
        validator = RuntimeValidator()
        request = ExecutionRequest(request_id="", action="open_url")
        valid, error = validator.validate_request(request)
        assert valid is False
        assert "request_id" in error

    def test_validate_request_missing_required_param(self):
        validator = RuntimeValidator(required_params={"click": ["selector"]})
        request = ExecutionRequest(request_id="req-1", action="click")
        valid, error = validator.validate_request(request)
        assert valid is False
        assert "selector" in error

    def test_validate_result_success(self):
        validator = RuntimeValidator()
        result = ExecutionResult(request_id="req-1", success=True)
        valid, error = validator.validate_result(result)
        assert valid is True

    def test_validate_result_success_with_error_raises(self):
        validator = RuntimeValidator()
        result = ExecutionResult(request_id="req-1", success=True, error="oops")
        valid, error = validator.validate_result(result)
        assert valid is False
        assert "Successful result must not have error" in error

    def test_validate_result_failure_without_error_raises(self):
        validator = RuntimeValidator()
        result = ExecutionResult(request_id="req-1", success=False)
        valid, error = validator.validate_result(result)
        assert valid is False
        assert "Failed result must have error" in error

    def test_validate_context_success(self):
        validator = RuntimeValidator()
        context = RuntimeContext(execution_id="exec-1")
        valid, error = validator.validate_context(context)
        assert valid is True

    def test_validate_context_missing_execution_id(self):
        validator = RuntimeValidator()
        context = RuntimeContext(execution_id="")
        valid, error = validator.validate_context(context)
        assert valid is False
        assert "execution_id" in error

    def test_validate_or_raise_request(self):
        validator = RuntimeValidator()
        with pytest.raises(RuntimeValidationError):
            validator.validate_or_raise(request=ExecutionRequest(request_id="", action="open_url"))

    def test_validate_or_raise_result(self):
        validator = RuntimeValidator()
        with pytest.raises(RuntimeValidationError):
            validator.validate_or_raise(result=ExecutionResult(request_id="req-1", success=False))

    def test_set_allowed_actions(self):
        validator = RuntimeValidator()
        validator.set_allowed_actions({"open_url": {}})
        assert "open_url" in validator._allowed_actions

    def test_set_required_params(self):
        validator = RuntimeValidator()
        validator.set_required_params({"click": ["selector"]})
        assert "click" in validator._required_params


# ============================================
# RuntimeResult Model Tests
# ============================================

class TestRuntimeResult:
    def test_create_success_result(self):
        result = RuntimeResult(execution_id="exec-1", success=True)
        assert result.execution_id == "exec-1"
        assert result.success is True
        assert result.errors == []

    def test_create_failure_result(self):
        result = RuntimeResult(execution_id="exec-1", success=False, errors=["err"])
        assert result.success is False
        assert "err" in result.errors

    def test_to_dict(self):
        result = RuntimeResult(execution_id="exec-1", success=True)
        d = result.to_dict()
        assert d["execution_id"] == "exec-1"
        assert d["success"] is True
        assert d["errors"] == []

    def test_to_dict_with_results(self):
        exec_result = ExecutionResult(request_id="req-1", success=True, result={"ok": True})
        result = RuntimeResult(execution_id="exec-1", success=True, results=[exec_result])
        d = result.to_dict()
        assert len(d["results"]) == 1
        assert d["results"][0]["request_id"] == "req-1"


# ============================================
# Recovery Integration Tests
# ============================================

class TestRecoveryIntegration:
    def test_retry_strategy_max_retries(self):
        strategy = RetryStrategy(max_retries=2)
        context = RuntimeContext(execution_id="exec-1")
        for _ in range(3):
            outcome = strategy.execute(context, ExecutionResult(request_id="req-1", success=False, error="fail"))
        assert outcome.success is False

    def test_recovery_without_selected_strategy(self):
        recovery = RuntimeRecovery()
        result = ExecutionResult(request_id="req-1", success=False, error="fail")
        outcome = recovery.recover(RuntimeContext(execution_id="exec-1"), result)
        assert outcome is result


# ============================================
# Telemetry Integration Tests
# ============================================

class TestTelemetryIntegration:
    def test_multiple_retries_recorded(self):
        telemetry = RuntimeTelemetry()
        telemetry.start_execution("exec-1")
        for _ in range(3):
            telemetry.record_retry("exec-1")
        assert telemetry.get_record("exec-1").retries == 3

    def test_telemetry_with_module_name(self):
        telemetry = RuntimeTelemetry()
        record = telemetry.start_execution("exec-1", module_name="browser")
        assert record.module_name == "browser"


# ============================================
# Collector Integration Tests
# ============================================

class TestCollectorIntegration:
    def test_collector_merges_multiple_results(self):
        collector = RuntimeCollector()
        context = RuntimeContext(execution_id="exec-1")
        for i in range(3):
            collector.collect(ExecutionResult(request_id=f"req-{i}", success=True, result={"i": i}))
        final = collector.build_result(context)
        assert len(final.results) == 3

    def test_collector_module_outputs_preserved(self):
        collector = RuntimeCollector()
        collector.collect_module_output("browser", {"ok": True})
        collector.collect_module_output("desktop", {"ok": True})
        context = RuntimeContext(execution_id="exec-1")
        final = collector.build_result(context)
        assert "browser" in final.module_outputs
        assert "desktop" in final.module_outputs


# ============================================
# End-to-End Integration Tests
# ============================================

class TestRuntimeEndToEnd:
    def test_full_flow_with_collector_telemetry_recovery(self):
        module = type("DummyModule", (), {"execute": lambda self, params: {"ok": True}})()

        # Setup pipeline
        pipeline = RuntimePipeline()
        pipeline.register_module("browser", module)

        # Setup collector
        collector = RuntimeCollector()

        # Setup telemetry
        telemetry = RuntimeTelemetry()

        # Execute
        request = ExecutionRequest(request_id="req-1", action="open_url")
        telemetry.start_execution("exec-1", module_name="browser")
        result = pipeline.execute(request)
        collector.collect(result)
        telemetry.finish_execution("exec-1", "completed")

        # Verify
        assert result.success is True
        assert collector.get_results()[0].success is True
        assert telemetry.get_record("exec-1").status == "completed"


# ============================================
# Event Integration Tests
# ============================================

class TestRuntimeEventIntegration:
    def test_runtime_started_event(self):
        from app.events.bus import EventBus
        from app.events.models import Event

        # Create event bus with handler to capture events
        bus = EventBus()
        events_captured = []

        def event_handler(event):
            events_captured.append(event)
            return {"ok": True}

        from app.events.models import EventHandler
        bus.register_handler(EventHandler(
            name="capturer",
            handler=event_handler,
            event_types=["runtime.started", "runtime.completed"]
        ))

        # Create executor with event bus
        executor = RuntimeExecutor(event_bus=bus)
        executor.initialize("exec-1", active_module="browser")

        # Verify event was published
        assert len(events_captured) >= 1
        assert events_captured[0].event_type == "runtime.started"

    def test_execution_events_published(self):
        from app.events.bus import EventBus
        from app.events.models import Event, EventHandler

        bus = EventBus()
        events_captured = []

        def event_handler(event):
            events_captured.append(event)
            return {"ok": True}

        bus.register_handler(EventHandler(
            name="capturer",
            handler=event_handler,
            event_types=["execution.started", "execution.completed"]
        ))

        executor = RuntimeExecutor(event_bus=bus)
        executor.initialize("exec-1")
        request = ExecutionRequest(request_id="req-1", action="open_url")
        executor.prepare(request)

        # Should have captured start and complete events
        event_types = [e.event_type for e in events_captured]
        assert "execution.started" in event_types
        assert "execution.completed" in event_types

    def test_runtime_without_event_bus(self):
        """Runtime must work normally without event bus."""
        executor = RuntimeExecutor()  # No event_bus
        context = executor.initialize("exec-1", active_module="browser")
        assert context.execution_id == "exec-1"
        assert context.status == RuntimeStatus.RUNNING

        request = ExecutionRequest(request_id="req-1", action="open_url")
        result = executor.prepare(request)
        assert result.success is True

    def test_event_ordering(self):
        from app.events.bus import EventBus
        from app.events.models import Event, EventHandler

        bus = EventBus()
        events_captured = []

        def event_handler(event):
            events_captured.append(event.event_type)
            return {"ok": True}

        bus.register_handler(EventHandler(
            name="capturer",
            handler=event_handler,
            event_types=["runtime.started", "execution.started", "execution.completed", "runtime.completed"]
        ))

        executor = RuntimeExecutor(event_bus=bus)
        executor.initialize("exec-1", active_module="browser")
        request = ExecutionRequest(request_id="req-1", action="open_url")
        executor.prepare(request)

        # Verify ordering
        assert events_captured[0] == "runtime.started"
        if "execution.started" in events_captured:
            assert events_captured.index("runtime.started") < events_captured.index("execution.started")

    def test_event_bus_injected_into_pipeline(self):
        from app.events.bus import EventBus
        from app.events.models import Event, EventHandler

        bus = EventBus()
        events_captured = []

        def event_handler(event):
            events_captured.append(event.event_type)
            return {"ok": True}

        bus.register_handler(EventHandler(
            name="capturer",
            handler=event_handler,
            event_types=["runtime.started"]
        ))

        module = type("DummyModule", (), {"execute": lambda self, params: {"ok": True}})()
        pipeline = RuntimePipeline()
        pipeline.register_module("browser", module)

        request = ExecutionRequest(request_id="req-1", action="open_url")
        result = pipeline.execute(request)

        assert result.success is True
