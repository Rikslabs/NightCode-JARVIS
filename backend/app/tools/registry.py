import warnings
from typing import Any, Dict, Optional, Type

from .base import Tool


# The central registry mapping tool names to Tool instances.
_TOOL_REGISTRY: Dict[str, Tool] = {}


def register_tool(name: str):
    """
    A decorator to register a Tool class with a unique name.

    The decorated class is instantiated once at registration time and
    stored as a stateless singleton. Warnings are issued if a duplicate
    name is registered.

    Usage:
        @register_tool("memory")
        class MemoryTool(Tool):
            ...

    Args:
        name: The unique string identifier for this tool.

    Returns:
        The decorator function.
    """

    def decorator(cls: Type[Tool]) -> Type[Tool]:
        if name in _TOOL_REGISTRY:
            warnings.warn(
                f"Duplicate tool registration: '{name}' already "
                f"registered by {_TOOL_REGISTRY[name].__class__.__name__}. "
                f"Overwriting with {cls.__name__}."
            )
        instance = cls()
        instance.name = name
        _TOOL_REGISTRY[name] = instance
        return cls

    return decorator


def get_tool(name: str) -> Optional[Tool]:
    """
    Retrieves a Tool instance by its registered name.

    Args:
        name: The unique identifier of the tool.

    Returns:
        The Tool instance if found, otherwise None.
    """
    return _TOOL_REGISTRY.get(name)


def get_all_tools() -> Dict[str, Tool]:
    """
    Returns a copy of the full tool registry.

    Returns:
        A dictionary mapping tool names to Tool instances.
    """
    return dict(_TOOL_REGISTRY)


def get_tool_metadata() -> Dict[str, Dict[str, Any]]:
    """
    Retrieves metadata for all registered tools.

    Each entry contains the tool's description and parameter schema.
    Tools with no description are omitted from the listing.

    Returns:
        A dictionary mapping tool names to dicts with keys:
            "description": str — human-readable description of the tool.
            "parameters": dict — parameter name → description mapping.
    """
    result = {}
    for name, tool in _TOOL_REGISTRY.items():
        description = tool.description or ""
        if not description:
            continue
        result[name] = {
            "description": description,
            "parameters": dict(tool.parameters),
        }
    return result