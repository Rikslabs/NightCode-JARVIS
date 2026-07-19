"""Typed models for project analysis."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass(frozen=True)
class FileInfo:
    """Filesystem metadata for a project file."""

    path: Path
    name: str
    extension: str
    size_bytes: int
    language: Optional[str] = None


@dataclass(frozen=True)
class ProjectInfo:
    """Summary metadata for a project."""

    name: str
    root_path: Path
    detected_languages: List[str] = field(default_factory=list)
    file_count: int = 0
    directory_count: int = 0
    top_level_modules: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class AnalysisResult:
    """Result returned by a project analyzer."""

    project: ProjectInfo
    files: List[FileInfo] = field(default_factory=list)


@dataclass(frozen=True)
class PythonSymbol:
    """A named symbol discovered in a Python source file."""

    name: str
    symbol_type: str
    relative_file_path: str
    line_number: int
    parent_symbol: Optional[str] = None
