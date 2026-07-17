import pytest
from unittest.mock import MagicMock
from app.brain.matcher import CommandMatcher
from app.ai.provider import AIProvider


class FakeProvider(AIProvider):
    def generate(self, prompt: str) -> str:
        return '{"intent": "remember_name", "params": {"name": "Vikash"}}'


def test_keyword_match_found():
    matcher = CommandMatcher()
    result = matcher._keyword_match("system status", {"system_status": {"description": "Get status.", "parameters": {}}})
    assert result == {"intent": "system_status", "params": {}}


def test_keyword_match_case_insensitive():
    matcher = CommandMatcher()
    result = matcher._keyword_match("SYSTEM STATUS", {"system_status": {"description": "Get status.", "parameters": {}}})
    assert result == {"intent": "system_status", "params": {}}


def test_keyword_match_not_found():
    matcher = CommandMatcher()
    result = matcher._keyword_match("hello", {"system_status": {"description": "Get status.", "parameters": {}}})
    assert result is None


def test_llm_match_returns_intent():
    provider = FakeProvider()
    matcher = CommandMatcher(ai_provider=provider)
    result = matcher._llm_match("my name is Vikash", {
        "remember_name": {"description": "Remember name.", "parameters": {"name": "The name."}},
        "get_name": {"description": "Get name.", "parameters": {}},
    })
    assert result == {"intent": "remember_name", "params": {"name": "Vikash"}}


def test_llm_match_handles_markdown_json():
    provider = MagicMock(spec=AIProvider)
    provider.generate.return_value = '```json\n{"intent": "remember_name", "params": {"name": "Vikash"}}\n```'
    matcher = CommandMatcher(ai_provider=provider)
    result = matcher._llm_match("my name is Vikash", {
        "remember_name": {"description": "Remember name.", "parameters": {"name": "The name."}},
    })
    assert result == {"intent": "remember_name", "params": {"name": "Vikash"}}


def test_llm_match_returns_none_when_no_intent():
    provider = MagicMock(spec=AIProvider)
    provider.generate.return_value = '{"intent": null, "params": {}}'
    matcher = CommandMatcher(ai_provider=provider)
    result = matcher._llm_match("hello", {"system_status": {"description": "Get status.", "parameters": {}}})
    assert result is None


def test_match_keyword_first_then_llm():
    provider = MagicMock(spec=AIProvider)
    provider.generate.return_value = '{"intent": "get_name", "params": {}}'
    matcher = CommandMatcher(ai_provider=provider)

    # Keyword should match first, LLM should not be called
    result = matcher.match("system status", {"system_status": {"description": "Get status.", "parameters": {}}})
    assert result == {"intent": "system_status", "params": {}}
    provider.generate.assert_not_called()


def test_match_falls_back_to_llm_when_keyword_fails():
    provider = FakeProvider()
    matcher = CommandMatcher(ai_provider=provider)
    result = matcher.match("my name is Vikash", {
        "remember_name": {"description": "Remember name.", "parameters": {"name": "The name."}},
        "get_name": {"description": "Get name.", "parameters": {}},
    })
    assert result == {"intent": "remember_name", "params": {"name": "Vikash"}}


def test_match_returns_none_when_no_match_and_no_llm():
    matcher = CommandMatcher()  # No AI provider
    result = matcher.match("hello", {"system_status": {"description": "Get status.", "parameters": {}}})
    assert result is None