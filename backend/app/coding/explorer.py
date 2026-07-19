"""Read-only repository explorer."""

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Union


@dataclass(frozen=True)
class RepositoryEntry:
    """Lightweight filesystem metadata for a repository entry."""

    relative_path: str
    name: str
    extension: str
    size: int
    last_modified: datetime


class RepositoryExplorer:
    """List repository entries without opening or parsing files."""

    def __init__(self, project_root: Union[str, Path]) -> None:
        self._project_root = Path(project_root).expanduser()
        self._ignored_directories = {
            ".git",
            "__pycache__",
            ".pytest_cache",
            "node_modules",
            ".venv",
            "venv",
        }

    @property
    def project_root(self) -> Path:
        return self._project_root

    def list_files(self, extension: Optional[str] = None) -> List[RepositoryEntry]:
        """List file metadata, optionally filtered by extension."""
        root = self._validated_root()
        requested_extension = self._normalize_extension(extension)
        entries: List[RepositoryEntry] = []

        for current, directory_names, file_names in self._walk(root):
            current_path = Path(current)
            for file_name in file_names:
                path = current_path / file_name
                suffix = path.suffix.lower()
                if requested_extension is not None and suffix != requested_extension:
                    continue
                entry = self._entry(path, root, suffix)
                if entry is not None:
                    entries.append(entry)
        return sorted(entries, key=lambda item: item.relative_path)

    def list_directories(self) -> List[RepositoryEntry]:
        """List directory metadata, excluding the repository root."""
        root = self._validated_root()
        entries: List[RepositoryEntry] = []

        for current, directory_names, _ in self._walk(root):
            current_path = Path(current)
            for directory_name in directory_names:
                entry = self._entry(current_path / directory_name, root, "")
                if entry is not None:
                    entries.append(entry)
        return sorted(entries, key=lambda item: item.relative_path)

    def _validated_root(self) -> Path:
        if not self._project_root.exists():
            raise FileNotFoundError(f"Project path does not exist: {self._project_root}")
        if not self._project_root.is_dir():
            raise NotADirectoryError(f"Project path is not a directory: {self._project_root}")
        return self._project_root.resolve()

    def _walk(self, root: Path):
        for current, directory_names, file_names in os.walk(root, followlinks=False):
            directory_names[:] = sorted(
                name for name in directory_names
                if name not in self._ignored_directories
            )
            file_names.sort()
            yield current, directory_names, file_names

    def _entry(
        self,
        path: Path,
        root: Path,
        extension: str,
    ) -> Optional[RepositoryEntry]:
        try:
            metadata = path.stat()
        except OSError:
            return None
        return RepositoryEntry(
            relative_path=path.relative_to(root).as_posix(),
            name=path.name,
            extension=extension,
            size=metadata.st_size,
            last_modified=datetime.fromtimestamp(metadata.st_mtime, timezone.utc),
        )

    @staticmethod
    def _normalize_extension(extension: Optional[str]) -> Optional[str]:
        if extension is None:
            return None
        normalized = extension.lower()
        return normalized if normalized.startswith(".") else f".{normalized}"
