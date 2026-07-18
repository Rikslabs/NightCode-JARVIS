"""Shared enums for JARVIS core domain."""

from enum import Enum


class RiskLevel(Enum):
    """Risk levels for execution planning and decision making."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplexityLevel(Enum):
    """Complexity levels for intent analysis and task planning."""

    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


class Priority(Enum):
    """Priority levels for task execution."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ExecutionStatus(Enum):
    """Status of execution operations."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    RETRYING = "retrying"