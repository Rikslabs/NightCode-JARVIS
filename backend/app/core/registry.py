"""Core registry for shared components."""

from typing import Any, Callable, Dict, Optional


class CoreRegistry:
    """
    Registry for core shared components.

    Provides centralized access to common utilities and factories.
    """

    _instance: Optional["CoreRegistry"] = None

    def __init__(self):
        self._factories: Dict[str, Callable[[], Any]] = {}
        self._singletons: Dict[str, Any] = {}

    @classmethod
    def get_instance(cls) -> "CoreRegistry":
        """Get singleton instance (for backward compatibility)."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register_factory(self, name: str, factory: Callable[[], Any]) -> None:
        """Register a factory for creating components."""
        self._factories[name] = factory

    def register_singleton(self, name: str, instance: Any) -> None:
        """Register a singleton instance."""
        self._singletons[name] = instance

    def get(self, name: str) -> Optional[Any]:
        """Get a component by name."""
        if name in self._singletons:
            return self._singletons[name]
        if name in self._factories:
            return self._factories[name]()
        return None

    def clear(self) -> None:
        """Clear all registered components."""
        self._factories.clear()
        self._singletons.clear()

    def list_components(self) -> list:
        """List all registered component names."""
        return list(set(self._factories.keys()) | set(self._singletons.keys()))

    def to_dict(self) -> Dict[str, Any]:
        """Export registry state."""
        return {
            "factories": list(self._factories.keys()),
            "singletons": list(self._singletons.keys()),
        }