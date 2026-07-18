"""Diagnostics controller for VS Code."""

from typing import Optional, Dict, Any

from .models import VSDiagnosticsAction, VSActionResult


class DiagnosticsController:
    """Controls VS Code diagnostics operations."""

    def __init__(self):
        self._problems: list = [
            {"file": "main.py", "line": 10, "type": "error", "message": "Syntax error"},
            {"file": "utils.py", "line": 5, "type": "warning", "message": "Unused import"},
        ]

    def get_problems(self) -> VSActionResult:
        """Read Problems panel (metadata only)."""
        return VSActionResult(
            success=True,
            action=VSDiagnosticsAction.READ_PROBLEMS.value,
            message="Problems retrieved",
            data={"problems": self._problems},
        )

    def count_errors(self) -> int:
        """Count errors in problems."""
        return sum(1 for p in self._problems if p["type"] == "error")

    def count_warnings(self) -> int:
        """Count warnings in problems."""
        return sum(1 for p in self._problems if p["type"] == "warning")

    def get_summary(self) -> Dict[str, int]:
        """Get diagnostics summary."""
        return {
            "errors": self.count_errors(),
            "warnings": self.count_warnings(),
            "total": len(self._problems),
        }