"""Coding assistant foundation."""

from .analyzer import ProjectAnalyzer
from .explorer import RepositoryEntry, RepositoryExplorer
from .explainer import CodeExplainer, FileExplanation, SymbolExplanation
from .models import AnalysisResult, FileInfo, ProjectInfo, PythonSymbol
from .patch_generator import PatchGenerator, PatchProposal
from .registry import AnalyzerRegistry
from .reader import (
    BinaryFileError,
    FileEncodingError,
    FileReader,
    FileReaderError,
    PathTraversalError,
)
from .symbols import PythonSymbolIndex
from .service import CodingService
from .safe_apply import ApplyResult, SafeApplyService

__all__ = [
    "ProjectInfo",
    "FileInfo",
    "AnalysisResult",
    "ProjectAnalyzer",
    "RepositoryEntry",
    "RepositoryExplorer",
    "AnalyzerRegistry",
    "PythonSymbol",
    "PythonSymbolIndex",
    "FileReader",
    "FileReaderError",
    "BinaryFileError",
    "FileEncodingError",
    "PathTraversalError",
    "CodeExplainer",
    "FileExplanation",
    "SymbolExplanation",
    "PatchGenerator",
    "PatchProposal",
    "CodingService",
    "ApplyResult",
    "SafeApplyService",
]
