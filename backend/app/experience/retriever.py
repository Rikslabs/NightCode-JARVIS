"""Experience Retriever - finds similar historical experiences."""

from typing import List, Optional
from .models import ExperienceRecord, ExperienceMatch
from .history import ExecutionHistory


class ExperienceRetriever:
    """
    Retrieves similar experiences from execution history.

    No AI - deterministic keyword matching and overlap scoring.
    """

    def __init__(self, history: Optional[ExecutionHistory] = None):
        """Initialize with optional history."""
        self._history = history or ExecutionHistory()

    def retrieve(self, goal: str, top_n: int = 10) -> List[ExperienceMatch]:
        """
        Retrieve similar experiences for a goal.

        Args:
            goal: Goal to match against.
            top_n: Maximum results to return.

        Returns:
            List of ExperienceMatch objects.
        """
        goal_lower = goal.lower()
        matches = []

        for record in self._history.list_all():
            similarity = self._calculate_similarity(goal_lower, record)
            if similarity > 0:
                matches.append(
                    ExperienceMatch(
                        record=record,
                        confidence=similarity,
                        similarity_score=similarity,
                        match_reason=self._get_match_reason(goal_lower, record),
                    )
                )

        # Sort by similarity descending
        matches.sort(key=lambda m: m.similarity_score, reverse=True)
        return matches[:top_n]

    def retrieve_by_tool(self, tool_name: str, top_n: int = 10) -> List[ExperienceMatch]:
        """Retrieve experiences for a specific tool."""
        matches = []
        for record in self._history.list_all():
            if record.tool_name == tool_name:
                matches.append(
                    ExperienceMatch(
                        record=record,
                        confidence=1.0,
                        similarity_score=1.0,
                        match_reason="same tool",
                    )
                )
        return matches[:top_n]

    def retrieve_by_capability(self, capability_id: str, top_n: int = 10) -> List[ExperienceMatch]:
        """Retrieve experiences for a specific capability."""
        matches = []
        for record in self._history.list_all():
            if record.capability_id == capability_id:
                matches.append(
                    ExperienceMatch(
                        record=record,
                        confidence=1.0,
                        similarity_score=1.0,
                        match_reason="same capability",
                    )
                )
        return matches[:top_n]

    def _calculate_similarity(self, goal: str, record: ExperienceRecord) -> float:
        """Calculate similarity between goal and historical record."""
        score = 0.0

        # Goal keyword overlap
        if record.goal:
            goal_words = set(goal.split())
            record_words = set(record.goal.lower().split())
            overlap = len(goal_words & record_words)
            if overlap > 0:
                score += min(0.5, overlap * 0.1)

        # Tool overlap boosts score
        score += 0.1

        # Successful executions get higher score
        if record.success:
            score += 0.2

        return min(1.0, score)

    def _get_match_reason(self, goal: str, record: ExperienceRecord) -> str:
        """Get match reason string."""
        reasons = []

        if record.goal:
            goal_words = set(goal.split())
            record_words = set(record.goal.lower().split())
            overlap = goal_words & record_words
            if overlap:
                reasons.append(f"goal overlap: {', '.join(overlap)}")

        if record.success:
            reasons.append("successful execution")

        return "; ".join(reasons) if reasons else "similar execution"