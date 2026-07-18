"""VS Code registry for component management."""

from typing import Any, Optional

from .controller import VSCodeController


class VSCodeRegistry:
    """Registry for VS Code automation components."""

    _instance: Optional["VSCodeRegistry"] = None

    def __init__(self):
        self._controllers: dict = {}

    @classmethod
    def get_instance(cls) -> "VSCodeRegistry":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register_controller(self, name: str, controller: VSCodeController) -> None:
        """Register a VS Code controller."""
        self._controllers[name] = controller

    def get_controller(self, name: str = "default") -> Optional[VSCodeController]:
        """Get a VS Code controller."""
        return self._controllers.get(name)

    def clear(self) -> None:
        """Clear all registered components."""
        self._controllers.clear()