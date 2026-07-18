"""Browser validator for action safety."""

from typing import Optional

from .models import BrowserAction, BrowserActionResult


class BrowserValidator:
    """Validates browser actions for safety and correctness."""

    def validate(self, action: str) -> BrowserActionResult:
        """Validate an action and return result."""
        if action not in [a.value for a in BrowserAction]:
            return BrowserActionResult(
                success=False,
                action=action,
                message="Unknown browser action",
            )

        return BrowserActionResult(
            success=True,
            action=action,
            message="Action validated",
        )

    def is_valid_action(self, action: str) -> bool:
        """Check if action is valid."""
        return action in [a.value for a in BrowserAction]