"""Goal Registry - registers goal components for future extensibility."""

import warnings
from typing import Any, Dict, List, Optional


class GoalRegistry:
    """
    Registry for pluggable goal components.

    Allows future modules to register decomposers, planners, validators, etc.
    """

    def __init__(self):
        self._decomposers: Dict[str, Any] = {}
        self._planners: Dict[str, Any] = {}
        self._validators: Dict[str, Any] = {}
        self._analyzers: Dict[str, Any] = {}

    def register_decomposer(self, name: str, decomposer: Any) -> None:
        """Register a goal decomposer."""
        if name in self._decomposers:
            warnings.warn(f"Overwriting decomposer: {name}")
        self._decomposers[name] = decomposer

    def register_planner(self, name: str, planner: Any) -> None:
        """Register a goal planner."""
        if name in self._planners:
            warnings.warn(f"Overwriting planner: {name}")
        self._planners[name] = planner

    def register_validator(self, name: str, validator: Any) -> None:
        """Register a goal validator."""
        if name in self._validators:
            warnings.warn(f"Overwriting validator: {name}")
        self._validators[name] = validator

    def register_analyzer(self, name: str, analyzer: Any) -> None:
        """Register a goal analyzer."""
        if name in self._analyzers:
            warnings.warn(f"Overwriting analyzer: {name}")
        self._analyzers[name] = analyzer

    def get_decomposer(self, name: str) -> Optional[Any]:
        """Get a registered decomposer."""
        return self._decomposers.get(name)

    def get_planner(self, name: str) -> Optional[Any]:
        """Get a registered planner."""
        return self._planners.get(name)

    def get_validator(self, name: str) -> Optional[Any]:
        """Get a registered validator."""
        return self._validators.get(name)

    def get_analyzer(self, name: str) -> Optional[Any]:
        """Get a registered analyzer."""
        return self._analyzers.get(name)

    def list_decomposers(self) -> List[str]:
        """List all registered decomposer names."""
        return list(self._decomposers.keys())

    def list_planners(self) -> List[str]:
        """List all registered planner names."""
        return list(self._planners.keys())

    def list_validators(self) -> List[str]:
        """List all registered validator names."""
        return list(self._validators.keys())

    def list_analyzers(self) -> List[str]:
        """List all registered analyzer names."""
        return list(self._analyzers.keys())

    def to_dict(self) -> Dict[str, Any]:
        """Convert registry to dictionary."""
        return {
            "decomposers": list(self._decomposers.keys()),
            "planners": list(self._planners.keys()),
            "validators": list(self._validators.keys()),
            "analyzers": list(self._analyzers.keys()),
        }