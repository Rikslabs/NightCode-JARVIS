"""Runtime registry."""

from typing import Any, Dict, Optional

from .context import RuntimeContext
from .models import RuntimeStatus


class RuntimeRegistry:
    """Registry for runtime components."""

    _instance: Optional["RuntimeRegistry"] = None

    def __init__(self):
        self._components: Dict[str, Any] = {}

    @classmethod
    def get_instance(cls) -> "RuntimeRegistry":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register(self, name: str, component: Any) -> None:
        """Register a runtime component."""
        self._components[name] = component

    def get(self, name: str) -> Optional[Any]:
        """Get a registered component."""
        return self._components.get(name)

    def clear(self) -> None:
        """Clear all registered components."""
        self._components.clear()