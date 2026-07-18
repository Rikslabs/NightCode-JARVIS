"""Learning Engine - Main engine for learning from execution history."""

from typing import Any, Dict, List, Optional

from .models import (
    ExecutionHistory,
    LearningRecord,
    LearningSummary,
    LearningStatistics,
)
from .registry import LearningRegistry


class LearningEngine:
    """
    Main learning engine that processes execution history.

    Learns from:
    - Successful executions
    - Failed executions
    - Workflow completion
    - Validation results
    - Execution duration
    - Decision confidence
    - Selected strategy
    - Capability usage
    - Tool reliability
    """

    def __init__(self, registry: Optional[LearningRegistry] = None):
        self._registry = registry or LearningRegistry()
        self._records: List[LearningRecord] = []
        self._histories: List[ExecutionHistory] = []
        self._statistics = LearningStatistics(
            total_records=0,
            total_analyses=0,
            suggestions_generated=0,
            patterns_identified=0,
        )

    def record_execution(
        self,
        tool_name: str,
        intent: str,
        success: bool,
        duration: float,
        confidence: float,
        risk: Any,
        capability_used: Optional[str] = None,
    ) -> LearningRecord:
        """Record a single execution for learning."""
        history = ExecutionHistory(
            tool_name=tool_name,
            intent=intent,
            success=success,
            duration=duration,
            confidence=confidence,
            risk=risk,
            capability_used=capability_used,
        )
        self._histories.append(history)

        record = LearningRecord(
            execution_id=f"exec_{len(self._records) + 1}",
            tool_name=tool_name,
            success=success,
            duration=duration,
            confidence=confidence,
            lessons=["Recorded execution"] if success else ["Failed execution"],
        )
        self._records.append(record)
        self._statistics.total_records += 1

        return record

    def analyze(self) -> LearningSummary:
        """Analyze execution history and return summary."""
        if not self._histories:
            return LearningSummary(
                total_executions=0,
                successful_executions=0,
                failed_executions=0,
                average_duration=0.0,
                success_rate=0.0,
                most_reliable_tools=[],
            )

        total = len(self._histories)
        successful = sum(1 for h in self._histories if h.success)
        failed = total - successful
        avg_duration = sum(h.duration for h in self._histories) / total
        success_rate = successful / total if total > 0 else 0.0

        tool_success: Dict[str, int] = {}
        for h in self._histories:
            if h.success:
                tool_success[h.tool_name] = tool_success.get(h.tool_name, 0) + 1

        most_reliable = sorted(
            tool_success.keys(),
            key=lambda t: tool_success[t],
            reverse=True,
        )[:3]

        self._statistics.total_analyses += 1

        return LearningSummary(
            total_executions=total,
            successful_executions=successful,
            failed_executions=failed,
            average_duration=avg_duration,
            success_rate=success_rate,
            most_reliable_tools=most_reliable,
        )

    def get_suggestions(self) -> List[Any]:
        """Get optimization suggestions based on history."""
        summary = self.analyze()
        suggestions = []

        for tool in summary.most_reliable_tools:
            suggestions.append({
                "tool_name": tool,
                "confidence": 0.95,
                "reason": "High reliability",
                "impact": "positive",
            })

        self._statistics.suggestions_generated += len(suggestions)
        return suggestions

    def get_statistics(self) -> LearningStatistics:
        """Get current learning statistics."""
        return self._statistics

    def clear(self) -> None:
        """Clear all learning records."""
        self._records.clear()
        self._histories.clear()
        self._statistics = LearningStatistics(
            total_records=0,
            total_analyses=0,
            suggestions_generated=0,
            patterns_identified=0,
        )