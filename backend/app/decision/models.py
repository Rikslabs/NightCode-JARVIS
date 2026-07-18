"""Data models for Decision Engine."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class RiskLevel(Enum):
    """Risk level for decision."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DecisionFactor(Enum):
    """Factors considered in decision making."""
    COMPLEXITY = "complexity"
    CONFIDENCE = "confidence"
    SUCCESS_RATE = "success_rate"
    EXECUTION_COST = "execution_cost"
    RISK = "risk"
    DURATION = "duration"
    TOOL_AVAILABILITY = "tool_availability"
    POLICY_COMPLIANCE = "policy_compliance"


@dataclass
class Strategy:
    """A possible execution strategy."""
    id: str
    name: str
    description: str
    tool: str
    capability: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    estimated_duration: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tool": self.tool,
            "capability": self.capability,
            "parameters": dict(self.parameters),
            "confidence": self.confidence,
            "estimated_duration": self.estimated_duration,
        }


@dataclass
class Decision:
    """Internal decision object."""
    strategy: Strategy
    total_score: float
    factor_scores: Dict[str, float]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "strategy": self.strategy.to_dict(),
            "total_score": self.total_score,
            "factor_scores": dict(self.factor_scores),
        }


@dataclass
class RiskAssessment:
    """Risk assessment for a strategy."""
    level: RiskLevel
    factors: List[str] = field(default_factory=list)
    score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "level": self.level.value,
            "factors": list(self.factors),
            "score": self.score,
        }


@dataclass
class CostEstimate:
    """Cost estimate for a strategy."""
    estimated_seconds: float = 0.0
    estimated_resources: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "estimated_seconds": self.estimated_seconds,
            "estimated_resources": self.estimated_resources,
        }


@dataclass
class ExecutionDecision:
    """Final execution decision output."""
    chosen_strategy: Strategy
    confidence: float
    explanation: str
    rejected_alternatives: List[Dict[str, Any]] = field(default_factory=list)
    risk_assessment: RiskAssessment = field(default_factory=lambda: RiskAssessment(level=RiskLevel.LOW))
    estimated_duration: float = 0.0
    estimated_cost: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "chosen_strategy": self.chosen_strategy.to_dict(),
            "confidence": self.confidence,
            "explanation": self.explanation,
            "rejected_alternatives": list(self.rejected_alternatives),
            "risk_assessment": self.risk_assessment.to_dict(),
            "estimated_duration": self.estimated_duration,
            "estimated_cost": self.estimated_cost,
            "created_at": self.created_at,
        }