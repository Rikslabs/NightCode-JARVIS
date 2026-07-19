"""Provider contract for future coding-engine integrations."""

from typing import Mapping, Optional, Protocol, Tuple, runtime_checkable

from .models import ProviderCapability, ProviderStatus
from .response import ProviderResponse


@runtime_checkable
class Provider(Protocol):
    """Minimum metadata contract implemented by every provider."""

    @property
    def id(self) -> str: ...

    @property
    def display_name(self) -> str: ...

    @property
    def status(self) -> ProviderStatus: ...

    @property
    def available(self) -> bool: ...

    @property
    def capabilities(self) -> Tuple[ProviderCapability, ...]: ...

    @property
    def metadata(self) -> Mapping[str, str]: ...

    @property
    def models(self) -> Tuple[str, ...]: ...

    @property
    def selected_model(self) -> Optional[str]: ...

    def refresh(self) -> bool: ...

    def generate(self, prompt: str) -> ProviderResponse: ...
