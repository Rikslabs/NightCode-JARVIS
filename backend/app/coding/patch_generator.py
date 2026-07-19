"""Read-only patch proposal generation."""

from dataclasses import asdict, dataclass, field
from difflib import unified_diff
from pathlib import Path
from typing import Dict, List, Optional, Union

from .explainer import FileExplanation, SymbolExplanation
from .reader import FileReader


@dataclass(frozen=True)
class PatchProposal:
    """A proposed code change that has not been applied."""

    summary: str
    target_file: str
    reasoning: str
    proposed_changes: List[str] = field(default_factory=list)
    unified_diff: str = ""
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, object]:
        """Serialize the proposal to plain Python values."""
        return asdict(self)


Explanation = Union[FileExplanation, SymbolExplanation]


class PatchGenerator:
    """Create safe patch proposals without changing the filesystem."""

    def __init__(
        self,
        project_root: Union[str, Path],
        reader: Optional[FileReader] = None,
    ) -> None:
        self._reader = reader or FileReader(project_root)

    def generate(
        self,
        file_path: Union[str, Path],
        explanation: Explanation,
        user_instruction: Optional[str] = None,
        proposed_content: Optional[str] = None,
    ) -> PatchProposal:
        """Create a proposal and, when exact content is supplied, a unified diff."""
        target = Path(file_path).as_posix()
        original = self._reader.read_text(file_path)
        instruction = (user_instruction or "").strip()
        context = self._explanation_context(explanation)

        if proposed_content is None:
            if not instruction:
                return PatchProposal(
                    summary="No changes proposed",
                    target_file=target,
                    reasoning=f"No user instruction or exact replacement content was provided. {context}",
                    confidence=0.0,
                )
            return PatchProposal(
                summary=f"Proposed update to {target}",
                target_file=target,
                reasoning=f"The instruction requires implementation details before a safe diff can be generated. {context}",
                proposed_changes=[instruction],
                confidence=0.5,
            )

        diff = self._unified_diff(target, original, proposed_content)
        if not diff:
            return PatchProposal(
                summary="No changes proposed",
                target_file=target,
                reasoning=f"The proposed content matches the current file. {context}",
                confidence=1.0,
            )

        change = instruction or "Replace the file with the supplied proposed content."
        return PatchProposal(
            summary=f"Proposed update to {target}",
            target_file=target,
            reasoning=f"Exact replacement content was supplied, so a deterministic diff could be generated. {context}",
            proposed_changes=[change],
            unified_diff=diff,
            confidence=0.95,
        )

    @staticmethod
    def _unified_diff(target: str, original: str, proposed: str) -> str:
        return "".join(unified_diff(
            original.splitlines(keepends=True),
            proposed.splitlines(keepends=True),
            fromfile=f"a/{target}",
            tofile=f"b/{target}",
        ))

    @staticmethod
    def _explanation_context(explanation: Explanation) -> str:
        if isinstance(explanation, FileExplanation):
            return f"The file was identified as {explanation.detected_language} module {explanation.module_name}."
        return f"The target context is {explanation.symbol_type} {explanation.name} at {explanation.location}."
