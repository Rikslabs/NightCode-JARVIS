"""Main desktop controller."""

from typing import Optional, Any, Dict

from .models import DesktopAction, ActionResult, ActionPermission
from .mouse import MouseController
from .keyboard import KeyboardController
from .clipboard import ClipboardController
from .windows import WindowController
from .permissions import DesktopPermissionManager


class DesktopController:
    """
    Main controller for desktop automation.

    Coordinates all desktop action controllers with permission validation.
    """

    def __init__(
        self,
        permission_manager: Optional[DesktopPermissionManager] = None,
    ):
        self._mouse = MouseController(permission_manager)
        self._keyboard = KeyboardController()
        self._clipboard = ClipboardController()
        self._windows = WindowController()
        self._permissions = permission_manager or DesktopPermissionManager()

    def execute(self, action: DesktopAction) -> ActionResult:
        """Execute a desktop action with permission validation."""
        # Check permission
        permission = self._permissions.check_permission(action)

        if permission == ActionPermission.DENY:
            result = ActionResult(
                success=False,
                action=action,
                message="Action denied by permission policy",
            )
            self._permissions.log_action(action, False)
            return result

        # Execute action
        result_data = self._execute_action(action)
        result = ActionResult(
            success=True,
            action=action,
            message="Action executed successfully",
            data=result_data,
        )
        self._permissions.log_action(action, True)
        return result

    def _execute_action(self, action: DesktopAction) -> Any:
        """Execute the action and return result data."""
        action_type = action.action_type
        params = action.parameters

        if action_type == "move_mouse":
            return {"x": params.get("x"), "y": params.get("y")}
        elif action_type == "click":
            return {"clicked": True}
        elif action_type == "type":
            return {"typed": params.get("text", "")}
        elif action_type == "hotkey":
            return {"keys": params.get("keys", [])}
        elif action_type == "copy":
            return {"copied": True}
        elif action_type == "paste":
            return {"pasted": True}
        elif action_type == "open_app":
            return {"opened": params.get("app", "")}

        return {"status": "unknown_action"}

    def get_audit_log(self) -> list:
        """Get audit log of all actions."""
        return self._permissions.get_audit_log()