"""Terminal controller for VS Code."""

from typing import Optional

from .models import VSTerminalAction, VSActionResult


class TerminalController:
    """Controls VS Code terminal operations."""

    def __init__(self):
        self._output_buffer: list = []
        self._exit_code: Optional[int] = None

    def open_terminal(self) -> VSActionResult:
        """Open a new terminal (metadata only)."""
        return VSActionResult(
            success=True,
            action=VSTerminalAction.OPEN.value,
            message="Terminal opened",
        )

    def run_command(self, command: str) -> VSActionResult:
        """Run a command in terminal (metadata only)."""
        self._output_buffer.append(f"$ {command}")
        self._output_buffer.append("command executed")
        return VSActionResult(
            success=True,
            action=VSTerminalAction.RUN.value,
            message=f"Command executed: {command}",
            data={"command": command, "output": "command executed"},
        )

    def clear_terminal(self) -> VSActionResult:
        """Clear terminal (metadata only)."""
        self._output_buffer.clear()
        return VSActionResult(
            success=True,
            action=VSTerminalAction.CLEAR.value,
            message="Terminal cleared",
        )

    def get_exit_code(self) -> Optional[int]:
        """Get last command exit code."""
        return self._exit_code

    def get_output(self) -> list:
        """Get terminal output."""
        return list(self._output_buffer)