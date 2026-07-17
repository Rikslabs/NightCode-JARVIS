"""Workflow executor - orchestrates workflow step execution."""
from typing import Any, Optional
from datetime import datetime, timezone

from .states import WorkflowState
from .models import Workflow, WorkflowContext, WorkflowResult
from .engine import WorkflowEngine
from .validators import WorkflowValidator
from .events import WorkflowEvent, WorkflowEventType
from .history import WorkflowHistory


class WorkflowExecutor:
    """Executes workflow steps using registered actions."""

    def __init__(self, engine: WorkflowEngine, history: Optional[WorkflowHistory] = None):
        self._engine = engine
        self._validator = WorkflowValidator()
        self._history = history
        self._pending_approval: Optional[str] = None

    def _emit_event(
        self,
        workflow_id: str,
        event_type: WorkflowEventType,
        step_id: Optional[str] = None,
        message: str = '',
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Emit an event to history if available."""
        if self._history is not None:
            event = WorkflowEvent.create(
                workflow_id=workflow_id,
                event_type=event_type,
                step=step_id,
                message=message,
                metadata=metadata,
            )
            self._history.append_event(event)

    def execute(self, workflow: Workflow, context: WorkflowContext) -> Optional[WorkflowResult]:
        """Execute a workflow."""
        # Emit workflow created event
        self._emit_event(
            workflow_id=workflow.id,
            event_type=WorkflowEventType.WORKFLOW_CREATED,
            message=f'Workflow {workflow.name} created',
        )

        # Validate workflow
        wf_valid = self._validator.validate_workflow(workflow)
        if not wf_valid.valid:
            self._emit_event(
                workflow_id=workflow.id,
                event_type=WorkflowEventType.WORKFLOW_FAILED,
                message=f'Workflow validation failed',
            )
            return WorkflowResult(
                success=False,
                workflow_id=workflow.id,
                state=WorkflowState.FAILED,
                summary=f'Workflow validation failed: {wf_valid.errors}',
                errors=wf_valid.errors,
            )

        # Validate context
        ctx_valid = self._validator.validate_context(context)
        if not ctx_valid.valid:
            self._emit_event(
                workflow_id=workflow.id,
                event_type=WorkflowEventType.WORKFLOW_FAILED,
                message='Context validation failed',
            )
            return WorkflowResult(
                success=False,
                workflow_id=workflow.id,
                state=WorkflowState.FAILED,
                summary=f'Context validation failed: {ctx_valid.errors}',
                errors=ctx_valid.errors,
            )

        # Start workflow
        self._engine.start_workflow(workflow.id)
        self._emit_event(
            workflow_id=workflow.id,
            event_type=WorkflowEventType.WORKFLOW_STARTED,
            message=f'Workflow {workflow.name} started',
        )

        # Execute steps sequentially
        for step in sorted(workflow.steps, key=lambda s: s.order):
            result = self.execute_step(workflow, step, context)
            if not result.success:
                error_msg = result.errors[0] if result.errors else result.summary
                self._engine.fail_workflow(workflow.id, error=error_msg)
                self._emit_event(
                    workflow_id=workflow.id,
                    event_type=WorkflowEventType.WORKFLOW_FAILED,
                    message=f'Workflow failed at step {step.id}',
                )
                return result

        # Complete workflow
        self._engine.complete_workflow(workflow.id)
        self._emit_event(
            workflow_id=workflow.id,
            event_type=WorkflowEventType.WORKFLOW_COMPLETED,
            message='Workflow completed successfully',
        )
        return WorkflowResult(
            success=True,
            workflow_id=workflow.id,
            state=WorkflowState.COMPLETED,
            summary=f'Workflow completed successfully with {len(workflow.steps)} steps',
        )

    def execute_step(
        self,
        workflow: Workflow,
        step: Any,
        context: WorkflowContext,
    ) -> WorkflowResult:
        """Execute a single workflow step."""
        # Emit step started event
        self._emit_event(
            workflow_id=workflow.id,
            event_type=WorkflowEventType.STEP_STARTED,
            step_id=step.id,
            message=f'Step {step.id} started',
        )

        # Check if approval is required (placeholder - no real tool calls)
        action = step.metadata.get('action', '') if step.metadata else None
        if action and action.requires_approval and not self._has_approval(workflow.id):
            self._engine.update_step(workflow.id, step.order, WorkflowState.WAITING_APPROVAL)
            self._emit_event(
                workflow_id=workflow.id,
                event_type=WorkflowEventType.APPROVAL_REQUIRED,
                step_id=step.id,
                message='Approval required for step',
            )
            return WorkflowResult(
                success=False,
                workflow_id=workflow.id,
                state=WorkflowState.WAITING_APPROVAL,
                summary=f'Step {step.id} waiting for approval',
            )

        # Simulate step execution (no real tool calls per requirements)
        self._engine.update_step(
            workflow.id,
            step.order,
            WorkflowState.COMPLETED,
            result=f'Step {step.id} executed',
        )

        # Emit step completed event
        self._emit_event(
            workflow_id=workflow.id,
            event_type=WorkflowEventType.STEP_COMPLETED,
            step_id=step.id,
            message=f'Step {step.id} completed',
        )

        return WorkflowResult(
            success=True,
            workflow_id=workflow.id,
            state=WorkflowState.RUNNING,
            summary=f'Step {step.id} completed',
        )

    def pause_for_approval(self, workflow_id: str) -> bool:
        """Pause workflow for approval."""
        workflow = self._engine._workflows.get(workflow_id)
        if workflow is None:
            return False
        if workflow.state != WorkflowState.WAITING_APPROVAL:
            return False

        self._pending_approval = workflow_id
        return True

    def resume(self, workflow_id: str) -> bool:
        """Resume a paused workflow."""
        if self._pending_approval != workflow_id:
            return False

        workflow = self._engine._workflows.get(workflow_id)
        if workflow is None:
            return False

        self._pending_approval = None
        # Find next pending step
        for step in workflow.steps:
            if step.status == WorkflowState.WAITING_APPROVAL:
                self._engine.update_step(workflow.id, step.order, WorkflowState.RUNNING)
            elif step.status == WorkflowState.PENDING:
                return True

        return True

    def get_execution_status(self, workflow_id: str) -> Optional[dict[str, Any]]:
        """Get execution status of a workflow."""
        status = self._engine.get_status(workflow_id)
        if status is None:
            return None

        workflow = self._engine._workflows.get(workflow_id)
        if workflow is None:
            return None

        # Add step details
        status['steps'] = [
            {'id': s.id, 'name': s.name, 'status': s.status.value, 'order': s.order}
            for s in workflow.steps
        ]
        status['pending_approval'] = workflow.id in [self._pending_approval] if self._pending_approval else False

        return status

    def _has_approval(self, workflow_id: str) -> bool:
        """Check if workflow has approval (placeholder)."""
        return self._pending_approval == workflow_id