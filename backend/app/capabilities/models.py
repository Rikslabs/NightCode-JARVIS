"""Data models for the Capability Graph system."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class EdgeType(Enum):
    """Types of relationships between capabilities."""

    DEPENDS_ON = "depends_on"
    REQUIRES = "requires"
    EXTENDS = "extends"
    RELATED_TO = "related_to"


class RiskLevel(Enum):
    """Risk levels for capability execution."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class CapabilityMetadata:
    """Metadata for a capability."""

    name: str
    description: str
    category: str
    provider: str
    required_inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.LOW
    priority: int = 0
    dependencies: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "provider": self.provider,
            "required_inputs": list(self.required_inputs),
            "outputs": list(self.outputs),
            "risk_level": self.risk_level.value,
            "priority": self.priority,
            "dependencies": list(self.dependencies),
            "created_at": self.created_at,
        }


@dataclass
class Capability:
    """A capability that JARVIS can provide."""

    id: str
    metadata: CapabilityMetadata
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "metadata": self.metadata.to_dict(),
            "tags": list(self.tags),
        }


@dataclass
class CapabilityNode:
    """Node in the capability graph."""

    capability_id: str
    capability: Capability

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {"capability_id": self.capability_id, "capability": self.capability.to_dict()}


@dataclass
class CapabilityEdge:
    """Edge in the capability graph representing relationships."""

    source_id: str
    target_id: str
    edge_type: EdgeType
    weight: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "edge_type": self.edge_type.value,
            "weight": self.weight,
        }


@dataclass
class CapabilityGroup:
    """A group of related capabilities."""

    category: str
    capabilities: List[Capability] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "category": self.category,
            "capabilities": [c.to_dict() for c in self.capabilities],
        }


@dataclass
class CapabilityMatch:
    """A matched capability with confidence score."""

    capability: Capability
    confidence: float
    match_reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "capability": self.capability.to_dict(),
            "confidence": self.confidence,
            "match_reason": self.match_reason,
        }


@dataclass
class CapabilityResult:
    """Result of capability resolution."""

    capability_match: CapabilityMatch
    tool_name: str
    execution_path: List[str] = field(default_factory=list)
    success: bool = True
    message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "capability_match": self.capability_match.to_dict(),
            "tool_name": self.tool_name,
            "execution_path": list(self.execution_path),
            "success": self.success,
            "message": self.message,
        }