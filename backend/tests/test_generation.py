"""Focused tests for the read-only AI generation pipeline."""

from dataclasses import dataclass, field
from io import BytesIO
import json
from typing import Mapping, Optional, Tuple

from app.cli.commands import CLICommands
from app.providers import (
    GenerationService,
    OllamaClient,
    OllamaProvider,
    Provider,
    ProviderCapability,
    ProviderManager,
    ProviderRegistry,
    ProviderResponse,
    ProviderStatus,
)


@dataclass
class FakeProvider:
    id: str
    display_name: str
    available: bool = True
    selected_model: Optional[str] = "test-model"
    response: object = field(default_factory=lambda: ProviderResponse("answer"))
    capabilities: Tuple[ProviderCapability, ...] = ()
    metadata: Mapping[str, str] = field(default_factory=dict)
    models: Tuple[str, ...] = ("test-model",)
    prompts: list[str] = field(default_factory=list)

    @property
    def status(self) -> ProviderStatus:
        return ProviderStatus.AVAILABLE if self.available else ProviderStatus.UNAVAILABLE

    def refresh(self) -> bool:
        return self.available

    def generate(self, prompt: str) -> ProviderResponse:
        self.prompts.append(prompt)
        if isinstance(self.response, BaseException):
            raise self.response
        return self.response  # type: ignore[return-value]


def manager_with(*providers: Provider) -> ProviderManager:
    manager = ProviderManager(ProviderRegistry())
    for provider in providers:
        manager.register(provider)
    return manager


def test_successful_generation_and_terminal_formatting() -> None:
    provider = FakeProvider("one", "Provider One")
    ticks = iter((10.0, 10.25))
    service = GenerationService(manager_with(provider), clock=lambda: next(ticks))

    result = service.ask("Explain this")

    assert result.successful is True
    assert result.response == "answer"
    assert "Provider: Provider One" in service.format_terminal(result)
    assert "Model: test-model" in service.format_terminal(result)
    assert "Latency: 0.250s" in service.format_terminal(result)


def test_unavailable_provider_is_reported_without_generation() -> None:
    provider = FakeProvider("offline", "Offline", available=False)

    result = GenerationService(manager_with(provider)).ask("question")

    assert result.successful is False
    assert "unavailable" in result.error
    assert provider.prompts == []


def test_timeout_is_reported() -> None:
    provider = FakeProvider("slow", "Slow", response=TimeoutError())

    result = GenerationService(manager_with(provider)).ask("question")

    assert result.successful is False
    assert "timed out" in result.error


def test_empty_and_invalid_responses_are_rejected() -> None:
    empty = FakeProvider("empty", "Empty", response=ProviderResponse("  "))
    invalid = FakeProvider("invalid", "Invalid", response={"text": "wrong"})

    empty_result = GenerationService(manager_with(empty)).ask("question")
    invalid_result = GenerationService(manager_with(invalid)).ask("question")

    assert "empty response" in empty_result.error
    assert "invalid response" in invalid_result.error


def test_prompt_builder_routes_prompt_without_inline_construction() -> None:
    provider = FakeProvider("one", "One")

    class PrefixBuilder:
        def build(self, user_input: str) -> str:
            return f"PREFIX: {user_input}"

    GenerationService(manager_with(provider), PrefixBuilder()).ask("question")

    assert provider.prompts == ["PREFIX: question"]


def test_generation_uses_active_provider() -> None:
    first = FakeProvider("first", "First")
    second = FakeProvider("second", "Second")
    manager = manager_with(first, second)
    manager.switch_provider("second")

    result = GenerationService(manager).ask("question")

    assert result.provider == "Second"
    assert first.prompts == []
    assert second.prompts == ["question"]


def test_ai_ask_cli_routes_quoted_prompt() -> None:
    provider = FakeProvider("one", "One")
    manager = manager_with(provider)
    output = []
    commands = CLICommands(
        service=object(),
        output=output.append,
        providers=manager,
        generation=GenerationService(manager),
    )

    commands.execute('ai ask "Explain reviewer.py"')

    assert provider.prompts == ["Explain reviewer.py"]
    assert "Response:\nanswer" in output[0]


def test_ollama_generation_routes_model_and_prompt_without_streaming() -> None:
    requests = []
    responses = iter((
        b'{"models":[{"name":"qwen2.5-coder:7b"}]}',
        b'{"response":"local answer"}',
    ))

    def open_response(request, timeout):
        requests.append(request)
        return BytesIO(next(responses))

    provider = OllamaProvider(OllamaClient(opener=open_response))
    manager = manager_with(provider)

    result = GenerationService(manager).ask("Explain this")

    body = json.loads(requests[1].data.decode("utf-8"))
    assert result.response == "local answer"
    assert body == {
        "model": "qwen2.5-coder:7b",
        "prompt": "Explain this",
        "stream": False,
    }
