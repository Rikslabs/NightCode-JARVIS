"""Workflow integrations - safe bridge to JARVIS tools."""
from dataclasses import dataclass, field
from typing import Any, Optional, Protocol, Dict

# Integration context for tool calls
@dataclass
class ToolIntegrationContext:
    """Context passed to tool integrations."""
    workflow_id: str
    project_path: str
    user_request: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            'workflow_id': self.workflow_id,
            'project_path': self.project_path,
            'user_request': self.user_request,
            'metadata': dict(self.metadata),
        }


# Protocol for integration handlers
class IntegrationHandler(Protocol):
    """Protocol for integration handlers."""
    def handle(self, context: ToolIntegrationContext) -> dict[str, Any]:
        """Handle the integration request."""
        ...


# Central integration registry
_INTEGRATION_REGISTRY: Dict[str, IntegrationHandler] = {}


def register_integration(name: str):
    """
    Decorator to register an integration handler.

    Args:
        name: The action name to register.

    Returns:
        Decorator function.
    """
    def decorator(cls: type) -> type:
        # Skip silently if already registered (prevent duplicate registrations)
        if name not in _INTEGRATION_REGISTRY:
            _INTEGRATION_REGISTRY[name] = cls()
        return cls
    return decorator


def get_integration(name: str) -> Optional[IntegrationHandler]:
    """
    Get an integration handler by name.

    Args:
        name: The integration name.

    Returns:
        Integration handler or None.
    """
    return _INTEGRATION_REGISTRY.get(name)


def list_integrations() -> Dict[str, IntegrationHandler]:
    """List all registered integrations."""
    return dict(_INTEGRATION_REGISTRY)


def execute_integration(action_name: str, context: ToolIntegrationContext) -> dict[str, Any]:
    """
    Execute an integration by name.

    Args:
        action_name: The action to execute.
        context: The integration context.

    Returns:
        Result dictionary.
    """
    handler = get_integration(action_name)
    if handler is None:
        return {'success': False, 'error': f'No integration registered for: {action_name}'}
    try:
        return {'success': True, 'data': handler.handle(context)}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def clear_integrations() -> None:
    """Clear all integrations (for testing)."""
    _INTEGRATION_REGISTRY.clear()