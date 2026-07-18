"""Service registry for managing service implementations."""
from typing import Any, Callable, Optional


class ServiceRegistry:
    """Registry for service implementations."""

    def __init__(self):
        self._services: dict[str, Any] = {}

    def register(self, name: str, service: Any) -> None:
        """Register a service by name."""
        self._services[name] = service

    def remove(self, name: str) -> bool:
        """Remove a service by name."""
        if name in self._services:
            del self._services[name]
            return True
        return False

    def resolve(self, name: str) -> Optional[Any]:
        """Resolve a service by name."""
        return self._services.get(name)

    def list_services(self) -> list[str]:
        """List all registered service names."""
        return list(self._services.keys())

    def clear(self) -> None:
        """Clear all registered services."""
        self._services.clear()

    def __contains__(self, name: str) -> bool:
        """Check if a service is registered."""
        return name in self._services

    def get(self, name: str, default: Any = None) -> Any:
        """Get a service by name with default."""
        return self._services.get(name, default)