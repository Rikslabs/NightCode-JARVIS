"""Focused tests for the interactive CLI framework."""

from types import SimpleNamespace
from unittest.mock import Mock

from app.cli import start_cli
from app.jarvis import JarvisService
from app.version import __version__


def run_cli(commands):
    output = []
    prompts = []
    iterator = iter(commands)

    def read(prompt):
        prompts.append(prompt)
        return next(iterator)

    service = Mock(spec=JarvisService)
    start_cli(
        service_factory=lambda: service,
        input_func=read,
        output_func=output.append,
    )
    return output, prompts, service


def test_cli_startup():
    output, prompts, _ = run_cli(["exit"])

    assert output[0] == f"NightCode-JARVIS v{__version__}"
    assert prompts == ["jarvis > "]


def test_cli_help():
    output, _, _ = run_cli(["help", "exit"])

    assert any("read <path>" in line and "git log" in line for line in output)


def test_cli_exit():
    output, prompts, _ = run_cli(["exit"])

    assert output[-1] == "Goodbye."
    assert len(prompts) == 1


def test_cli_invalid_command():
    output, prompts, _ = run_cli(["unknown", "exit"])

    assert "Unknown command." in output
    assert "Type 'help' to see available commands." in output
    assert len(prompts) == 2


def test_cli_analyze_command():
    service = Mock(spec=JarvisService)
    project = SimpleNamespace(
        name="demo",
        detected_languages=["Python"],
        file_count=3,
        directory_count=2,
    )
    service.analyze_project.return_value = Mock(project=project)
    output = []
    commands = iter(["analyze", "exit"])

    start_cli(
        service_factory=lambda: service,
        input_func=lambda prompt: next(commands),
        output_func=output.append,
    )

    service.analyze_project.assert_called_once_with()
    assert "Project: demo\nLanguages: Python\nFiles: 3\nDirectories: 2" in output


def test_cli_files_command():
    service = Mock(spec=JarvisService)
    service.list_files.return_value = [
        Mock(relative_path="src/app.py", size=42),
        Mock(relative_path="README.md", size=10),
    ]
    output = []
    commands = iter(["files", "exit"])

    start_cli(
        service_factory=lambda: service,
        input_func=lambda prompt: next(commands),
        output_func=output.append,
    )

    service.list_files.assert_called_once_with()
    assert "Files:\n- src/app.py (42 bytes)\n- README.md (10 bytes)" in output


def test_cli_git_status_command():
    service = Mock(spec=JarvisService)
    service.git_status.return_value = [
        Mock(index_status=" ", worktree_status="M", path="module.py"),
    ]
    output = []
    commands = iter(["git status", "exit"])

    start_cli(
        service_factory=lambda: service,
        input_func=lambda prompt: next(commands),
        output_func=output.append,
    )

    service.git_status.assert_called_once_with()
    assert "Git status:\n-  M module.py" in output


def test_cli_handles_service_exception():
    service = Mock(spec=JarvisService)
    service.analyze_project.side_effect = RuntimeError("analysis unavailable")
    output = []
    commands = iter(["analyze", "exit"])

    start_cli(
        service_factory=lambda: service,
        input_func=lambda prompt: next(commands),
        output_func=output.append,
    )

    assert "Error: analysis unavailable" in output
    assert output[-1] == "Goodbye."


def test_cli_read_command():
    service = Mock(spec=JarvisService)
    service._coding = Mock()
    service._coding.read_file.return_value = "hello\n"
    output = []
    commands = iter(["read notes.txt", "exit"])

    start_cli(lambda: service, lambda prompt: next(commands), output.append)

    service._coding.read_file.assert_called_once_with("notes.txt")
    assert "File: notes.txt\nhello\n" in output


def test_cli_explain_file_command():
    service = Mock(spec=JarvisService)
    service.explain_file.return_value = SimpleNamespace(
        module_name="module",
        detected_language="Python",
        classes=["Worker"],
        functions=["run"],
        async_functions=["fetch"],
    )
    output = []
    commands = iter(["explain module.py", "exit"])

    start_cli(lambda: service, lambda prompt: next(commands), output.append)

    service.explain_file.assert_called_once_with("module.py")
    assert "Module: module\nLanguage: Python\nClasses: Worker\nFunctions: run, fetch" in output


def test_cli_explain_symbol_command():
    service = Mock(spec=JarvisService)
    service.explain_file.side_effect = FileNotFoundError()
    service.explain_symbol.return_value = SimpleNamespace(
        name="run",
        symbol_type="function",
        location="module.py:1",
        parent=None,
        signature="run()",
    )
    output = []
    commands = iter(["explain run", "exit"])

    start_cli(lambda: service, lambda prompt: next(commands), output.append)

    service.explain_symbol.assert_called_once_with("run")
    assert any(
        "Symbol: run\nType: function\nLocation: module.py:1" in line
        for line in output
    )


def test_cli_patch_command_does_not_apply():
    service = Mock(spec=JarvisService)
    explanation = Mock()
    service.explain_file.return_value = explanation
    service.generate_patch.return_value = SimpleNamespace(
        summary="Review module.py",
        reasoning="Manual review required.",
        proposed_changes=["Update run"],
        unified_diff="",
    )
    output = []
    commands = iter(["patch module.py", "exit"])

    start_cli(lambda: service, lambda prompt: next(commands), output.append)

    service.generate_patch.assert_called_once()
    service.apply_patch.assert_not_called()
    assert any("Patch proposal: Review module.py" in line for line in output)


def test_cli_run_command():
    service = Mock(spec=JarvisService)
    service.run_command.return_value = SimpleNamespace(
        command="pytest -q",
        exit_code=0,
        stdout="2 passed\n",
        stderr="",
    )
    output = []
    commands = iter(["run pytest -q", "exit"])

    start_cli(lambda: service, lambda prompt: next(commands), output.append)

    service.run_command.assert_called_once_with("pytest -q")
    assert "Command: pytest -q\nExit code: 0\nOutput:\n2 passed" in output


def test_cli_git_diff_command():
    service = Mock(spec=JarvisService)
    service.run_command.return_value = SimpleNamespace(
        command="git diff", exit_code=0, stdout="diff output", stderr="",
    )
    output = []
    commands = iter(["git diff", "exit"])

    start_cli(lambda: service, lambda prompt: next(commands), output.append)

    service.run_command.assert_called_once_with("git diff")
    assert any("diff output" in line for line in output)


def test_cli_git_log_command():
    service = Mock(spec=JarvisService)
    service.repository_summary.return_value = SimpleNamespace(
        recent_commits=[SimpleNamespace(commit_hash="abc123", message="Initial")],
    )
    output = []
    commands = iter(["git log", "exit"])

    start_cli(lambda: service, lambda prompt: next(commands), output.append)

    service.repository_summary.assert_called_once_with()
    assert "Git log:\n- abc123 Initial" in output


def test_cli_session_history_and_clear():
    output, _, _ = run_cli(["help", "history", "history clear", "history", "exit"])

    assert "History:\n1. help\n2. history" in output
    assert "History cleared." in output
    assert "History:\n1. history" in output


def test_cli_invalid_arguments():
    output, _, service = run_cli(["read", "explain", "patch", "run", "exit"])

    assert "Usage: read <path>" in output
    assert "Usage: explain <path|symbol>" in output
    assert "Usage: patch <path>" in output
    assert "Usage: run <allowed-command>" in output
    service.explain_file.assert_not_called()
    service.generate_patch.assert_not_called()
    service.run_command.assert_not_called()
