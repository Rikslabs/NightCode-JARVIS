"""Learning analytics for pattern recognition."""

from typing import Any, Dict, List


class LearningAnalytics:
    """Analyzes learning data for patterns and insights."""

    def __init__(self):
        self._tool_metrics: Dict[str, Dict[str, Any]] = {}
        self._capability_metrics: Dict[str, Dict[str, Any]] = {}

    def track_tool(self, tool_name: str, duration: float, success: bool) -> None:
        """Track tool execution metrics."""
        if tool_name not in self._tool_metrics:
            self._tool_metrics[tool_name] = {
                "total_executions": 0,
                "successful": 0,
                "total_duration": 0.0,
            }

        metrics = self._tool_metrics[tool_name]
        metrics["total_executions"] += 1
        metrics["total_duration"] += duration
        if success:
            metrics["successful"] += 1

    def track_capability(
        self,
        capability: str,
        duration: float,
        success: bool,
    ) -> None:
        """Track capability execution metrics."""
        if capability not in self._capability_metrics:
            self._capability_metrics[capability] = {
                "total_executions": 0,
                "successful": 0,
                "total_duration": 0.0,
            }

        metrics = self._capability_metrics[capability]
        metrics["total_executions"] += 1
        metrics["total_duration"] += duration
        if success:
            metrics["successful"] += 1

    def get_tool_reliability(self, tool_name: str) -> float:
        """Get reliability score for a tool."""
        metrics = self._tool_metrics.get(tool_name, {})
        total = metrics.get("total_executions", 0)
        if total == 0:
            return 0.5
        return metrics.get("successful", 0) / total

    def get_avg_duration(self, tool_name: str) -> float:
        """Get average duration for a tool."""
        metrics = self._tool_metrics.get(tool_name, {})
        total = metrics.get("total_executions", 0)
        if total == 0:
            return 0.0
        return metrics.get("total_duration", 0.0) / total

    def get_top_tools(self, limit: int = 3) -> List[str]:
        """Get top performing tools."""
        sorted_tools = sorted(
            self._tool_metrics.items(),
            key=lambda x: self.get_tool_reliability(x[0]),
            reverse=True,
        )
        return [t[0] for t in sorted_tools[:limit]]

    def to_dict(self) -> Dict[str, Any]:
        """Export analytics as dictionary."""
        return {
            "tool_metrics": {
                t: {
                    "success_rate": self.get_tool_reliability(t),
                    "avg_duration": self.get_avg_duration(t),
                }
                for t in self._tool_metrics
            },
            "capability_metrics": dict(self._capability_metrics),
        }

    def clear(self) -> None:
        """Clear all analytics data."""
        self._tool_metrics.clear()
        self._capability_metrics.clear()