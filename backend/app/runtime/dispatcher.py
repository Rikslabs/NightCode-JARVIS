"""Runtime dispatcher."""

from typing import Any, Dict, Optional

from .context import RuntimeContext
from .models import ExecutionRequest, ExecutionResult, RuntimeStatus


class RuntimeDispatcher:
    """Routes execution requests to the correct module."""

    def __init__(self, module_registry: Optional[Dict[str, Any]] = None):
        self._modules = module_registry or {}

    def register_module(self, name: str, module: Any) -> None:
        """Register a module for dispatch."""
        self._modules[name] = module

    def dispatch(
        self, request: ExecutionRequest, context: RuntimeContext
    ) -> ExecutionResult:
        """Dispatch request to the appropriate module."""
        context.status = RuntimeStatus.RUNNING
        context.active_module = self._resolve_module(request.action)

        if not context.active_module:
            context.status = RuntimeStatus.FAILED
            return ExecutionResult(
                request_id=request.request_id,
                success=False,
                error=f"No module registered for action: {request.action}",
            )

        module = self._modules.get(context.active_module)
        if module is None:
            context.status = RuntimeStatus.FAILED
            return ExecutionResult(
                request_id=request.request_id,
                success=False,
                error=f"Module not found: {context.active_module}",
            )

        try:
            handler = getattr(module, "execute", None)
            if handler is None:
                context.status = RuntimeStatus.FAILED
                return ExecutionResult(
                    request_id=request.request_id,
                    success=False,
                    error=f"Module {context.active_module} has no execute method",
                )
            payload = handler(request.parameters)
            context.status = RuntimeStatus.COMPLETED
            return ExecutionResult(
                request_id=request.request_id,
                success=True,
                result=payload,
            )
        except Exception as exc:  # pragma: no cover - defensive
            context.status = RuntimeStatus.FAILED
            return ExecutionResult(
                request_id=request.request_id,
                success=False,
                error=str(exc),
            )

    def _resolve_module(self, action: str) -> Optional[str]:
        """Map action to module name."""
        mapping = {
            "open_url": "browser",
            "back": "browser",
            "forward": "browser",
            "click": "browser",
            "type": "browser",
            "scroll": "browser",
            "submit_form": "browser",
            "new_tab": "browser",
            "close_tab": "browser",
            "switch_tab": "browser",
            "list_tabs": "browser",
            "get_title": "browser",
            "get_text": "browser",
            "get_links": "browser",
            "get_metadata": "browser",
            "get_status": "browser",
            "upload_file": "browser",
            "start_download": "browser",
            "monitor_download": "browser",
            "cancel_download": "browser",
            "list_downloads": "browser",
            "move_mouse": "desktop",
            "press_key": "desktop",
            "get_window": "desktop",
            "list_windows": "desktop",
            "open_workspace": "vscode",
            "open_terminal": "vscode",
            "run_command": "vscode",
            "open_file": "vscode",
            "get_problems": "vscode",
            "run_build": "vscode",
        }
        return mapping.get(action)