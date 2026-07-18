"""Goal Planner - creates execution plans from goals."""

from typing import Any, Dict, List, Optional
from .models import Goal, GoalPlan, GoalStep, GoalStatus
from .graph import GoalGraph


class GoalPlanner:
    """
    Creates execution plans from goals.

    Determines execution order and parallel groups.
    """

    def plan(self, goal: Goal) -> GoalPlan:
        """
        Create an execution plan from a goal.

        Args:
            goal: The goal to plan.

        Returns:
            GoalPlan with execution order and parallel groups.
        """
        graph = GoalGraph(goal)
        graph.build(goal)

        return GoalPlan(
            goal=goal,
            execution_order=graph.get_execution_order(),
            parallel_groups=graph.get_parallel_groups(),
        )

    def get_critical_path(self, goal: Goal) -> List[str]:
        """Get the critical path through the goal."""
        # For now, just return the longest dependency chain
        graph = GoalGraph(goal)
        graph.build(goal)

        # Simple implementation: return execution order
        return graph.get_execution_order()