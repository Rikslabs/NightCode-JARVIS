"""Focused tests for the secure terminal assistant."""

from app.terminal import TerminalAssistant


def test_allowed_command_and_stdout_capture():
    result = TerminalAssistant().run("python -c \"print('hello')\"")

    assert result.success is True
    assert result.exit_code == 0
    assert result.stdout.strip() == "hello"
    assert result.stderr == ""
    assert result.duration_seconds >= 0


def test_blocked_command_returns_structured_result():
    result = TerminalAssistant().run("git push origin main")

    assert result.success is False
    assert result.exit_code == 126
    assert "Only git status, git diff, and git log" in result.stderr
    assert result.stdout == ""
    assert result.timed_out is False


def test_stderr_capture_and_exit_code():
    result = TerminalAssistant().run(
        "python -c \"import sys; print('problem', file=sys.stderr); sys.exit(7)\""
    )

    assert result.exit_code == 7
    assert result.stderr.strip() == "problem"
    assert result.success is False


def test_timeout():
    result = TerminalAssistant(timeout_seconds=0.05).run(
        "python -c \"import time; time.sleep(1)\""
    )

    assert result.exit_code == 124
    assert result.timed_out is True
    assert result.success is False
    assert "timed out" in result.stderr


def test_success_flag_for_zero_exit_code():
    result = TerminalAssistant().run("python -c \"raise SystemExit(0)\"")

    assert result.exit_code == 0
    assert result.success is True
    assert result.timed_out is False
