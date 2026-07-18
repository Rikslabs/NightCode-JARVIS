"""Data models for Goal Decomposition Engine."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class GoalStatus(Enum):
    """Status of a goal or goal step."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"


class GoalStepType(Enum):
    """Type of goal step."""
    ANALYSIS = "analysis"
    ACTION = "action"
    VALIDATION = "validation"
    REVIEW = "review"
    DECISION = "decision"


@dataclass
class GoalDependency:
    """Represents a dependency between goal steps."""
    step_id: str
    depends_on_step_id: str
    required: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "step_id": self.step_id,
            "depends_on_step_id": self.depends_on_step_id,
            "required": self.required,
        }


@dataclass
class GoalStep:
    """A single step in a goal plan."""
    id: str
    description: str
    step_type: GoalStepType
    capability: str
    tool: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: GoalStatus = GoalStatus.PENDING
    confidence: float = 1.0
    priority: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "description": self.description,
            "step_type": self.step_type.value,
            "capability": self.capability,
            "tool": self.tool,
            "parameters": dict(self.parameters),
            "status": self.status.value,
            "confidence": self.confidence,
            "priority": self.priority,
        }


@dataclass
class Goal:
    """A goal to be decomposed and executed."""
    goal_id: str
    description: str
    steps: List[GoalStep] = field(default_factory=list)
    dependencies: List[GoalDependency] = field(default_factory=list)
    status: GoalStatus = GoalStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "goal_id": self.goal_id,
            "description": self.description,
            "steps": [s.to_dict() for s in self.steps],
            "dependencies": [d.to_dict() for d in self.dependencies],
            "status": self.status.value,
            "created_at": self.created_at,
        }


@dataclass
class GoalPlan:
    """Complete plan for goal execution."""
    goal: Goal
    execution_order: List[str]
    parallel_groups: List[List[str]]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "goal": self.goal.to_dict(),
            "execution_order": list(self.execution_order),
            "parallel_groups": [list(g) for g in self.parallel_groups],
        }


@dataclass
class GoalStatistics:
    """Statistics for goal analysis."""
    total_goals: int
    completed_goals: int
    failed_goals: int
    average_steps_per_goal: float
    most_common_tools: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "total_goals": self.total_goals,
            "completed_goals": self.completed_goals,
            "failed_goals": self.failed_goals,
            "average_steps_per_goal": self.average_steps_per_goal,
            "most_common_tools": list(self.most_common_tools),
        }


@dataclass
class GoalRecommendation:
    """Recommendation for goal improvement."""
    step_id: str
    reason: str
    suggested_action: str
    confidence: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "step_id": self.step_id,
            "reason": self.reason,
            "suggested_action": self.suggested_action,
            "confidence": self.confidence,
        }


@dataclass
class GoalValidationResult:
    """Result of goal validation."""
    valid: bool
    errors: List[str]
    warnings: List[str]
    cycle_detected: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "valid": self.valid,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "cycle_detected": self.cycle_detected,
        }