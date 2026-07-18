"""Data models for the Experience layer."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class ExperienceRecord:
    """A single execution experience record."""

    id: str
    goal: str
    capability_id: str
    tool_name: str
    workflow: Optional[str]
    duration_ms: float
    success: bool
    result: Dict[str, Any]
    failure_reason: Optional[str]
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "goal": self.goal,
            "capability_id": self.capability_id,
            "tool_name": self.tool_name,
            "workflow": self.workflow,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "result": dict(self.result),
            "failure_reason": self.failure_reason,
            "timestamp": self.timestamp,
        }


@dataclass
class ExperienceSummary:
    """Summary of experiences for a capability or tool."""

    capability_id: str
    tool_name: str
    total_executions: int
    successful_executions: int
    failed_executions: int
    success_rate: float
    average_duration_ms: float
    last_execution: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "capability_id": self.capability_id,
            "tool_name": self.tool_name,
            "total_executions": self.total_executions,
            "successful_executions": self.successful_executions,
            "failed_executions": self.failed_executions,
            "success_rate": self.success_rate,
            "average_duration_ms": self.average_duration_ms,
            "last_execution": self.last_execution,
        }


@dataclass
class ExperienceMatch:
    """A matched experience with confidence score."""

    record: ExperienceRecord
    confidence: float
    similarity_score: float
    match_reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "record": self.record.to_dict(),
            "confidence": self.confidence,
            "similarity_score": self.similarity_score,
            "match_reason": self.match_reason,
        }


@dataclass
class ExperienceScore:
    """Scoring details for an experience."""

    record_id: str
    success_score: float
    recency_score: float
    frequency_score: float
    duration_score: float
    overall_score: float
    factors: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "record_id": self.record_id,
            "success_score": self.success_score,
            "recency_score": self.recency_score,
            "frequency_score": self.frequency_score,
            "duration_score": self.duration_score,
            "overall_score": self.overall_score,
            "factors": dict(self.factors),
        }


@dataclass
class ExperienceStatistics:
    """Aggregated statistics for the experience layer."""

    total_records: int
    total_successful: int
    total_failed: int
    overall_success_rate: float
    tool_statistics: Dict[str, ExperienceSummary]
    capability_statistics: Dict[str, ExperienceSummary]
    average_duration_ms: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "total_records": self.total_records,
            "total_successful": self.total_successful,
            "total_failed": self.total_failed,
            "overall_success_rate": self.overall_success_rate,
            "tool_statistics": {k: v.to_dict() for k, v in self.tool_statistics.items()},
            "capability_statistics": {k: v.to_dict() for k, v in self.capability_statistics.items()},
            "average_duration_ms": self.average_duration_ms,
        }


@dataclass
class ExperienceContext:
    """Context for experience-based reasoning."""

    goal: str
    project_path: Optional[str]
    user_id: Optional[str]
    capabilities_used: List[str]
    tools_used: List[str]
    previous_executions: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "goal": self.goal,
            "project_path": self.project_path,
            "user_id": self.user_id,
            "capabilities_used": list(self.capabilities_used),
            "tools_used": list(self.tools_used),
            "previous_executions": list(self.previous_executions),
        }


@dataclass
class ExperienceRecommendation:
    """Recommendation based on historical experiences."""

    tool_name: str
    capability_id: str
    confidence: float
    reason: str
    based_on_experiences: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "tool_name": self.tool_name,
            "capability_id": self.capability_id,
            "confidence": self.confidence,
            "reason": self.reason,
            "based_on_experiences": list(self.based_on_experiences),
        }