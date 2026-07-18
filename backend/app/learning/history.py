"""Learning history management."""

from typing import Any, Dict, List, Optional


class LearningHistory:
    """Manages historical learning data."""

    def __init__(self):
        self._history: List[Dict[str, Any]] = []

    def add_record(self, record: Dict[str, Any]) -> None:
        """Add a record to history."""
        self._history.append(record)

    def get_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent history records."""
        return self._history[-limit:]

    def get_by_tool(self, tool_name: str) -> List[Dict[str, Any]]:
        """Get history records filtered by tool name."""
        return [r for r in self._history if r.get("tool_name") == tool_name]

    def get_successful(self) -> List[Dict[str, Any]]:
        """Get successful execution records."""
        return [r for r in self._history if r.get("success", False)]

    def get_failed(self) -> List[Dict[str, Any]]:
        """Get failed execution records."""
        return [r for r in self._history if not r.get("success", True)]

    def clear(self) -> None:
        """Clear all history."""
        self._history.clear()

    def to_dict(self) -> Dict[str, Any]:
        """Export history as dictionary."""
        return {
            "total": len(self._history),
            "history": self._history,
        }