"""Tests for Core Domain module."""

import pytest

from app.core.enums import RiskLevel, ComplexityLevel, Priority, ExecutionStatus
from app.core.models import Confidence, ExecutionResult, TimestampedRecord
from app.core.registry import CoreRegistry
from app.core.constants import DEFAULT_CONFIDENCE, DEFAULT_TIMEOUT


class TestRiskLevel:
    def test_all_risk_levels(self):
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.HIGH.value == "high"
        assert RiskLevel.CRITICAL.value == "critical"


class TestComplexityLevel:
    def test_all_complexity_levels(self):
        assert ComplexityLevel.SIMPLE.value == "simple"
        assert ComplexityLevel.MODERATE.value == "moderate"
        assert ComplexityLevel.COMPLEX.value == "complex"


class TestPriority:
    def test_all_priority_levels(self):
        assert Priority.LOW.value == "low"
        assert Priority.MEDIUM.value == "medium"
        assert Priority.HIGH.value == "high"
        assert Priority.CRITICAL.value == "critical"


class TestExecutionStatus:
    def test_all_execution_statuses(self):
        assert ExecutionStatus.PENDING.value == "pending"
        assert ExecutionStatus.RUNNING.value == "running"
        assert ExecutionStatus.SUCCESS.value == "success"
        assert ExecutionStatus.FAILED.value == "failed"
        assert ExecutionStatus.TIMEOUT.value == "timeout"
        assert ExecutionStatus.CANCELLED.value == "cancelled"
        assert ExecutionStatus.RETRYING.value == "retrying"


class TestConfidence:
    def test_create_confidence(self):
        c = Confidence(value=0.8)
        assert c.value == 0.8

    def test_confidence_bounds_lower(self):
        c = Confidence(value=-0.5)
        assert c.value == 0.0

    def test_confidence_bounds_upper(self):
        c = Confidence(value=1.5)
        assert c.value == 1.0

    def test_is_high(self):
        assert Confidence(0.8).is_high() is True
        assert Confidence(0.5).is_high() is False

    def test_is_medium(self):
        assert Confidence(0.5).is_medium() is True
        assert Confidence(0.3).is_medium() is False

    def test_is_low(self):
        assert Confidence(0.3).is_low() is True
        assert Confidence(0.5).is_low() is False

    def test_to_dict(self):
        c = Confidence(0.9)
        assert c.to_dict() == {"value": 0.9}


class TestExecutionResult:
    def test_create_success_result(self):
        r = ExecutionResult(success=True, data="output")
        assert r.success is True
        assert r.data == "output"

    def test_create_failure_result(self):
        r = ExecutionResult(success=False, error="failed")
        assert r.success is False
        assert r.error == "failed"

    def test_to_dict(self):
        r = ExecutionResult(success=True, tool_used="review")
        d = r.to_dict()
        assert d["success"] is True
        assert d["tool_used"] == "review"

    def test_from_dict(self):
        d = {"success": True, "data": "test"}
        r = ExecutionResult.from_dict(d)
        assert r.success is True
        assert r.data == "test"


class TestTimestampedRecord:
    def test_create_record(self):
        r = TimestampedRecord()
        assert r.timestamp is not None
        assert r.metadata == {}


class TestCoreRegistry:
    def test_get_instance(self):
        registry = CoreRegistry.get_instance()
        assert isinstance(registry, CoreRegistry)

    def test_register_and_get(self):
        registry = CoreRegistry()
        registry.register_singleton("test", "value")
        assert registry.get("test") == "value"

    def test_clear(self):
        registry = CoreRegistry()
        registry.register_singleton("test", "value")
        registry.clear()
        assert registry.get("test") is None

    def test_list_components(self):
        registry = CoreRegistry()
        registry.register_singleton("a", 1)
        registry.register_singleton("b", 2)
        assert "a" in registry.list_components()
        assert "b" in registry.list_components()


class TestConstants:
    def test_default_confidence(self):
        assert DEFAULT_CONFIDENCE == 1.0

    def test_default_timeout(self):
        assert DEFAULT_TIMEOUT == 30.0