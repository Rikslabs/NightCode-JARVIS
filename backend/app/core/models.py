"""Shared models for JARVIS core domain."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class Confidence:
    """Immutable confidence value with bounds validation."""

    value: float

    def __post_init__(self):
        self.value = max(0.0, min(1.0, self.value))

    def is_high(self) -> bool:
        """Check if confidence is high (>= 0.7)."""
        return self.value >= 0.7

    def is_medium(self) -> bool:
        """Check if confidence is medium (>= 0.4)."""
        return self.value >= 0.4

    def is_low(self) -> bool:
        """Check if confidence is low (< 0.4)."""
        return self.value < 0.4

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {"value": self.value}


@dataclass
class ExecutionResult:
    """Result of an execution operation."""

    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    duration: float = 0.0
    tool_used: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "duration": self.duration,
            "tool_used": self.tool_used,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionResult":
        """Create from dictionary."""
        return cls(
            success=data.get("success", False),
            data=data.get("data"),
            error=data.get("error"),
            duration=data.get("duration", 0.0),
            tool_used=data.get("tool_used"),
            timestamp=data.get(
                "timestamp", datetime.now(timezone.utc).isoformat()
            ),
        )


@dataclass
class TimestampedRecord:
    """Base class for timestamped records."""

    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "metadata": dict(self.metadata),
        }