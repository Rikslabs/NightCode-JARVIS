"""Runtime result collector."""

from typing import Any, Dict, List, Optional

from .models import ExecutionResult, RuntimeResult
from .context import RuntimeContext


class RuntimeCollector:
    """Collects and aggregates execution results."""

    def __init__(self):
        self._results: List[ExecutionResult] = []
        self._module_outputs: Dict[str, Any] = {}

    def collect(self, result: ExecutionResult) -> None:
        """Collect an execution result."""
        self._results.append(result)

    def collect_module_output(self, module_name: str, output: Any) -> None:
        """Aggregate module output."""
        self._module_outputs[module_name] = output

    def build_result(self, context: RuntimeContext) -> RuntimeResult:
        """Build final RuntimeResult from collected data."""
        success = all(r.success for r in self._results) if self._results else False
        errors = [r.error for r in self._results if r.error]
        return RuntimeResult(
            execution_id=context.execution_id,
            success=success,
            results=self._results,
            module_outputs=self._module_outputs,
            errors=errors,
        )

    def clear(self) -> None:
        """Clear collected results."""
        self._results.clear()
        self._module_outputs.clear()

    def get_results(self) -> List[ExecutionResult]:
        """Get all collected results."""
        return list(self._results)

    def get_module_outputs(self) -> Dict[str, Any]:
        """Get aggregated module outputs."""
        return dict(self._module_outputs)