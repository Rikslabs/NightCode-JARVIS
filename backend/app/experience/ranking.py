"""Experience Ranking - ranks experiences for recommendations."""

from typing import List, Optional
from .models import ExperienceMatch, ExperienceRecommendation
from .scoring import ExperienceScorer
from .history import ExecutionHistory


class ExperienceRanker:
    """
    Ranks experiences and produces recommendations.

    Considers success rate, recency, frequency, and execution time.
    """

    def __init__(self, history: Optional[ExecutionHistory] = None, scorer: Optional[ExperienceScorer] = None):
        """Initialize with optional history and scorer."""
        self._history = history or ExecutionHistory()
        self._scorer = scorer or ExperienceScorer()

    def rank(self, matches: List[ExperienceMatch]) -> List[ExperienceMatch]:
        """
        Rank experiences by their scores.

        Args:
            matches: Experience matches to rank.

        Returns:
            Sorted list by overall score.
        """
        # Apply scoring to each match
        for match in matches:
            score = self._scorer.score(match.record)
            match.confidence = score.overall_score

        return sorted(matches, key=lambda m: m.confidence, reverse=True)

    def recommend(self, goal: str, top_n: int = 5) -> List[ExperienceRecommendation]:
        """
        Generate recommendations for a goal.

        Args:
            goal: Goal to base recommendations on.
            top_n: Number of recommendations to return.

        Returns:
            List of ExperienceRecommendation objects.
        """
        # Group records by tool
        tool_records: dict = {}
        for record in self._history.list_all():
            if record.tool_name not in tool_records:
                tool_records[record.tool_name] = []
            tool_records[record.tool_name].append(record)

        recommendations = []

        for tool_name, records in tool_records.items():
            # Calculate tool success rate
            success_count = sum(1 for r in records if r.success)
            success_rate = success_count / len(records) if records else 0

            # Get most common capability
            capability_counts: dict = {}
            for r in records:
                capability_counts[r.capability_id] = capability_counts.get(r.capability_id, 0) + 1
            best_capability = max(capability_counts.items(), key=lambda x: x[1])[0] if capability_counts else ""

            recommendations.append(
                ExperienceRecommendation(
                    tool_name=tool_name,
                    capability_id=best_capability,
                    confidence=success_rate,
                    reason=f"based on {len(records)} previous executions",
                    based_on_experiences=[r.id for r in records],
                )
            )

        # Sort by confidence
        recommendations.sort(key=lambda r: r.confidence, reverse=True)
        return recommendations[:top_n]