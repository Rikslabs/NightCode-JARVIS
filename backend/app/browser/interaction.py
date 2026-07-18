"""Interaction controller for Browser."""

from typing import Optional, Dict, Any

from .models import BrowserAction, BrowserActionResult


class InteractionController:
    """Controls browser interaction operations."""

    def __init__(self):
        self._interaction_buffer: list = []

    def click(self, selector: str) -> BrowserActionResult:
        """Click an element (metadata only)."""
        self._interaction_buffer.append({"action": "click", "selector": selector})
        return BrowserActionResult(
            success=True,
            action=BrowserAction.CLICK.value,
            message=f"Clicked: {selector}",
            data={"selector": selector},
        )

    def type(self, selector: str, text: str) -> BrowserActionResult:
        """Type into an element (metadata only)."""
        self._interaction_buffer.append({"action": "type", "selector": selector, "text": text})
        return BrowserActionResult(
            success=True,
            action=BrowserAction.TYPE.value,
            message=f"Typed in {selector}",
            data={"selector": selector, "text": text},
        )

    def scroll(self, direction: str = "down", amount: Optional[int] = None) -> BrowserActionResult:
        """Scroll the page (metadata only)."""
        self._interaction_buffer.append({"action": "scroll", "direction": direction, "amount": amount})
        return BrowserActionResult(
            success=True,
            action=BrowserAction.SCROLL.value,
            message=f"Scrolled {direction}",
            data={"direction": direction, "amount": amount},
        )

    def submit_form(self, selector: str) -> BrowserActionResult:
        """Submit a form (metadata only)."""
        self._interaction_buffer.append({"action": "submit", "selector": selector})
        return BrowserActionResult(
            success=True,
            action=BrowserAction.SUBMIT_FORM.value,
            message=f"Form submitted: {selector}",
            data={"selector": selector},
        )

    def upload_file(self, selector: str, file_path: str) -> BrowserActionResult:
        """Upload a file (metadata only - requires approval)."""
        self._interaction_buffer.append({
            "action": "upload",
            "selector": selector,
            "file_path": file_path,
        })
        return BrowserActionResult(
            success=True,
            action=BrowserAction.UPLOAD_FILE.value,
            message=f"File uploaded: {file_path}",
            data={"selector": selector, "file_path": file_path},
        )