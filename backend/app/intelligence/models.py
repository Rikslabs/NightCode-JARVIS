"""Data models for the Intelligence Orchestrator."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class IntentType(Enum):
    """Types of intents that can be analyzed."""

    REVIEW_PROJECT = "review_project"
    PLAN_FEATURE = "plan_feature"
    PLAN_BUGFIX = "plan_bugfix"
    PLAN_REFACTOR = "plan_refactor"
    ANALYZE_CODE = "analyze_code"
    QUERY_KNOWLEDGE = "query_knowledge"
    EDIT_CODE = "edit_code"
    EXECUTE_WORKFLOW = "execute_workflow"
    UNKNOWN = "unknown"


class ComplexityLevel(Enum):
    """Complexity levels for intent analysis."""

    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


class RiskLevel(Enum):
    """Risk levels for execution planning."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ReasoningContext:
    """
    Context for the reasoning process.

    Contains all information needed to understand and execute a request.
    """

    request: str
    project_path: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary representation."""
        return {
            "request": self.request,
            "project_path": self.project_path,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "metadata": dict(self.metadata),
            "timestamp": self.timestamp,
        }


@dataclass
class IntentAnalysis:
    """
    Result of intent analysis.

    Represents the understood intent from a natural language request.
    """

    intent: IntentType
    confidence: float
    entities: List[str]
    complexity: ComplexityLevel
    risk: RiskLevel
    reasoning: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "intent": self.intent.value,
            "confidence": self.confidence,
            "entities": list(self.entities),
            "complexity": self.complexity.value,
            "risk": self.risk.value,
            "reasoning": self.reasoning,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IntentAnalysis":
        """Create IntentAnalysis from dictionary."""
        return cls(
            intent=IntentType(data["intent"]),
            confidence=data["confidence"],
            entities=list(data.get("entities", [])),
            complexity=ComplexityLevel(data["complexity"]),
            risk=RiskLevel(data["risk"]),
            reasoning=data.get("reasoning", ""),
            timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
        )


@dataclass
class ExecutionPlan:
    """
    Execution plan for an intent.

    Contains steps to be executed to fulfill the intent.
    """

    goal: str
    intent: IntentType
    steps: List[Dict[str, Any]]
    estimated_steps: int
    requires_workflow: bool
    requires_planning: bool
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "goal": self.goal,
            "intent": self.intent.value,
            "steps": list(self.steps),
            "estimated_steps": self.estimated_steps,
            "requires_workflow": self.requires_workflow,
            "requires_planning": self.requires_planning,
            "timestamp": self.timestamp,
        }


@dataclass
class ExecutionDecision:
    """
    Decision about which tool(s) to execute.
    """

    tool_name: str
    parameters: Dict[str, Any]
    confidence: float
    requires_multiple_steps: bool
    next_step_tool: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "tool_name": self.tool_name,
            "parameters": dict(self.parameters),
            "confidence": self.confidence,
            "requires_multiple_steps": self.requires_multiple_steps,
            "next_step_tool": self.next_step_tool,
        }


@dataclass
class ReasoningResult:
    """
    Complete result of the reasoning process.
    """

    intent_analysis: IntentAnalysis
    execution_plan: ExecutionPlan
    execution_decision: ExecutionDecision
    success: bool = True
    message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "intent_analysis": self.intent_analysis.to_dict(),
            "execution_plan": self.execution_plan.to_dict(),
            "execution_decision": self.execution_decision.to_dict(),
            "success": self.success,
            "message": self.message,
        }


@dataclass
class VerificationResult:
    """
    Result of verification after execution.
    """

    success: bool
    validation_errors: List[str] = field(default_factory=list)
    missing_outputs: List[str] = field(default_factory=list)
    tool_failures: List[str] = field(default_factory=list)
    partial_completion: bool = False
    retry_recommended: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "success": self.success,
            "validation_errors": list(self.validation_errors),
            "missing_outputs": list(self.missing_outputs),
            "tool_failures": list(self.tool_failures),
            "partial_completion": self.partial_completion,
            "retry_recommended": self.retry_recommended,
            "timestamp": self.timestamp,
        }