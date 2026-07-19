"""Read-only project metadata analyzer."""

import os
from pathlib import Path
from typing import Mapping, Optional, Union

from .models import AnalysisResult, FileInfo, ProjectInfo


class ProjectAnalyzer:
    """Analyze a project tree without reading file contents."""

    def __init__(
        self,
        project_root: Union[str, Path],
        language_extensions: Optional[Mapping[str, str]] = None,
    ) -> None:
        self._project_root = Path(project_root).expanduser()
        self._language_extensions = dict(language_extensions or {
            ".py": "Python",
            ".js": "JavaScript",
            ".jsx": "JavaScript",
            ".ts": "TypeScript",
            ".tsx": "TypeScript",
            ".java": "Java",
            ".go": "Go",
            ".rs": "Rust",
            ".c": "C",
            ".h": "C",
            ".cc": "C++",
            ".cpp": "C++",
            ".cs": "C#",
            ".rb": "Ruby",
            ".php": "PHP",
            ".swift": "Swift",
            ".kt": "Kotlin",
            ".kts": "Kotlin",
        })

    @property
    def project_root(self) -> Path:
        return self._project_root

    def analyze(self) -> AnalysisResult:
        """Collect filesystem metadata for the configured project."""
        root = self._project_root
        if not root.exists():
            raise FileNotFoundError(f"Project path does not exist: {root}")
        if not root.is_dir():
            raise NotADirectoryError(f"Project path is not a directory: {root}")

        resolved_root = root.resolve()
        files = []
        languages = set()
        directory_count = 0
        top_level_modules = []

        for current, directory_names, file_names in os.walk(resolved_root, followlinks=False):
            current_path = Path(current)
            directory_names.sort()
            file_names.sort()
            directory_count += len(directory_names)

            if current_path == resolved_root:
                top_level_modules = [name for name in directory_names if not name.startswith(".")]

            for file_name in file_names:
                path = current_path / file_name
                try:
                    stat = path.stat()
                except OSError:
                    continue
                extension = path.suffix.lower()
                language = self._language_extensions.get(extension)
                if language is not None:
                    languages.add(language)
                    if current_path == resolved_root and not file_name.startswith("."):
                        top_level_modules.append(path.stem)
                files.append(FileInfo(
                    path=path,
                    name=file_name,
                    extension=extension,
                    size_bytes=stat.st_size,
                    language=language,
                ))

        project = ProjectInfo(
            name=resolved_root.name,
            root_path=resolved_root,
            detected_languages=sorted(languages),
            file_count=len(files),
            directory_count=directory_count,
            top_level_modules=sorted(set(top_level_modules)),
        )
        return AnalysisResult(project=project, files=files)
