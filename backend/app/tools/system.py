from .base import Tool, ToolResult
from .registry import register_tool
from ..version import __version__


@register_tool("system")
class SystemTool(Tool):
    """
    Provides read-only system information about the JARVIS environment.

    This tool encapsulates reusable system operations such as checking
    the system status and listing available modules.
    """

    name = "system"
    description = "Provides read-only system information about the JARVIS environment."
    parameters = {
        "operation": "The operation to perform: 'status' or 'modules'.",
    }

    def execute(self, operation: str) -> ToolResult:
        """
        Executes a system information operation.

        Args:
            operation: 'status' — returns whether the system is operational.
                       'modules' — returns a list of available module names.

        Returns:
            A ToolResult with structured system information.
        """
        try:
            if operation == "status":
                return ToolResult(
                    success=True,
                    data={
                        "status": "Operational",
                        "version": __version__,
                    },
                )

            if operation == "modules":
                return ToolResult(
                    success=True,
                    data={
                        "modules": ["system", "memory"],
                    },
                )

            return ToolResult(
                success=False,
                error=f"Unknown system operation: '{operation}'. "
                f"Use 'status' or 'modules'.",
            )

        except Exception as e:
            return ToolResult(
                success=False,
                error=f"System operation failed: {e}",
            )
