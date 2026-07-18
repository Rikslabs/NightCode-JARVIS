"""Browser registry for component management."""

from typing import Any, Optional

from .controller import BrowserController


class BrowserRegistry:
    """Registry for browser automation components."""

    _instance: Optional["BrowserRegistry"] = None

    def __init__(self):
        self._controllers: dict = {}

    @classmethod
    def get_instance(cls) -> "BrowserRegistry":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register_controller(self, name: str, controller: BrowserController) -> None:
        """Register a browser controller."""
        self._controllers[name] = controller

    def get_controller(self, name: str = "default") -> Optional[BrowserController]:
        """Get a browser controller."""
        return self._controllers.get(name)

    def clear(self) -> None:
        """Clear all registered components."""
        self._controllers.clear()