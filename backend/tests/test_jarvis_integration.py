"""Stage 23 integration tests for the V1 developer assistant."""

import subprocess
from pathlib import Path

import pytest

from app.coding import (
    CodeExplainer,
    CodingService,
    FileReader,
    PatchGenerator,
    ProjectAnalyzer,
    PythonSymbolIndex,
    RepositoryExplorer,
    SafeApplyService,
)
from app.git import GitAssistant
from app.jarvis import JarvisService
from app.terminal import TerminalAssistant


class GitRunner:
    def __call__(self, command, **kwargs):
        outputs = {
            ("status", "--short"): " M module.py\n?? notes.txt\n",
            ("branch", "--show-current"): "main\n",
            ("log", "--oneline", "-n", "10"): "abc123 Initial commit\n",
        }
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=outputs.get(tuple(command[1:]), ""),
            stderr="",
        )


def create_jarvis(project_root: Path) -> JarvisService:
    explorer = RepositoryExplorer(project_root)
    reader = FileReader(project_root)
    symbols = PythonSymbolIndex(project_root, explorer=explorer)
    explainer = CodeExplainer(project_root, reader=reader, symbol_index=symbols)
    coding = CodingService(
        analyzer=ProjectAnalyzer(project_root),
        explorer=explorer,
        symbol_index=symbols,
        reader=reader,
        explainer=explainer,
        patch_generator=PatchGenerator(project_root, reader=reader),
    )
    return JarvisService(
        coding=coding,
        terminal=TerminalAssistant(working_directory=project_root),
        git=GitAssistant(project_root, runner=GitRunner()),
        safe_apply=SafeApplyService(project_root),
    )


def test_service_initialization(tmp_path: Path):
    assert isinstance(create_jarvis(tmp_path), JarvisService)


def test_end_to_end_coding_workflow(tmp_path: Path):
    (tmp_path / "module.py").write_text(
        "def run():\n    return 1\n",
        encoding="utf-8",
    )
    jarvis = create_jarvis(tmp_path)

    assert jarvis.analyze_project().project.file_count == 1
    assert [entry.name for entry in jarvis.list_files(".py")] == ["module.py"]
    explanation = jarvis.explain_file("module.py")
    assert explanation.functions == ["run"]
    assert jarvis.explain_symbol("run").location == "module.py:1"
    proposal = jarvis.generate_patch(
        "module.py",
        explanation,
        "Return two",
        proposed_content="def run():\n    return 2\n",
    )
    assert proposal.unified_diff


def test_terminal_workflow(tmp_path: Path):
    result = create_jarvis(tmp_path).run_command("python -c \"print('ready')\"")

    assert result.success is True
    assert result.stdout.strip() == "ready"


def test_git_workflow(tmp_path: Path):
    jarvis = create_jarvis(tmp_path)

    statuses = jarvis.git_status()
    summary = jarvis.repository_summary()

    assert [entry.path for entry in statuses] == ["module.py", "notes.txt"]
    assert summary.current_branch == "main"
    assert summary.modified_files == ["module.py"]
    assert summary.untracked_files == ["notes.txt"]
    assert summary.clean is False


def test_safe_apply_workflow(tmp_path: Path):
    target = tmp_path / "module.py"
    target.write_text("value = 1\n", encoding="utf-8")
    jarvis = create_jarvis(tmp_path)
    explanation = jarvis.explain_file("module.py")
    proposal = jarvis.generate_patch(
        "module.py",
        explanation,
        "Update value",
        proposed_content="value = 2\n",
    )

    result = jarvis.apply_patch(proposal, approval=True)

    assert result.success is True
    assert result.applied is True
    assert result.backup_path is not None
    assert target.read_text(encoding="utf-8") == "value = 2\n"


def test_invalid_input_handling(tmp_path: Path):
    jarvis = create_jarvis(tmp_path)

    with pytest.raises(FileNotFoundError):
        jarvis.explain_file("missing.py")
    with pytest.raises(KeyError):
        jarvis.explain_symbol("missing")

    blocked = jarvis.run_command("git push origin main")
    assert blocked.success is False
    assert blocked.exit_code == 126
