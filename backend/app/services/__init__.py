"""Service Layer - The ONLY public backend interface."""
from .models import BaseRequest, BaseResponse, ServiceMetadata, ExecutionStatistics
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
from .exceptions import (
    ServiceException,
    ValidationException,
    WorkflowException,
    AuthorizationException,
    ToolException,
    ConfigurationException,
)
from .registry import ServiceRegistry
from .middleware import (
    Middleware, MiddlewarePipeline,
    LoggingMiddleware, TimingMiddleware, ValidationMiddleware, StatisticsMiddleware,
)
from .service import JarvisService

__all__ = [
    # Models
    'BaseRequest',
    'BaseResponse',
    'ServiceMetadata',
    'ExecutionStatistics',
    # Requests
    'AnalyzeProjectRequest',
    'ReviewProjectRequest',
    'PlanningRequest',
    'KnowledgeRequest',
    'EditingRequest',
    'WorkflowRequest',
    'StatusRequest',
    # Responses
    'SuccessResponse',
    'FailureResponse',
    'WorkflowResponse',
    'PlanningResponse',
    'KnowledgeResponse',
    'ReviewResponse',
    'EditingResponse',
    'StatusResponse',
    # Context
    'ServiceContext',
    'ServiceContextFactory',
    # Exceptions
    'ServiceException',
    'ValidationException',
    'WorkflowException',
    'AuthorizationException',
    'ToolException',
    'ConfigurationException',
    # Registry
    'ServiceRegistry',
    # Middleware
    'Middleware',
    'MiddlewarePipeline',
    'LoggingMiddleware',
    'TimingMiddleware',
    'ValidationMiddleware',
    'StatisticsMiddleware',
    # Service
    'JarvisService',
]