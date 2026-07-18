"""Clipboard controller for desktop automation."""

from typing import Optional


class ClipboardController:
    """Controls clipboard actions on the desktop."""

    def __init__(self):
        self._mock_content: Optional[str] = None

    def copy(self, text: str) -> bool:
        """Copy text to clipboard (metadata only)."""
        if text:
            self._mock_content = text
            return True
        return False

    def paste(self) -> Optional[str]:
        """Get clipboard content (returns mock content)."""
        return self._mock_content

    def clear(self) -> bool:
        """Clear clipboard (metadata only)."""
        self._mock_content = None
        return True