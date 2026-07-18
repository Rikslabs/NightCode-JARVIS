"""Runtime coordinator."""

from typing import Any, Dict, Optional

from .context import RuntimeContext
from .dispatcher import RuntimeDispatcher
from .executor import RuntimeExecutor
from .models import ExecutionRequest, ExecutionResult, RuntimeStatus
from .scheduler import RuntimeScheduler


class RuntimeCoordinator:
    """Coordinates runtime components."""

    def __init__(
        self,
        executor: Optional[RuntimeExecutor] = None,
        dispatcher: Optional[RuntimeDispatcher] = None,
        scheduler: Optional[RuntimeScheduler] = None,
    ):
        self._executor = executor or RuntimeExecutor()
        self._dispatcher = dispatcher or RuntimeDispatcher()
        self._scheduler = scheduler or RuntimeScheduler(self._executor)
        self._context: Optional[RuntimeContext] = None

    def start(self, execution_id: str, active_module: str = "") -> RuntimeContext:
        """Start execution lifecycle."""
        self._context = self._executor.initialize(execution_id, active_module=active_module)
        return self._context

    def submit(self, request: ExecutionRequest) -> ExecutionResult:
        """Submit request for execution."""
        if self._context is None:
            self._context = self._executor.initialize(request.request_id)

        result = self._dispatcher.dispatch(request, self._context)
        if result.success:
            self._context.status = RuntimeStatus.COMPLETED
        else:
            self._context.status = RuntimeStatus.FAILED
        self._context.active_module = result.error or self._context.active_module
        return result

    def enqueue(self, request: ExecutionRequest) -> None:
        """Enqueue request for later execution."""
        self._scheduler.enqueue(request)

    def execute_next(self) -> ExecutionResult:
        """Execute next queued request."""
        if self._context is None:
            raise RuntimeError("Execution not started")
        return self._scheduler.run_next(self._context)

    def execute_all(self) -> list:
        """Execute all queued requests."""
        if self._context is None:
            raise RuntimeError("Execution not started")
        return self._scheduler.run_all(self._context)

    def get_context(self) -> Optional[RuntimeContext]:
        """Get current execution context."""
        return self._context

    def get_status(self) -> RuntimeStatus:
        """Get current execution status."""
        if self._context is None:
            return RuntimeStatus.IDLE
        return self._context.status

    def reset(self) -> None:
        """Reset coordinator state."""
        self._scheduler.clear()
        self._context = None

    def register_module(self, name: str, module: Any) -> None:
        """Register module with dispatcher."""
        self._dispatcher.register_module(name, module)