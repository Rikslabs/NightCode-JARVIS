"""Focused tests for the multi-provider foundation."""

import pytest
from io import BytesIO
from urllib.error import URLError

from app.cli.commands import CLICommands
from app.providers import (
    DuplicateProviderError,
    ProviderCapability,
    ProviderDescriptor,
    ProviderManager,
    ProviderNotFoundError,
    ProviderRegistry,
    ProviderStatus,
    OllamaClient,
    OllamaProvider,
    create_default_provider_manager,
)


class FakeResponse(BytesIO):
    pass


def client_response(payload: bytes) -> OllamaClient:
    return OllamaClient(opener=lambda request, timeout: FakeResponse(payload))


def descriptor(provider_id: str, name: str) -> ProviderDescriptor:
    return ProviderDescriptor(
        id=provider_id,
        display_name=name,
        capabilities=(ProviderCapability.CODE_REVIEW,),
    )


def test_provider_registration_and_current_provider() -> None:
    manager = ProviderManager(ProviderRegistry())
    codex = descriptor("codex", "Codex")

    manager.register(codex)

    assert manager.has_provider("CODEX") is True
    assert manager.active_provider() is codex


def test_provider_switching_and_unknown_provider() -> None:
    manager = ProviderManager(ProviderRegistry())
    manager.register(descriptor("codex", "Codex"))
    manager.register(descriptor("ollama", "Ollama"))

    assert manager.switch_provider("OLLAMA").id == "ollama"
    assert manager.active_provider().id == "ollama"
    with pytest.raises(ProviderNotFoundError, match="missing.*not registered"):
        manager.switch_provider("missing")


def test_duplicate_registration_is_rejected() -> None:
    manager = ProviderManager(ProviderRegistry())
    manager.register(descriptor("codex", "Codex"))

    with pytest.raises(DuplicateProviderError, match="already registered"):
        manager.register(descriptor("CODEX", "Duplicate"))


def test_unregister_updates_current_provider() -> None:
    manager = ProviderManager(ProviderRegistry())
    manager.register(descriptor("codex", "Codex"))
    manager.register(descriptor("ollama", "Ollama"))

    removed = manager.unregister("codex")

    assert removed.id == "codex"
    assert manager.active_provider().id == "ollama"


def test_default_provider_listing_contains_placeholders_only() -> None:
    providers = create_default_provider_manager().list_providers()

    assert [provider.id for provider in providers] == [
        "codex", "ollama", "gemini", "claude"
    ]
    assert all(provider.status is ProviderStatus.UNAVAILABLE for provider in providers)
    assert all(provider.available is False for provider in providers)


def test_ollama_connection_success_and_model_discovery() -> None:
    provider = OllamaProvider(client_response(
        b'{"models":[{"name":"qwen2.5-coder:7b"},{"model":"llama3.1:8b"}]}'
    ))

    assert provider.connection_test() is True
    assert provider.status is ProviderStatus.AVAILABLE
    assert provider.models == ("qwen2.5-coder:7b", "llama3.1:8b")
    assert provider.selected_model == "qwen2.5-coder:7b"


def test_ollama_connection_failure_is_unavailable() -> None:
    def offline(request, timeout):
        raise URLError("offline")

    provider = OllamaProvider(OllamaClient(opener=offline))

    assert provider.connection_test() is False
    assert provider.status is ProviderStatus.UNAVAILABLE
    assert provider.models == ()


def test_ollama_timeout_is_unavailable() -> None:
    def timeout(request, timeout):
        raise TimeoutError("timed out")

    provider = OllamaProvider(OllamaClient(opener=timeout))

    assert provider.connection_test() is False
    assert provider.status is ProviderStatus.UNAVAILABLE


def test_ollama_empty_model_list_remains_available() -> None:
    provider = OllamaProvider(client_response(b'{"models":[]}'))

    assert provider.refresh() is True
    assert provider.available is True
    assert provider.models == ()
    assert provider.selected_model is None


def test_ollama_current_model_selection() -> None:
    provider = OllamaProvider(client_response(
        b'{"models":[{"name":"qwen2.5-coder:7b"},{"name":"llama3.1:8b"}]}'
    ))
    provider.refresh()

    provider.select_model("llama3.1:8b")

    assert provider.selected_model == "llama3.1:8b"


def test_provider_cli_summary_current_switch_and_unknown_error() -> None:
    output = []
    commands = CLICommands(
        service=object(),
        output=output.append,
        providers=create_default_provider_manager(),
    )

    commands.execute("provider")
    commands.execute("provider models")
    commands.execute("provider current")
    commands.execute("provider switch gemini")
    commands.execute("provider switch missing")

    rendered = "\n".join(output)
    assert "Codex (codex) [active]" in rendered
    assert "Status: UNAVAILABLE" in rendered
    assert "Available Models: none" in rendered
    assert "Active provider switched to Gemini (gemini)." in rendered
    assert "Error: Provider 'missing' is not registered." in rendered


def test_provider_current_displays_ollama_connection_and_selected_model() -> None:
    manager = create_default_provider_manager(client_response(
        b'{"models":[{"name":"qwen2.5-coder:7b"}]}'
    ))
    manager.switch_provider("ollama")
    output = []
    commands = CLICommands(service=object(), output=output.append, providers=manager)

    commands.execute("provider current")

    assert output == [
        "Current Provider: Ollama (ollama)\n"
        "Selected Model: qwen2.5-coder:7b\n"
        "Connection Status: AVAILABLE"
    ]
