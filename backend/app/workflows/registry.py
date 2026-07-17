"""Workflow action registry."""
import warnings
from typing import Any, Dict, Optional

from .actions import ActionDefinition


# Central registry for workflow actions
_ACTION_REGISTRY: Dict[str, ActionDefinition] = {}


def register_action(name: str, definition: Optional[ActionDefinition] = None):
    """
    Decorator to register an action definition.

    Args:
        name: The unique identifier for this action.
        definition: Optional ActionDefinition instance.

    Returns:
        The decorator function.
    """
    def decorator(cls: type) -> type:
        if name in _ACTION_REGISTRY:
            warnings.warn(
                f"Duplicate action registration: '{name}' already "
                f"registered. Overwriting with {cls.__name__}."
            )
        if definition:
            _ACTION_REGISTRY[name] = definition
        else:
            _ACTION_REGISTRY[name] = ActionDefinition(name=name, description=cls.__name__)
        return cls
    return decorator


def get_action(name: str) -> Optional[ActionDefinition]:
    """
    Retrieve an action definition by name.

    Args:
        name: The unique identifier of the action.

    Returns:
        The ActionDefinition if found, otherwise None.
    """
    return _ACTION_REGISTRY.get(name)


def list_actions() -> Dict[str, ActionDefinition]:
    """
    Returns a copy of all registered actions.

    Returns:
        Dictionary mapping action names to definitions.
    """
    return dict(_ACTION_REGISTRY)


def remove_action(name: str) -> bool:
    """
    Remove an action from the registry.

    Args:
        name: The action name to remove.

    Returns:
        True if removed, False if not found.
    """
    if name in _ACTION_REGISTRY:
        del _ACTION_REGISTRY[name]
        return True
    return False


def clear_registry() -> None:
    """Clear all registered actions (for testing)."""
    _ACTION_REGISTRY.clear()


def register_action_direct(name: str, definition: ActionDefinition) -> None:
    """Register an action definition directly (for testing)."""
    if name in _ACTION_REGISTRY:
        warnings.warn(f"Duplicate action registration: '{name}' already registered.")
    _ACTION_REGISTRY[name] = definition
