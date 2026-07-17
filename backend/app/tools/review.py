import ast
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from app.tools.coding import CodingTool
from app.tools.project_index import ProjectIndex


class ReviewSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ReviewCategory(Enum):
    COMPLEXITY = "complexity"
    DOCUMENTATION = "documentation"
    DUPLICATION = "duplication"
    NAMING = "naming"
    SECURITY = "security"
    PERFORMANCE = "performance"
    ARCHITECTURE = "architecture"
    MAINTAINABILITY = "maintainability"
    TESTING = "testing"
    STYLE = "style"


@dataclass
class ReviewFinding:
    category: ReviewCategory
    severity: ReviewSeverity
    message: str
    file_path: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category.value,
            "severity": self.severity.value,
            "message": self.message,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "suggestion": self.suggestion,
        }


@dataclass
class ReviewReport:
    findings: list[ReviewFinding] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)
    score: int = 0

    def add_finding(self, finding: ReviewFinding) -> None:
        self.findings.append(finding)

    def to_dict(self) -> dict[str, Any]:
        return {
            "findings": [f.to_dict() for f in self.findings],
            "summary": self.summary,
            "score": self.score,
        }


class ReviewTool:
    """Read-only engineering review engine."""

    def __init__(self):
        self._coding = CodingTool()
        self._index: Optional[ProjectIndex] = None

    def review_file(self, path: str) -> ReviewReport:
        report = ReviewReport()
        result = self._coding.execute(operation="analyze_module", path=path)
        if not result.success:
            report.add_finding(ReviewFinding(
                category=ReviewCategory.ARCHITECTURE,
                severity=ReviewSeverity.CRITICAL,
                message=f"Unable to read file: {result.error}",
                file_path=path,
            ))
            return report

        data = result.data
        content = data.get("preview", "")
        lines = content.splitlines()
        imports = data.get("imports", [])
        todos = data.get("todos", [])

        self._check_docstring(path, content, report)
        self._check_todos(path, todos, report)
        self._check_imports(path, imports, report)
        self._check_long_lines(path, lines, report)
        self._check_naming(path, lines, report)
        self._check_function_complexity(path, content, report)
        self._check_security(path, lines, report)
        self._check_exception_handling(path, content, report)
        self._check_parameters(path, content, report)
        self._check_missing_docstrings(path, content, report)

        report.summary = {
            "file_path": path,
            "total_findings": len(report.findings),
            "by_severity": self._count_by_severity(report.findings),
            "by_category": self._count_by_category(report.findings),
        }
        report.score = self._calculate_score(report.findings)
        return report

    def review_directory(self, path: str) -> ReviewReport:
        report = ReviewReport()
        if not self._index:
            self._index = ProjectIndex(path)
            self._index.build_index()

        summary = self._index.get_project_summary()
        for rel_path in summary.get("modules", []):
            file_report = self.review_file(rel_path)
            report.findings.extend(file_report.findings)

        report.summary = {
            "path": path,
            "files_reviewed": len(summary.get("modules", [])),
            "total_findings": len(report.findings),
            "by_severity": self._count_by_severity(report.findings),
            "by_category": self._count_by_category(report.findings),
        }
        report.score = self._calculate_score(report.findings)
        return report

    def review_project(self, path: str) -> ReviewReport:
        self._index = ProjectIndex(path)
        self._index.build_index()
        return self.review_directory(path)

    def score_project(self, path: str) -> dict[str, Any]:
        report = self.review_project(path)
        return {"score": report.score, "summary": report.summary}

    def _check_docstring(self, path: str, content: str, report: ReviewReport) -> None:
        if not content.strip():
            report.add_finding(ReviewFinding(
                category=ReviewCategory.DOCUMENTATION,
                severity=ReviewSeverity.HIGH,
                message="Empty module.",
                file_path=path,
                suggestion="Add module-level docstring.",
            ))

    def _check_todos(self, path: str, todos: list[dict], report: ReviewReport) -> None:
        for todo in todos:
            report.add_finding(ReviewFinding(
                category=ReviewCategory.DOCUMENTATION,
                severity=ReviewSeverity.LOW,
                message=todo.get("content", "TODO/FIXME found"),
                file_path=path,
                line_number=todo.get("line"),
                suggestion="Resolve or convert to tracked issue.",
            ))

    def _check_imports(self, path: str, imports: list[str], report: ReviewReport) -> None:
        wildcards = [i for i in imports if "import *" in i]
        for w in wildcards:
            report.add_finding(ReviewFinding(
                category=ReviewCategory.DOCUMENTATION,
                severity=ReviewSeverity.MEDIUM,
                message=f"Wildcard import detected: {w}",
                file_path=path,
                suggestion="Replace with explicit imports.",
            ))

        seen = {}
        duplicates = []
        for imp in imports:
            seen[imp] = seen.get(imp, 0) + 1
            if seen[imp] > 1:
                duplicates.append(imp)
        for dup in duplicates:
            report.add_finding(ReviewFinding(
                category=ReviewCategory.DUPLICATION,
                severity=ReviewSeverity.LOW,
                message=f"Duplicate import: {dup}",
                file_path=path,
                suggestion="Remove duplicate import.",
            ))

    def _check_long_lines(self, path: str, lines: list[str], report: ReviewReport) -> None:
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                report.add_finding(ReviewFinding(
                    category=ReviewCategory.STYLE,
                    severity=ReviewSeverity.LOW,
                    message=f"Line too long ({len(line)} chars)",
                    file_path=path,
                    line_number=i,
                    suggestion="Break line to <= 120 chars.",
                ))

    def _check_naming(self, path: str, lines: list[str], report: ReviewReport) -> None:
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith("def ") or stripped.startswith("class "):
                name_match = re.search(r"(?:def|class)\s+([A-Za-z_][A-Za-z0-9_]*)", stripped)
                if name_match:
                    name = name_match.group(1)
                    if name.lower() != name and "_" not in name and not name[0].isupper():
                        report.add_finding(ReviewFinding(
                            category=ReviewCategory.NAMING,
                            severity=ReviewSeverity.LOW,
                            message=f"Inconsistent casing: {name}",
                            file_path=path,
                            line_number=i,
                            suggestion="Use snake_case for functions, PascalCase for classes.",
                        ))

    def _check_function_complexity(self, path: str, content: str, report: ReviewReport) -> None:
        try:
            tree = ast.parse(content)
        except Exception:
            return
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                start = node.lineno
                end = node.end_lineno or start
                size = end - start + 1
                if size > 50:
                    report.add_finding(ReviewFinding(
                        category=ReviewCategory.COMPLEXITY,
                        severity=ReviewSeverity.MEDIUM,
                        message=f"Function '{node.name}' is {size} lines long.",
                        file_path=path,
                        line_number=start,
                        suggestion="Split into smaller functions.",
                    ))

    def _check_security(self, path: str, lines: list[str], report: ReviewReport) -> None:
        for i, line in enumerate(lines, 1):
            if "eval(" in line or "exec(" in line:
                report.add_finding(ReviewFinding(
                    category=ReviewCategory.SECURITY,
                    severity=ReviewSeverity.CRITICAL,
                    message="Potential code execution via eval/exec.",
                    file_path=path,
                    line_number=i,
                    suggestion="Avoid eval/exec; use safer alternatives.",
                ))
            if "password" in line.lower() and "=" in line:
                report.add_finding(ReviewFinding(
                    category=ReviewCategory.SECURITY,
                    severity=ReviewSeverity.HIGH,
                    message="Potential hardcoded password.",
                    file_path=path,
                    line_number=i,
                    suggestion="Use environment variables or secret managers.",
                ))

    def _check_exception_handling(self, path: str, content: str, report: ReviewReport) -> None:
        if "except:" in content or "except Exception:" in content:
            report.add_finding(ReviewFinding(
                category=ReviewCategory.MAINTAINABILITY,
                severity=ReviewSeverity.MEDIUM,
                message="Bare except clause detected.",
                file_path=path,
                suggestion="Specify exception types.",
            ))

    def _check_parameters(self, path: str, content: str, report: ReviewReport) -> None:
        try:
            tree = ast.parse(content)
        except Exception:
            return
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                args = node.args
                param_count = len(args.args) + len(args.kwonlyargs) + len(args.posonlyargs)
                if param_count > 5:
                    report.add_finding(ReviewFinding(
                        category=ReviewCategory.COMPLEXITY,
                        severity=ReviewSeverity.MEDIUM,
                        message=f"Function '{node.name}' has {param_count} parameters.",
                        file_path=path,
                        line_number=node.lineno,
                        suggestion="Consider grouping params into a dataclass or kwargs.",
                    ))

    def _check_missing_docstrings(self, path: str, content: str, report: ReviewReport) -> None:
        try:
            tree = ast.parse(content)
        except Exception:
            return
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    kind = "Class" if isinstance(node, ast.ClassDef) else "Function"
                    report.add_finding(ReviewFinding(
                        category=ReviewCategory.DOCUMENTATION,
                        severity=ReviewSeverity.MEDIUM,
                        message=f"{kind} '{node.name}' missing docstring.",
                        file_path=path,
                        line_number=node.lineno,
                        suggestion="Add docstring describing purpose and params.",
                    ))

    def _count_by_severity(self, findings: list[ReviewFinding]) -> dict[str, int]:
        counts = {s.value: 0 for s in ReviewSeverity}
        for f in findings:
            counts[f.severity.value] += 1
        return counts

    def _count_by_category(self, findings: list[ReviewFinding]) -> dict[str, int]:
        counts = {c.value: 0 for c in ReviewCategory}
        for f in findings:
            counts[f.category.value] += 1
        return counts

    def _calculate_score(self, findings: list[ReviewFinding]) -> int:
        if not findings:
            return 100
        deductions = {
            ReviewSeverity.LOW: 1,
            ReviewSeverity.MEDIUM: 3,
            ReviewSeverity.HIGH: 6,
            ReviewSeverity.CRITICAL: 10,
        }
        total_deduction = sum(deductions.get(f.severity, 0) for f in findings)
        return max(0, 100 - total_deduction)