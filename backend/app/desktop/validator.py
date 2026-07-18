"""Desktop validator for action safety."""

from typing import Optional

from .models import DesktopAction, ActionResult, ActionPermission
from .permissions import DesktopPermissionManager


class DesktopValidator:
    """Validates desktop actions for safety and correctness."""

    def __init__(self, permission_manager: Optional[DesktopPermissionManager] = None):
        self._permissions = permission_manager or DesktopPermissionManager()

    def validate(self, action: DesktopAction) -> ActionResult:
        """Validate an action and return result."""
        # Check required fields
        if not action.action_type:
            return ActionResult(
                success=False,
                action=action,
                message="Action type is required",
            )

        # Check permission
        permission = self._permissions.check_permission(action)
        if permission == ActionPermission.DENY:
            return ActionResult(
                success=False,
                action=action,
                message="Action denied by permission policy",
            )

        return ActionResult(
            success=True,
            action=action,
            message="Action validated successfully",
        )

    def validate_coordinates(self, x: Optional[int], y: Optional[int]) -> bool:
        """Validate mouse coordinates."""
        if x is None or y is None:
            return True  # Optional
        if x < 0 or y < 0:
            return False
        if x > 10000 or y > 10000:
            return False
        return True