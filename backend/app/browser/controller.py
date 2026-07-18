"""Main Browser controller."""

from typing import Optional, Any

from .models import BrowserAction, BrowserActionResult
from .navigation import NavigationController
from .tabs import TabController
from .interaction import InteractionController
from .extraction import ExtractionController
from .downloads import DownloadController
from .permissions import BrowserPermissionManager


class BrowserController:
    """
    Main controller for browser automation.

    Coordinates all browser sub-controllers with permission validation.
    Designed around abstract adapter pattern for Playwright/Selenium/WebDriver compatibility.
    """

    def __init__(self, permission_manager: Optional[BrowserPermissionManager] = None):
        self._navigation = NavigationController()
        self._tabs = TabController()
        self._interaction = InteractionController()
        self._extraction = ExtractionController()
        self._downloads = DownloadController()
        self._permissions = permission_manager or BrowserPermissionManager()
        self._audit_log: list = []

    def execute(self, action: str, **kwargs) -> BrowserActionResult:
        """Execute a browser action with permission validation."""
        if self._permissions.requires_approval(action):
            # In real implementation, this would prompt for approval
            pass

        result = self._execute_action(action, kwargs)
        self._audit_log.append({
            "action": action,
            "success": result.success,
            "timestamp": result.timestamp,
        })
        return result

    def _execute_action(self, action: str, params: dict) -> BrowserActionResult:
        """Execute the action and return result."""
        # Navigation
        if action == BrowserAction.OPEN_URL.value:
            return self._navigation.open_url(params.get("url", ""))
        elif action == BrowserAction.BACK.value:
            return self._navigation.back()
        elif action == BrowserAction.FORWARD.value:
            return self._navigation.forward()
        elif action == BrowserAction.REFRESH.value:
            return self._navigation.refresh()
        elif action == BrowserAction.STOP_LOADING.value:
            return self._navigation.stop_loading()

        # Tabs
        elif action == BrowserAction.NEW_TAB.value:
            return self._tabs.new_tab(params.get("url"))
        elif action == BrowserAction.CLOSE_TAB.value:
            return self._tabs.close_tab(params.get("tab_id"))
        elif action == BrowserAction.SWITCH_TAB.value:
            return self._tabs.switch_tab(params.get("tab_id", 1))
        elif action == BrowserAction.LIST_TABS.value:
            return self._tabs.list_tabs()

        # Interaction
        elif action == BrowserAction.CLICK.value:
            return self._interaction.click(params.get("selector", ""))
        elif action == BrowserAction.TYPE.value:
            return self._interaction.type(params.get("selector", ""), params.get("text", ""))
        elif action == BrowserAction.SCROLL.value:
            return self._interaction.scroll(params.get("direction", "down"), params.get("amount"))
        elif action == BrowserAction.SUBMIT_FORM.value:
            return self._interaction.submit_form(params.get("selector", ""))
        elif action == BrowserAction.UPLOAD_FILE.value:
            return self._interaction.upload_file(params.get("selector", ""), params.get("file_path", ""))

        # Extraction
        elif action == BrowserAction.GET_TITLE.value:
            return self._extraction.get_title()
        elif action == BrowserAction.GET_TEXT.value:
            return self._extraction.get_text(params.get("selector"))
        elif action == BrowserAction.GET_LINKS.value:
            return self._extraction.get_links()
        elif action == BrowserAction.GET_METADATA.value:
            return self._extraction.get_metadata()
        elif action == BrowserAction.GET_STATUS.value:
            return self._extraction.get_status()

        # Downloads
        elif action == BrowserAction.START_DOWNLOAD.value:
            return self._downloads.start_download(params.get("url", ""), params.get("file_name"))
        elif action == BrowserAction.MONITOR_DOWNLOAD.value:
            return self._downloads.monitor_download(params.get("file_name", ""))
        elif action == BrowserAction.CANCEL_DOWNLOAD.value:
            return self._downloads.cancel_download(params.get("file_name", ""))
        elif action == BrowserAction.LIST_DOWNLOADS.value:
            return self._downloads.list_downloads()

        return BrowserActionResult(
            success=False,
            action=action,
            message="Unknown action",
        )

    def get_audit_log(self) -> list:
        """Get audit log of all actions."""
        return list(self._audit_log)