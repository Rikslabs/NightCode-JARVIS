"""Navigation controller for Browser."""

from typing import Optional

from .models import BrowserAction, BrowserActionResult


class NavigationController:
    """Controls browser navigation operations."""

    def __init__(self):
        self._current_url: Optional[str] = None
        self._is_loading: bool = False

    def open_url(self, url: str) -> BrowserActionResult:
        """Open a URL in the browser (metadata only)."""
        self._current_url = url
        self._is_loading = True
        return BrowserActionResult(
            success=True,
            action=BrowserAction.OPEN_URL.value,
            message=f"Navigated to: {url}",
            data={"url": url},
        )

    def back(self) -> BrowserActionResult:
        """Navigate back (metadata only)."""
        return BrowserActionResult(
            success=True,
            action=BrowserAction.BACK.value,
            message="Navigated back",
        )

    def forward(self) -> BrowserActionResult:
        """Navigate forward (metadata only)."""
        return BrowserActionResult(
            success=True,
            action=BrowserAction.FORWARD.value,
            message="Navigated forward",
        )

    def refresh(self) -> BrowserActionResult:
        """Refresh the current page (metadata only)."""
        return BrowserActionResult(
            success=True,
            action=BrowserAction.REFRESH.value,
            message="Page refreshed",
        )

    def stop_loading(self) -> BrowserActionResult:
        """Stop loading the current page."""
        self._is_loading = False
        return BrowserActionResult(
            success=True,
            action=BrowserAction.STOP_LOADING.value,
            message="Loading stopped",
        )

    def get_current_url(self) -> Optional[str]:
        """Get current URL."""
        return self._current_url