"""Goal Optimizer - optimizes goal execution plans."""

from typing import Any, Dict, List, Optional
from .models import Goal, GoalStep, GoalStatus, GoalRecommendation
from .graph import GoalGraph


class GoalOptimizer:
    """
    Optimizes goal plans.

    Detects parallel execution opportunities and suggests improvements.
    """

    def optimize(self, goal: Goal) -> List[GoalRecommendation]:
        """
        Optimize a goal plan.

        Args:
            goal: Goal to optimize.

        Returns:
            List of recommendations for improvement.
        """
        recommendations = []
        graph = GoalGraph(goal)
        graph.build(goal)

        # Check for parallel execution opportunities
        parallel_groups = graph.get_parallel_groups()
        for group in parallel_groups:
            if len(group) > 1:
                for step_id in group[:2]:  # Just first 2 for example
                    recommendations.append(GoalRecommendation(
                        step_id=step_id,
                        reason="Can run in parallel with other steps",
                        suggested_action="Execute simultaneously",
                        confidence=0.8,
                    ))

        # Check for steps with duplicate tools
        tool_count: Dict[str, int] = {}
        for step in goal.steps:
            tool_count[step.tool] = tool_count.get(step.tool, 0) + 1

        for step in goal.steps:
            if tool_count.get(step.tool, 0) > 2:
                recommendations.append(GoalRecommendation(
                    step_id=step.id,
                    reason="Tool used multiple times",
                    suggested_action="Consider batching",
                    confidence=0.6,
                ))

        return recommendations

    def get_parallel_execution_steps(self, goal: Goal) -> List[List[str]]:
        """Get groups of steps that can be executed in parallel."""
        graph = GoalGraph(goal)
        graph.build(goal)
        return graph.get_parallel_groups()