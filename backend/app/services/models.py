"""Shared models for the service layer."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4


@dataclass(kw_only=True)
class BaseRequest:
    """Base request model."""
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'id': self.id,
            'created_at': self.created_at,
            'metadata': self.metadata,
        }


@dataclass
class BaseResponse:
    """Base response model."""
    request_id: str
    success: bool
    message: str = ''
    data: Optional[dict[str, Any]] = None
    completed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'request_id': self.request_id,
            'success': self.success,
            'message': self.message,
            'data': self.data,
            'completed_at': self.completed_at,
        }


@dataclass
class ServiceMetadata:
    """Metadata about a service."""
    name: str
    version: str
    id: str = field(default_factory=lambda: str(uuid4()))
    description: str = ''
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'version': self.version,
            'created_at': self.created_at,
            'description': self.description,
        }


@dataclass
class ExecutionStatistics:
    """Statistics for service execution."""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    average_duration_ms: float = 0.0
    last_call_at: Optional[str] = None

    def record_call(self, success: bool, duration_ms: float) -> None:
        """Record a call execution."""
        self.total_calls += 1
        if success:
            self.successful_calls += 1

        # Update average
        total_time = self.average_duration_ms * (self.total_calls - 1)
        self.average_duration_ms = (total_time + duration_ms) / self.total_calls
        self.last_call_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'total_calls': self.total_calls,
            'successful_calls': self.successful_calls,
            'failed_calls': self.failed_calls,
            'average_duration_ms': self.average_duration_ms,
            'last_call_at': self.last_call_at,
        }