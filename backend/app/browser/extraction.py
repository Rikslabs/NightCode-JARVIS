"""Extraction controller for Browser."""

from typing import Optional, Dict, Any, List

from .models import BrowserAction, BrowserActionResult


class ExtractionController:
    """Controls browser content extraction operations."""

    def __init__(self):
        self._mock_title: str = "Mock Page Title"
        self._mock_text: str = "This is mock page text content."
        self._mock_links: List[str] = ["/link1", "/link2", "https://example.com"]

    def get_title(self) -> BrowserActionResult:
        """Extract page title (metadata only)."""
        return BrowserActionResult(
            success=True,
            action=BrowserAction.GET_TITLE.value,
            message="Title extracted",
            data={"title": self._mock_title},
        )

    def get_text(self, selector: Optional[str] = None) -> BrowserActionResult:
        """Extract visible text (metadata only)."""
        return BrowserActionResult(
            success=True,
            action=BrowserAction.GET_TEXT.value,
            message="Text extracted",
            data={"text": self._mock_text},
        )

    def get_links(self) -> BrowserActionResult:
        """Extract all links (metadata only)."""
        return BrowserActionResult(
            success=True,
            action=BrowserAction.GET_LINKS.value,
            message="Links extracted",
            data={"links": self._mock_links},
        )

    def get_metadata(self) -> BrowserActionResult:
        """Extract page metadata (metadata only)."""
        metadata = {
            "title": self._mock_title,
            "url": "https://example.com",
            "description": "Mock description",
        }
        return BrowserActionResult(
            success=True,
            action=BrowserAction.GET_METADATA.value,
            message="Metadata extracted",
            data={"metadata": metadata},
        )

    def get_status(self) -> BrowserActionResult:
        """Get page status (metadata only)."""
        status = {
            "ready": True,
            "status_code": 200,
        }
        return BrowserActionResult(
            success=True,
            action=BrowserAction.GET_STATUS.value,
            message="Page status retrieved",
            data={"status": status},
        )