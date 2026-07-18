"""Browser permissions management."""

from typing import Optional

from .models import BrowserAction, BrowserPermission


class BrowserPermissionManager:
    """Manages browser action permissions."""

    # Actions allowed by default
    DEFAULT_ALLOW = {
        BrowserAction.OPEN_URL.value,
        BrowserAction.BACK.value,
        BrowserAction.FORWARD.value,
        BrowserAction.REFRESH.value,
        BrowserAction.NEW_TAB.value,
        BrowserAction.CLOSE_TAB.value,
        BrowserAction.SWITCH_TAB.value,
        BrowserAction.LIST_TABS.value,
        BrowserAction.GET_TITLE.value,
        BrowserAction.GET_TEXT.value,
        BrowserAction.GET_LINKS.value,
        BrowserAction.GET_METADATA.value,
        BrowserAction.GET_STATUS.value,
    }

    # Actions requiring approval
    REQUIRE_APPROVAL = {
        BrowserAction.UPLOAD_FILE.value,
        BrowserAction.SUBMIT_FORM.value,
        BrowserAction.START_DOWNLOAD.value,
        BrowserAction.CANCEL_DOWNLOAD.value,
    }

    def __init__(self):
        self._permissions: dict = {}

    def check_permission(self, action: str) -> BrowserPermission:
        """Check permission for an action."""
        if action in self._permissions:
            return self._permissions[action]
        if action in self.REQUIRE_APPROVAL:
            return BrowserPermission.PROMPT
        return BrowserPermission.ALLOW

    def set_permission(self, action: str, permission: BrowserPermission) -> None:
        """Set permission for an action."""
        self._permissions[action] = permission

    def is_safe(self, action: str) -> bool:
        """Check if action is safe to execute without approval."""
        return action in self.DEFAULT_ALLOW

    def requires_approval(self, action: str) -> bool:
        """Check if action requires approval."""
        return action in self.REQUIRE_APPROVAL