"""Workflow action definitions."""
from enum import Enum
from dataclasses import dataclass, field
from typing import Any


class WorkflowAction(Enum):
    """Enumeration of available workflow actions."""
    ANALYZE_PROJECT = 'analyze_project'
    RUN_REVIEW = 'run_review'
    CREATE_PLAN = 'create_plan'
    GENERATE_PATCH = 'generate_patch'
    VALIDATE_PATCH = 'validate_patch'
    APPLY_PATCH = 'apply_patch'
    RUN_TESTS = 'run_tests'
    STORE_KNOWLEDGE = 'store_knowledge'


@dataclass
class ActionDefinition:
    """Definition of a workflow action."""
    name: str
    description: str
    requires_approval: bool = False
    risk_level: str = 'medium'
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert action definition to dictionary."""
        return {
            'name': self.name,
            'description': self.description,
            'requires_approval': self.requires_approval,
            'risk_level': self.risk_level,
            'metadata': dict(self.metadata),
        }