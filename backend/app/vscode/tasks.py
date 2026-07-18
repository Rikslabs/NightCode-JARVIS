"""Task controller for VS Code."""

from typing import Optional

from .models import VSTaskAction, VSActionResult


class TaskController:
    """Controls VS Code task operations."""

    def __init__(self):
        self._tasks: dict = {
            "build": {"label": "build", "type": "shell", "command": "npm run build"},
            "test": {"label": "test", "type": "shell", "command": "npm test"},
        }
        self._last_task_result: Optional[dict] = None

    def run_build(self) -> VSActionResult:
        """Run build task (metadata only)."""
        task = self._tasks.get("build", {})
        self._last_task_result = {"status": "completed", "task": "build"}
        return VSActionResult(
            success=True,
            action=VSTaskAction.BUILD.value,
            message="Build task executed",
            data=self._last_task_result,
        )

    def run_test(self) -> VSActionResult:
        """Run test task (metadata only)."""
        task = self._tasks.get("test", {})
        self._last_task_result = {"status": "completed", "task": "test"}
        return VSActionResult(
            success=True,
            action=VSTaskAction.TEST.value,
            message="Test task executed",
            data=self._last_task_result,
        )

    def run_task(self, task_name: str) -> VSActionResult:
        """Run a configured task (metadata only)."""
        task = self._tasks.get(task_name)
        if not task:
            return VSActionResult(
                success=False,
                action=VSTaskAction.RUN.value,
                message=f"Task not found: {task_name}",
            )
        self._last_task_result = {"status": "completed", "task": task_name}
        return VSActionResult(
            success=True,
            action=VSTaskAction.RUN.value,
            message=f"Task executed: {task_name}",
            data=self._last_task_result,
        )

    def wait_for_completion(self, task_name: str, timeout: int = 30000) -> VSActionResult:
        """Wait for task completion (metadata only)."""
        return VSActionResult(
            success=True,
            action=VSTaskAction.RUN.value,
            message=f"Task completed: {task_name}",
            data={"status": "success"},
        )