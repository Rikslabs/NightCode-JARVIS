"""Desktop Action Framework models."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional


class MouseAction(Enum):
    """Mouse action types."""

    MOVE = "move"
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    SCROLL = "scroll"
    DRAG = "drag"


class KeyboardAction(Enum):
    """Keyboard action types."""

    TYPE = "type"
    PRESS = "press"
    HOTKEY = "hotkey"


class WindowAction(Enum):
    """Window action types."""

    OPEN = "open"
    FOCUS = "focus"
    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"
    CLOSE = "close"


class ClipboardAction(Enum):
    """Clipboard action types."""

    COPY = "copy"
    PASTE = "paste"


class ActionPermission(Enum):
    """Permission levels for desktop actions."""

    DENY = "deny"
    ALLOW = "allow"
    PROMPT = "prompt"


@dataclass
class DesktopAction:
    """Represents a desktop action request."""

    action_type: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_type": self.action_type,
            "parameters": dict(self.parameters),
            "timestamp": self.timestamp,
        }


@dataclass
class ActionResult:
    """Result of a desktop action execution."""

    success: bool
    action: DesktopAction
    message: str = ""
    data: Optional[Any] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "action": self.action.to_dict(),
            "message": self.message,
            "data": self.data,
            "timestamp": self.timestamp,
        }