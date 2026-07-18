"""Desktop registry for component management."""

from typing import Any, Optional

from .controller import DesktopController
from .permissions import DesktopPermissionManager
from .validator import DesktopValidator


class DesktopRegistry:
    """Registry for desktop automation components."""

    _instance: Optional["DesktopRegistry"] = None

    def __init__(self):
        self._controllers: dict = {}
        self._validators: dict = {}
        self._permission_managers: dict = {}

    @classmethod
    def get_instance(cls) -> "DesktopRegistry":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register_controller(self, name: str, controller: DesktopController) -> None:
        """Register a desktop controller."""
        self._controllers[name] = controller

    def register_validator(self, name: str, validator: DesktopValidator) -> None:
        """Register a desktop validator."""
        self._validators[name] = validator

    def register_permission_manager(
        self,
        name: str,
        manager: DesktopPermissionManager,
    ) -> None:
        """Register a permission manager."""
        self._permission_managers[name] = manager

    def get_controller(self, name: str = "default") -> Optional[DesktopController]:
        """Get a desktop controller."""
        return self._controllers.get(name)

    def get_validator(self, name: str = "default") -> Optional[DesktopValidator]:
        """Get a desktop validator."""
        return self._validators.get(name)

    def get_permission_manager(
        self,
        name: str = "default",
    ) -> Optional[DesktopPermissionManager]:
        """Get a permission manager."""
        return self._permission_managers.get(name)

    def clear(self) -> None:
        """Clear all registered components."""
        self._controllers.clear()
        self._validators.clear()
        self._permission_managers.clear()