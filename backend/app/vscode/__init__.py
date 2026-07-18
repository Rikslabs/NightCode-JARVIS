"""VS Code Workspace Controller - Deterministic VS Code integration layer."""

from .models import (
    VSAction,
    VSWorkspaceAction,
    VSTerminalAction,
    VSEditorAction,
    VSDiagnosticsAction,
    VSTaskAction,
    VSActionResult,
)
from .controller import VSCodeController
from .workspace import WorkspaceController
from .terminal import TerminalController
from .editor import EditorController
from .diagnostics import DiagnosticsController
from .tasks import TaskController
from .registry import VSCodeRegistry
from .validator import VSCodeValidator

__all__ = [
    "VSAction",
    "VSWorkspaceAction",
    "VSTerminalAction",
    "VSEditorAction",
    "VSDiagnosticsAction",
    "VSTaskAction",
    "VSActionResult",
    "VSCodeController",
    "WorkspaceController",
    "TerminalController",
    "EditorController",
    "DiagnosticsController",
    "TaskController",
    "VSCodeRegistry",
    "VSCodeValidator",
]