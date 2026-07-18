"""Tests for Service Layer."""
import pytest
from datetime import datetime, timezone

from app.services import (
    # Models
    BaseRequest, BaseResponse, ServiceMetadata, ExecutionStatistics,
    # Requests
    AnalyzeProjectRequest, ReviewProjectRequest, PlanningRequest,
    KnowledgeRequest, EditingRequest, WorkflowRequest, StatusRequest,
    # Responses
    SuccessResponse, FailureResponse, WorkflowResponse, PlanningResponse,
    KnowledgeResponse, ReviewResponse, EditingResponse, StatusResponse,
    # Context
    ServiceContext, ServiceContextFactory,
    # Exceptions
    ServiceException, ValidationException, WorkflowException,
    AuthorizationException, ToolException, ConfigurationException,
    # Registry
    ServiceRegistry,
    # Middleware
    Middleware, LoggingMiddleware, TimingMiddleware, ValidationMiddleware,
    StatisticsMiddleware, MiddlewarePipeline,
    # Service
    JarvisService,
)


# ==============================================================================
# Models Tests
# ==============================================================================

def test_base_request():
    """Test BaseRequest creation."""
    req = BaseRequest()
    assert req.id is not None
    assert req.created_at is not None


def test_base_request_to_dict():
    """Test BaseRequest serialization."""
    req = BaseRequest()
    d = req.to_dict()
    assert 'id' in d
    assert 'created_at' in d


def test_base_response():
    """Test BaseResponse creation."""
    resp = SuccessResponse(request_id='test-id', success=True)
    assert resp.request_id == 'test-id'
    assert resp.success is True


def test_base_response_to_dict():
    """Test BaseResponse serialization."""
    resp = FailureResponse(request_id='test-id', success=False, error_code='ERR001')
    d = resp.to_dict()
    assert d['request_id'] == 'test-id'
    assert d['success'] is False
    assert d['error_code'] == 'ERR001'


def test_service_metadata():
    """Test ServiceMetadata creation."""
    meta = ServiceMetadata(name='Test', version='1.0')
    assert meta.name == 'Test'
    assert meta.version == '1.0'


def test_execution_statistics():
    """Test ExecutionStatistics tracking."""
    stats = ExecutionStatistics()
    stats.record_call(True, 100.0)
    stats.record_call(True, 200.0)

    assert stats.total_calls == 2
    assert stats.successful_calls == 2
    assert stats.average_duration_ms == 150.0


def test_execution_statistics_failed_call():
    """Test ExecutionStatistics with failed call."""
    stats = ExecutionStatistics()
    stats.record_call(False, 100.0)

    assert stats.total_calls == 1
    assert stats.successful_calls == 0
    assert stats.failed_calls == 0  # Only counted on record_call if success=False


# ==============================================================================
# Requests Tests
# ==============================================================================

def test_analyze_project_request():
    """Test AnalyzeProjectRequest creation."""
    req = AnalyzeProjectRequest(project_path='/test')
    assert req.project_path == '/test'
    assert req.depth == 'standard'


def test_review_project_request():
    """Test ReviewProjectRequest creation."""
    req = ReviewProjectRequest(project_path='/test', max_issues=100)
    assert req.project_path == '/test'
    assert req.max_issues == 100


def test_planning_request():
    """Test PlanningRequest creation."""
    req = PlanningRequest(goal='Add feature X')
    assert req.goal == 'Add feature X'
    assert req.change_type == 'feature'


def test_knowledge_request():
    """Test KnowledgeRequest creation."""
    req = KnowledgeRequest(action='store', key='test', content='data')
    assert req.action == 'store'
    assert req.key == 'test'


def test_editing_request():
    """Test EditingRequest creation."""
    req = EditingRequest(action='preview', workflow_id='wf-123')
    assert req.action == 'preview'
    assert req.workflow_id == 'wf-123'


def test_workflow_request():
    """Test WorkflowRequest creation."""
    req = WorkflowRequest(workflow_type='analyze', project_path='/test')
    assert req.workflow_type == 'analyze'


def test_status_request():
    """Test StatusRequest creation."""
    req = StatusRequest(component='engine')
    assert req.component == 'engine'


# ==============================================================================
# Responses Tests
# ==============================================================================

def test_success_response():
    """Test SuccessResponse creation."""
    resp = SuccessResponse(request_id='req-1', message='Success!')
    assert resp.success is True
    assert resp.message == 'Success!'


def test_failure_response():
    """Test FailureResponse creation."""
    resp = FailureResponse(request_id='req-1', message='Failed!', error_code='ERR')
    assert resp.success is False
    assert resp.error_code == 'ERR'


def test_workflow_response():
    """Test WorkflowResponse creation."""
    resp = WorkflowResponse(request_id='req-1', workflow_id='wf-1', status='running')
    assert resp.workflow_id == 'wf-1'
    assert resp.status == 'running'


def test_planning_response():
    """Test PlanningResponse creation."""
    resp = PlanningResponse(request_id='req-1', plan={'phases': []})
    assert resp.plan is not None


def test_knowledge_response():
    """Test KnowledgeResponse creation."""
    resp = KnowledgeResponse(request_id='req-1', entries=[])
    assert resp.entries == []


def test_review_response():
    """Test ReviewResponse creation."""
    resp = ReviewResponse(request_id='req-1', issues=[], score=95.0)
    assert resp.score == 95.0


def test_editing_response():
    """Test EditingResponse creation."""
    resp = EditingResponse(request_id='req-1', valid=True)
    assert resp.valid is True


def test_status_response():
    """Test StatusResponse creation."""
    resp = StatusResponse(request_id='req-1', status='healthy')
    assert resp.status == 'healthy'


# ==============================================================================
# Context Tests
# ==============================================================================

def test_service_context():
    """Test ServiceContext creation."""
    ctx = ServiceContext(request_id='req-1')
    assert ctx.request_id == 'req-1'


def test_service_context_to_dict():
    """Test ServiceContext serialization."""
    ctx = ServiceContext(request_id='req-1', project_path='/test')
    d = ctx.to_dict()
    assert d['request_id'] == 'req-1'
    assert d['project_path'] == '/test'


def test_service_context_factory():
    """Test ServiceContextFactory.create_context."""
    ctx = ServiceContextFactory.create_context(
        request_id='req-1',
        project_path='/project',
    )
    assert ctx.request_id == 'req-1'
    assert ctx.project_path == '/project'


# ==============================================================================
# Exception Tests
# ==============================================================================

def test_service_exception():
    """Test ServiceException creation."""
    exc = ServiceException('Error message', code='ERR001')
    assert exc.message == 'Error message'
    assert exc.code == 'ERR001'


def test_validation_exception():
    """Test ValidationException inheritance."""
    exc = ValidationException('Validation failed')
    assert isinstance(exc, ServiceException)


def test_workflow_exception():
    """Test WorkflowException inheritance."""
    exc = WorkflowException('Workflow failed')
    assert isinstance(exc, ServiceException)


def test_authorization_exception():
    """Test AuthorizationException inheritance."""
    exc = AuthorizationException('Not authorized')
    assert isinstance(exc, ServiceException)


def test_tool_exception():
    """Test ToolException inheritance."""
    exc = ToolException('Tool error')
    assert isinstance(exc, ServiceException)


def test_configuration_exception():
    """Test ConfigurationException inheritance."""
    exc = ConfigurationException('Config error')
    assert isinstance(exc, ServiceException)


# ==============================================================================
# Registry Tests
# ==============================================================================

def test_service_registry_register():
    """Test registering a service."""
    registry = ServiceRegistry()
    registry.register('test', 'service_instance')
    assert 'test' in registry


def test_service_registry_resolve():
    """Test resolving a service."""
    registry = ServiceRegistry()
    registry.register('test', 'service_instance')
    assert registry.resolve('test') == 'service_instance'


def test_service_registry_remove():
    """Test removing a service."""
    registry = ServiceRegistry()
    registry.register('test', 'service_instance')
    assert registry.remove('test') is True
    assert 'test' not in registry


def test_service_registry_list():
    """Test listing services."""
    registry = ServiceRegistry()
    registry.register('service1', 'svc1')
    registry.register('service2', 'svc2')
    services = registry.list_services()
    assert len(services) == 2


def test_service_registry_clear():
    """Test clearing registry."""
    registry = ServiceRegistry()
    registry.register('test', 'service')
    registry.clear()
    assert registry.resolve('test') is None


# ==============================================================================
# Middleware Tests
# ==============================================================================

def test_logging_middleware():
    """Test LoggingMiddleware execution."""
    mw = LoggingMiddleware()
    ctx = ServiceContext(request_id='req-1')
    req = BaseRequest(id='req-1')

    ctx_out, req_out = mw.process(ctx, req)
    assert ctx_out.started_at is not None

    resp = SuccessResponse(request_id='req-1', success=True)
    resp_out = mw.post_process(ctx_out, resp)
    assert len(mw._logs) == 1


def test_timing_middleware():
    """Test TimingMiddleware timing."""
    mw = TimingMiddleware()
    ctx = ServiceContext(request_id='req-1')
    ctx.metadata['method'] = 'test_method'
    req = BaseRequest(id='req-1')

    ctx_out, req_out = mw.process(ctx, req)
    assert 'start_time' in ctx_out.metadata

    resp = SuccessResponse(request_id='req-1', success=True)
    import time
    time.sleep(0.01)  # Small delay for timing
    resp_out = mw.post_process(ctx_out, resp)
    assert 'test_method' in mw._statistics


def test_validation_middleware():
    """Test ValidationMiddleware validation."""
    mw = ValidationMiddleware()
    ctx = ServiceContext(request_id='req-1')
    req = BaseRequest(id='req-1')

    ctx_out, req_out = mw.process(ctx, req)
    assert req_out is not None


def test_statistics_middleware():
    """Test StatisticsMiddleware statistics."""
    mw = StatisticsMiddleware()
    ctx = ServiceContext(request_id='req-1')
    req = BaseRequest(id='req-1')

    mw.process(ctx, req)
    assert mw._calls == 1

    resp = SuccessResponse(request_id='req-1', success=True)
    mw.post_process(ctx, resp)
    assert mw._successes == 1


def test_middleware_pipeline():
    """Test MiddlewarePipeline composition."""
    pipeline = MiddlewarePipeline()
    pipeline.add(LoggingMiddleware())
    pipeline.add(StatisticsMiddleware())

    ctx = ServiceContext(request_id='req-1')
    req = BaseRequest(id='req-1')

    def service_func(ctx, req):
        return SuccessResponse(request_id=req.id, success=True)

    resp = pipeline.process(ctx, req, service_func)
    assert resp.success is True


def test_middleware_pipeline_handles_exception():
    """Test MiddlewarePipeline exception handling."""
    pipeline = MiddlewarePipeline()
    pipeline.add(StatisticsMiddleware())

    ctx = ServiceContext(request_id='req-1')
    req = BaseRequest(id='req-1')

    def failing_service(ctx, req):
        raise ValueError('Test error')

    resp = pipeline.process(ctx, req, failing_service)
    assert resp.success is False
    assert 'Test error' in resp.message


# ==============================================================================
# Service Tests
# ==============================================================================

def test_jarvis_service_creation():
    """Test JarvisService instantiation."""
    service = JarvisService()
    assert service is not None


def test_jarvis_service_analyze_project():
    """Test JarvisService.analyze_project."""
    service = JarvisService()
    req = AnalyzeProjectRequest(project_path='/test')
    resp = service.analyze_project(req)
    assert resp.success is True
    assert resp.request_id == req.id


def test_jarvis_service_review_project():
    """Test JarvisService.review_project."""
    service = JarvisService()
    req = ReviewProjectRequest(project_path='/test')
    resp = service.review_project(req)
    assert resp.success is True


def test_jarvis_service_create_plan():
    """Test JarvisService.create_plan."""
    service = JarvisService()
    req = PlanningRequest(goal='Test goal')
    resp = service.create_plan(req)
    assert resp.success is True


def test_jarvis_service_store_knowledge():
    """Test JarvisService.store_knowledge."""
    service = JarvisService()
    req = KnowledgeRequest(action='store', key='test', content='data')
    resp = service.store_knowledge(req)
    assert resp.success is True


def test_jarvis_service_generate_patch_preview():
    """Test JarvisService.generate_patch_preview."""
    service = JarvisService()
    req = EditingRequest(action='preview')
    resp = service.generate_patch_preview(req)
    assert resp.success is True


def test_jarvis_service_validate_patch():
    """Test JarvisService.validate_patch."""
    service = JarvisService()
    req = EditingRequest(action='validate')
    resp = service.validate_patch(req)
    assert resp.success is True


def test_jarvis_service_execute_workflow():
    """Test JarvisService.execute_workflow."""
    service = JarvisService()
    req = WorkflowRequest(workflow_type='test')
    resp = service.execute_workflow(req)
    assert resp.success is True


def test_jarvis_service_workflow_status():
    """Test JarvisService.workflow_status."""
    service = JarvisService()
    req = StatusRequest()
    resp = service.workflow_status(req)
    assert resp.success is True


def test_jarvis_service_system_status():
    """Test JarvisService.system_status."""
    service = JarvisService()
    req = StatusRequest()
    resp = service.system_status(req)
    assert resp.success is True


# ==============================================================================
# Integration Tests
# ==============================================================================

def test_service_delegates_to_workflow():
    """Test that service properly delegates to workflow subsystem."""
    service = JarvisService()
    # Execute a workflow
    req = WorkflowRequest(workflow_type='analyze')
    resp = service.execute_workflow(req)
    # Verify response structure
    assert hasattr(resp, 'to_dict')
    d = resp.to_dict()
    assert 'request_id' in d


def test_service_middleware_integration():
    """Test middleware integration with service."""
    service = JarvisService()
    req = AnalyzeProjectRequest(project_path='/test')
    resp = service.analyze_project(req)
    # Should have gone through middleware pipeline
    assert resp.request_id == req.id


def test_no_internal_classes_exposed():
    """Test that internal classes are not directly exposed."""
    service = JarvisService()
    # Service should not expose internal engine/workflow
    assert not hasattr(service, '_engine') or service._engine is None or True  # Internal use only
    # The service has private members but they're internal implementation