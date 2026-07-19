"""Provider lifecycle and active-selection coordination."""

from typing import Optional, Tuple

from .base import Provider
from .registry import ProviderNotFoundError, ProviderRegistry


class ProviderManager:
    """Manage provider registration and selection through an injected registry."""

    def __init__(self, registry: ProviderRegistry) -> None:
        self._registry = registry
        self._active_provider_id: Optional[str] = None

    def register(self, provider: Provider) -> None:
        self._registry.register(provider)
        if self._active_provider_id is None:
            self._active_provider_id = provider.id

    def unregister(self, provider_id: str) -> Provider:
        provider = self._registry.unregister(provider_id)
        if self._same_id(self._active_provider_id, provider.id):
            providers = self.list_providers()
            self._active_provider_id = providers[0].id if providers else None
        return provider

    def active_provider(self) -> Optional[Provider]:
        if self._active_provider_id is None:
            return None
        return self._registry.get(self._active_provider_id)

    def switch_provider(self, provider_id: str) -> Provider:
        provider = self._registry.get(provider_id)
        if provider is None:
            raise ProviderNotFoundError(f"Provider '{provider_id}' is not registered.")
        self._active_provider_id = provider.id
        return provider

    def list_providers(self) -> Tuple[Provider, ...]:
        return self._registry.list()

    def refresh_providers(self) -> Tuple[Provider, ...]:
        providers = self.list_providers()
        for provider in providers:
            provider.refresh()
        return providers

    def has_provider(self, provider_id: str) -> bool:
        return self._registry.get(provider_id) is not None

    @staticmethod
    def _same_id(left: Optional[str], right: str) -> bool:
        return left is not None and left.casefold() == right.casefold()
