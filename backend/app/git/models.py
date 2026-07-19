"""Typed Git assistant models."""

from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class GitFileStatus:
    """Parsed entry from Git short status output."""

    path: str
    index_status: str
    worktree_status: str

    @property
    def staged(self) -> bool:
        return self.index_status not in {" ", "?"}

    @property
    def modified(self) -> bool:
        return self.worktree_status not in {" ", "?"}

    @property
    def untracked(self) -> bool:
        return self.index_status == "?" and self.worktree_status == "?"


@dataclass(frozen=True)
class GitCommit:
    """Commit summary from one-line Git log output."""

    commit_hash: str
    message: str


@dataclass(frozen=True)
class RepositorySummary:
    """Read-only summary of repository state."""

    current_branch: str
    modified_files: List[str] = field(default_factory=list)
    staged_files: List[str] = field(default_factory=list)
    untracked_files: List[str] = field(default_factory=list)
    recent_commits: List[GitCommit] = field(default_factory=list)
    clean: bool = True
