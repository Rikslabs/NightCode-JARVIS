"""Runtime scheduler."""

from typing import Any, List

from .context import RuntimeContext
from .models import ExecutionRequest, ExecutionResult


class RuntimeScheduler:
    """Schedules execution steps sequentially."""

    def __init__(self, executor: Any):
        self._executor = executor
        self._queue: List[ExecutionRequest] = []

    def enqueue(self, request: ExecutionRequest) -> None:
        """Add request to execution queue."""
        self._queue.append(request)

    def dequeue(self) -> ExecutionRequest:
        """Get next request from queue."""
        if not self._queue:
            raise RuntimeError("Execution queue is empty")
        return self._queue.pop(0)

    def run_next(self, context: RuntimeContext) -> ExecutionResult:
        """Execute next queued request."""
        request = self.dequeue()
        return self._executor.prepare(request)

    def run_all(self, context: RuntimeContext) -> List[ExecutionResult]:
        """Execute all queued requests sequentially."""
        results: List[ExecutionResult] = []
        while self._queue:
            results.append(self.run_next(context))
        return results

    def clear(self) -> None:
        """Clear execution queue."""
        self._queue.clear()

    def size(self) -> int:
        """Get current queue size."""
        return len(self._queue)