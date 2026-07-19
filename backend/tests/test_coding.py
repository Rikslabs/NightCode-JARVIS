"""Tests for the coding assistant foundation."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from app.coding import (
    AnalyzerRegistry,
    BinaryFileError,
    CodeExplainer,
    CodingService,
    FileReader,
    FileEncodingError,
    PathTraversalError,
    PatchGenerator,
    ProjectAnalyzer,
    PythonSymbolIndex,
    RepositoryExplorer,
    SafeApplyService,
)


def test_analyzer_creation(tmp_path: Path):
    analyzer = ProjectAnalyzer(tmp_path)
    assert analyzer.project_root == tmp_path


def test_project_analysis_uses_filesystem_metadata(tmp_path: Path):
    package = tmp_path / "package"
    package.mkdir()
    (package / "module.py").write_text("print('not inspected')", encoding="utf-8")
    (tmp_path / "app.ts").write_text("export {};", encoding="utf-8")
    (tmp_path / "README.md").write_text("project", encoding="utf-8")

    result = ProjectAnalyzer(tmp_path).analyze()

    assert result.project.name == tmp_path.name
    assert result.project.root_path == tmp_path.resolve()
    assert result.project.detected_languages == ["Python", "TypeScript"]
    assert result.project.file_count == 3
    assert result.project.directory_count == 1
    assert result.project.top_level_modules == ["app", "package"]
    assert len(result.files) == 3
    assert all(file.size_bytes >= 0 for file in result.files)


def test_registry_operations(tmp_path: Path):
    registry = AnalyzerRegistry()
    analyzer = ProjectAnalyzer(tmp_path)
    registry.register("default", analyzer)
    assert registry.get("default") is analyzer
    assert registry.list() == ["default"]
    assert registry.unregister("default") is True
    assert registry.unregister("default") is False
    assert registry.get("default") is None


def test_invalid_path_handling(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        ProjectAnalyzer(tmp_path / "missing").analyze()

    file_path = tmp_path / "file.py"
    file_path.touch()
    with pytest.raises(NotADirectoryError):
        ProjectAnalyzer(file_path).analyze()


def test_explorer_file_listing(tmp_path: Path):
    source = tmp_path / "src"
    source.mkdir()
    (source / "main.py").write_text("print('hello')", encoding="utf-8")
    (tmp_path / "README.md").write_text("readme", encoding="utf-8")

    files = RepositoryExplorer(tmp_path).list_files()

    assert [entry.relative_path for entry in files] == ["README.md", "src/main.py"]
    assert files[1].name == "main.py"
    assert files[1].extension == ".py"
    assert files[1].size > 0
    assert files[1].last_modified.tzinfo is not None


def test_explorer_directory_listing(tmp_path: Path):
    (tmp_path / "src" / "package").mkdir(parents=True)

    directories = RepositoryExplorer(tmp_path).list_directories()

    assert [entry.relative_path for entry in directories] == ["src", "src/package"]


def test_explorer_extension_filtering(tmp_path: Path):
    (tmp_path / "one.py").touch()
    (tmp_path / "two.PY").touch()
    (tmp_path / "three.txt").touch()

    files = RepositoryExplorer(tmp_path).list_files("py")

    assert [entry.name for entry in files] == ["one.py", "two.PY"]


def test_explorer_ignores_generated_directories(tmp_path: Path):
    ignored_names = [
        ".git", "__pycache__", ".pytest_cache", "node_modules", ".venv", "venv",
    ]
    for name in ignored_names:
        directory = tmp_path / name
        directory.mkdir()
        (directory / "ignored.py").touch()
    (tmp_path / "visible.py").touch()

    explorer = RepositoryExplorer(tmp_path)

    assert [entry.name for entry in explorer.list_files()] == ["visible.py"]
    assert explorer.list_directories() == []


def test_explorer_invalid_path(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        RepositoryExplorer(tmp_path / "missing").list_files()

    file_path = tmp_path / "file.py"
    file_path.touch()
    with pytest.raises(NotADirectoryError):
        RepositoryExplorer(file_path).list_directories()


def test_registry_supports_explorers(tmp_path: Path):
    registry = AnalyzerRegistry()
    explorer = RepositoryExplorer(tmp_path)
    registry.register_explorer("repository", explorer)
    assert registry.get_explorer("repository") is explorer
    assert registry.list_explorers() == ["repository"]
    assert registry.unregister_explorer("repository") is True


def test_symbol_class_discovery(tmp_path: Path):
    (tmp_path / "models.py").write_text("class User:\n    pass\n", encoding="utf-8")

    symbols = PythonSymbolIndex(tmp_path).index()

    user = next(symbol for symbol in symbols if symbol.name == "User")
    assert user.symbol_type == "class"
    assert user.relative_file_path == "models.py"
    assert user.line_number == 1


def test_symbol_function_and_async_function_discovery(tmp_path: Path):
    (tmp_path / "tasks.py").write_text(
        "def run():\n    pass\n\nasync def fetch():\n    pass\n",
        encoding="utf-8",
    )

    symbols = PythonSymbolIndex(tmp_path).index()

    types = {symbol.name: symbol.symbol_type for symbol in symbols}
    assert types["tasks"] == "module"
    assert types["run"] == "function"
    assert types["fetch"] == "async_function"


def test_symbol_method_parent_relationship(tmp_path: Path):
    (tmp_path / "service.py").write_text(
        "class Service:\n    def execute(self):\n        pass\n",
        encoding="utf-8",
    )

    symbols = PythonSymbolIndex(tmp_path).index()

    method = next(symbol for symbol in symbols if symbol.name == "execute")
    assert method.symbol_type == "method"
    assert method.parent_symbol == "Service"


def test_symbol_exact_and_partial_search(tmp_path: Path):
    (tmp_path / "search.py").write_text(
        "def load_user():\n    pass\n\ndef load_project():\n    pass\n",
        encoding="utf-8",
    )
    index = PythonSymbolIndex(tmp_path)
    index.index()

    assert [symbol.name for symbol in index.search("load_user", exact=True)] == ["load_user"]
    assert [symbol.name for symbol in index.search("LOAD_")] == ["load_user", "load_project"]


def test_symbol_index_ignores_directories(tmp_path: Path):
    ignored = tmp_path / "__pycache__"
    ignored.mkdir()
    (ignored / "hidden.py").write_text("class Hidden:\n    pass\n", encoding="utf-8")
    (tmp_path / "visible.py").write_text("class Visible:\n    pass\n", encoding="utf-8")

    names = [symbol.name for symbol in PythonSymbolIndex(tmp_path).index()]

    assert "Visible" in names
    assert "Hidden" not in names


def test_malformed_python_file_does_not_stop_symbol_index(tmp_path: Path):
    (tmp_path / "broken.py").write_text("def broken(:\n", encoding="utf-8")
    (tmp_path / "valid.py").write_text("def valid():\n    pass\n", encoding="utf-8")

    names = [symbol.name for symbol in PythonSymbolIndex(tmp_path).index()]

    assert "valid" in names
    assert "broken" not in names


def test_symbol_index_invalid_root(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        PythonSymbolIndex(tmp_path / "missing").index()

    file_path = tmp_path / "file.py"
    file_path.touch()
    with pytest.raises(NotADirectoryError):
        PythonSymbolIndex(file_path).index()


def test_file_reader_full_read_and_metadata(tmp_path: Path):
    file_path = tmp_path / "notes.txt"
    file_path.write_text("hello\nworld\n", encoding="utf-8")
    reader = FileReader(tmp_path)

    assert reader.read_text("notes.txt") == "hello\nworld\n"
    assert reader.exists("notes.txt") is True
    assert reader.exists("missing.txt") is False
    assert reader.file_size("notes.txt") == file_path.stat().st_size


def test_file_reader_line_range(tmp_path: Path):
    (tmp_path / "lines.txt").write_text("one\ntwo\nthree\nfour\n", encoding="utf-8")

    assert FileReader(tmp_path).read_lines("lines.txt", 2, 3) == ["two", "three"]


def test_file_reader_missing_file(tmp_path: Path):
    reader = FileReader(tmp_path)
    with pytest.raises(FileNotFoundError):
        reader.read_text("missing.txt")
    with pytest.raises(FileNotFoundError):
        reader.file_size("missing.txt")


def test_file_reader_rejects_binary_file(tmp_path: Path):
    (tmp_path / "data.bin").write_bytes(b"binary\x00data")

    with pytest.raises(BinaryFileError):
        FileReader(tmp_path).read_text("data.bin")


def test_file_reader_reports_encoding_error(tmp_path: Path):
    (tmp_path / "invalid.txt").write_bytes(b"text\xff")

    with pytest.raises(FileEncodingError):
        FileReader(tmp_path).read_text("invalid.txt")


def test_file_reader_rejects_path_traversal(tmp_path: Path):
    reader = FileReader(tmp_path)

    with pytest.raises(PathTraversalError):
        reader.read_text("../outside.txt")
    with pytest.raises(PathTraversalError):
        reader.exists(tmp_path.parent / "outside.txt")


def test_code_explainer_file_explanation(tmp_path: Path):
    (tmp_path / "service.py").write_text(
        '"""Service module."""\n'
        "import os\n"
        "from pathlib import Path\n\n"
        "class Service:\n    pass\n\n"
        "def run(value: int) -> bool:\n    return bool(value)\n\n"
        "async def fetch():\n    pass\n\n"
        "def _helper():\n    pass\n",
        encoding="utf-8",
    )

    result = CodeExplainer(tmp_path).explain_file("service.py")

    assert result.module_name == "service"
    assert result.imports == ["os", "pathlib"]
    assert result.classes == ["Service"]
    assert result.functions == ["run", "_helper"]
    assert result.async_functions == ["fetch"]
    assert result.public_api_count == 3
    assert result.private_member_count == 1
    assert result.line_count > 0
    assert result.has_docstring is True
    assert result.detected_language == "Python"


def test_code_explainer_symbol_explanation(tmp_path: Path):
    (tmp_path / "worker.py").write_text(
        "class Worker:\n"
        "    def execute(self, task: str = 'default') -> bool:\n"
        '        """Execute a task."""\n'
        "        return True\n",
        encoding="utf-8",
    )

    result = CodeExplainer(tmp_path).explain_symbol("execute")

    assert result.name == "execute"
    assert result.symbol_type == "method"
    assert result.location == "worker.py:2"
    assert result.parent == "Worker"
    assert result.signature == "execute(self, task: str='default') -> bool"
    assert result.docstring == "Execute a task."


def test_code_explainer_handles_syntax_error(tmp_path: Path):
    (tmp_path / "broken.py").write_text("def broken(:\n", encoding="utf-8")

    result = CodeExplainer(tmp_path).explain_file("broken.py")

    assert result.module_name == "broken"
    assert result.functions == []
    assert result.detected_language == "Python"


def test_code_explainer_missing_file(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        CodeExplainer(tmp_path).explain_file("missing.py")


def test_code_explainer_missing_symbol(tmp_path: Path):
    (tmp_path / "module.py").write_text("value = 1\n", encoding="utf-8")

    with pytest.raises(KeyError):
        CodeExplainer(tmp_path).explain_symbol("missing")


def test_patch_proposal_creation(tmp_path: Path):
    (tmp_path / "module.py").write_text("value = 1\n", encoding="utf-8")
    explanation = CodeExplainer(tmp_path).explain_file("module.py")

    proposal = PatchGenerator(tmp_path).generate(
        "module.py", explanation, "Rename value to count",
    )

    assert proposal.summary == "Proposed update to module.py"
    assert proposal.target_file == "module.py"
    assert proposal.proposed_changes == ["Rename value to count"]
    assert proposal.unified_diff == ""


def test_empty_patch_proposal(tmp_path: Path):
    (tmp_path / "module.py").write_text("value = 1\n", encoding="utf-8")
    explanation = CodeExplainer(tmp_path).explain_file("module.py")

    proposal = PatchGenerator(tmp_path).generate("module.py", explanation)

    assert proposal.summary == "No changes proposed"
    assert proposal.proposed_changes == []
    assert proposal.unified_diff == ""
    assert proposal.confidence == 0.0


def test_patch_unified_diff_generation(tmp_path: Path):
    (tmp_path / "module.py").write_text("value = 1\n", encoding="utf-8")
    explanation = CodeExplainer(tmp_path).explain_file("module.py")

    proposal = PatchGenerator(tmp_path).generate(
        "module.py",
        explanation,
        "Update the value",
        proposed_content="value = 2\n",
    )

    assert "--- a/module.py" in proposal.unified_diff
    assert "+++ b/module.py" in proposal.unified_diff
    assert "-value = 1" in proposal.unified_diff
    assert "+value = 2" in proposal.unified_diff
    assert (tmp_path / "module.py").read_text(encoding="utf-8").strip() == "value = 1"


def test_patch_generator_invalid_file(tmp_path: Path):
    (tmp_path / "context.py").write_text("value = 1\n", encoding="utf-8")
    explanation = CodeExplainer(tmp_path).explain_file("context.py")
    with pytest.raises(FileNotFoundError):
        PatchGenerator(tmp_path).generate(
            "missing.py",
            explanation,
        )


def test_patch_confidence_range_and_serialization(tmp_path: Path):
    (tmp_path / "module.py").write_text("value = 1\n", encoding="utf-8")
    explanation = CodeExplainer(tmp_path).explain_file("module.py")
    proposals = [
        PatchGenerator(tmp_path).generate("module.py", explanation),
        PatchGenerator(tmp_path).generate("module.py", explanation, "Review value"),
        PatchGenerator(tmp_path).generate(
            "module.py", explanation, proposed_content="value = 2\n",
        ),
    ]

    assert all(0.0 <= proposal.confidence <= 1.0 for proposal in proposals)
    serialized = proposals[-1].to_dict()
    assert serialized["target_file"] == "module.py"
    assert isinstance(serialized["proposed_changes"], list)


def create_coding_service(project_root: Path) -> CodingService:
    explorer = RepositoryExplorer(project_root)
    reader = FileReader(project_root)
    symbol_index = PythonSymbolIndex(project_root, explorer=explorer)
    explainer = CodeExplainer(project_root, reader=reader, symbol_index=symbol_index)
    return CodingService(
        analyzer=ProjectAnalyzer(project_root),
        explorer=explorer,
        symbol_index=symbol_index,
        reader=reader,
        explainer=explainer,
        patch_generator=PatchGenerator(project_root, reader=reader),
    )


def test_coding_service_creation(tmp_path: Path):
    assert isinstance(create_coding_service(tmp_path), CodingService)


def test_coding_service_delegates_operations():
    analyzer = Mock()
    explorer = Mock()
    symbol_index = Mock()
    reader = Mock()
    explainer = Mock()
    patch_generator = Mock()
    service = CodingService(
        analyzer, explorer, symbol_index, reader, explainer, patch_generator,
    )
    explanation = Mock()

    service.analyze_project()
    service.list_files(".py")
    service.find_symbols("run", exact=True)
    service.find_symbols()
    service.read_file("module.py")
    service.explain_file("module.py")
    service.explain_symbol("run")
    service.generate_patch("module.py", explanation, "Update", "updated\n")

    analyzer.analyze.assert_called_once_with()
    explorer.list_files.assert_called_once_with(".py")
    symbol_index.search.assert_called_once_with("run", exact=True)
    symbol_index.index.assert_called_once_with()
    reader.read_text.assert_called_once_with("module.py")
    explainer.explain_file.assert_called_once_with("module.py")
    explainer.explain_symbol.assert_called_once_with("run")
    patch_generator.generate.assert_called_once_with(
        "module.py", explanation, "Update", "updated\n",
    )


def test_coding_service_invalid_inputs(tmp_path: Path):
    service = create_coding_service(tmp_path)
    with pytest.raises(FileNotFoundError):
        service.read_file("missing.py")
    with pytest.raises(KeyError):
        service.explain_symbol("missing")


def test_coding_service_integration(tmp_path: Path):
    (tmp_path / "module.py").write_text(
        "def run():\n    return True\n",
        encoding="utf-8",
    )
    service = create_coding_service(tmp_path)

    assert service.analyze_project().project.file_count == 1
    assert [entry.name for entry in service.list_files(".py")] == ["module.py"]
    assert [symbol.name for symbol in service.find_symbols("run", exact=True)] == ["run"]
    assert "def run" in service.read_file("module.py")
    explanation = service.explain_file("module.py")
    assert explanation.functions == ["run"]
    assert service.explain_symbol("run").symbol_type == "function"
    proposal = service.generate_patch("module.py", explanation, "Review run")
    assert proposal.target_file == "module.py"
    assert proposal.unified_diff == ""


def make_patch_proposal(tmp_path: Path, proposed_content: str = "value = 2\n"):
    explanation = CodeExplainer(tmp_path).explain_file("module.py")
    return PatchGenerator(tmp_path).generate(
        "module.py",
        explanation,
        "Update value",
        proposed_content=proposed_content,
    )


def test_safe_apply_approval_denied(tmp_path: Path):
    target = tmp_path / "module.py"
    target.write_text("value = 1\n", encoding="utf-8")
    proposal = make_patch_proposal(tmp_path)

    result = SafeApplyService(tmp_path).apply(proposal, approval=False)

    assert result.success is True
    assert result.applied is False
    assert result.backup_path is None
    assert target.read_text(encoding="utf-8").strip() == "value = 1"
    assert list(tmp_path.glob("*.backup-*")) == []


def test_safe_apply_success_and_backup(tmp_path: Path):
    target = tmp_path / "module.py"
    target.write_text("value = 1\n", encoding="utf-8")
    proposal = make_patch_proposal(tmp_path)

    result = SafeApplyService(tmp_path).apply(proposal, approval=True)

    assert result.success is True
    assert result.applied is True
    assert result.target_file == "module.py"
    assert result.message == "Patch applied successfully."
    assert result.backup_path is not None
    assert target.read_text(encoding="utf-8") == "value = 2\n"
    backup = tmp_path / result.backup_path
    assert backup.exists()
    assert backup.read_text(encoding="utf-8").strip() == "value = 1"


def test_safe_apply_rejects_invalid_diff(tmp_path: Path):
    target = tmp_path / "module.py"
    target.write_text("value = 1\n", encoding="utf-8")
    proposal = make_patch_proposal(tmp_path)
    invalid = proposal.__class__(
        summary=proposal.summary,
        target_file=proposal.target_file,
        reasoning=proposal.reasoning,
        proposed_changes=proposal.proposed_changes,
        unified_diff=proposal.unified_diff.replace("-value = 1", "-value = 9"),
        confidence=proposal.confidence,
    )

    result = SafeApplyService(tmp_path).apply(invalid, approval=True)

    assert result.success is False
    assert result.applied is False
    assert result.backup_path is None
    assert "Invalid unified diff" in result.message
    assert target.read_text(encoding="utf-8").strip() == "value = 1"


def test_safe_apply_rejects_missing_file(tmp_path: Path):
    target = tmp_path / "module.py"
    target.write_text("value = 1\n", encoding="utf-8")
    proposal = make_patch_proposal(tmp_path)
    missing = proposal.__class__(
        summary=proposal.summary,
        target_file="missing.py",
        reasoning=proposal.reasoning,
        proposed_changes=proposal.proposed_changes,
        unified_diff=proposal.unified_diff,
        confidence=proposal.confidence,
    )

    result = SafeApplyService(tmp_path).apply(missing, approval=True)

    assert result.success is False
    assert result.applied is False
    assert result.backup_path is None
    assert result.target_file == "missing.py"
    assert "does not exist" in result.message
