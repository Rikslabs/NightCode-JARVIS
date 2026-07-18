"""Desktop permission management."""

from typing import Dict, Optional

from .models import ActionPermission, DesktopAction


class DesktopPermissionManager:
    """
    Manages permissions for desktop actions.

    Dangerous actions are blocked by default.
    All actions require permission validation.
    """

    DANGEROUS_ACTIONS = {
        "open_app",
        "delete_file",
        "execute_command",
    }

    def __init__(self):
        self._permissions: Dict[str, ActionPermission] = {}
        self._audit_log: list = []

    def check_permission(self, action: DesktopAction) -> ActionPermission:
        """Check if an action is permitted."""
        action_type = action.action_type

        # Check explicit permission
        if action_type in self._permissions:
            return self._permissions[action_type]

        # Dangerous actions denied by default
        if action_type in self.DANGEROUS_ACTIONS:
            return ActionPermission.DENY

        # Default to prompt for safety
        return ActionPermission.PROMPT

    def set_permission(
        self,
        action_type: str,
        permission: ActionPermission,
    ) -> None:
        """Set permission for an action type."""
        self._permissions[action_type] = permission

    def allow_action(self, action_type: str) -> None:
        """Allow an action type."""
        self.set_permission(action_type, ActionPermission.ALLOW)

    def deny_action(self, action_type: str) -> None:
        """Deny an action type."""
        self.set_permission(action_type, ActionPermission.DENY)

    def log_action(self, action: DesktopAction, result: bool) -> None:
        """Log action for audit purposes."""
        self._audit_log.append({
            "action": action.action_type,
            "parameters": action.parameters,
            "result": result,
            "timestamp": action.timestamp,
        })

    def get_audit_log(self) -> list:
        """Get all logged actions."""
        return list(self._audit_log)

    def clear_audit_log(self) -> None:
        """Clear audit log."""
        self._audit_log.clear()