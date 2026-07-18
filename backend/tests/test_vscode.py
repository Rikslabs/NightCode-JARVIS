"""Tests for VS Code Workspace Controller."""

import pytest

from app.vscode.models import (
    VSAction,
    VSWorkspaceAction,
    VSTerminalAction,
    VSEditorAction,
    VSDiagnosticsAction,
    VSTaskAction,
    VSActionResult,
)
from app.vscode.controller import VSCodeController
from app.vscode.workspace import WorkspaceController
from app.vscode.terminal import TerminalController
from app.vscode.editor import EditorController
from app.vscode.diagnostics import DiagnosticsController
from app.vscode.tasks import TaskController
from app.vscode.registry import VSCodeRegistry
from app.vscode.validator import VSCodeValidator


class TestVSAction:
    def test_all_actions(self):
        assert VSAction.OPEN_WORKSPACE.value == "open_workspace"
        assert VSAction.CLOSE_WORKSPACE.value == "close_workspace"
        assert VSAction.SWITCH_WORKSPACE.value == "switch_workspace"
        assert VSAction.GET_CURRENT_WORKSPACE.value == "get_current_workspace"
        assert VSAction.OPEN_TERMINAL.value == "open_terminal"
        assert VSAction.RUN_COMMAND.value == "run_command"
        assert VSAction.CLEAR_TERMINAL.value == "clear_terminal"
        assert VSAction.OPEN_FILE.value == "open_file"
        assert VSAction.CLOSE_FILE.value == "close_file"
        assert VSAction.SAVE.value == "save"
        assert VSAction.SAVE_ALL.value == "save_all"
        assert VSAction.REVEAL_FILE.value == "reveal_file"
        assert VSAction.GET_PROBLEMS.value == "get_problems"
        assert VSAction.RUN_BUILD.value == "run_build"
        assert VSAction.RUN_TEST.value == "run_test"
        assert VSAction.RUN_TASK.value == "run_task"


# ============================================
# WorkspaceController Tests
# ============================================

class TestWorkspaceController:
    def test_open_workspace(self):
        workspace = WorkspaceController()
        result = workspace.open_workspace("/path/to/project")
        assert result.success is True

    def test_close_workspace(self):
        workspace = WorkspaceController()
        result = workspace.close_workspace()
        assert result.success is True

    def test_switch_workspace(self):
        workspace = WorkspaceController()
        result = workspace.switch_workspace("/new/project")
        assert result.success is True

    def test_get_current_workspace(self):
        workspace = WorkspaceController()
        result = workspace.get_current_workspace()
        assert result.success is True


# ============================================
# TerminalController Tests
# ============================================

class TestTerminalController:
    def test_open_terminal(self):
        terminal = TerminalController()
        result = terminal.open_terminal()
        assert result.success is True

    def test_run_command(self):
        terminal = TerminalController()
        result = terminal.run_command("ls -la")
        assert result.success is True

    def test_clear_terminal(self):
        terminal = TerminalController()
        terminal.run_command("ls")
        result = terminal.clear_terminal()
        assert result.success is True

    def test_get_output(self):
        terminal = TerminalController()
        terminal.run_command("echo hello")
        output = terminal.get_output()
        assert len(output) > 0


# ============================================
# EditorController Tests
# ============================================

class TestEditorController:
    def test_open_file(self):
        editor = EditorController()
        result = editor.open_file("/path/to/file.py")
        assert result.success is True

    def test_close_file(self):
        editor = EditorController()
        editor.open_file("/path/to/file.py")
        result = editor.close_file("/path/to/file.py")
        assert result.success is True

    def test_save(self):
        editor = EditorController()
        result = editor.save()
        assert result.success is True

    def test_save_all(self):
        editor = EditorController()
        result = editor.save_all()
        assert result.success is True

    def test_reveal_file(self):
        editor = EditorController()
        result = editor.reveal_file("/path/to/file.py")
        assert result.success is True


# ============================================
# DiagnosticsController Tests
# ============================================

class TestDiagnosticsController:
    def test_get_problems(self):
        diagnostics = DiagnosticsController()
        result = diagnostics.get_problems()
        assert result.success is True
        assert "problems" in result.data

    def test_count_errors(self):
        diagnostics = DiagnosticsController()
        count = diagnostics.count_errors()
        assert count == 1

    def test_count_warnings(self):
        diagnostics = DiagnosticsController()
        count = diagnostics.count_warnings()
        assert count == 1

    def test_get_summary(self):
        diagnostics = DiagnosticsController()
        summary = diagnostics.get_summary()
        assert "errors" in summary
        assert "warnings" in summary


# ============================================
# TaskController Tests
# ============================================

class TestTaskController:
    def test_run_build(self):
        tasks = TaskController()
        result = tasks.run_build()
        assert result.success is True

    def test_run_test(self):
        tasks = TaskController()
        result = tasks.run_test()
        assert result.success is True

    def test_run_task(self):
        tasks = TaskController()
        result = tasks.run_task("build")
        assert result.success is True

    def test_run_unknown_task(self):
        tasks = TaskController()
        result = tasks.run_task("unknown")
        assert result.success is False

    def test_wait_for_completion(self):
        tasks = TaskController()
        result = tasks.wait_for_completion("build")
        assert result.success is True


# ============================================
# VSCodeController Tests
# ============================================

class TestVSCodeController:
    def test_execute_open_workspace(self):
        controller = VSCodeController()
        result = controller.execute(VSAction.OPEN_WORKSPACE.value, path="/test")
        assert result.success is True

    def test_execute_get_current_workspace(self):
        controller = VSCodeController()
        result = controller.execute(VSAction.GET_CURRENT_WORKSPACE.value)
        assert result.success is True

    def test_execute_open_terminal(self):
        controller = VSCodeController()
        result = controller.execute(VSAction.OPEN_TERMINAL.value)
        assert result.success is True

    def test_execute_run_command(self):
        controller = VSCodeController()
        result = controller.execute(VSAction.RUN_COMMAND.value, command="ls")
        assert result.success is True

    def test_execute_open_file(self):
        controller = VSCodeController()
        result = controller.execute(VSAction.OPEN_FILE.value, path="/test.py")
        assert result.success is True

    def test_execute_get_problems(self):
        controller = VSCodeController()
        result = controller.execute(VSAction.GET_PROBLEMS.value)
        assert result.success is True

    def test_execute_run_build(self):
        controller = VSCodeController()
        result = controller.execute(VSAction.RUN_BUILD.value)
        assert result.success is True

    def test_execute_unknown_action(self):
        controller = VSCodeController()
        result = controller.execute("unknown_action")
        assert result.success is False

    def test_get_audit_log(self):
        controller = VSCodeController()
        controller.execute(VSAction.OPEN_WORKSPACE.value, path="/test")
        log = controller.get_audit_log()
        assert len(log) == 1


# ============================================
# VSCodeRegistry Tests
# ============================================

class TestVSCodeRegistry:
    def test_get_instance(self):
        registry = VSCodeRegistry.get_instance()
        assert isinstance(registry, VSCodeRegistry)

    def test_register_and_get_controller(self):
        registry = VSCodeRegistry()
        controller = VSCodeController()
        registry.register_controller("test", controller)
        assert registry.get_controller("test") is controller

    def test_clear(self):
        registry = VSCodeRegistry()
        controller = VSCodeController()
        registry.register_controller("test", controller)
        registry.clear()
        assert registry.get_controller("test") is None


# ============================================
# VSCodeValidator Tests
# ============================================

class TestVSCodeValidator:
    def test_validate_valid_action(self):
        validator = VSCodeValidator()
        result = validator.validate(VSAction.OPEN_WORKSPACE.value)
        assert result.success is True

    def test_validate_unknown_action(self):
        validator = VSCodeValidator()
        result = validator.validate("unknown_action")
        assert result.success is False

    def test_is_read_only(self):
        validator = VSCodeValidator()
        assert validator.is_read_only(VSAction.GET_CURRENT_WORKSPACE.value) is True
        assert validator.is_read_only(VSAction.OPEN_WORKSPACE.value) is False

    def test_requires_approval(self):
        validator = VSCodeValidator()
        assert validator.requires_approval(VSAction.RUN_COMMAND.value) is True
        assert validator.requires_approval(VSAction.OPEN_WORKSPACE.value) is False