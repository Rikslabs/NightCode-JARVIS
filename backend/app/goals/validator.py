"""Goal Validator - validates goal structure and dependencies."""

from typing import Any, Dict, List, Optional
from .models import Goal, GoalValidationResult, GoalStep, GoalStatus
from .graph import GoalGraph


class GoalValidator:
    """
    Validates goal structure and detects issues.

    Checks for cycles, missing dependencies, and invalid states.
    """

    def validate(self, goal: Goal) -> GoalValidationResult:
        """
        Validate a goal.

        Args:
            goal: Goal to validate.

        Returns:
            GoalValidationResult with any errors found.
        """
        errors = []
        warnings = []

        # Build graph and check for cycles
        graph = GoalGraph(goal)
        graph.build(goal)

        if graph.has_cycles():
            errors.append("Goal contains circular dependencies")

        # Check for missing step references
        step_ids = {step.id for step in goal.steps}
        for dep in goal.dependencies:
            if dep.step_id not in step_ids:
                errors.append(f"Dependency references unknown step: {dep.step_id}")
            if dep.depends_on_step_id not in step_ids:
                errors.append(f"Dependency references unknown step: {dep.depends_on_step_id}")

        # Check for empty goal
        if not goal.steps:
            warnings.append("Goal has no steps")

        return GoalValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            cycle_detected=graph.has_cycles(),
        )

    def validate_step_ids(self, goal: Goal) -> List[str]:
        """Validate that all step IDs are unique."""
        errors = []
        ids = [step.id for step in goal.steps]
        if len(ids) != len(set(ids)):
            errors.append("Duplicate step IDs found")
        return errors