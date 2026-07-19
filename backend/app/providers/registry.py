"""Instance-scoped provider registry."""

from typing import Dict, Optional, Tuple

from .base import Provider


class DuplicateProviderError(ValueError):
    pass


class ProviderNotFoundError(ValueError):
    pass


class ProviderRegistry:
    """Store providers without constructing or invoking engines."""

    def __init__(self) -> None:
        self._providers: Dict[str, Provider] = {}

    def register(self, provider: Provider) -> None:
        provider_id = self._normalize(provider.id)
        if not provider_id:
            raise ValueError("Provider id cannot be empty.")
        if provider_id in self._providers:
            raise DuplicateProviderError(f"Provider '{provider.id}' is already registered.")
        self._providers[provider_id] = provider

    def unregister(self, provider_id: str) -> Provider:
        normalized = self._normalize(provider_id)
        try:
            return self._providers.pop(normalized)
        except KeyError as exc:
            raise ProviderNotFoundError(
                f"Provider '{provider_id}' is not registered."
            ) from exc

    def get(self, provider_id: str) -> Optional[Provider]:
        return self._providers.get(self._normalize(provider_id))

    def list(self) -> Tuple[Provider, ...]:
        return tuple(self._providers.values())

    @staticmethod
    def _normalize(provider_id: str) -> str:
        return provider_id.strip().casefold()
