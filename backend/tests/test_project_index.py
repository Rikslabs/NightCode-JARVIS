import pytest
from pathlib import Path
from app.tools.project_index import ProjectIndex, FileMetadata


def test_build_index_basic(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[tool.poetry]\nname='demo'\n", encoding="utf-8")
    (tmp_path / "main.py").write_text("import os\n", encoding="utf-8")
    (tmp_path / "utils.py").write_text("import sys\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Project\n", encoding="utf-8")

    index = ProjectIndex(str(tmp_path))
    summary = index.build_index()

    assert summary["total_files"] == 4
    assert summary["project_type"] == "Python"
    assert summary["package_manager"] == "pip"
    assert "main" in summary["modules"]
    assert "utils" in summary["modules"]


def test_project_type_detection(tmp_path):
    (tmp_path / "package.json").write_text("{}", encoding="utf-8")
    (tmp_path / "index.js").write_text("console.log(1)", encoding="utf-8")

    index = ProjectIndex(str(tmp_path))
    summary = index.build_index()

    assert summary["project_type"] == "Node.js"
    assert summary["package_manager"] == "npm"


def test_file_category(tmp_path):
    (tmp_path / "app.py").write_text("pass", encoding="utf-8")
    (tmp_path / "main.py").write_text("pass", encoding="utf-8")
    (tmp_path / "test_app.py").write_text("pass", encoding="utf-8")
    (tmp_path / "logo.png").write_text("", encoding="utf-8")
    (tmp_path / "config.json").write_text("{}", encoding="utf-8")
    (tmp_path / "README.md").write_text("# docs", encoding="utf-8")

    index = ProjectIndex(str(tmp_path))
    index.build_index()

    assert index.files["app.py"].category == "entry"
    assert index.files["main.py"].category == "entry"
    assert index.files["test_app.py"].category == "test"
    assert index.files["logo.png"].category == "asset"
    assert index.files["config.json"].category == "docs"
    assert index.files["README.md"].category == "docs"


def test_get_file_metadata(tmp_path):
    (tmp_path / "a.py").write_text("import os\n", encoding="utf-8")
    index = ProjectIndex(str(tmp_path))
    index.build_index()
    meta = index.get_file_metadata("a.py")
    assert meta is not None
    assert meta["language"] == "Python"
    assert meta["category"] == "source"
    assert "import os" in meta["imports"]


def test_get_dependencies(tmp_path):
    (tmp_path / "a.py").write_text("import os\nimport sys\n", encoding="utf-8")
    index = ProjectIndex(str(tmp_path))
    index.build_index()
    deps = index.get_dependencies("a.py")
    assert len(deps) == 2
    assert "import os" in deps
    assert "import sys" in deps


def test_find_entry_points(tmp_path):
    (tmp_path / "app.py").write_text("pass", encoding="utf-8")
    (tmp_path / "utils.py").write_text("pass", encoding="utf-8")
    index = ProjectIndex(str(tmp_path))
    index.build_index()
    eps = index.find_entry_points()
    assert "app.py" in eps
    assert "utils.py" not in eps


def test_list_modules_and_search(tmp_path):
    (tmp_path / "auth.py").write_text("pass", encoding="utf-8")
    (tmp_path / "user_auth.py").write_text("pass", encoding="utf-8")
    index = ProjectIndex(str(tmp_path))
    index.build_index()
    modules = index.list_modules()
    assert len(modules) >= 1
    results = index.search_module("auth")
    assert len(results) >= 1


def test_refresh_index(tmp_path):
    (tmp_path / "a.py").write_text("pass", encoding="utf-8")
    index = ProjectIndex(str(tmp_path))
    index.build_index()
    assert len(index.files) == 1
    (tmp_path / "b.py").write_text("pass", encoding="utf-8")
    summary = index.refresh_index()
    assert summary["total_files"] == 2


def test_skip_directories(tmp_path):
    (tmp_path / "node_modules" / "pkg").mkdir(parents=True)
    (tmp_path / "node_modules" / "pkg" / "index.js").write_text("", encoding="utf-8")
    (tmp_path / "src.py").write_text("pass", encoding="utf-8")
    index = ProjectIndex(str(tmp_path))
    index.build_index()
    assert "src.py" in index.files
    assert all("node_modules" not in p for p in index.files.keys())


def test_detect_large_repo(tmp_path):
    for i in range(100):
        (tmp_path / f"file_{i}.py").write_text("pass\n" * 10, encoding="utf-8")
    index = ProjectIndex(str(tmp_path))
    summary = index.build_index()
    assert summary["total_files"] == 100
    assert summary["by_language"].get("Python") == 100