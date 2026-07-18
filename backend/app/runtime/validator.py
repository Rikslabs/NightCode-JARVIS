"""Runtime validator."""

from typing import Any, Dict, Optional, Tuple

from .models import ExecutionRequest, ExecutionResult, RuntimeStatus
from .context import RuntimeContext


class RuntimeValidationError(Exception):
    """Runtime validation error."""
    pass


class RuntimeValidator:
    """Validates runtime requests, results, and execution context."""

    def __init__(self, allowed_actions: Optional[Dict[str, Any]] = None, required_params: Optional[Dict[str, list]] = None):
        self._allowed_actions = allowed_actions or {}
        self._required_params = required_params or {}

    def validate_request(self, request: ExecutionRequest) -> Tuple[bool, Optional[str]]:
        """Validate execution request. Returns (is_valid, error_message)."""
        if not request.request_id:
            return False, "request_id is required"
        if not request.action:
            return False, "action is required"
        if request.action in self._required_params:
            missing = [p for p in self._required_params[request.action] if p not in request.parameters]
            if missing:
                return False, f"Missing required parameters: {missing}"
        return True, None

    def validate_result(self, result: ExecutionResult) -> Tuple[bool, Optional[str]]:
        """Validate execution result. Returns (is_valid, error_message)."""
        if not result.request_id:
            return False, "request_id is required"
        if result.success and result.error is not None:
            return False, "Successful result must not have error"
        if not result.success and not result.error:
            return False, "Failed result must have error"
        return True, None

    def validate_context(self, context: RuntimeContext) -> Tuple[bool, Optional[str]]:
        """Validate execution context. Returns (is_valid, error_message)."""
        if not context.execution_id:
            return False, "execution_id is required"
        if not isinstance(context.status, RuntimeStatus):
            return False, "status must be a RuntimeStatus"
        return True, None

    def validate_or_raise(self, request: Optional[ExecutionRequest] = None, result: Optional[ExecutionResult] = None, context: Optional[RuntimeContext] = None) -> None:
        """Validate and raise RuntimeValidationError on failure."""
        if request is not None:
            valid, error = self.validate_request(request)
            if not valid:
                raise RuntimeValidationError(f"Invalid request: {error}")
        if result is not None:
            valid, error = self.validate_result(result)
            if not valid:
                raise RuntimeValidationError(f"Invalid result: {error}")
        if context is not None:
            valid, error = self.validate_context(context)
            if not valid:
                raise RuntimeValidationError(f"Invalid context: {error}")

    def set_allowed_actions(self, actions: Dict[str, Any]) -> None:
        """Set allowed actions."""
        self._allowed_actions = actions

    def set_required_params(self, params: Dict[str, list]) -> None:
        """Set required parameters per action."""
        self._required_params = params