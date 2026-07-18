"""Knowledge management for learning engine."""

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone


class LearningKnowledge:
    """Manages learned knowledge for tool reliability and recommendations."""

    def __init__(self):
        self._tool_reliability: Dict[str, float] = {}
        self._capability_effectiveness: Dict[str, float] = {}

    def update_tool_reliability(self, tool_name: str, success: bool) -> None:
        """Update reliability score for a tool."""
        current = self._tool_reliability.get(tool_name, 0.5)
        if success:
            self._tool_reliability[tool_name] = min(1.0, current + 0.1)
        else:
            self._tool_reliability[tool_name] = max(0.0, current - 0.1)

    def get_tool_reliability(self, tool_name: str) -> float:
        """Get reliability score for a tool."""
        return self._tool_reliability.get(tool_name, 0.5)

    def get_most_reliable_tools(self, limit: int = 3) -> List[str]:
        """Get most reliable tools."""
        sorted_tools = sorted(
            self._tool_reliability.items(),
            key=lambda x: x[1],
            reverse=True,
        )
        return [t[0] for t in sorted_tools[:limit]]

    def update_capability_effectiveness(
        self,
        capability: str,
        success: bool,
        confidence: float,
    ) -> None:
        """Update effectiveness score for a capability."""
        current = self._capability_effectiveness.get(capability, 0.5)
        if success:
            self._capability_effectiveness[capability] = min(
                1.0, current + confidence * 0.1
            )
        else:
            self._capability_effectiveness[capability] = max(
                0.0, current - 0.05
            )

    def get_capability_effectiveness(self, capability: str) -> float:
        """Get effectiveness score for a capability."""
        return self._capability_effectiveness.get(capability, 0.5)

    def get_recommendations(self, intent: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get tool recommendations based on learned knowledge."""
        recommendations = []
        for tool, reliability in self._tool_reliability.items():
            if reliability >= 0.7:
                recommendations.append({
                    "tool": tool,
                    "confidence": reliability,
                    "reason": "High reliability based on history",
                })
        return recommendations[:5]

    def to_dict(self) -> Dict[str, Any]:
        """Export knowledge as dictionary."""
        return {
            "tool_reliability": dict(self._tool_reliability),
            "capability_effectiveness": dict(self._capability_effectiveness),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def clear(self) -> None:
        """Clear all knowledge."""
        self._tool_reliability.clear()
        self._capability_effectiveness.clear()