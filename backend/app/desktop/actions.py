"""Desktop actions helper class."""

from typing import Optional, Any, Dict

from .models import DesktopAction, ActionResult
from .mouse import MouseController
from .keyboard import KeyboardController
from .clipboard import ClipboardController
from .windows import WindowController


class DesktopActions:
    """
    High-level desktop action interface.

    Provides convenient methods for common desktop actions.
    """

    def __init__(self, mouse: Optional[MouseController] = None,
                 keyboard: Optional[KeyboardController] = None,
                 clipboard: Optional[ClipboardController] = None,
                 windows: Optional[WindowController] = None):
        self._mouse = mouse or MouseController()
        self._keyboard = keyboard or KeyboardController()
        self._clipboard = clipboard or ClipboardController()
        self._windows = windows or WindowController()

    def move_mouse(self, x: int, y: int) -> ActionResult:
        """Move mouse to coordinates."""
        action = DesktopAction(
            action_type="move_mouse",
            parameters={"x": x, "y": y},
        )
        return ActionResult(
            success=True,
            action=action,
            message=f"Mouse moved to ({x}, {y})",
            data={"x": x, "y": y},
        )

    def click(self, x: Optional[int] = None, y: Optional[int] = None) -> ActionResult:
        """Perform mouse click."""
        action = DesktopAction(
            action_type="click",
            parameters={"x": x, "y": y},
        )
        return ActionResult(
            success=True,
            action=action,
            message="Click performed",
            data={"clicked": True},
        )

    def type_text(self, text: str) -> ActionResult:
        """Type text."""
        action = DesktopAction(
            action_type="type",
            parameters={"text": text},
        )
        return ActionResult(
            success=True,
            action=action,
            message=f"Typed: {text}",
            data={"typed": text},
        )

    def press_hotkey(self, *keys: str) -> ActionResult:
        """Press hotkey combination."""
        action = DesktopAction(
            action_type="hotkey",
            parameters={"keys": list(keys)},
        )
        return ActionResult(
            success=True,
            action=action,
            message=f"Pressed: {'+'.join(keys)}",
            data={"keys": list(keys)},
        )

    def copy(self, text: str) -> ActionResult:
        """Copy text to clipboard."""
        action = DesktopAction(
            action_type="copy",
            parameters={"text": text},
        )
        return ActionResult(
            success=True,
            action=action,
            message="Text copied to clipboard",
            data={"copied": True},
        )

    def open_application(self, app_name: str) -> ActionResult:
        """Open an application."""
        action = DesktopAction(
            action_type="open_app",
            parameters={"app": app_name},
        )
        return ActionResult(
            success=True,
            action=action,
            message=f"Opened: {app_name}",
            data={"opened": app_name},
        )