"""Runtime executor."""

from typing import Any, Dict, Optional, TYPE_CHECKING

from .context import RuntimeContext
from .models import ExecutionRequest, ExecutionResult, RuntimeStatus

if TYPE_CHECKING:
    from app.events.bus import EventBus
    from app.events.models import Event

from .events import (
    RuntimeStarted,
    RuntimeCompleted,
    RuntimeFailed,
    ExecutionStarted,
    ExecutionCompleted,
    ExecutionFailed,
)


class RuntimeExecutor:
    """Initializes and prepares execution."""

    def __init__(
        self,
        context: Optional[RuntimeContext] = None,
        event_bus: Optional["EventBus"] = None,
    ):
        self._context = context or RuntimeContext(execution_id="default")
        self._status: RuntimeStatus = RuntimeStatus.IDLE
        self._event_bus = event_bus

    def _publish_event(self, event_class, **kwargs) -> None:
        """Publish event if event bus is configured. Never fails execution."""
        if self._event_bus is None:
            return
        try:
            event = event_class(**kwargs)
            from app.events.models import Event
            event_obj = Event(
                event_id=event.event_id,
                event_type=event.event_type,
                source=event.source,
                payload=event.payload,
            )
            self._event_bus.publish(event_obj)
        except Exception:
            pass

    def initialize(self, execution_id: str, active_module: str = "") -> RuntimeContext:
        """Initialize execution context."""
        self._context = RuntimeContext(
            execution_id=execution_id,
            active_module=active_module,
        )
        self._context.status = RuntimeStatus.RUNNING
        self._status = RuntimeStatus.RUNNING

        self._publish_event(RuntimeStarted, execution_id=execution_id, module_name=active_module)
        return self._context

    def prepare(self, request: ExecutionRequest) -> ExecutionResult:
        """Prepare execution and return structured result."""
        self._context.status = RuntimeStatus.RUNNING
        self._status = RuntimeStatus.RUNNING

        self._publish_event(
            ExecutionStarted,
            execution_id=self._context.execution_id,
            request_id=request.request_id,
        )

        result = ExecutionResult(
            request_id=request.request_id,
            success=True,
            result={
                "status": "prepared",
                "action": request.action,
            },
        )

        self._context.status = RuntimeStatus.COMPLETED
        self._status = RuntimeStatus.COMPLETED

        self._publish_event(
            ExecutionCompleted,
            execution_id=self._context.execution_id,
            result=result.result,
        )

        return result

    def get_status(self) -> RuntimeStatus:
        """Get current executor status."""
        return self._status

    def get_context(self) -> RuntimeContext:
        """Get current execution context."""
        return self._context