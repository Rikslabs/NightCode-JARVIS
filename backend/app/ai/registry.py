import warnings
from typing import Any, Dict, Optional, Type

from app.ai.provider import AIProvider


class ProviderHealth:
    """Tracks health metrics for an AI provider."""

    __slots__ = (
        "available",
        "healthy",
        "last_success",
        "last_failure",
        "failure_count",
        "consecutive_failures",
        "latency",
    )

    def __init__(self):
        self.available = True
        self.healthy = True
        self.last_success: Optional[float] = None
        self.last_failure: Optional[float] = None
        self.failure_count = 0
        self.consecutive_failures = 0
        self.latency: Optional[float] = None

    def record_success(self, timestamp: float) -> None:
        self.last_success = timestamp
        self.consecutive_failures = 0
        self.healthy = True

    def record_failure(self, timestamp: float) -> None:
        self.last_failure = timestamp
        self.failure_count += 1
        self.consecutive_failures += 1
        if self.consecutive_failures >= 3:
            self.healthy = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "available": self.available,
            "healthy": self.healthy,
            "last_success": self.last_success,
            "last_failure": self.last_failure,
            "failure_count": self.failure_count,
            "consecutive_failures": self.consecutive_failures,
            "latency": self.latency,
        }


class ProviderMetadata:
    """Metadata for an AI provider."""

    def __init__(
        self,
        name: str,
        provider: Type[AIProvider],
        capabilities: list[str],
        priority: int = 0,
    ):
        self.name = name
        self.provider = provider
        self.capabilities = capabilities
        self.priority = priority
        self.health = ProviderHealth()

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "capabilities": self.capabilities,
            "priority": self.priority,
            "health": self.health.to_dict(),
        }


class ProviderRegistry:
    """Central registry for AI providers."""

    def __init__(self):
        self._providers: Dict[str, ProviderMetadata] = {}
        self._instances: Dict[str, AIProvider] = {}

    def register(
        self,
        name: str,
        provider_cls: Type[AIProvider],
        capabilities: list[str],
        priority: int = 0,
    ) -> None:
        if name in self._providers:
            warnings.warn(
                f"Duplicate provider registration: '{name}' already "
                f"registered. Overwriting."
            )
        self._providers[name] = ProviderMetadata(
            name=name,
            provider=provider_cls,
            capabilities=capabilities,
            priority=priority,
        )

    def get(self, name: str) -> Optional[AIProvider]:
        if name not in self._instances:
            if name not in self._providers:
                return None
            self._instances[name] = self._providers[name].provider()
        return self._instances[name]

    def get_metadata(self, name: str) -> Optional[dict[str, Any]]:
        meta = self._providers.get(name)
        return meta.to_dict() if meta else None

    def get_all(self) -> Dict[str, ProviderMetadata]:
        return dict(self._providers)

    def get_sorted_by_priority(self) -> list[ProviderMetadata]:
        return sorted(self._providers.values(), key=lambda m: m.priority, reverse=True)


# Global registry instance
_registry: Optional[ProviderRegistry] = None


def get_provider_registry() -> ProviderRegistry:
    global _registry
    if _registry is None:
        _registry = ProviderRegistry()
    return _registry