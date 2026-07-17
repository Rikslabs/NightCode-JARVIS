"""Workflow validators."""
from dataclasses import dataclass, field
from typing import Any, Optional

from .models import Workflow, WorkflowContext
from .registry import get_action


@dataclass
class ValidationResult:
    """Result of workflow validation."""
    valid: bool
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            'valid': self.valid,
            'errors': list(self.errors),
        }


class WorkflowValidator:
    """Validates workflows and their components."""

    def validate_workflow(self, workflow: Workflow) -> ValidationResult:
        """Validate a workflow structure."""
        errors = []

        if not workflow.id:
            errors.append('Workflow must have an id')

        if not workflow.steps:
            errors.append('Workflow must contain steps')

        # Validate each step has a valid action reference
        for step in workflow.steps:
            if not step.id:
                errors.append(f'Step must have an id')
            if not step.name:
                errors.append(f'Step {step.id} must have a name')

        return ValidationResult(valid=len(errors) == 0, errors=errors)

    def validate_action(self, action_name: str) -> ValidationResult:
        """Validate an action exists in registry."""
        if not action_name:
            return ValidationResult(valid=False, errors=['Action name is required'])

        action = get_action(action_name)
        if action is None:
            return ValidationResult(valid=False, errors=[f'Action not found: {action_name}'])

        return ValidationResult(valid=True, errors=[])

    def validate_context(self, context: WorkflowContext) -> ValidationResult:
        """Validate workflow context."""
        errors = []

        if not context.workflow_id:
            errors.append('Context must have workflow_id')

        if not context.project_path:
            errors.append('Context must have project_path')

        if not context.user_request:
            errors.append('Context must have user_request')

        return ValidationResult(valid=len(errors) == 0, errors=errors)