"""Unified facade for coding assistant capabilities."""

from pathlib import Path
from typing import List, Optional, Union

from .analyzer import ProjectAnalyzer
from .explainer import CodeExplainer, FileExplanation, SymbolExplanation
from .explorer import RepositoryEntry, RepositoryExplorer
from .models import AnalysisResult, PythonSymbol
from .patch_generator import Explanation, PatchGenerator, PatchProposal
from .reader import FileReader
from .symbols import PythonSymbolIndex


class CodingService:
    """Delegate coding operations to injected, read-only components."""

    def __init__(
        self,
        analyzer: ProjectAnalyzer,
        explorer: RepositoryExplorer,
        symbol_index: PythonSymbolIndex,
        reader: FileReader,
        explainer: CodeExplainer,
        patch_generator: PatchGenerator,
    ) -> None:
        self._analyzer = analyzer
        self._explorer = explorer
        self._symbol_index = symbol_index
        self._reader = reader
        self._explainer = explainer
        self._patch_generator = patch_generator

    def analyze_project(self) -> AnalysisResult:
        return self._analyzer.analyze()

    def list_files(self, extension: Optional[str] = None) -> List[RepositoryEntry]:
        return self._explorer.list_files(extension)

    def find_symbols(
        self,
        name: Optional[str] = None,
        exact: bool = False,
    ) -> List[PythonSymbol]:
        if name is None:
            return self._symbol_index.index()
        return self._symbol_index.search(name, exact=exact)

    def read_file(self, path: Union[str, Path]) -> str:
        return self._reader.read_text(path)

    def explain_file(self, path: Union[str, Path]) -> FileExplanation:
        return self._explainer.explain_file(path)

    def explain_symbol(self, name: str) -> SymbolExplanation:
        return self._explainer.explain_symbol(name)

    def generate_patch(
        self,
        file_path: Union[str, Path],
        explanation: Explanation,
        user_instruction: Optional[str] = None,
        proposed_content: Optional[str] = None,
    ) -> PatchProposal:
        return self._patch_generator.generate(
            file_path,
            explanation,
            user_instruction,
            proposed_content,
        )
