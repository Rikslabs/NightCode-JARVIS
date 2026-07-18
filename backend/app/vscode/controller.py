"""Main VS Code controller."""

from typing import Optional, Any

from .models import VSAction, VSActionResult
from .workspace import WorkspaceController
from .terminal import TerminalController
from .editor import EditorController
from .diagnostics import DiagnosticsController
from .tasks import TaskController


class VSCodeController:
    """
    Main controller for VS Code operations.

    Coordinates all VS Code action controllers.
    """

    def __init__(self):
        self._workspace = WorkspaceController()
        self._terminal = TerminalController()
        self._editor = EditorController()
        self._diagnostics = DiagnosticsController()
        self._tasks = TaskController()
        self._audit_log: list = []

    def execute(self, action: str, **kwargs) -> VSActionResult:
        """Execute a VS Code action."""
        result = self._execute_action(action, kwargs)
        self._audit_log.append({
            "action": action,
            "success": result.success,
            "timestamp": result.timestamp,
        })
        return result

    def _execute_action(self, action: str, params: dict) -> VSActionResult:
        """Execute the action and return result."""
        if action == VSAction.OPEN_WORKSPACE.value:
            return self._workspace.open_workspace(params.get("path", ""))
        elif action == VSAction.CLOSE_WORKSPACE.value:
            return self._workspace.close_workspace(params.get("path"))
        elif action == VSAction.SWITCH_WORKSPACE.value:
            return self._workspace.switch_workspace(params.get("path", ""))
        elif action == VSAction.GET_CURRENT_WORKSPACE.value:
            return self._workspace.get_current_workspace()
        elif action == VSAction.OPEN_TERMINAL.value:
            return self._terminal.open_terminal()
        elif action == VSAction.RUN_COMMAND.value:
            return self._terminal.run_command(params.get("command", ""))
        elif action == VSAction.CLEAR_TERMINAL.value:
            return self._terminal.clear_terminal()
        elif action == VSAction.OPEN_FILE.value:
            return self._editor.open_file(params.get("path", ""))
        elif action == VSAction.CLOSE_FILE.value:
            return self._editor.close_file(params.get("path"))
        elif action == VSAction.SAVE.value:
            return self._editor.save(params.get("path"))
        elif action == VSAction.SAVE_ALL.value:
            return self._editor.save_all()
        elif action == VSAction.REVEAL_FILE.value:
            return self._editor.reveal_file(params.get("path", ""))
        elif action == VSAction.GET_PROBLEMS.value:
            return self._diagnostics.get_problems()
        elif action == VSAction.RUN_BUILD.value:
            return self._tasks.run_build()
        elif action == VSAction.RUN_TEST.value:
            return self._tasks.run_test()
        elif action == VSAction.RUN_TASK.value:
            return self._tasks.run_task(params.get("task", ""))

        return VSActionResult(
            success=False,
            action=action,
            message="Unknown action",
        )

    def get_audit_log(self) -> list:
        """Get audit log of all actions."""
        return list(self._audit_log)