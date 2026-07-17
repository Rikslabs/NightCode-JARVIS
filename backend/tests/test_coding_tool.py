import ast
import pytest
from pathlib import Path
from app.tools.coding import CodingTool


@pytest.fixture
def coding_tool():
    return CodingTool()


def test_read_file_success(coding_tool, tmp_path):
    target = tmp_path / "hello.py"
    target.write_text("print('hello')", encoding="utf-8")
    result = coding_tool.execute(operation="read_file", path=str(target))
    assert result.success is True
    assert result.data["content"] == "print('hello')"
    assert result.data["path"] == str(target)


def test_read_file_not_found(coding_tool):
    result = coding_tool.execute(operation="read_file", path="/nonexistent.py")
    assert result.success is False
    assert "not found" in result.error.lower()


def test_read_file_directory(coding_tool, tmp_path):
    result = coding_tool.execute(operation="read_file", path=str(tmp_path))
    assert result.success is False
    assert "not a file" in result.error.lower()


def test_list_dir_success(coding_tool, tmp_path):
    (tmp_path / "a.py").write_text("", encoding="utf-8")
    result = coding_tool.execute(operation="list_dir", path=str(tmp_path))
    assert result.success is True
    names = {e["name"] for e in result.data["entries"]}
    assert "a.py" in names


def test_search_files_success(coding_tool, tmp_path):
    (tmp_path / "a.py").write_text("", encoding="utf-8")
    (tmp_path / "b.txt").write_text("", encoding="utf-8")
    result = coding_tool.execute(operation="search_files", path=str(tmp_path), pattern="*.py")
    assert result.success is True
    assert len(result.data["matches"]) == 1


def test_search_text_success(coding_tool, tmp_path):
    (tmp_path / "a.py").write_text("def foo(): pass", encoding="utf-8")
    result = coding_tool.execute(operation="search_text", path=str(tmp_path), query="foo")
    assert result.success is True
    assert len(result.data["matches"]) == 1


def test_detect_language_python(coding_tool, tmp_path):
    target = tmp_path / "app.py"
    target.write_text("", encoding="utf-8")
    result = coding_tool.execute(operation="detect_language", path=str(target))
    assert result.success is True
    assert result.data["language"] == "Python"


def test_summarize_file(coding_tool, tmp_path):
    target = tmp_path / "app.py"
    target.write_text("x=1\ny=2\nz=3\n", encoding="utf-8")
    result = coding_tool.execute(operation="summarize_file", path=str(target))
    assert result.success is True
    assert result.data["lines"] == 3
    assert "x=1" in result.data["preview"]


def test_explain_class(coding_tool, tmp_path):
    target = tmp_path / "app.py"
    target.write_text("class Foo:\n    pass\n", encoding="utf-8")
    result = coding_tool.execute(operation="explain_class", path=str(target), name="Foo")
    assert result.success is True
    assert result.data["class_name"] == "Foo"
    assert len(result.data["matches"]) == 1
    assert result.data["matches"][0]["line"] == 1


def test_explain_function(coding_tool, tmp_path):
    target = tmp_path / "app.py"
    target.write_text('def bar():\n    """docstring"""\n    pass\n', encoding="utf-8")
    result = coding_tool.execute(operation="explain_function", path=str(target), name="bar")
    assert result.success is True
    assert result.data["function_name"] == "bar"
    assert len(result.data["matches"]) == 2


def test_list_imports(coding_tool, tmp_path):
    target = tmp_path / "app.py"
    target.write_text("import os\nfrom pathlib import Path\n", encoding="utf-8")
    result = coding_tool.execute(operation="list_imports", path=str(target))
    assert result.success is True
    assert "import os" in result.data["imports"]
    assert len(result.data["imports"]) == 2


def test_detect_todos(coding_tool, tmp_path):
    target = tmp_path / "app.py"
    target.write_text("# TODO: fix this\n# FIXME: broken\n# normal comment\n", encoding="utf-8")
    result = coding_tool.execute(operation="detect_todos", path=str(target), max_results=10)
    assert result.success is True
    assert len(result.data["todos"]) == 2


def test_detect_large_functions(coding_tool, tmp_path):
    target = tmp_path / "app.py"
    target.write_text("def big():\n" + "\n".join([f"    x={i}" for i in range(60)]) + "\n", encoding="utf-8")
    result = coding_tool.execute(operation="detect_large_functions", path=str(target), max_results=10)
    assert result.success is True
    assert len(result.data["large_functions"]) == 1
    assert result.data["large_functions"][0]["name"] == "big"
    assert result.data["large_functions"][0]["size"] > 50


def test_detect_duplicates(coding_tool, tmp_path):
    (tmp_path / "a.py").write_text("x=1\n", encoding="utf-8")
    (tmp_path / "b.py").write_text("x=1\n", encoding="utf-8")
    result = coding_tool.execute(operation="detect_duplicates", path=str(tmp_path), max_results=10)
    assert result.success is True
    assert len(result.data["duplicates"]) == 2


def test_summarize_project(coding_tool, tmp_path):
    (tmp_path / "app.py").write_text("", encoding="utf-8")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "readme.md").write_text("", encoding="utf-8")
    result = coding_tool.execute(operation="summarize_project", path=str(tmp_path), max_results=10)
    assert result.success is True
    names = {e["name"] for e in result.data["entries"]}
    assert "app.py" in names
    assert "docs" in names


def test_analyze_module(coding_tool, tmp_path):
    target = tmp_path / "app.py"
    target.write_text("import os\n# TODO: implement\n\ndef foo():\n    pass\n", encoding="utf-8")
    result = coding_tool.execute(operation="analyze_module", path=str(target))
    assert result.success is True
    assert result.data["lines"] == 5
    assert "import os" in result.data["imports"]
    assert len(result.data["todos"]) == 1


def test_unknown_operation(coding_tool):
    result = coding_tool.execute(operation="write_file", path="/tmp/x")
    assert result.success is False
    assert "unknown coding operation" in result.error.lower()