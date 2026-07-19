"""Allowlisted, no-shell terminal command execution."""

import shlex
import subprocess
from pathlib import Path
from time import perf_counter
from typing import List, Optional, Tuple, Union

from .models import TerminalResult


class TerminalAssistant:
    """Run a small allowlist of development commands without a shell."""

    def __init__(
        self,
        timeout_seconds: float = 30.0,
        working_directory: Optional[Union[str, Path]] = None,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero")
        self._timeout_seconds = timeout_seconds
        self._working_directory = (
            Path(working_directory) if working_directory is not None else None
        )
        self._allowed_families = {"pytest", "python", "uvicorn", "npm"}
        self._allowed_git_commands = {"status", "diff", "log"}

    def run(self, command: str) -> TerminalResult:
        """Validate and execute a command with captured output."""
        started = perf_counter()
        arguments, rejection = self._validate(command)
        if rejection is not None:
            return self._result(
                command=command,
                exit_code=126,
                stderr=rejection,
                duration_seconds=perf_counter() - started,
            )

        try:
            completed = subprocess.run(
                arguments,
                cwd=self._working_directory,
                capture_output=True,
                text=True,
                timeout=self._timeout_seconds,
                shell=False,
                check=False,
            )
            return self._result(
                command=command,
                exit_code=completed.returncode,
                stdout=completed.stdout,
                stderr=completed.stderr,
                duration_seconds=perf_counter() - started,
            )
        except subprocess.TimeoutExpired as exc:
            return self._result(
                command=command,
                exit_code=124,
                stdout=self._output_text(exc.stdout),
                stderr=self._output_text(exc.stderr) or (
                    f"Command timed out after {self._timeout_seconds} seconds"
                ),
                duration_seconds=perf_counter() - started,
                timed_out=True,
            )
        except OSError as exc:
            return self._result(
                command=command,
                exit_code=127,
                stderr=str(exc),
                duration_seconds=perf_counter() - started,
            )

    def _validate(self, command: str) -> Tuple[List[str], Optional[str]]:
        if not command.strip():
            return [], "Command is empty"
        try:
            arguments = shlex.split(command, posix=True)
        except ValueError as exc:
            return [], f"Invalid command syntax: {exc}"
        if not arguments:
            return [], "Command is empty"

        raw_executable = arguments[0]
        if "/" in raw_executable or "\\" in raw_executable:
            return [], "Executable paths are not allowed"
        executable = raw_executable.casefold()
        if executable.endswith(".exe"):
            executable = executable[:-4]

        if executable == "git":
            if len(arguments) < 2 or arguments[1].casefold() not in self._allowed_git_commands:
                return [], "Only git status, git diff, and git log are allowed"
            if any(
                argument.casefold() == "--output"
                or argument.casefold().startswith("--output=")
                for argument in arguments[2:]
            ):
                return [], "Git output-file options are not allowed"
            return arguments, None
        if executable not in self._allowed_families:
            return [], f"Command family is not allowed: {raw_executable}"
        return arguments, None

    @staticmethod
    def _result(
        command: str,
        exit_code: int,
        duration_seconds: float,
        stdout: str = "",
        stderr: str = "",
        timed_out: bool = False,
    ) -> TerminalResult:
        return TerminalResult(
            command=command,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            duration_seconds=duration_seconds,
            timed_out=timed_out,
            success=exit_code == 0 and not timed_out,
        )

    @staticmethod
    def _output_text(output: Optional[Union[str, bytes]]) -> str:
        if output is None:
            return ""
        return output.decode(errors="replace") if isinstance(output, bytes) else output
