"""Safe, read-only project file access."""

from pathlib import Path
from typing import List, Union


class FileReaderError(ValueError):
    """Base error for rejected file reads."""


class PathTraversalError(FileReaderError):
    """Raised when a path resolves outside the project root."""


class BinaryFileError(FileReaderError):
    """Raised when a file contains binary data."""


class FileEncodingError(FileReaderError):
    """Raised when a text file cannot be decoded with the configured encoding."""


class FileReader:
    """Read text files confined to a project root."""

    def __init__(self, project_root: Union[str, Path], encoding: str = "utf-8") -> None:
        self._project_root = Path(project_root).expanduser()
        self._encoding = encoding

    @property
    def project_root(self) -> Path:
        return self._project_root

    def read_text(self, path: Union[str, Path]) -> str:
        """Read an entire UTF-8 text file."""
        resolved = self._resolve(path)
        if not resolved.exists():
            raise FileNotFoundError(f"File does not exist: {path}")
        if not resolved.is_file():
            raise IsADirectoryError(f"Path is not a file: {path}")

        data = resolved.read_bytes()
        if self._is_binary(data):
            raise BinaryFileError(f"Binary files cannot be read: {path}")
        try:
            text = data.decode(self._encoding)
        except UnicodeDecodeError as exc:
            raise FileEncodingError(
                f"File is not valid {self._encoding} text: {path}"
            ) from exc
        return text.replace("\r\n", "\n").replace("\r", "\n")

    def read_lines(self, path: Union[str, Path], start: int, end: int) -> List[str]:
        """Read a one-based, inclusive range of text lines."""
        if start < 1 or end < start:
            raise ValueError("Line range must satisfy 1 <= start <= end")
        return self.read_text(path).splitlines()[start - 1:end]

    def exists(self, path: Union[str, Path]) -> bool:
        """Return whether a confined path exists."""
        return self._resolve(path).exists()

    def file_size(self, path: Union[str, Path]) -> int:
        """Return file size from filesystem metadata."""
        resolved = self._resolve(path)
        if not resolved.exists():
            raise FileNotFoundError(f"File does not exist: {path}")
        if not resolved.is_file():
            raise IsADirectoryError(f"Path is not a file: {path}")
        return resolved.stat().st_size

    def _resolve(self, path: Union[str, Path]) -> Path:
        root = self._validated_root()
        candidate = Path(path).expanduser()
        resolved = (candidate if candidate.is_absolute() else root / candidate).resolve()
        try:
            resolved.relative_to(root)
        except ValueError:
            raise PathTraversalError(f"Path is outside project root: {path}") from None
        return resolved

    def _validated_root(self) -> Path:
        if not self._project_root.exists():
            raise FileNotFoundError(f"Project path does not exist: {self._project_root}")
        if not self._project_root.is_dir():
            raise NotADirectoryError(f"Project path is not a directory: {self._project_root}")
        return self._project_root.resolve()

    @staticmethod
    def _is_binary(data: bytes) -> bool:
        return b"\x00" in data
