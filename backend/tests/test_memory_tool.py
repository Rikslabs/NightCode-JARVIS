import pytest
from app.tools.memory import MemoryTool
from app.tools.base import ToolResult


@pytest.fixture
def memory_tool():
    return MemoryTool()


def test_memory_set_stores_value(memory_tool):
    result = memory_tool.execute(operation="set", key="name", value="Vikash")
    assert result.success is True
    assert result.data == "Vikash"


def test_memory_get_returns_value(memory_tool):
    memory_tool.execute(operation="set", key="name", value="Vikash")
    result = memory_tool.execute(operation="get", key="name")
    assert result.success is True
    assert result.data == "Vikash"


def test_memory_get_missing_key_returns_none(memory_tool):
    result = memory_tool.execute(operation="get", key="nonexistent")
    assert result.success is True
    assert result.data is None


def test_memory_has_existing_key(memory_tool):
    memory_tool.execute(operation="set", key="name", value="Vikash")
    result = memory_tool.execute(operation="has", key="name")
    assert result.success is True
    assert result.data is True


def test_memory_has_missing_key(memory_tool):
    result = memory_tool.execute(operation="has", key="nonexistent")
    assert result.success is True
    assert result.data is False


def test_memory_unknown_operation_returns_error(memory_tool):
    result = memory_tool.execute(operation="delete", key="name")
    assert result.success is False
    assert "Unknown memory operation" in result.error


def test_memory_set_then_get_preserves_value(memory_tool):
    memory_tool.execute(operation="set", key="color", value="blue")
    get_result = memory_tool.execute(operation="get", key="color")
    assert get_result.data == "blue"