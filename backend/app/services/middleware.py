"""Middleware pipeline for service layer."""
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Optional
import time

from .models import ExecutionStatistics
from .context import ServiceContext


class Middleware(ABC):
    """Base middleware class."""

    @abstractmethod
    def process(self, ctx: ServiceContext, request: Any) -> tuple[ServiceContext, Any]:
        """Process request before service call."""
        pass

    @abstractmethod
    def post_process(self, ctx: ServiceContext, response: Any) -> Any:
        """Process response after service call."""
        pass


class LoggingMiddleware(Middleware):
    """Logs all requests and responses."""

    def __init__(self):
        self._logs: list[dict[str, Any]] = []

    def process(self, ctx: ServiceContext, request: Any) -> tuple[ServiceContext, Any]:
        """Log the incoming request."""
        ctx.started_at = datetime.now(timezone.utc).isoformat()
        return ctx, request

    def post_process(self, ctx: ServiceContext, response: Any) -> Any:
        """Log the outgoing response."""
        self._logs.append({
            'request_id': ctx.request_id,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'response': response.to_dict() if hasattr(response, 'to_dict') else str(response),
        })
        return response


class TimingMiddleware(Middleware):
    """Times request execution."""

    def __init__(self):
        self._statistics: dict[str, ExecutionStatistics] = {}

    def process(self, ctx: ServiceContext, request: Any) -> tuple[ServiceContext, Any]:
        """Record start time."""
        ctx.metadata['start_time'] = time.time()
        return ctx, request

    def post_process(self, ctx: ServiceContext, response: Any) -> Any:
        """Record end time and update statistics."""
        start_time = ctx.metadata.get('start_time', time.time())
        duration_ms = (time.time() - start_time) * 1000

        method = ctx.metadata.get('method', 'unknown')
        if method not in self._statistics:
            self._statistics[method] = ExecutionStatistics()
        self._statistics[method].record_call(response.success, duration_ms)

        return response


class ValidationMiddleware(Middleware):
    """Validates requests."""

    def __init__(self):
        pass

    def process(self, ctx: ServiceContext, request: Any) -> tuple[ServiceContext, Any]:
        """Validate request."""
        if request is None:
            raise ValueError('Request cannot be None')
        return ctx, request

    def post_process(self, ctx: ServiceContext, response: Any) -> Any:
        """No post-processing for validation."""
        return response


class ExceptionTranslationMiddleware(Middleware):
    """Translates exceptions."""

    def __init__(self):
        pass

    def process(self, ctx: ServiceContext, request: Any) -> tuple[ServiceContext, Any]:
        """No pre-processing."""
        return ctx, request

    def post_process(self, ctx: ServiceContext, response: Any) -> Any:
        """No post-processing."""
        return response


class StatisticsMiddleware(Middleware):
    """Collects statistics."""

    def __init__(self):
        self._calls: int = 0
        self._successes: int = 0
        self._failures: int = 0

    def process(self, ctx: ServiceContext, request: Any) -> tuple[ServiceContext, Any]:
        """Increment call counter."""
        self._calls += 1
        return ctx, request

    def post_process(self, ctx: ServiceContext, response: Any) -> Any:
        """Update success/failure counters."""
        if response.success:
            self._successes += 1
        else:
            self._failures += 1
        return response


class MiddlewarePipeline:
    """Pipeline for middleware execution."""

    def __init__(self):
        self._middlewares: list[Middleware] = []

    def add(self, middleware: Middleware) -> None:
        """Add middleware to pipeline."""
        self._middlewares.append(middleware)

    def process(self, ctx: ServiceContext, request: Any, service_func: Any) -> Any:
        """Run through pipeline and execute service."""
        # Pre-process through all middlewares
        current_ctx = ctx
        current_request = request
        for middleware in self._middlewares:
            current_ctx, current_request = middleware.process(current_ctx, current_request)

        # Execute service
        try:
            response = service_func(current_ctx, current_request)
        except Exception as e:
            response = FailureResponse(
                request_id=ctx.request_id,
                success=False,
                message=str(e),
            )
            for middleware in reversed(self._middlewares):
                response = middleware.post_process(current_ctx, response)
            return response

        # Post-process through all middlewares in reverse
        for middleware in reversed(self._middlewares):
            response = middleware.post_process(current_ctx, response)

        return response


# Need to import FailureResponse for exception handling in middleware
from .responses import FailureResponse