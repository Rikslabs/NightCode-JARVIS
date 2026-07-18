"""Workspace controller for VS Code."""

from typing import Optional

from .models import VSWorkspaceAction, VSActionResult


class WorkspaceController:
    """Controls VS Code workspace operations."""

    def __init__(self):
        self._current_workspace: Optional[str] = None
        self._workspaces: list = ["project1", "project2"]

    def open_workspace(self, path: str) -> VSActionResult:
        """Open a workspace (metadata only)."""
        self._workspaces.append(path)
        return VSActionResult(
            success=True,
            action=VSWorkspaceAction.OPEN.value,
            message=f"Workspace opened: {path}",
            data={"path": path},
        )

    def close_workspace(self, path: Optional[str] = None) -> VSActionResult:
        """Close current workspace (metadata only)."""
        return VSActionResult(
            success=True,
            action=VSWorkspaceAction.CLOSE.value,
            message="Workspace closed",
        )

    def switch_workspace(self, path: str) -> VSActionResult:
        """Switch to a workspace (metadata only)."""
        self._current_workspace = path
        return VSActionResult(
            success=True,
            action=VSWorkspaceAction.SWITCH.value,
            message=f"Switched to: {path}",
            data={"path": path},
        )

    def get_current_workspace(self) -> VSActionResult:
        """Get current workspace path."""
        return VSActionResult(
            success=True,
            action=VSWorkspaceAction.GET_CURRENT.value,
            message="Current workspace retrieved",
            data={"path": self._current_workspace},
        )