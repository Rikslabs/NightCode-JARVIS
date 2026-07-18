"""Runtime execution pipeline."""

from typing import Any, Dict, List, Optional

from .context import RuntimeContext
from .coordinator import RuntimeCoordinator
from .models import ExecutionRequest, ExecutionResult, RuntimeStatus


class RuntimePipeline:
    """Builds the complete execution pipeline."""

    def __init__(self, coordinator: Optional[RuntimeCoordinator] = None):
        self._coordinator = coordinator or RuntimeCoordinator()
        self._results: List[ExecutionResult] = []

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        """Execute a single request through the pipeline."""
        if self._coordinator.get_context() is None:
            self._coordinator.start(request.request_id)

        result = self._coordinator.submit(request)
        self._results.append(result)
        return result

    def enqueue(self, request: ExecutionRequest) -> None:
        """Enqueue request for scheduled execution."""
        self._coordinator.enqueue(request)

    def execute_scheduled(self) -> List[ExecutionResult]:
        """Execute all scheduled requests."""
        results = self._coordinator.execute_all()
        self._results.extend(results)
        return results

    def register_module(self, name: str, module: Any) -> None:
        """Register a module in the pipeline."""
        self._coordinator.register_module(name, module)

    def start(self, execution_id: str, active_module: str = "") -> RuntimeContext:
        """Start execution lifecycle."""
        return self._coordinator.start(execution_id, active_module=active_module)

    def get_context(self) -> Optional[RuntimeContext]:
        """Get current execution context."""
        return self._coordinator.get_context()

    def get_status(self) -> RuntimeStatus:
        """Get current pipeline status."""
        return self._coordinator.get_status()

    def reset(self) -> None:
        """Reset pipeline state."""
        self._coordinator.reset()
        self._results.clear()

    def get_results(self) -> List[ExecutionResult]:
        """Get all execution results."""
        return list(self._results)