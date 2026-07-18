"""VS Code models."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional


class VSAction(Enum):
    """VS Code action types."""

    # Workspace
    OPEN_WORKSPACE = "open_workspace"
    CLOSE_WORKSPACE = "close_workspace"
    SWITCH_WORKSPACE = "switch_workspace"
    GET_CURRENT_WORKSPACE = "get_current_workspace"

    # Terminal
    OPEN_TERMINAL = "open_terminal"
    RUN_COMMAND = "run_command"
    CLEAR_TERMINAL = "clear_terminal"

    # Editor
    OPEN_FILE = "open_file"
    CLOSE_FILE = "close_file"
    SAVE = "save"
    SAVE_ALL = "save_all"
    REVEAL_FILE = "reveal_file"

    # Diagnostics
    GET_PROBLEMS = "get_problems"

    # Tasks
    RUN_BUILD = "run_build"
    RUN_TEST = "run_test"
    RUN_TASK = "run_task"


class VSWorkspaceAction(Enum):
    """Workspace action types."""

    OPEN = "open"
    CLOSE = "close"
    SWITCH = "switch"
    GET_CURRENT = "get_current"


class VSTerminalAction(Enum):
    """Terminal action types."""

    OPEN = "open"
    RUN = "run"
    CLEAR = "clear"


class VSEditorAction(Enum):
    """Editor action types."""

    OPEN_FILE = "open_file"
    CLOSE_FILE = "close_file"
    SAVE = "save"
    REVEAL = "reveal"


class VSDiagnosticsAction(Enum):
    """Diagnostics action types."""

    READ_PROBLEMS = "read_problems"


class VSTaskAction(Enum):
    """Task action types."""

    BUILD = "build"
    TEST = "test"
    RUN = "run"


@dataclass
class VSActionResult:
    """Result of a VS Code action."""

    success: bool
    action: str
    message: str = ""
    data: Optional[Any] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "action": self.action,
            "message": self.message,
            "data": self.data,
            "timestamp": self.timestamp,
        }