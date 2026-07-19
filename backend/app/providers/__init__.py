"""Multi-provider framework with unavailable placeholder providers."""

from .base import Provider
from .client import OllamaClient
from .exceptions import OllamaConnectionError, OllamaTimeoutError
from .generation import GenerationService
from .manager import ProviderManager
from .models import ProviderCapability, ProviderDescriptor, ProviderStatus
from .ollama import OllamaProvider
from .prompt import PlainPromptBuilder, PromptBuilder
from .response import GenerationResult, ProviderResponse
from .registry import DuplicateProviderError, ProviderNotFoundError, ProviderRegistry


def create_default_provider_manager(
    ollama_client: OllamaClient | None = None,
) -> ProviderManager:
    """Build an isolated manager with placeholders and Ollama connectivity."""
    manager = ProviderManager(ProviderRegistry())
    capabilities = (
        ProviderCapability.CODE_COMPLETION,
        ProviderCapability.CODE_REVIEW,
        ProviderCapability.PLANNING,
    )

    def register_placeholder(provider_id: str, display_name: str) -> None:
        manager.register(ProviderDescriptor(
            id=provider_id,
            display_name=display_name,
            capabilities=capabilities,
            metadata={"implementation": "placeholder"},
        ))

    register_placeholder("codex", "Codex")
    manager.register(OllamaProvider(ollama_client or OllamaClient()))
    register_placeholder("gemini", "Gemini")
    register_placeholder("claude", "Claude")
    return manager


__all__ = [
    "Provider",
    "ProviderCapability",
    "ProviderDescriptor",
    "ProviderManager",
    "ProviderRegistry",
    "ProviderStatus",
    "DuplicateProviderError",
    "ProviderNotFoundError",
    "OllamaClient",
    "OllamaConnectionError",
    "OllamaTimeoutError",
    "OllamaProvider",
    "GenerationResult",
    "GenerationService",
    "PlainPromptBuilder",
    "PromptBuilder",
    "ProviderResponse",
    "create_default_provider_manager",
]
