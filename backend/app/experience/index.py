"""Experience Index - indexes experiences for fast lookup."""

from typing import Any, Dict, List, Optional
from .models import ExperienceRecord
from .history import ExecutionHistory


class ExperienceIndex:
    """
    Index for fast experience lookups.

    Maintains indexes by tool, capability, and goal keywords.
    """

    def __init__(self, history: Optional[ExecutionHistory] = None):
        """Initialize with optional history."""
        self._history = history or ExecutionHistory()
        self._tool_index: Dict[str, List[str]] = {}
        self._capability_index: Dict[str, List[str]] = {}
        self._goal_index: Dict[str, List[str]] = {}

    def build(self) -> None:
        """Build indexes from history."""
        self._tool_index.clear()
        self._capability_index.clear()
        self._goal_index.clear()

        for record in self._history.list_all():
            # Index by tool
            if record.tool_name not in self._tool_index:
                self._tool_index[record.tool_name] = []
            self._tool_index[record.tool_name].append(record.id)

            # Index by capability
            if record.capability_id not in self._capability_index:
                self._capability_index[record.capability_id] = []
            self._capability_index[record.capability_id].append(record.id)

            # Index by goal keywords
            if record.goal:
                for word in set(record.goal.lower().split()):
                    if word not in self._goal_index:
                        self._goal_index[word] = []
                    self._goal_index[word].append(record.id)

    def get_by_tool(self, tool_name: str) -> List[str]:
        """Get record IDs by tool name."""
        return self._tool_index.get(tool_name, [])

    def get_by_capability(self, capability_id: str) -> List[str]:
        """Get record IDs by capability."""
        return self._capability_index.get(capability_id, [])

    def get_by_goal_keyword(self, keyword: str) -> List[str]:
        """Get record IDs by goal keyword."""
        return self._goal_index.get(keyword.lower(), [])

    def search(self, goal: str) -> List[str]:
        """Search for records matching goal keywords."""
        matching_ids = set()
        for word in goal.lower().split():
            ids = self._goal_index.get(word, [])
            matching_ids.update(ids)
        return list(matching_ids)

    def to_dict(self) -> Dict[str, Any]:
        """Convert index to dictionary."""
        return {
            "tools": {k: len(v) for k, v in self._tool_index.items()},
            "capabilities": {k: len(v) for k, v in self._capability_index.items()},
            "goal_keywords": {k: len(v) for k, v in self._goal_index.items()},
        }