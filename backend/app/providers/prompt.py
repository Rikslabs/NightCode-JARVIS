"""Extensible prompt construction for read-only generation."""

from typing import Protocol


class PromptBuilder(Protocol):
    """Convert user input into a provider-ready prompt."""

    def build(self, user_input: str) -> str: ...


class PlainPromptBuilder:
    """Pass user questions through without adding provider-specific content."""

    def build(self, user_input: str) -> str:
        return user_input.strip()
