"""Approved, root-confined patch application."""

import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Union

from .patch_generator import PatchProposal


@dataclass(frozen=True)
class ApplyResult:
    """Outcome of a safe patch application request."""

    success: bool
    applied: bool
    backup_path: Optional[str]
    target_file: str
    message: str


class SafeApplyService:
    """Validate and apply approved unified diffs inside a project root."""

    def __init__(self, project_root: Union[str, Path]) -> None:
        self._project_root = Path(project_root).expanduser()

    def apply(self, proposal: PatchProposal, approval: bool) -> ApplyResult:
        """Apply an approved proposal after fully validating its diff."""
        if not approval:
            return ApplyResult(
                success=True,
                applied=False,
                backup_path=None,
                target_file=proposal.target_file,
                message="Patch was not applied because approval was denied.",
            )

        try:
            target = self._resolve_target(proposal.target_file)
        except (FileNotFoundError, NotADirectoryError, ValueError) as exc:
            return self._failure(proposal.target_file, str(exc))
        if not target.exists() or not target.is_file():
            return self._failure(proposal.target_file, "Target file does not exist.")

        try:
            original = target.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            return self._failure(proposal.target_file, f"Target file could not be read as UTF-8: {exc}")

        try:
            updated = self._apply_diff(
                original,
                proposal.unified_diff,
                Path(proposal.target_file).as_posix(),
            )
        except ValueError as exc:
            return self._failure(proposal.target_file, f"Invalid unified diff: {exc}")

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup = target.with_name(f"{target.name}.backup-{timestamp}")
        try:
            shutil.copy2(target, backup)
            target.write_bytes(updated.encode("utf-8"))
        except OSError as exc:
            if backup.exists():
                try:
                    shutil.copy2(backup, target)
                except OSError:
                    pass
            return ApplyResult(
                success=False,
                applied=False,
                backup_path=backup.relative_to(self._project_root.resolve()).as_posix()
                if backup.exists() else None,
                target_file=proposal.target_file,
                message=f"Patch could not be applied: {exc}",
            )

        if not target.exists():
            return ApplyResult(
                success=False,
                applied=False,
                backup_path=backup.relative_to(self._project_root.resolve()).as_posix(),
                target_file=proposal.target_file,
                message="Target file was not present after applying the patch.",
            )
        return ApplyResult(
            success=True,
            applied=True,
            backup_path=backup.relative_to(self._project_root.resolve()).as_posix(),
            target_file=proposal.target_file,
            message="Patch applied successfully.",
        )

    def _resolve_target(self, target_file: str) -> Path:
        if not self._project_root.exists():
            raise FileNotFoundError(f"Project path does not exist: {self._project_root}")
        if not self._project_root.is_dir():
            raise NotADirectoryError(f"Project path is not a directory: {self._project_root}")
        root = self._project_root.resolve()
        candidate = Path(target_file)
        resolved = (candidate if candidate.is_absolute() else root / candidate).resolve()
        try:
            resolved.relative_to(root)
        except ValueError:
            raise ValueError("Target file is outside the project root.") from None
        return resolved

    @classmethod
    def _apply_diff(cls, original: str, diff: str, target_file: str) -> str:
        lines = diff.splitlines(keepends=True)
        if len(lines) < 3 or not lines[0].startswith("--- ") or not lines[1].startswith("+++ "):
            raise ValueError("missing file headers")
        if cls._header_path(lines[0]) != f"a/{target_file}":
            raise ValueError("source header does not match target file")
        if cls._header_path(lines[1]) != f"b/{target_file}":
            raise ValueError("destination header does not match target file")

        source = original.splitlines(keepends=True)
        output: List[str] = []
        source_index = 0
        index = 2
        hunk_count = 0

        while index < len(lines):
            header = lines[index].rstrip("\r\n")
            match = re.fullmatch(
                r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@.*",
                header,
            )
            if match is None:
                raise ValueError("invalid hunk header")
            old_start = int(match.group(1))
            old_count = int(match.group(2) or "1")
            new_count = int(match.group(4) or "1")
            hunk_start = old_start if old_count == 0 else max(old_start - 1, 0)
            if hunk_start < source_index or hunk_start > len(source):
                raise ValueError("hunk range is outside the target file")
            output.extend(source[source_index:hunk_start])
            source_index = hunk_start
            index += 1
            old_seen = 0
            new_seen = 0

            while index < len(lines) and not lines[index].startswith("@@ "):
                patch_line = lines[index]
                if not patch_line or patch_line[0] not in " +-":
                    raise ValueError("invalid hunk line")
                marker, content = patch_line[0], patch_line[1:]
                if marker in " -":
                    if source_index >= len(source) or source[source_index] != content:
                        raise ValueError("hunk context does not match target file")
                    source_index += 1
                    old_seen += 1
                if marker in " +":
                    output.append(content)
                    new_seen += 1
                index += 1

            if old_seen != old_count or new_seen != new_count:
                raise ValueError("hunk line counts do not match header")
            hunk_count += 1

        if hunk_count == 0:
            raise ValueError("diff contains no hunks")
        output.extend(source[source_index:])
        return "".join(output)

    @staticmethod
    def _header_path(line: str) -> str:
        return line[4:].rstrip("\r\n").split("\t", 1)[0]

    @staticmethod
    def _failure(target_file: str, message: str) -> ApplyResult:
        return ApplyResult(
            success=False,
            applied=False,
            backup_path=None,
            target_file=target_file,
            message=message,
        )
