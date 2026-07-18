"""Learning Engine models."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.core.enums import RiskLevel, ExecutionStatus


@dataclass
class ExecutionHistory:
    """History of a single execution."""

    tool_name: str
    intent: str
    success: bool
    duration: float
    confidence: float
    risk: RiskLevel
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    capability_used: Optional[str] = None
    output_summary: Optional[str] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "intent": self.intent,
            "success": self.success,
            "duration": self.duration,
            "confidence": self.confidence,
            "risk": self.risk.value,
            "timestamp": self.timestamp,
            "capability_used": self.capability_used,
            "output_summary": self.output_summary,
            "error_message": self.error_message,
        }


@dataclass
class LearningRecord:
    """Record of learning from an execution."""

    execution_id: str
    tool_name: str
    success: bool
    duration: float
    confidence: float
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    lessons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "tool_name": self.tool_name,
            "success": self.success,
            "duration": self.duration,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "lessons": list(self.lessons),
        }


@dataclass
class LearningSummary:
    """Summary of learning patterns."""

    total_executions: int
    successful_executions: int
    failed_executions: int
    average_duration: float
    success_rate: float
    most_reliable_tools: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_executions": self.total_executions,
            "successful_executions": self.successful_executions,
            "failed_executions": self.failed_executions,
            "average_duration": self.average_duration,
            "success_rate": self.success_rate,
            "most_reliable_tools": list(self.most_reliable_tools),
        }


@dataclass
class OptimizationSuggestion:
    """Suggestion for improving execution strategies."""

    tool_name: str
    current_confidence: float
    suggested_confidence: float
    reason: str
    impact: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "current_confidence": self.current_confidence,
            "suggested_confidence": self.suggested_confidence,
            "reason": self.reason,
            "impact": self.impact,
        }


@dataclass
class FailurePattern:
    """Pattern of failure for learning."""

    pattern_id: str
    tool_name: str
    error_type: str
    occurrence_count: int
    last_occurrence: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern_id": self.pattern_id,
            "tool_name": self.tool_name,
            "error_type": self.error_type,
            "occurrence_count": self.occurrence_count,
            "last_occurrence": self.last_occurrence,
        }


@dataclass
class SuccessPattern:
    """Pattern of success for learning."""

    pattern_id: str
    tool_name: str
    confidence_level: float
    occurrence_count: int
    last_occurrence: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern_id": self.pattern_id,
            "tool_name": self.tool_name,
            "confidence_level": self.confidence_level,
            "occurrence_count": self.occurrence_count,
            "last_occurrence": self.last_occurrence,
        }


@dataclass
class Recommendation:
    """Learning-based recommendation."""

    tool_name: str
    confidence: float
    reasoning: str
    based_on_pattern: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "based_on_pattern": self.based_on_pattern,
        }


@dataclass
class LearningStatistics:
    """Statistics for the learning engine."""

    total_records: int
    total_analyses: int
    suggestions_generated: int
    patterns_identified: int
    last_updated: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_records": self.total_records,
            "total_analyses": self.total_analyses,
            "suggestions_generated": self.suggestions_generated,
            "patterns_identified": self.patterns_identified,
            "last_updated": self.last_updated,
        }