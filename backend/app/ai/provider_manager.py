import time
from typing import Optional

from app.ai.provider import AIProvider
from app.ai.registry import ProviderMetadata, get_provider_registry


class ProviderManager:
    """Central entry point for all AI provider interactions with health-aware routing."""

    def __init__(self, registry=None, max_retries: int = 1):
        self._registry = registry or get_provider_registry()
        self.max_retries = max_retries

    def generate(
        self,
        prompt: str,
        provider_name: Optional[str] = None,
        capability: Optional[str] = None,
    ) -> str:
        """Generate a response using the specified provider, capability filter, or healthy fallback."""
        if provider_name:
            provider = self._registry.get(provider_name)
            if provider is None:
                raise ValueError(f"Provider '{provider_name}' is not registered.")
            return self._invoke(provider, provider_name, prompt)

        candidates = self._registry.get_sorted_by_priority()
        if not candidates:
            raise RuntimeError("No AI providers are registered.")

        if capability:
            candidates = [m for m in candidates if capability in m.capabilities]
            if not candidates:
                raise ValueError(
                    f"No providers support capability '{capability}'."
                )

        last_error = None
        for meta in candidates:
            provider = self._registry.get(meta.name)
            if provider is None:
                continue
            if not meta.health.healthy:
                continue
            try:
                return self._invoke(provider, meta.name, prompt)
            except Exception as exc:
                last_error = exc
                continue

        raise RuntimeError(
            f"All AI providers failed. Last error: {last_error}"
        )

    def _invoke(self, provider: AIProvider, name: str, prompt: str) -> str:
        """Invoke provider with retry and health tracking."""
        start = time.time()
        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                result = provider.generate(prompt)
                latency = time.time() - start
                meta = self._registry.get_all().get(name)
                if meta:
                    meta.health.record_success(time.time())
                    meta.health.latency = latency
                return result
            except Exception as exc:
                last_error = exc
                meta = self._registry.get_all().get(name)
                if meta:
                    meta.health.record_failure(time.time())
                continue
        raise RuntimeError(
            f"Provider '{name}' failed after {self.max_retries} attempts: {last_error}"
        )

    def register_provider(
        self,
        name: str,
        provider_cls,
        capabilities: list[str],
        priority: int = 0,
    ) -> None:
        self._registry.register(
            name=name,
            provider_cls=provider_cls,
            capabilities=capabilities,
            priority=priority,
        )

    def get_provider(self, name: str) -> Optional[AIProvider]:
        return self._registry.get(name)

    def list_providers(self) -> list[dict]:
        return [meta.to_dict() for meta in self._registry.get_all().values()]
