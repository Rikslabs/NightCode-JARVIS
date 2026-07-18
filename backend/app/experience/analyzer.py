"""Experience Analyzer - generates analytics and statistics."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from .models import ExperienceStatistics, ExperienceSummary
from .history import ExecutionHistory


class ExperienceAnalyzer:
    """
    Analyzes experience history for insights.

    Generates statistics, identifies patterns, and provides analytics.
    """

    def __init__(self, history: Optional[ExecutionHistory] = None):
        """Initialize with optional history."""
        self._history = history or ExecutionHistory()

    def get_statistics(self) -> ExperienceStatistics:
        """Get overall experience statistics."""
        records = self._history.list_all()
        total = len(records)
        successful = sum(1 for r in records if r.success)
        failed = total - successful

        # Calculate average duration
        avg_duration = sum(r.duration_ms for r in records) / total if total > 0 else 0.0

        return ExperienceStatistics(
            total_records=total,
            total_successful=successful,
            total_failed=failed,
            overall_success_rate=successful / total if total > 0 else 0.0,
            tool_statistics=self._get_tool_statistics(),
            capability_statistics=self._get_capability_statistics(),
            average_duration_ms=avg_duration,
        )

    def _get_tool_statistics(self) -> Dict[str, ExperienceSummary]:
        """Get per-tool statistics."""
        tool_records: Dict[str, List] = {}
        for record in self._history.list_all():
            if record.tool_name not in tool_records:
                tool_records[record.tool_name] = []
            tool_records[record.tool_name].append(record)

        result = {}
        for tool_name, records in tool_records.items():
            successful = sum(1 for r in records if r.success)
            total = len(records)
            avg_duration = sum(r.duration_ms for r in records) / total

            result[tool_name] = ExperienceSummary(
                capability_id=records[0].capability_id if records else "",
                tool_name=tool_name,
                total_executions=total,
                successful_executions=successful,
                failed_executions=total - successful,
                success_rate=successful / total if total > 0 else 0.0,
                average_duration_ms=avg_duration,
                last_execution=records[-1].timestamp if records else None,
            )
        return result

    def _get_capability_statistics(self) -> Dict[str, ExperienceSummary]:
        """Get per-capability statistics."""
        cap_records: Dict[str, List] = {}
        for record in self._history.list_all():
            if record.capability_id not in cap_records:
                cap_records[record.capability_id] = []
            cap_records[record.capability_id].append(record)

        result = {}
        for capability_id, records in cap_records.items():
            successful = sum(1 for r in records if r.success)
            total = len(records)
            avg_duration = sum(r.duration_ms for r in records) / total

            result[capability_id] = ExperienceSummary(
                capability_id=capability_id,
                tool_name=records[0].tool_name if records else "",
                total_executions=total,
                successful_executions=successful,
                failed_executions=total - successful,
                success_rate=successful / total if total > 0 else 0.0,
                average_duration_ms=avg_duration,
                last_execution=records[-1].timestamp if records else None,
            )
        return result

    def get_most_used_tools(self, limit: int = 10) -> List[str]:
        """Get most frequently used tools."""
        tool_counts: Dict[str, int] = {}
        for record in self._history.list_all():
            tool_counts[record.tool_name] = tool_counts.get(record.tool_name, 0) + 1

        sorted_tools = sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)
        return [t[0] for t in sorted_tools[:limit]]

    def get_most_successful_capabilities(self, limit: int = 10) -> List[str]:
        """Get capabilities with highest success rates."""
        cap_stats = self._get_capability_statistics()
        sorted_caps = sorted(
            [(k, v.success_rate) for k, v in cap_stats.items()],
            key=lambda x: x[1],
            reverse=True,
        )
        return [c[0] for c in sorted_caps[:limit]]

    def get_failure_statistics(self) -> Dict[str, int]:
        """Get tool/capability failure counts."""
        failures: Dict[str, int] = {}
        for record in self._history.list_all():
            if not record.success:
                key = f"{record.tool_name}/{record.capability_id}"
                failures[key] = failures.get(key, 0) + 1
        return failures

    def to_dict(self) -> Dict[str, Any]:
        """Convert analyzer results to dictionary."""
        stats = self.get_statistics()
        return {
            "statistics": stats.to_dict(),
            "most_used_tools": self.get_most_used_tools(),
            "most_successful_capabilities": self.get_most_successful_capabilities(),
            "failure_statistics": self.get_failure_statistics(),
        }