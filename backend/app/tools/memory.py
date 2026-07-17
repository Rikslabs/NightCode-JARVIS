from ..memory.manager import MemoryManager
from .base import Tool, ToolResult
from .registry import register_tool


@register_tool("memory")
class MemoryTool(Tool):
    """
    Provides persistent key-value storage for the JARVIS system.

    This tool wraps the existing MemoryManager and exposes structured
    get/set/has operations. It does not duplicate the underlying storage
    logic — all reads and writes delegate to MemoryManager.
    """

    name = "memory"
    description = "Provides persistent key-value storage for remembering user information."
    parameters = {
        "operation": "The operation to perform: 'get', 'set', or 'has'.",
        "key": "The storage key (string).",
        "value": "The value to store (required for 'set' operation).",
    }

    def __init__(self):
        self._manager = MemoryManager()

    def execute(self, operation: str, key: str, value: str = "") -> ToolResult:
        """
        Executes a memory operation.

        Args:
            operation: 'get' — retrieve the value for the given key.
                       'set' — store a value under the given key.
                       'has' — check if a key exists.
            key: The storage key.
            value: The value to store (required only for 'set').

        Returns:
            A ToolResult with:
                - For 'get': data containing the retrieved value (or None).
                - For 'set': data containing the stored value.
                - For 'has': data containing a boolean.
        """
        try:
            if operation == "get":
                data = self._manager.load()
                return ToolResult(success=True, data=data.get(key))

            if operation == "set":
                data = self._manager.load()
                data[key] = value
                self._manager.save(data)
                return ToolResult(success=True, data=value)

            if operation == "has":
                data = self._manager.load()
                return ToolResult(success=True, data=key in data)

            return ToolResult(
                success=False,
                error=f"Unknown memory operation: '{operation}'. "
                f"Use 'get', 'set', or 'has'.",
            )

        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Memory operation failed: {e}",
            )