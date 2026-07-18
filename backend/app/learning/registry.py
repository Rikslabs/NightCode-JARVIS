"""Registry for Learning Engine components."""

from typing import Any, Callable, Dict, Optional


class LearningRegistry:
    """
    Registry for learning engine components.

    Centralizes access to:
    - Engines
    - Optimizers
    - Knowledge stores
    - History managers
    - Feedback collectors
    """

    _instance: Optional["LearningRegistry"] = None

    def __init__(self):
        self._engines: Dict[str, Any] = {}
        self._optimizers: Dict[str, Any] = {}
        self._knowledge: Dict[str, Any] = {}
        self._histories: Dict[str, Any] = {}

    @classmethod
    def get_instance(cls) -> "LearningRegistry":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register_engine(self, name: str, engine: Any) -> None:
        """Register a learning engine."""
        self._engines[name] = engine

    def register_optimizer(self, name: str, optimizer: Any) -> None:
        """Register an optimizer."""
        self._optimizers[name] = optimizer

    def register_knowledge(self, name: str, knowledge: Any) -> None:
        """Register a knowledge store."""
        self._knowledge[name] = knowledge

    def register_history(self, name: str, history: Any) -> None:
        """Register a history manager."""
        self._histories[name] = history

    def get_engine(self, name: str = "default") -> Optional[Any]:
        """Get a learning engine."""
        return self._engines.get(name)

    def get_optimizer(self, name: str = "default") -> Optional[Any]:
        """Get an optimizer."""
        return self._optimizers.get(name)

    def get_knowledge(self, name: str = "default") -> Optional[Any]:
        """Get a knowledge store."""
        return self._knowledge.get(name)

    def get_history(self, name: str = "default") -> Optional[Any]:
        """Get a history manager."""
        return self._histories.get(name)

    def clear(self) -> None:
        """Clear all registered components."""
        self._engines.clear()
        self._optimizers.clear()
        self._knowledge.clear()
        self._histories.clear()

    def list_engines(self) -> list:
        """List registered engine names."""
        return list(self._engines.keys())

    def list_optimizers(self) -> list:
        """List registered optimizer names."""
        return list(self._optimizers.keys())

    def list_knowledge(self) -> list:
        """List registered knowledge names."""
        return list(self._knowledge.keys())

    def list_histories(self) -> list:
        """List registered history names."""
        return list(self._histories.keys())

    def to_dict(self) -> Dict[str, Any]:
        """Export registry state."""
        return {
            "engines": list(self._engines.keys()),
            "optimizers": list(self._optimizers.keys()),
            "knowledge": list(self._knowledge.keys()),
            "histories": list(self._histories.keys()),
        }