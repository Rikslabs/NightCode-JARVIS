"""Instance-scoped analyzer registry."""

from typing import Dict, List, Optional

from .analyzer import ProjectAnalyzer
from .explorer import RepositoryExplorer


class AnalyzerRegistry:
    """Register and retrieve project analyzers by name."""

    def __init__(self) -> None:
        self._analyzers: Dict[str, ProjectAnalyzer] = {}
        self._explorers: Dict[str, RepositoryExplorer] = {}

    def register(self, name: str, analyzer: ProjectAnalyzer) -> None:
        if not name:
            raise ValueError("Analyzer name is required")
        self._analyzers[name] = analyzer

    def unregister(self, name: str) -> bool:
        return self._analyzers.pop(name, None) is not None

    def get(self, name: str) -> Optional[ProjectAnalyzer]:
        return self._analyzers.get(name)

    def list(self) -> List[str]:
        return list(self._analyzers)

    def register_explorer(self, name: str, explorer: RepositoryExplorer) -> None:
        if not name:
            raise ValueError("Explorer name is required")
        self._explorers[name] = explorer

    def unregister_explorer(self, name: str) -> bool:
        return self._explorers.pop(name, None) is not None

    def get_explorer(self, name: str) -> Optional[RepositoryExplorer]:
        return self._explorers.get(name)

    def list_explorers(self) -> List[str]:
        return list(self._explorers)
