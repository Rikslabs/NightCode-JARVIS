import warnings
from typing import Any, Dict, Optional, Type, Callable
from .base import Command

# The central registry mapping intent names to command class instances.
_COMMAND_REGISTRY: Dict[str, Command] = {}


def register_command(intent_name: str) -> Callable[[Type[Command]], Type[Command]]:
    """
    A decorator to register a command class with a specific intent name.

    This allows for a clean, declarative way to add new commands. The system
    will automatically discover and register any class decorated with this.
    Warnings are issued if a duplicate intent is registered.

    Usage:
        @register_command("get_weather")
        class GetWeatherCommand(Command):
            ...

    Args:
        intent_name: The unique string identifier for the intent that this
                     command handles.

    Returns:
        The decorator function.
    """

    def decorator(cls: Type[Command]) -> Type[Command]:
        if intent_name in _COMMAND_REGISTRY:
            warnings.warn(
                f"Duplicate intent registration: '{intent_name}' already "
                f"registered by {_COMMAND_REGISTRY[intent_name].__class__.__name__}. "
                f"Overwriting with {cls.__name__}."
            )
        _COMMAND_REGISTRY[intent_name] = cls()
        return cls

    return decorator


def get_command(intent_name: str) -> Optional[Command]:
    """
    Retrieves a command instance from the registry by its intent name.

    The JarvisBrain will use this function to look up the appropriate command
    to execute based on the LLM's intent recognition.
    """
    return _COMMAND_REGISTRY.get(intent_name)


def get_command_details() -> Dict[str, Dict[str, Any]]:
    """
    Retrieves details for all registered commands.

    Used by the dispatcher to understand the available tools. Each entry
    contains a description (from the `description` class attribute or the
    class docstring) and a parameters schema.

    Commands with no description at all are omitted from the listing.

    Returns:
        A dictionary mapping intent names to dicts with keys:
            "description": str — human-readable description of the command.
            "parameters": dict — parameter name → description mapping.
    """
    result = {}
    for intent, command in _COMMAND_REGISTRY.items():
        description = getattr(command, "description", None)
        if description is None and command.__class__.__doc__:
            description = command.__class__.__doc__.strip()
        if not description:
            continue
        result[intent] = {
            "description": description,
            "parameters": getattr(command, "parameters", {}),
        }
    return result
