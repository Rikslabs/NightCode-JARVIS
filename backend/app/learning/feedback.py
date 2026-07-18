"""Feedback collector for learning engine."""

from typing import Any, Dict, List, Optional


class FeedbackCollector:
    """Collects feedback from execution results."""

    def __init__(self):
        self._feedback: List[Dict[str, Any]] = []

    def collect(
        self,
        execution_id: str,
        success: bool,
        feedback: Optional[str] = None,
        metrics: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Collect feedback for an execution."""
        self._feedback.append({
            "execution_id": execution_id,
            "success": success,
            "feedback": feedback,
            "metrics": metrics or {},
        })

    def get_all(self) -> List[Dict[str, Any]]:
        """Get all collected feedback."""
        return list(self._feedback)

    def get_failure_feedback(self) -> List[Dict[str, Any]]:
        """Get feedback for failed executions."""
        return [f for f in self._feedback if not f.get("success", True)]

    def clear(self) -> None:
        """Clear all feedback."""
        self._feedback.clear()

    def to_dict(self) -> Dict[str, Any]:
        """Export feedback as dictionary."""
        return {
            "total": len(self._feedback),
            "failures": len(self.get_failure_feedback()),
            "feedback": self._feedback,
        }