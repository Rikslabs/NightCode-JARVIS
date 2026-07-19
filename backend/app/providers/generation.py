"""Provider-agnostic, read-only AI generation coordination."""

from time import perf_counter
from typing import Callable, Optional

from .manager import ProviderManager
from .prompt import PlainPromptBuilder, PromptBuilder
from .response import GenerationResult, ProviderResponse


class GenerationService:
    """Route questions to the active provider without repository side effects."""

    def __init__(
        self,
        providers: ProviderManager,
        prompt_builder: Optional[PromptBuilder] = None,
        clock: Callable[[], float] = perf_counter,
    ) -> None:
        self._providers = providers
        self._prompt_builder = prompt_builder or PlainPromptBuilder()
        self._clock = clock

    def ask(self, user_input: str) -> GenerationResult:
        provider = self._providers.active_provider()
        if provider is None:
            return self._failure("none", None, "No active provider is configured.")

        prompt = self._prompt_builder.build(user_input)
        if not prompt:
            return self._failure(provider.display_name, provider.selected_model, "Prompt is empty.")
        try:
            refreshed = provider.refresh()
        except TimeoutError:
            return self._failure(
                provider.display_name,
                provider.selected_model,
                f"Provider {provider.display_name} timed out.",
            )
        except Exception as exc:
            return self._failure(
                provider.display_name,
                provider.selected_model,
                f"Provider {provider.display_name} failed: {exc}",
            )
        if not refreshed or not provider.available:
            return self._failure(
                provider.display_name,
                provider.selected_model,
                f"Provider {provider.display_name} is unavailable.",
            )
        if provider.selected_model is None:
            return self._failure(
                provider.display_name,
                None,
                f"Provider {provider.display_name} has no selected model.",
            )

        started = self._clock()
        try:
            response = provider.generate(prompt)
        except TimeoutError:
            return self._failure(
                provider.display_name,
                provider.selected_model,
                f"Provider {provider.display_name} timed out.",
            )
        except Exception as exc:
            return self._failure(
                provider.display_name,
                provider.selected_model,
                f"Provider {provider.display_name} failed: {exc}",
            )
        latency = max(0.0, self._clock() - started)
        if not isinstance(response, ProviderResponse):
            return self._failure(
                provider.display_name,
                provider.selected_model,
                f"Provider {provider.display_name} returned an invalid response.",
            )
        text = response.text.strip()
        if not text:
            return self._failure(
                provider.display_name,
                provider.selected_model,
                f"Provider {provider.display_name} returned an empty response.",
            )
        return GenerationResult(
            provider=provider.display_name,
            model=provider.selected_model,
            response=text,
            latency_seconds=latency,
        )

    @staticmethod
    def format_terminal(result: GenerationResult) -> str:
        latency = (
            f"{result.latency_seconds:.3f}s"
            if result.latency_seconds is not None
            else "not available"
        )
        parts = [
            f"Provider: {result.provider}",
            f"Model: {result.model or 'none'}",
            f"Latency: {latency}",
        ]
        parts.append(
            f"Response:\n{result.response}"
            if result.successful
            else f"Error: {result.error}"
        )
        return "\n".join(parts)

    @staticmethod
    def _failure(provider: str, model: Optional[str], error: str) -> GenerationResult:
        return GenerationResult(provider, model, None, None, error)
