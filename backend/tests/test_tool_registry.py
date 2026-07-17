import pytest
from app.tools.base import Tool, ToolResult
from app.tools.registry import register_tool, get_tool, get_all_tools, get_tool_metadata


class DummyTool(Tool):
    description = "A dummy tool for testing."
    parameters = {"param1": "First parameter."}

    def execute(self, **kwargs) -> ToolResult:
        return ToolResult(success=True, data="dummy")


def test_register_tool_stores_instance():
    register_tool("dummy")(DummyTool)
    tool = get_tool("dummy")
    assert tool is not None
    assert isinstance(tool, DummyTool)


def test_register_tool_sets_name():
    register_tool("dummy")(DummyTool)
    tool = get_tool("dummy")
    assert tool.name == "dummy"


def test_register_tool_returns_metadata():
    register_tool("dummy")(DummyTool)
    metadata = get_tool_metadata()
    assert "dummy" in metadata
    assert metadata["dummy"]["description"] == "A dummy tool for testing."
    assert metadata["dummy"]["parameters"] == {"param1": "First parameter."}


def test_register_duplicate_tool_warns():
    # Register once, then register again to trigger warning
    register_tool("dummy")(DummyTool)
    with pytest.warns(UserWarning, match="Duplicate tool registration"):
        register_tool("dummy")(DummyTool)


def test_get_tool_missing_returns_none():
    assert get_tool("nonexistent") is None


def test_get_all_tools_returns_copy():
    register_tool("dummy")(DummyTool)
    all_tools = get_all_tools()
    assert "dummy" in all_tools
    # Mutating the returned dict should not affect the registry
    all_tools["dummy"] = None
    assert get_tool("dummy") is not None