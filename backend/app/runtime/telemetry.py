"""Runtime telemetry."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class ExecutionTelemetry:
    """Execution telemetry data."""
    execution_id: str
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: Optional[datetime] = None
    duration_ms: Optional[float] = None
    status: str = "idle"
    retries: int = 0
    module_name: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def finish(self, status: str) -> None:
        """Mark execution as finished."""
        self.finished_at = datetime.now(timezone.utc)
        delta = self.finished_at - self.started_at
        self.duration_ms = delta.total_seconds() * 1000
        self.status = status

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "execution_id": self.execution_id,
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "duration_ms": self.duration_ms,
            "status": self.status,
            "retries": self.retries,
            "module_name": self.module_name,
            "metadata": self.metadata,
        }


class RuntimeTelemetry:
    """Records execution metadata."""

    def __init__(self):
        self._records: List[ExecutionTelemetry] = []
        self._active: Dict[str, ExecutionTelemetry] = {}

    def start_execution(self, execution_id: str, module_name: str = "", metadata: Dict[str, Any] | None = None) -> ExecutionTelemetry:
        """Start recording telemetry for an execution."""
        record = ExecutionTelemetry(
            execution_id=execution_id,
            module_name=module_name,
            metadata=metadata or {},
        )
        self._active[execution_id] = record
        return record

    def finish_execution(self, execution_id: str, status: str) -> Optional[ExecutionTelemetry]:
        """Finish recording telemetry for an execution."""
        record = self._active.pop(execution_id, None)
        if record is None:
            return None
        record.finish(status)
        self._records.append(record)
        return record

    def record_retry(self, execution_id: str) -> None:
        """Record a retry attempt."""
        record = self._active.get(execution_id)
        if record is not None:
            record.retries += 1

    def get_record(self, execution_id: str) -> Optional[ExecutionTelemetry]:
        """Get telemetry record by execution ID."""
        for record in self._records:
            if record.execution_id == execution_id:
                return record
        return self._active.get(execution_id)

    def get_all_records(self) -> List[ExecutionTelemetry]:
        """Get all telemetry records."""
        return list(self._records)

    def clear(self) -> None:
        """Clear all telemetry data."""
        self._records.clear()
        self._active.clear()