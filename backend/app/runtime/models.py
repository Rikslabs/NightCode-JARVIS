"""Runtime models."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class RuntimeStatus(Enum):
    """Runtime execution status."""

    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ExecutionContext:
    """Execution context information."""

    execution_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    active_module: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "timestamp": self.timestamp.isoformat(),
            "active_module": self.active_module,
            "metadata": self.metadata,
        }


@dataclass
class ExecutionRequest:
    """Execution request."""

    request_id: str
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    context: Optional[ExecutionContext] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "action": self.action,
            "parameters": self.parameters,
            "context": self.context.to_dict() if self.context else None,
        }


@dataclass
class ExecutionResult:
    """Execution result."""

    request_id: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class RuntimeResult:
    """Aggregated runtime result from multiple execution results."""

    execution_id: str
    success: bool
    results: List[ExecutionResult] = field(default_factory=list)
    module_outputs: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "success": self.success,
            "results": [r.to_dict() for r in self.results],
            "module_outputs": self.module_outputs,
            "errors": self.errors,
            "timestamp": self.timestamp.isoformat(),
        }