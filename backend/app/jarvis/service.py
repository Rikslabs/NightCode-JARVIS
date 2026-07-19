"""V1 developer assistant integration facade."""

from pathlib import Path
from typing import List, Optional, Union

from app.coding import (
    AnalysisResult,
    ApplyResult,
    CodingService,
    FileExplanation,
    PatchProposal,
    RepositoryEntry,
    SafeApplyService,
    SymbolExplanation,
)
from app.coding.patch_generator import Explanation
from app.git import GitAssistant, GitFileStatus, RepositorySummary
from app.terminal import TerminalAssistant, TerminalResult


class JarvisService:
    """Delegate developer workflows to injected V1 services."""

    def __init__(
        self,
        coding: CodingService,
        terminal: TerminalAssistant,
        git: GitAssistant,
        safe_apply: SafeApplyService,
    ) -> None:
        self._coding = coding
        self._terminal = terminal
        self._git = git
        self._safe_apply = safe_apply

    def analyze_project(self) -> AnalysisResult:
        return self._coding.analyze_project()

    def list_files(self, extension: Optional[str] = None) -> List[RepositoryEntry]:
        return self._coding.list_files(extension)

    def explain_file(self, path: Union[str, Path]) -> FileExplanation:
        return self._coding.explain_file(path)

    def explain_symbol(self, name: str) -> SymbolExplanation:
        return self._coding.explain_symbol(name)

    def generate_patch(
        self,
        file_path: Union[str, Path],
        explanation: Explanation,
        user_instruction: Optional[str] = None,
        proposed_content: Optional[str] = None,
    ) -> PatchProposal:
        return self._coding.generate_patch(
            file_path,
            explanation,
            user_instruction,
            proposed_content,
        )

    def apply_patch(self, proposal: PatchProposal, approval: bool) -> ApplyResult:
        return self._safe_apply.apply(proposal, approval)

    def run_command(self, command: str) -> TerminalResult:
        return self._terminal.run(command)

    def git_status(self) -> List[GitFileStatus]:
        return self._git.status()

    def repository_summary(self) -> RepositorySummary:
        return self._git.repository_summary()
