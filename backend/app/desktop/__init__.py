"""Desktop Action Framework - Deterministic desktop automation layer."""

from .models import (
    MouseAction,
    KeyboardAction,
    WindowAction,
    ClipboardAction,
    DesktopAction,
    ActionResult,
    ActionPermission,
)
from .controller import DesktopController
from .actions import DesktopActions
from .permissions import DesktopPermissionManager
from .registry import DesktopRegistry
from .validator import DesktopValidator
from .mouse import MouseController
from .keyboard import KeyboardController
from .clipboard import ClipboardController
from .windows import WindowController

__all__ = [
    "MouseAction",
    "KeyboardAction",
    "WindowAction",
    "ClipboardAction",
    "DesktopAction",
    "ActionResult",
    "ActionPermission",
    "DesktopController",
    "DesktopActions",
    "DesktopPermissionManager",
    "DesktopRegistry",
    "DesktopValidator",
    "MouseController",
    "KeyboardController",
    "ClipboardController",
    "WindowController",
]
