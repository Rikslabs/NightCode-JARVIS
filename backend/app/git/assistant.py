"""Strictly read-only Git command facade."""

import subprocess
from pathlib import Path
from typing import Callable, List, Sequence, Tuple, Union

from .models import GitCommit, GitFileStatus, RepositorySummary


class GitCommandRejectedError(ValueError):
    """Raised when a Git command is outside the read-only allowlist."""


class GitCommandError(RuntimeError):
    """Raised when an allowed Git command cannot complete successfully."""


class GitAssistant:
    """Inspect a Git repository using fixed, read-only commands."""

    def __init__(
        self,
        repository_path: Union[str, Path],
        timeout_seconds: float = 30.0,
        runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero")
        self._repository_path = Path(repository_path)
        self._timeout_seconds = timeout_seconds
        self._runner = runner

    def status(self) -> List[GitFileStatus]:
        """Return parsed entries from ``git status --short``."""
        output = self._execute(("status", "--short"))
        entries: List[GitFileStatus] = []
        for line in output.splitlines():
            if len(line) < 3:
                continue
            entries.append(GitFileStatus(
                path=line[3:],
                index_status=line[0],
                worktree_status=line[1],
            ))
        return entries

    def diff(self) -> str:
        """Return the current unstaged diff."""
        return self._execute(("diff",))

    def log(self, limit: int = 10) -> List[GitCommit]:
        """Return recent commits parsed from one-line log output."""
        if limit <= 0:
            raise ValueError("limit must be greater than zero")
        output = self._execute(("log", "--oneline", "-n", str(limit)))
        commits: List[GitCommit] = []
        for line in output.splitlines():
            commit_hash, separator, message = line.partition(" ")
            if commit_hash and separator:
                commits.append(GitCommit(commit_hash=commit_hash, message=message))
        return commits

    def current_branch(self) -> str:
        """Return the current branch, or an empty string for detached HEAD."""
        return self._execute(("branch", "--show-current")).strip()

    def repository_summary(self) -> RepositorySummary:
        """Compose branch, status, and recent commit information."""
        statuses = self.status()
        return RepositorySummary(
            current_branch=self.current_branch(),
            modified_files=[entry.path for entry in statuses if entry.modified],
            staged_files=[entry.path for entry in statuses if entry.staged],
            untracked_files=[entry.path for entry in statuses if entry.untracked],
            recent_commits=self.log(),
            clean=not statuses,
        )

    def _execute(self, arguments: Sequence[str]) -> str:
        command = tuple(arguments)
        if not self._is_allowed(command):
            raise GitCommandRejectedError(
                f"Git command is not allowed: git {' '.join(command)}"
            )
        try:
            completed = self._runner(
                ["git", *command],
                cwd=self._repository_path,
                capture_output=True,
                text=True,
                timeout=self._timeout_seconds,
                shell=False,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise GitCommandError(str(exc)) from exc
        if completed.returncode != 0:
            message = completed.stderr.strip() or "Git command failed"
            raise GitCommandError(message)
        return completed.stdout

    @staticmethod
    def _is_allowed(arguments: Tuple[str, ...]) -> bool:
        if arguments in {
            ("status", "--short"),
            ("diff",),
            ("branch", "--show-current"),
        }:
            return True
        return (
            len(arguments) == 4
            and arguments[:3] == ("log", "--oneline", "-n")
            and arguments[3].isdigit()
            and int(arguments[3]) > 0
        )
