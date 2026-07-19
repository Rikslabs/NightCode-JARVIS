"""Typed models for provider discovery and selection."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping, Optional, Tuple

from .response import ProviderResponse


class ProviderStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"


class ProviderCapability(str, Enum):
    CODE_COMPLETION = "CODE_COMPLETION"
    CODE_REVIEW = "CODE_REVIEW"
    PLANNING = "PLANNING"


@dataclass(frozen=True)
class ProviderDescriptor:
    """Read-only provider identity and advertised capabilities."""

    id: str
    display_name: str
    status: ProviderStatus = ProviderStatus.UNAVAILABLE
    capabilities: Tuple[ProviderCapability, ...] = field(default_factory=tuple)
    metadata: Mapping[str, str] = field(default_factory=dict)

    @property
    def available(self) -> bool:
        return self.status is ProviderStatus.AVAILABLE

    @property
    def models(self) -> Tuple[str, ...]:
        return ()

    @property
    def selected_model(self) -> Optional[str]:
        return None

    def refresh(self) -> bool:
        return self.available

    def generate(self, prompt: str) -> ProviderResponse:
        raise RuntimeError(f"Provider {self.display_name} is unavailable.")
