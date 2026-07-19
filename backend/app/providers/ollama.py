"""Connection-only Ollama provider."""

from typing import Mapping, Optional, Tuple

from .client import OllamaClient
from .exceptions import OllamaConnectionError
from .models import ProviderCapability, ProviderStatus
from .response import ProviderResponse


class OllamaProvider:
    """Expose read-only Ollama discovery and single-response generation."""

    id = "ollama"
    display_name = "Ollama"
    capabilities: Tuple[ProviderCapability, ...] = (
        ProviderCapability.CODE_COMPLETION,
        ProviderCapability.CODE_REVIEW,
        ProviderCapability.PLANNING,
    )
    metadata: Mapping[str, str] = {"implementation": "read-only-generation"}

    def __init__(self, client: OllamaClient) -> None:
        self._client = client
        self._status = ProviderStatus.UNAVAILABLE
        self._models: Tuple[str, ...] = ()
        self._selected_model: Optional[str] = None

    @property
    def status(self) -> ProviderStatus:
        return self._status

    @property
    def available(self) -> bool:
        return self._status is ProviderStatus.AVAILABLE

    @property
    def models(self) -> Tuple[str, ...]:
        return self._models

    @property
    def selected_model(self) -> Optional[str]:
        return self._selected_model

    def refresh(self) -> bool:
        """Test the connection and refresh local model metadata."""
        try:
            self._models = tuple(dict.fromkeys(self._client.list_models()))
        except OllamaConnectionError:
            self._status = ProviderStatus.UNAVAILABLE
            self._models = ()
            self._selected_model = None
            return False
        self._status = ProviderStatus.AVAILABLE
        if self._selected_model not in self._models:
            self._selected_model = self._models[0] if self._models else None
        return True

    def connection_test(self) -> bool:
        return self.refresh()

    def select_model(self, model: str) -> None:
        if model not in self._models:
            raise ValueError(f"Ollama model '{model}' is not available.")
        self._selected_model = model

    def generate(self, prompt: str) -> ProviderResponse:
        if not self.available or self._selected_model is None:
            raise OllamaConnectionError("Ollama is unavailable or has no selected model.")
        return ProviderResponse(self._client.generate(self._selected_model, prompt))
