"""Tab controller for Browser."""

from typing import Optional, List, Dict, Any

from .models import BrowserAction, BrowserActionResult


class TabController:
    """Controls browser tab operations."""

    def __init__(self):
        self._tabs: List[Dict[str, Any]] = [
            {"id": 1, "url": "about:blank", "active": True},
        ]
        self._active_tab: int = 1

    def new_tab(self, url: Optional[str] = None) -> BrowserActionResult:
        """Open a new tab (metadata only)."""
        tab_id = len(self._tabs) + 1
        self._tabs.append({"id": tab_id, "url": url or "about:blank", "active": False})
        return BrowserActionResult(
            success=True,
            action=BrowserAction.NEW_TAB.value,
            message=f"New tab opened: {tab_id}",
            data={"tab_id": tab_id, "url": url},
        )

    def close_tab(self, tab_id: Optional[int] = None) -> BrowserActionResult:
        """Close a tab (metadata only)."""
        if tab_id is None:
            tab_id = self._active_tab
        self._tabs = [t for t in self._tabs if t["id"] != tab_id]
        return BrowserActionResult(
            success=True,
            action=BrowserAction.CLOSE_TAB.value,
            message=f"Tab closed: {tab_id}",
        )

    def switch_tab(self, tab_id: int) -> BrowserActionResult:
        """Switch to a tab (metadata only)."""
        for tab in self._tabs:
            tab["active"] = (tab["id"] == tab_id)
        self._active_tab = tab_id
        return BrowserActionResult(
            success=True,
            action=BrowserAction.SWITCH_TAB.value,
            message=f"Switched to tab: {tab_id}",
            data={"tab_id": tab_id},
        )

    def list_tabs(self) -> BrowserActionResult:
        """List all tabs."""
        return BrowserActionResult(
            success=True,
            action=BrowserAction.LIST_TABS.value,
            message="Tabs listed",
            data={"tabs": self._tabs},
        )

    def get_active_tab(self) -> Optional[Dict[str, Any]]:
        """Get active tab info."""
        for tab in self._tabs:
            if tab["active"]:
                return tab
        return None