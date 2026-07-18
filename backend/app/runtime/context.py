"""Runtime context."""

from typing import Any, Dict, Optional

from .models import ExecutionContext, RuntimeStatus


class RuntimeContext:
    """Stores runtime execution information."""

    def __init__(self, execution_id: str, active_module: str = "", metadata: Optional[Dict[str, Any]] = None):
        self._context = ExecutionContext(
            execution_id=execution_id,
            active_module=active_module,
            metadata=metadata or {},
        )
        self._status: RuntimeStatus = RuntimeStatus.IDLE

    @property
    def execution_id(self) -> str:
        return self._context.execution_id

    @property
    def timestamp(self):
        return self._context.timestamp

    @property
    def active_module(self) -> str:
        return self._context.active_module

    @active_module.setter
    def active_module(self, value: str) -> None:
        self._context.active_module = value

    @property
    def metadata(self) -> Dict[str, Any]:
        return self._context.metadata

    @metadata.setter
    def metadata(self, value: Dict[str, Any]) -> None:
        self._context.metadata = value

    @property
    def status(self) -> RuntimeStatus:
        return self._status

    @status.setter
    def status(self, value: RuntimeStatus) -> None:
        self._status = value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "context": self._context.to_dict(),
            "status": self._status.value,
        }