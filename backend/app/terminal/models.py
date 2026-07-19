"""Terminal assistant models."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TerminalResult:
    """Captured result of a terminal command."""

    command: str
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float
    timed_out: bool
    success: bool
