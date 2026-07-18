"""Runtime recovery strategies."""

from typing import Any, Callable, Dict, Optional


class RecoveryStrategy:
    """Abstract recovery strategy."""

    def execute(self, context: Any, result: Any) -> Any:
        """Execute recovery logic."""
        raise NotImplementedError()


class RetryStrategy(RecoveryStrategy):
    """Retry failed execution."""

    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self._attempts: Dict[str, int] = {}

    def execute(self, context: Any, result: Any) -> Any:
        """Retry execution up to max_retries."""
        key = getattr(context, "execution_id", "default")
        self._attempts[key] = self._attempts.get(key, 0) + 1
        if self._attempts[key] > self.max_retries:
            return result
        return None


class SkipStrategy(RecoveryStrategy):
    """Skip failed execution."""

    def execute(self, context: Any, result: Any) -> Any:
        """Return original result, effectively skipping recovery."""
        return result


class AbortStrategy(RecoveryStrategy):
    """Abort execution on failure."""

    def execute(self, context: Any, result: Any) -> Any:
        """Raise error to abort."""
        raise RuntimeError("Execution aborted")


class FallbackStrategy(RecoveryStrategy):
    """Execute fallback logic."""

    def __init__(self, fallback_callable: Callable[[Any], Any]):
        self._fallback = fallback_callable

    def execute(self, context: Any, result: Any) -> Any:
        """Execute fallback callable."""
        return self._fallback(context)


class RuntimeRecovery:
    """Configurable recovery manager."""

    def __init__(self, result_failure_key: str = "success"):
        self._strategies: Dict[str, RecoveryStrategy] = {}
        self._result_failure_key = result_failure_key
        self._default_strategy = SkipStrategy()

    def register_strategy(self, name: str, strategy: RecoveryStrategy) -> None:
        """Register a recovery strategy by name."""
        self._strategies[name] = strategy

    def set_default_strategy(self, strategy: RecoveryStrategy) -> None:
        """Set default recovery strategy for unknown failures."""
        self._default_strategy = strategy

    def recover(self, context: Any, result: Any) -> Any:
        """Apply recovery strategy if result indicates failure."""
        if isinstance(result, dict) and result.get(self._result_failure_key, True):
            return result
        if hasattr(result, self._result_failure_key) and not getattr(result, self._result_failure_key):
            name = getattr(self, "_selected_strategy", None)
            strategy = self._strategies.get(name, self._default_strategy) if name else self._default_strategy
            return strategy.execute(context, result)
        return result

    def select_strategy(self, name: str) -> None:
        """Select strategy to use for next recovery."""
        if name not in self._strategies:
            raise KeyError(f"Unknown recovery strategy: {name}")
        self._selected_strategy = name

    def get_strategy(self, name: str) -> RecoveryStrategy:
        """Get registered strategy by name."""
        return self._strategies[name]

    def clear(self) -> None:
        """Clear strategies and attempts."""
        self._strategies.clear()
        self._selected_strategy = None