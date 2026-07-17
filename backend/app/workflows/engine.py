"""Workflow engine for state management."""
import uuid
from typing import Any, Optional
from datetime import datetime, timezone

from .states import WorkflowState
from .models import Workflow, WorkflowStep, WorkflowContext, WorkflowResult


class WorkflowEngine:
    """Manages workflow lifecycle and state transitions."""

    def __init__(self):
        self._workflows: dict[str, Workflow] = {}

    def create_workflow(
        self,
        name: str,
        description: str,
        steps: list[WorkflowStep],
        project_path: str = '',
        user_request: str = '',
    ) -> Workflow:
        """Create a new workflow with given steps."""
        workflow_id = f'{name}_{uuid.uuid4().hex[:8]}'
        workflow = Workflow(
            id=workflow_id,
            name=name,
            description=description,
            steps=steps,
            state=WorkflowState.PENDING,
        )
        self._workflows[workflow_id] = workflow
        return workflow

    def start_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Start a workflow execution."""
        workflow = self._workflows.get(workflow_id)
        if workflow is None:
            return None

        workflow.state = WorkflowState.RUNNING
        if workflow.steps:
            workflow.current_step = 0
            workflow.steps[0].status = WorkflowState.RUNNING

        return workflow

    def update_step(
        self,
        workflow_id: str,
        step_order: int,
        status: WorkflowState,
        result: Optional[str] = None,
        error: Optional[str] = None,
    ) -> Optional[WorkflowStep]:
        """Update a step's status and result."""
        workflow = self._workflows.get(workflow_id)
        if workflow is None:
            return None

        step = next((s for s in workflow.steps if s.order == step_order), None)
        if step is None:
            return None

        step.status = status
        step.result = result
        step.error = error

        # Update workflow current_step if this step is done
        if status in (WorkflowState.COMPLETED, WorkflowState.FAILED, WorkflowState.ROLLED_BACK):
            # Find next pending step
            next_step = next(
                (s for s in workflow.steps if s.order > step_order and s.status == WorkflowState.PENDING),
                None
            )
            if next_step is not None:
                workflow.current_step = next_step.order
            else:
                # All steps done, update workflow state
                if status == WorkflowState.FAILED:
                    workflow.state = WorkflowState.FAILED
                else:
                    workflow.state = WorkflowState.COMPLETED
                workflow.completed_at = datetime.now(timezone.utc).isoformat()

        return step

    def complete_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Mark workflow as completed."""
        workflow = self._workflows.get(workflow_id)
        if workflow is None:
            return None

        workflow.state = WorkflowState.COMPLETED
        workflow.completed_at = datetime.now(timezone.utc).isoformat()

        # Mark all remaining pending steps as completed
        for step in workflow.steps:
            if step.status == WorkflowState.PENDING:
                step.status = WorkflowState.COMPLETED

        return workflow

    def fail_workflow(self, workflow_id: str, error: Optional[str] = None) -> Optional[Workflow]:
        """Mark workflow as failed."""
        workflow = self._workflows.get(workflow_id)
        if workflow is None:
            return None

        workflow.state = WorkflowState.FAILED
        workflow.completed_at = datetime.now(timezone.utc).isoformat()

        if workflow.current_step is not None:
            step = next(
                (s for s in workflow.steps if s.order == workflow.current_step),
                None
            )
            if step is not None:
                step.status = WorkflowState.FAILED
                step.error = error

        return workflow

    def rollback_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Mark workflow as rolled back."""
        workflow = self._workflows.get(workflow_id)
        if workflow is None:
            return None

        workflow.state = WorkflowState.ROLLED_BACK
        workflow.completed_at = datetime.now(timezone.utc).isoformat()

        # Mark all steps as rolled back
        for step in workflow.steps:
            step.status = WorkflowState.ROLLED_BACK

        return workflow

    def get_status(self, workflow_id: str) -> Optional[dict[str, Any]]:
        """Get workflow status as dictionary."""
        workflow = self._workflows.get(workflow_id)
        if workflow is None:
            return None

        return {
            'workflow_id': workflow.id,
            'name': workflow.name,
            'state': workflow.state.value,
            'current_step': workflow.current_step,
            'total_steps': len(workflow.steps),
            'created_at': workflow.created_at,
            'completed_at': workflow.completed_at,
        }