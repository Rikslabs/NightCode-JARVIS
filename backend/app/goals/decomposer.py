"""Goal Decomposer - breaks down goals into executable steps."""

from typing import Any, Dict, List, Optional
from .models import Goal, GoalStep, GoalStepType, GoalStatus


class GoalDecomposer:
    """
    Decomposes high-level goals into executable steps.

    Deterministic decomposition based on goal keywords.
    """

    # Goal patterns mapped to step types
    GOAL_PATTERNS = {
        "review": [GoalStepType.REVIEW, GoalStepType.ANALYSIS],
        "analyze": [GoalStepType.ANALYSIS, GoalStepType.VALIDATION],
        "plan": [GoalStepType.DECISION, GoalStepType.ACTION],
        "refactor": [GoalStepType.ANALYSIS, GoalStepType.ACTION],
        "fix": [GoalStepType.ANALYSIS, GoalStepType.ACTION, GoalStepType.VALIDATION],
        "implement": [GoalStepType.ACTION, GoalStepType.VALIDATION],
        "test": [GoalStepType.ACTION, GoalStepType.VALIDATION],
        "optimize": [GoalStepType.ANALYSIS, GoalStepType.ACTION],
    }

    def decompose(self, goal_description: str) -> Goal:
        """
        Decompose a goal into steps.

        Args:
            goal_description: Natural language goal description.

        Returns:
            Goal with decomposed steps.
        """
        goal_id = f"goal_{goal_description.lower().replace(' ', '_')}"
        steps = []

        # Analyze the goal to determine step types
        step_types = self._analyze_goal(goal_description)

        for i, step_type in enumerate(step_types):
            step = GoalStep(
                id=f"{goal_id}_step_{i}",
                description=f"{step_type.value}: {goal_description}",
                step_type=step_type,
                capability=self._map_step_to_capability(step_type),
                tool=self._map_step_to_tool(step_type),
                status=GoalStatus.PENDING,
            )
            steps.append(step)

        return Goal(
            goal_id=goal_id,
            description=goal_description,
            steps=steps,
        )

    def _analyze_goal(self, goal: str) -> List[GoalStepType]:
        """Analyze goal to determine required steps."""
        goal_lower = goal.lower()
        step_types = []

        # Check for patterns in goal
        for keyword, patterns in self.GOAL_PATTERNS.items():
            if keyword in goal_lower:
                step_types.extend(patterns)
                break

        # Default: single action step
        if not step_types:
            step_types = [GoalStepType.ACTION]

        return step_types

    def _map_step_to_capability(self, step_type: GoalStepType) -> str:
        """Map step type to capability."""
        mapping = {
            GoalStepType.ANALYSIS: "code_analysis",
            GoalStepType.ACTION: "implementation",
            GoalStepType.VALIDATION: "verification",
            GoalStepType.REVIEW: "code_review",
            GoalStepType.DECISION: "planning",
        }
        return mapping.get(step_type, "generic")

    def _map_step_to_tool(self, step_type: GoalStepType) -> str:
        """Map step type to tool."""
        mapping = {
            GoalStepType.ANALYSIS: "analyze",
            GoalStepType.ACTION: "code",
            GoalStepType.VALIDATION: "validate",
            GoalStepType.REVIEW: "review",
            GoalStepType.DECISION: "planning",
        }
        return mapping.get(step_type, "generic")