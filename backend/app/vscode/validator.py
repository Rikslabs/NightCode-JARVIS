"""VS Code validator for action safety."""

from typing import Optional

from .models import VSAction, VSActionResult


class VSCodeValidator:
    """Validates VS Code actions for safety and correctness."""

    # Dangerous actions that require approval
    DANGEROUS_ACTIONS = {
        VSAction.RUN_COMMAND.value,
    }

    # Read-only actions allowed by default
    READ_ONLY_ACTIONS = {
        VSAction.GET_CURRENT_WORKSPACE.value,
        VSAction.GET_PROBLEMS.value,
    }

    def validate(self, action: str) -> VSActionResult:
        """Validate an action and return result."""
        if action not in [a.value for a in VSAction]:
            return VSActionResult(
                success=False,
                action=action,
                message="Unknown VS Code action",
            )

        return VSActionResult(
            success=True,
            action=action,
            message="Action validated",
        )

    def is_read_only(self, action: str) -> bool:
        """Check if action is read-only."""
        return action in self.READ_ONLY_ACTIONS

    def requires_approval(self, action: str) -> bool:
        """Check if action requires approval."""
        return action in self.DANGEROUS_ACTIONS