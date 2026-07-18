"""Registry for intelligence components."""

import warnings
from typing import Any, Callable, Dict, Optional, Type

from .reasoner import IntentReasoner
from .planner import ExecutionPlanner
from .selector import ToolSelector
from .validator import ExecutionValidator


class IntelligenceRegistry:
    """
    Registry for intelligence components.

    Allows registration and lookup of reasoners, validators, planners, and selectors.
    """

    def __init__(self):
        self._reasoners: Dict[str, IntentReasoner] = {}
        self._planners: Dict[str, ExecutionPlanner] = {}
        self._selectors: Dict[str, ToolSelector] = {}
        self._validators: Dict[str, ExecutionValidator] = {}

    def register_reasoner(self, name: str, reasoner: IntentReasoner) -> None:
        """Register an intent reasoner."""
        if name in self._reasoners:
            warnings.warn(f"Overwriting existing reasoner: {name}")
        self._reasoners[name] = reasoner

    def register_planner(self, name: str, planner: ExecutionPlanner) -> None:
        """Register an execution planner."""
        if name in self._planners:
            warnings.warn(f"Overwriting existing planner: {name}")
        self._planners[name] = planner

    def register_selector(self, name: str, selector: ToolSelector) -> None:
        """Register a tool selector."""
        if name in self._selectors:
            warnings.warn(f"Overwriting existing selector: {name}")
        self._selectors[name] = selector

    def register_validator(self, name: str, validator: ExecutionValidator) -> None:
        """Register an execution validator."""
        if name in self._validators:
            warnings.warn(f"Overwriting existing validator: {name}")
        self._validators[name] = validator

    def get_reasoner(self, name: str = "default") -> Optional[IntentReasoner]:
        """Get a reasoner by name."""
        if name == "default":
            return self._reasoners.get("default", IntentReasoner())
        return self._reasoners.get(name)

    def get_planner(self, name: str = "default") -> Optional[ExecutionPlanner]:
        """Get a planner by name."""
        if name == "default":
            return self._planners.get("default", ExecutionPlanner())
        return self._planners.get(name)

    def get_selector(self, name: str = "default") -> Optional[ToolSelector]:
        """Get a selector by name."""
        if name == "default":
            return self._selectors.get("default", ToolSelector())
        return self._selectors.get(name)

    def get_validator(self, name: str = "default") -> Optional[ExecutionValidator]:
        """Get a validator by name."""
        if name == "default":
            return self._validators.get("default", ExecutionValidator())
        return self._validators.get(name)

    def list_reasoners(self) -> Dict[str, IntentReasoner]:
        """List all registered reasoners."""
        return dict(self._reasoners)

    def list_planners(self) -> Dict[str, ExecutionPlanner]:
        """List all registered planners."""
        return dict(self._planners)

    def list_selectors(self) -> Dict[str, ToolSelector]:
        """List all registered selectors."""
        return dict(self._selectors)

    def list_validators(self) -> Dict[str, ExecutionValidator]:
        """List all registered validators."""
        return dict(self._validators)

    def clear(self) -> None:
        """Clear all registrations."""
        self._reasoners.clear()
        self._planners.clear()
        self._selectors.clear()
        self._validators.clear()


# Global registry instance
_registry: Optional[IntelligenceRegistry] = None


def get_registry() -> IntelligenceRegistry:
    """Get the global intelligence registry."""
    global _registry
    if _registry is None:
        _registry = IntelligenceRegistry()
    return _registry


def register_reasoner(name: str, reasoner: IntentReasoner) -> None:
    """Register a reasoner with the global registry."""
    get_registry().register_reasoner(name, reasoner)


def register_planner(name: str, planner: ExecutionPlanner) -> None:
    """Register a planner with the global registry."""
    get_registry().register_planner(name, planner)


def register_selector(name: str, selector: ToolSelector) -> None:
    """Register a selector with the global registry."""
    get_registry().register_selector(name, selector)


def register_validator(name: str, validator: ExecutionValidator) -> None:
    """Register a validator with the global registry."""
    get_registry().register_validator(name, validator)