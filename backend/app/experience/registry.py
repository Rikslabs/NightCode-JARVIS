"""Experience Registry - registers experience components."""

import warnings
from typing import Any, Callable, Dict, List, Optional, Type


class ExperienceRegistry:
    """
    Registry for experience components.

    Allows future modules to plug into the system.
    """

    def __init__(self):
        self._retrievers: Dict[str, Any] = {}
        self._rankers: Dict[str, Any] = {}
        self._analyzers: Dict[str, Any] = {}
        self._matchers: Dict[str, Any] = {}

    def register_retriever(self, name: str, retriever: Any) -> None:
        """Register an experience retriever."""
        if name in self._retrievers:
            warnings.warn(f"Overwriting retriever: {name}")
        self._retrievers[name] = retriever

    def register_ranker(self, name: str, ranker: Any) -> None:
        """Register an experience ranker."""
        if name in self._rankers:
            warnings.warn(f"Overwriting ranker: {name}")
        self._rankers[name] = ranker

    def register_analyzer(self, name: str, analyzer: Any) -> None:
        """Register an experience analyzer."""
        if name in self._analyzers:
            warnings.warn(f"Overwriting analyzer: {name}")
        self._analyzers[name] = analyzer

    def register_matcher(self, name: str, matcher: Any) -> None:
        """Register an experience matcher."""
        if name in self._matchers:
            warnings.warn(f"Overwriting matcher: {name}")
        self._matchers[name] = matcher

    def get_retriever(self, name: str) -> Optional[Any]:
        """Get a registered retriever."""
        return self._retrievers.get(name)

    def get_ranker(self, name: str) -> Optional[Any]:
        """Get a registered ranker."""
        return self._rankers.get(name)

    def get_analyzer(self, name: str) -> Optional[Any]:
        """Get a registered analyzer."""
        return self._analyzers.get(name)

    def get_matcher(self, name: str) -> Optional[Any]:
        """Get a registered matcher."""
        return self._matchers.get(name)

    def list_retrievers(self) -> List[str]:
        """List all retriever names."""
        return list(self._retrievers.keys())

    def list_rankers(self) -> List[str]:
        """List all ranker names."""
        return list(self._rankers.keys())

    def list_analyzers(self) -> List[str]:
        """List all analyzer names."""
        return list(self._analyzers.keys())

    def list_matchers(self) -> List[str]:
        """List all matcher names."""
        return list(self._matchers.keys())

    def to_dict(self) -> Dict[str, Any]:
        """Convert registry to dictionary."""
        return {
            "retrievers": list(self._retrievers.keys()),
            "rankers": list(self._rankers.keys()),
            "analyzers": list(self._analyzers.keys()),
            "matchers": list(self._matchers.keys()),
        }