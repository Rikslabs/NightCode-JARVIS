"""Editor controller for VS Code."""

from typing import Optional

from .models import VSEditorAction, VSActionResult


class EditorController:
    """Controls VS Code editor operations."""

    def __init__(self):
        self._open_files: list = []

    def open_file(self, path: str) -> VSActionResult:
        """Open a file in editor (metadata only)."""
        self._open_files.append(path)
        return VSActionResult(
            success=True,
            action=VSEditorAction.OPEN_FILE.value,
            message=f"File opened: {path}",
            data={"path": path},
        )

    def close_file(self, path: Optional[str] = None) -> VSActionResult:
        """Close a file in editor (metadata only)."""
        if path and path in self._open_files:
            self._open_files.remove(path)
        return VSActionResult(
            success=True,
            action=VSEditorAction.CLOSE_FILE.value,
            message="File closed",
        )

    def save(self, path: Optional[str] = None) -> VSActionResult:
        """Save a file (metadata only)."""
        return VSActionResult(
            success=True,
            action=VSEditorAction.SAVE.value,
            message="File saved",
        )

    def save_all(self) -> VSActionResult:
        """Save all files (metadata only)."""
        return VSActionResult(
            success=True,
            action=VSEditorAction.SAVE.value,
            message="All files saved",
        )

    def reveal_file(self, path: str) -> VSActionResult:
        """Reveal file in editor (metadata only)."""
        return VSActionResult(
            success=True,
            action=VSEditorAction.REVEAL.value,
            message=f"File revealed: {path}",
            data={"path": path},
        )