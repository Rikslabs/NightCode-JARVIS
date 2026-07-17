import pytest
from pathlib import Path
from app.tools.review import ReviewTool, ReviewSeverity, ReviewCategory


@pytest.fixture
def review_tool():
    return ReviewTool()


def test_review_file_empty(review_tool, tmp_path):
    target = tmp_path / "empty.py"
    target.write_text("", encoding="utf-8")
    report = review_tool.review_file(str(target))
    assert report.findings[0].severity == ReviewSeverity.HIGH
    assert report.findings[0].category == ReviewCategory.DOCUMENTATION
    assert report.score > 0


def test_review_file_todo(review_tool, tmp_path):
    target = tmp_path / "todo.py"
    target.write_text("# TODO: fix\n# FIXME: broken\n", encoding="utf-8")
    report = review_tool.review_file(str(target))
    assert len(report.findings) >= 2
    messages = [f.message for f in report.findings]
    assert any("TODO" in m for m in messages)
    assert any("FIXME" in m for m in messages)


def test_review_file_security_eval(review_tool, tmp_path):
    target = tmp_path / "bad.py"
    target.write_text("eval('1+1')\n", encoding="utf-8")
    report = review_tool.review_file(str(target))
    assert any(f.category == ReviewCategory.SECURITY and f.severity == ReviewSeverity.CRITICAL for f in report.findings)


def test_review_file_long_line(review_tool, tmp_path):
    target = tmp_path / "long.py"
    target.write_text("x = '{}'\n".format("a" * 130), encoding="utf-8")
    report = review_tool.review_file(str(target))
    assert any(f.category == ReviewCategory.STYLE for f in report.findings)


def test_review_file_complex_function(review_tool, tmp_path):
    target = tmp_path / "complex.py"
    lines = ["def big():\n"] + ["    x={}\n".format(i) for i in range(60)]
    target.write_text("".join(lines), encoding="utf-8")
    report = review_tool.review_file(str(target))
    assert any(f.category == ReviewCategory.COMPLEXITY and "big" in f.message for f in report.findings)


def test_review_file_too_many_params(review_tool, tmp_path):
    target = tmp_path / "params.py"
    args = ", ".join([f"a{i}" for i in range(6)])
    target.write_text(f"def many({args}):\n    pass\n", encoding="utf-8")
    report = review_tool.review_file(str(target))
    assert any(f.category == ReviewCategory.COMPLEXITY and "parameters" in f.message for f in report.findings)


def test_review_file_wildcard_import(review_tool, tmp_path):
    target = tmp_path / "wild.py"
    target.write_text("from os import *\n", encoding="utf-8")
    report = review_tool.review_file(str(target))
    assert any(f.category == ReviewCategory.DOCUMENTATION and "Wildcard import" in f.message for f in report.findings)


def test_review_file_missing_docstring(review_tool, tmp_path):
    target = tmp_path / "nodoc.py"
    target.write_text("def foo():\n    pass\n", encoding="utf-8")
    report = review_tool.review_file(str(target))
    assert any(f.category == ReviewCategory.DOCUMENTATION and "missing docstring" in f.message for f in report.findings)


def test_review_score_perfect():
    tool = ReviewTool()
    report = tool.review_file(__file__)
    assert report.score >= 0
    assert report.score <= 100


def test_review_project_basic(review_tool, tmp_path):
    (tmp_path / "pyproject.toml").write_text("", encoding="utf-8")
    (tmp_path / "good.py").write_text('"""Great module."""\n', encoding="utf-8")
    report = review_tool.review_project(str(tmp_path))
    assert report.summary["files_reviewed"] >= 1
    assert hasattr(report, "score")
    assert 0 <= report.score <= 100
