"""Decision Registry - registers decision components for extensibility."""

import warnings
from typing import Any, Dict, List, Optional


class DecisionRegistry:
    """
    Registry for pluggable decision components.

    Allows future modules to register policies, scorers, etc.
    """

    def __init__(self):
        self._policies: Dict[str, Any] = {}
        self._scorers: Dict[str, Any] = {}
        self._validators: Dict[str, Any] = {}

    def register_policy(self, name: str, policy: Any) -> None:
        """Register a policy engine."""
        if name in self._policies:
            warnings.warn(f"Overwriting policy: {name}")
        self._policies[name] = policy

    def register_scorer(self, name: str, scorer: Any) -> None:
        """Register a decision scorer."""
        if name in self._scorers:
            warnings.warn(f"Overwriting scorer: {name}")
        self._scorers[name] = scorer

    def register_validator(self, name: str, validator: Any) -> None:
        """Register a decision validator."""
        if name in self._validators:
            warnings.warn(f"Overwriting validator: {name}")
        self._validators[name] = validator

    def get_policy(self, name: str) -> Optional[Any]:
        """Get a registered policy."""
        return self._policies.get(name)

    def get_scorer(self, name: str) -> Optional[Any]:
        """Get a registered scorer."""
        return self._scorers.get(name)

    def get_validator(self, name: str) -> Optional[Any]:
        """Get a registered validator."""
        return self._validators.get(name)

    def list_policies(self) -> List[str]:
        """List all registered policy names."""
        return list(self._policies.keys())

    def list_scorers(self) -> List[str]:
        """List all registered scorer names."""
        return list(self._scorers.keys())

    def list_validators(self) -> List[str]:
        """List all registered validator names."""
        return list(self._validators.keys())

    def to_dict(self) -> Dict[str, Any]:
        """Convert registry to dictionary."""
        return {
            "policies": list(self._policies.keys()),
            "scorers": list(self._scorers.keys()),
            "validators": list(self._validators.keys()),
        }