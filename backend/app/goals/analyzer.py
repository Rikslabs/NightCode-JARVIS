"""Goal Analyzer - analyzes goal patterns and statistics."""

from typing import Any, Dict, List, Optional
from .models import Goal, GoalStatistics, GoalStep
from collections import Counter


class GoalAnalyzer:
    """
    Analyzes goals to extract statistics and patterns.

    Generates reports on goal execution patterns.
    """

    def analyze(self, goals: List[Goal]) -> GoalStatistics:
        """
        Analyze a list of goals.

        Args:
            goals: List of goals to analyze.

        Returns:
            GoalStatistics with analysis results.
        """
        total = len(goals)
        completed = sum(1 for g in goals if g.status.name == "COMPLETED")
        failed = sum(1 for g in goals if g.status.name == "FAILED")

        # Count tools across all goals
        tool_counts: Dict[str, int] = {}
        for goal in goals:
            for step in goal.steps:
                tool_counts[step.tool] = tool_counts.get(step.tool, 0) + 1

        # Get most common tools
        tool_counter = Counter(tool_counts)
        most_common = [t[0] for t in tool_counter.most_common(10)]

        # Calculate average steps
        total_steps = sum(len(g.steps) for g in goals)
        avg_steps = total_steps / total if total > 0 else 0.0

        return GoalStatistics(
            total_goals=total,
            completed_goals=completed,
            failed_goals=failed,
            average_steps_per_goal=avg_steps,
            most_common_tools=most_common,
        )

    def get_step_distribution(self, goals: List[Goal]) -> Dict[str, int]:
        """Get distribution of step types."""
        distribution: Dict[str, int] = {}
        for goal in goals:
            for step in goal.steps:
                stype = step.step_type.name
                distribution[stype] = distribution.get(stype, 0) + 1
        return distribution

    def get_dependency_complexity(self, goal: Goal) -> int:
        """Get dependency complexity score for a goal."""
        return len(goal.dependencies)

    def to_dict(self, goals: List[Goal]) -> Dict[str, Any]:
        """Convert analysis to dictionary."""
        stats = self.analyze(goals)
        return {
            "statistics": stats.to_dict(),
            "step_distribution": self.get_step_distribution(goals),
        }