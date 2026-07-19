"""Typed responses for provider and terminal generation layers."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ProviderResponse:
    """Provider-neutral response returned by a generation-capable provider."""

    text: str


@dataclass(frozen=True)
class GenerationResult:
    """Validated generation outcome safe for terminal rendering."""

    provider: str
    model: Optional[str]
    response: Optional[str]
    latency_seconds: Optional[float]
    error: Optional[str] = None

    @property
    def successful(self) -> bool:
        return self.error is None
