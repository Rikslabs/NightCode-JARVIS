"""Intelligence context for managing reasoning state."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class IntelligenceContext:
    """
    Context manager for the Intelligence Orchestrator.

    Maintains the state throughout the reasoning, planning, and execution pipeline.
    """

    project_path: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def add_to_history(self, event: str, data: Dict[str, Any]) -> None:
        """
        Add an event to the intelligence history.

        Args:
            event: Name of the event (e.g., "intent_analyzed", "tool_selected").
            data: Event data to store.
        """
        self.history.append(
            {"event": event, "data": data, "timestamp": datetime.now(timezone.utc).isoformat()}
        )

    def get_history(self) -> List[Dict[str, Any]]:
        """Get the history of events."""
        return list(self.history)

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary representation."""
        return {
            "project_path": self.project_path,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "metadata": dict(self.metadata),
            "history": list(self.history),
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IntelligenceContext":
        """Create IntelligenceContext from dictionary."""
        return cls(
            project_path=data.get("project_path"),
            user_id=data.get("user_id"),
            session_id=data.get("session_id"),
            metadata=dict(data.get("metadata", {})),
            history=list(data.get("history", [])),
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
        )