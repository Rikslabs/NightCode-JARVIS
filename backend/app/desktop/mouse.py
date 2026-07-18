"""Mouse controller for desktop automation."""

from dataclasses import dataclass
from typing import Optional

from .models import MouseAction
from .permissions import DesktopPermissionManager


@dataclass
class MouseController:
    """Controls mouse actions on the desktop."""

    permission_manager: Optional[DesktopPermissionManager] = None

    def move(self, x: int, y: int) -> bool:
        """Move mouse to position (metadata only - no actual movement)."""
        if self.permission_manager:
            permission = self.permission_manager.check_permission(
                type("DesktopAction", (), {"action_type": MouseAction.MOVE.value})()
            )
            if permission.name == "DENY":
                return False

        # Deterministic: just log the action
        return True

    def click(self, x: Optional[int] = None, y: Optional[int] = None) -> bool:
        """Perform mouse click (metadata only)."""
        return True

    def double_click(self, x: Optional[int] = None, y: Optional[int] = None) -> bool:
        """Perform double click (metadata only)."""
        return True

    def right_click(self, x: Optional[int] = None, y: Optional[int] = None) -> bool:
        """Perform right click (metadata only)."""
        return True

    def scroll(self, direction: str = "down", amount: int = 1) -> bool:
        """Scroll mouse wheel (metadata only)."""
        return True

    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int) -> bool:
        """Drag mouse from start to end position (metadata only)."""
        return True

    def get_position(self) -> tuple:
        """Get current mouse position (returns mock position)."""
        return (0, 0)