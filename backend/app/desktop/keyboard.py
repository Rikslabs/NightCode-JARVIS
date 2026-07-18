"""Keyboard controller for desktop automation."""

from typing import Optional

from .models import KeyboardAction


class KeyboardController:
    """Controls keyboard actions on the desktop."""

    def type_text(self, text: str) -> bool:
        """Type text (metadata only - no actual typing)."""
        if not text:
            return False
        return True

    def press(self, key: str) -> bool:
        """Press a single key (metadata only)."""
        return True

    def hotkey(self, *keys: str) -> bool:
        """Press a combination of keys (metadata only)."""
        return True

    def get_supported_keys(self) -> list:
        """Get list of supported keys."""
        return ["ctrl", "alt", "shift", "win", "enter", "esc", "tab"]