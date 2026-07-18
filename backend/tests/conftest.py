import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

from app.memory import registry as command_registry
from app.tools import registry as tool_registry
from app.ai import registry as ai_registry


@pytest.fixture(autouse=True)
def clean_registries():
    """Reset all registries before and after each test to ensure isolation."""
    command_registry._COMMAND_REGISTRY.clear()
    tool_registry._TOOL_REGISTRY.clear()
    ai_registry._registry = None
    yield
    command_registry._COMMAND_REGISTRY.clear()
    tool_registry._TOOL_REGISTRY.clear()
    ai_registry._registry = None