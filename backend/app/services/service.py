"""Jarvis Service - The ONLY public backend interface."""
from typing import Any, Optional
from datetime import datetime, timezone

from .requests import (
    AnalyzeProjectRequest,
    ReviewProjectRequest,
    PlanningRequest,
    KnowledgeRequest,
    EditingRequest,
    WorkflowRequest,
    StatusRequest,
)
from .responses import (
    SuccessResponse,
    FailureResponse,
    WorkflowResponse,
    PlanningResponse,
    KnowledgeResponse,
    ReviewResponse,
    EditingResponse,
    StatusResponse,
)
from .context import ServiceContext, ServiceContextFactory
from .middleware import MiddlewarePipeline, LoggingMiddleware, TimingMiddleware, ValidationMiddleware
from .exceptions import ServiceException, ValidationException, WorkflowException

# Import workflow components
from ..workflows import (
    WorkflowEngine, WorkflowState, WorkflowStep, Workflow, WorkflowContext,
    WorkflowExecutor, WorkflowHistory, WorkflowStorage, WorkflowMetrics,
    WorkflowScheduler, WorkflowPriority,
    register_handlers,
)


class JarvisService:
    """The ONLY public backend interface for JARVIS."""

    def __init__(self):
        # Initialize workflow components
        self._engine = WorkflowEngine()
        self._history = WorkflowHistory()
        self._storage = WorkflowStorage()
        self._metrics = WorkflowMetrics()
        self._executor = WorkflowExecutor(self._engine, history=self._history)
        self._scheduler = WorkflowScheduler(
            self._executor, self._storage, self._history, self._metrics
        )

        # Register handlers
        register_handlers()

        # Setup middleware pipeline
        self._pipeline = MiddlewarePipeline()
        self._pipeline.add(LoggingMiddleware())
        self._pipeline.add(TimingMiddleware())
        self._pipeline.add(ValidationMiddleware())

    def analyze_project(self, request: AnalyzeProjectRequest) -> ReviewResponse:
        """Analyze a project."""
        ctx = ServiceContextFactory.create_context(
            request_id=request.id,
            project_path=request.project_path,
        )
        ctx.metadata['method'] = 'analyze_project'

        def execute(ctx: ServiceContext, req: AnalyzeProjectRequest) -> ReviewResponse:
            # Create workflow for analysis
            steps = [WorkflowStep(
                id='analyze', name='Analyze Project',
                description='Analyze project structure',
                order=1,
            )]
            workflow = self._engine.create_workflow(
                'analyze_project',
                f'Analyze {request.project_path}',
                steps,
            )

            wf_ctx = WorkflowContext(
                workflow_id=workflow.id,
                project_path=request.project_path,
                user_request=f'Analyze project at {request.project_path}',
            )

            self._scheduler.submit(workflow, wf_ctx, priority=WorkflowPriority.HIGH)
            result = self._scheduler.start_next()

            return ReviewResponse(
                request_id=request.id,
                success=result.success if result else False,
                message=result.message if result else 'Analysis failed',
                data={'workflow_id': workflow.id} if result else None,
            )

        return self._pipeline.process(ctx, request, execute)

    def review_project(self, request: ReviewProjectRequest) -> ReviewResponse:
        """Review a project."""
        ctx = ServiceContextFactory.create_context(
            request_id=request.id,
            project_path=request.project_path,
        )
        ctx.metadata['method'] = 'review_project'

        def execute(ctx: ServiceContext, req: ReviewProjectRequest) -> ReviewResponse:
            steps = [WorkflowStep(
                id='review', name='Review Project',
                description='Review project for issues',
                order=1,
            )]
            workflow = self._engine.create_workflow(
                'review_project',
                f'Review {request.project_path}',
                steps,
            )

            wf_ctx = WorkflowContext(
                workflow_id=workflow.id,
                project_path=request.project_path,
                user_request=f'Review project at {request.project_path}',
            )

            self._scheduler.submit(workflow, wf_ctx, priority=WorkflowPriority.NORMAL)
            result = self._scheduler.start_next()

            return ReviewResponse(
                request_id=request.id,
                success=result.success if result else False,
                message=result.message if result else 'Review failed',
                data={'workflow_id': workflow.id} if result else None,
            )

        return self._pipeline.process(ctx, request, execute)

    def create_plan(self, request: PlanningRequest) -> PlanningResponse:
        """Create a plan."""
        ctx = ServiceContextFactory.create_context(
            request_id=request.id,
            project_path=request.project_path,
        )
        ctx.metadata['method'] = 'create_plan'

        def execute(ctx: ServiceContext, req: PlanningRequest) -> PlanningResponse:
            steps = [WorkflowStep(
                id='plan', name='Create Plan',
                description=f'Plan: {request.goal}',
                order=1,
            )]
            workflow = self._engine.create_workflow(
                'create_plan',
                f'Plan: {request.goal}',
                steps,
            )

            wf_ctx = WorkflowContext(
                workflow_id=workflow.id,
                project_path=request.project_path or '.',
                user_request=f'Create plan for: {request.goal}',
            )

            self._scheduler.submit(workflow, wf_ctx, priority=WorkflowPriority.NORMAL)
            result = self._scheduler.start_next()

            return PlanningResponse(
                request_id=request.id,
                success=result.success if result else False,
                message=result.message if result else 'Planning failed',
                data={'workflow_id': workflow.id} if result else None,
            )

        return self._pipeline.process(ctx, request, execute)

    def store_knowledge(self, request: KnowledgeRequest) -> KnowledgeResponse:
        """Store knowledge."""
        ctx = ServiceContextFactory.create_context(
            request_id=request.id,
            project_path=request.project_path,
        )
        ctx.metadata['method'] = 'store_knowledge'

        def execute(ctx: ServiceContext, req: KnowledgeRequest) -> KnowledgeResponse:
            steps = [WorkflowStep(
                id='knowledge', name='Store Knowledge',
                description=f'Store knowledge: {request.key}',
                order=1,
            )]
            workflow = self._engine.create_workflow(
                'store_knowledge',
                f'Store knowledge: {request.key}',
                steps,
            )

            wf_ctx = WorkflowContext(
                workflow_id=workflow.id,
                project_path=request.project_path or '.',
                user_request=f'Store knowledge for: {request.key}',
            )

            self._scheduler.submit(workflow, wf_ctx, priority=WorkflowPriority.LOW)
            result = self._scheduler.start_next()

            return KnowledgeResponse(
                request_id=request.id,
                success=result.success if result else False,
                message=result.message if result else 'Knowledge storage failed',
                data={'workflow_id': workflow.id} if result else None,
            )

        return self._pipeline.process(ctx, request, execute)

    def generate_patch_preview(self, request: EditingRequest) -> EditingResponse:
        """Generate patch preview."""
        ctx = ServiceContextFactory.create_context(
            request_id=request.id,
            workflow_id=request.workflow_id,
            project_path=request.project_path,
        )
        ctx.metadata['method'] = 'generate_patch_preview'

        def execute(ctx: ServiceContext, req: EditingRequest) -> EditingResponse:
            steps = [WorkflowStep(
                id='patch', name='Generate Patch',
                description='Generate patch preview',
                order=1,
            )]
            workflow = self._engine.create_workflow(
                'generate_patch',
                'Generate patch preview',
                steps,
            )

            wf_ctx = WorkflowContext(
                workflow_id=workflow.id,
                project_path=request.project_path or '.',
                user_request='Generate patch preview',
            )

            self._scheduler.submit(workflow, wf_ctx, priority=WorkflowPriority.NORMAL)
            result = self._scheduler.start_next()

            return EditingResponse(
                request_id=request.id,
                success=result.success if result else False,
                message=result.message if result else 'Patch generation failed',
                data={'workflow_id': workflow.id} if result else None,
            )

        return self._pipeline.process(ctx, request, execute)

    def validate_patch(self, request: EditingRequest) -> EditingResponse:
        """Validate a patch."""
        ctx = ServiceContextFactory.create_context(
            request_id=request.id,
            workflow_id=request.workflow_id,
            project_path=request.project_path,
        )
        ctx.metadata['method'] = 'validate_patch'

        def execute(ctx: ServiceContext, req: EditingRequest) -> EditingResponse:
            steps = [WorkflowStep(
                id='validate', name='Validate Patch',
                description='Validate patch',
                order=1,
            )]
            workflow = self._engine.create_workflow(
                'validate_patch',
                'Validate patch',
                steps,
            )

            wf_ctx = WorkflowContext(
                workflow_id=workflow.id,
                project_path=request.project_path or '.',
                user_request='Validate patch',
            )

            self._scheduler.submit(workflow, wf_ctx, priority=WorkflowPriority.NORMAL)
            result = self._scheduler.start_next()

            return EditingResponse(
                request_id=request.id,
                success=result.success if result else False,
                message=result.message if result else 'Patch validation failed',
                data={'workflow_id': workflow.id} if result else None,
            )

        return self._pipeline.process(ctx, request, execute)

    def execute_workflow(self, request: WorkflowRequest) -> WorkflowResponse:
        """Execute a workflow."""
        ctx = ServiceContextFactory.create_context(
            request_id=request.id,
            project_path=request.project_path,
        )
        ctx.metadata['method'] = 'execute_workflow'

        def execute(ctx: ServiceContext, req: WorkflowRequest) -> WorkflowResponse:
            steps = [WorkflowStep(
                id='execute', name='Execute Workflow',
                description=f'Execute: {request.workflow_type}',
                order=1,
            )]
            workflow = self._engine.create_workflow(
                request.workflow_type,
                f'Execute {request.workflow_type}',
                steps,
            )

            wf_ctx = WorkflowContext(
                workflow_id=workflow.id,
                project_path=request.project_path or '.',
                user_request=request.user_request or f'Execute {request.workflow_type}',
            )

            self._scheduler.submit(workflow, wf_ctx, priority=WorkflowPriority.NORMAL)
            result = self._scheduler.start_next()

            return WorkflowResponse(
                request_id=request.id,
                success=result.success if result else False,
                message=result.message if result else 'Workflow execution failed',
                workflow_id=workflow.id,
                status='completed' if result and result.success else 'failed',
            )

        return self._pipeline.process(ctx, request, execute)

    def workflow_status(self, request: StatusRequest) -> StatusResponse:
        """Get workflow status."""
        ctx = ServiceContextFactory.create_context(
            request_id=request.id,
        )
        ctx.metadata['method'] = 'workflow_status'

        def execute(ctx: ServiceContext, req: StatusRequest) -> StatusResponse:
            status = self._scheduler.active_workflow()
            return StatusResponse(
                request_id=request.id,
                success=True,
                message='Status retrieved',
                status='active' if status else 'idle',
                details={'active_workflow': status.to_dict() if status else None},
            )

        return self._pipeline.process(ctx, request, execute)

    def system_status(self, request: StatusRequest) -> StatusResponse:
        """Get system status."""
        ctx = ServiceContextFactory.create_context(
            request_id=request.id,
        )
        ctx.metadata['method'] = 'system_status'

        def execute(ctx: ServiceContext, req: StatusRequest) -> StatusResponse:
            stats = self._storage.statistics()
            metrics = self._metrics.summary()
            return StatusResponse(
                request_id=request.id,
                success=True,
                message='System status retrieved',
                status='healthy',
                details={
                    'storage': stats.to_dict(),
                    'metrics': metrics,
                },
            )

        return self._pipeline.process(ctx, request, execute)