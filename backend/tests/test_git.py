"""Focused tests for the read-only Git assistant."""

import subprocess
from pathlib import Path

import pytest

from app.git import GitAssistant, GitCommandRejectedError


class FakeGitRunner:
    def __init__(self, outputs):
        self.outputs = outputs
        self.commands = []

    def __call__(self, command, **kwargs):
        self.commands.append((command, kwargs))
        key = tuple(command[1:])
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=self.outputs.get(key, ""),
            stderr="",
        )


def test_current_branch(tmp_path: Path):
    runner = FakeGitRunner({("branch", "--show-current"): "main\n"})

    assert GitAssistant(tmp_path, runner=runner).current_branch() == "main"
    assert runner.commands[0][1]["shell"] is False


def test_clean_repository(tmp_path: Path):
    runner = FakeGitRunner({
        ("status", "--short"): "",
        ("branch", "--show-current"): "main\n",
        ("log", "--oneline", "-n", "10"): "abc123 Initial commit\n",
    })

    summary = GitAssistant(tmp_path, runner=runner).repository_summary()

    assert summary.clean is True
    assert summary.modified_files == []
    assert summary.staged_files == []
    assert summary.untracked_files == []


def test_modified_repository(tmp_path: Path):
    runner = FakeGitRunner({
        ("status", "--short"): " M modified.py\nA  staged.py\n?? new.py\n",
        ("branch", "--show-current"): "feature\n",
        ("log", "--oneline", "-n", "10"): "",
    })

    summary = GitAssistant(tmp_path, runner=runner).repository_summary()

    assert summary.clean is False
    assert summary.modified_files == ["modified.py"]
    assert summary.staged_files == ["staged.py"]
    assert summary.untracked_files == ["new.py"]


def test_git_log_parsing(tmp_path: Path):
    runner = FakeGitRunner({
        ("log", "--oneline", "-n", "2"): "abc123 First commit\ndef456 Second commit details\n",
    })

    commits = GitAssistant(tmp_path, runner=runner).log(limit=2)

    assert [(commit.commit_hash, commit.message) for commit in commits] == [
        ("abc123", "First commit"),
        ("def456", "Second commit details"),
    ]


def test_blocked_git_command_never_runs(tmp_path: Path):
    runner = FakeGitRunner({})
    assistant = GitAssistant(tmp_path, runner=runner)

    with pytest.raises(GitCommandRejectedError):
        assistant._execute(("push", "origin", "main"))

    assert runner.commands == []
