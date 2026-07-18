"""Execution History - maintains in-memory history of executions."""

from typing import Any, Dict, List, Optional
from .models import ExperienceRecord, ExperienceSummary


class ExecutionHistory:
    """
    In-memory storage for execution history.

    No databases - purely in-memory with optional persistence hooks.
    """

    def __init__(self):
        self._records: Dict[str, ExperienceRecord] = {}
        self._counter = 0

    def add(self, record: ExperienceRecord) -> None:
        """Add an execution record to history."""
        self._records[record.id] = record

    def get(self, record_id: str) -> Optional[ExperienceRecord]:
        """Get a record by ID."""
        return self._records.get(record_id)

    def list_all(self) -> List[ExperienceRecord]:
        """List all records."""
        return list(self._records.values())

    def remove(self, record_id: str) -> bool:
        """Remove a record."""
        if record_id in self._records:
            del self._records[record_id]
            return True
        return False

    def clear(self) -> None:
        """Clear all history."""
        self._records.clear()

    def count(self) -> int:
        """Get total record count."""
        return len(self._records)

    def get_summary_for_tool(self, tool_name: str) -> ExperienceSummary:
        """Get summary of executions for a tool."""
        tool_records = [r for r in self._records.values() if r.tool_name == tool_name]
        return self._create_summary(tool_name, tool_records)

    def get_summary_for_capability(self, capability_id: str) -> ExperienceSummary:
        """Get summary of executions for a capability."""
        cap_records = [r for r in self._records.values() if r.capability_id == capability_id]
        if cap_records:
            return self._create_summary(capability_id, cap_records, capability_id=capability_id)
        return ExperienceSummary(
            capability_id=capability_id,
            tool_name="",
            total_executions=0,
            successful_executions=0,
            failed_executions=0,
            success_rate=0.0,
            average_duration_ms=0.0,
            last_execution=None,
        )

    def _create_summary(
        self, tool_name: str, records: List[ExperienceRecord], capability_id: str = ""
    ) -> ExperienceSummary:
        """Create an ExperienceSummary from records."""
        if not records:
            return ExperienceSummary(
                capability_id=capability_id or "",
                tool_name=tool_name,
                total_executions=0,
                successful_executions=0,
                failed_executions=0,
                success_rate=0.0,
                average_duration_ms=0.0,
                last_execution=None,
            )

        successful = sum(1 for r in records if r.success)
        total = len(records)
        avg_duration = sum(r.duration_ms for r in records) / total

        return ExperienceSummary(
            capability_id=capability_id or records[0].capability_id,
            tool_name=tool_name,
            total_executions=total,
            successful_executions=successful,
            failed_executions=total - successful,
            success_rate=successful / total if total > 0 else 0.0,
            average_duration_ms=avg_duration,
            last_execution=records[-1].timestamp,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert history to dictionary."""
        return {
            "records": {k: v.to_dict() for k, v in self._records.items()},
            "count": self.count(),
        }