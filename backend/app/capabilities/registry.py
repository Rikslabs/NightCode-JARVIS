"""Capability Registry - registers and looks up capabilities."""

import warnings
from typing import Any, Dict, List, Optional

from .models import Capability, CapabilityMetadata, RiskLevel


class CapabilityRegistry:
    """
    Registry for all capabilities in JARVIS.

    Each capability registers with:
    - name, description, category, provider
    - required inputs, outputs
    - risk level, priority, dependencies
    """

    def __init__(self):
        self._capabilities: Dict[str, Capability] = {}

    def register(
        self,
        capability_id: str,
        metadata: CapabilityMetadata,
    ) -> None:
        """
        Register a capability.

        Args:
            capability_id: Unique identifier for the capability.
            metadata: Metadata describing the capability.
        """
        if capability_id in self._capabilities:
            warnings.warn(f"Overwriting existing capability: {capability_id}")
        self._capabilities[capability_id] = Capability(
            id=capability_id, metadata=metadata
        )

    def get(self, capability_id: str) -> Optional[Capability]:
        """Get a capability by ID."""
        return self._capabilities.get(capability_id)

    def get_by_name(self, name: str) -> Optional[Capability]:
        """Get a capability by name."""
        for cap in self._capabilities.values():
            if cap.metadata.name == name:
                return cap
        return None

    def get_by_category(self, category: str) -> List[Capability]:
        """Get all capabilities in a category."""
        result = []
        for cap in self._capabilities.values():
            if cap.metadata.category == category:
                result.append(cap)
            elif cap.metadata.category.startswith(category + "/"):
                result.append(cap)
        return result

    def get_by_provider(self, provider: str) -> List[Capability]:
        """Get all capabilities provided by a tool/provider."""
        return [cap for cap in self._capabilities.values() if cap.metadata.provider == provider]

    def get_by_risk_level(self, risk: RiskLevel) -> List[Capability]:
        """Get all capabilities with a specific risk level."""
        return [cap for cap in self._capabilities.values() if cap.metadata.risk_level == risk]

    def list_all(self) -> Dict[str, Capability]:
        """List all capabilities."""
        return dict(self._capabilities)

    def get_all_capabilities(self) -> Dict[str, Capability]:
        """Get all capabilities (alias for compatibility)."""
        return dict(self._capabilities)

    def remove(self, capability_id: str) -> bool:
        """Remove a capability from the registry."""
        if capability_id in self._capabilities:
            del self._capabilities[capability_id]
            return True
        return False

    def clear(self) -> None:
        """Clear all capabilities."""
        self._capabilities.clear()

    def count(self) -> int:
        """Get count of registered capabilities."""
        return len(self._capabilities)

    def to_dict(self) -> Dict[str, Any]:
        """Convert registry to dictionary."""
        return {
            "capabilities": {k: v.to_dict() for k, v in self._capabilities.items()},
            "count": self.count(),
        }