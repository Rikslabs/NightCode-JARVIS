import ast
import os
from pathlib import Path
from typing import Optional

from .base import Tool, ToolResult
from .registry import register_tool


@register_tool("coding")
class CodingTool(Tool):
    """Read-only source code inspection and understanding tool."""

    name = "coding"
    description = "Read-only tool for inspecting, analyzing, and understanding source code files and projects."
    parameters = {
        "operation": "Operation to perform: 'read_file', 'list_dir', 'search_files', 'search_text', 'detect_language', 'summarize_file', 'explain_class', 'explain_function', 'list_imports', 'detect_todos', 'detect_large_functions', 'detect_duplicates', 'summarize_project', 'analyze_module'.",
        "path": "File or directory path.",
        "pattern": "Filename glob pattern for search_files.",
        "query": "Text pattern for search_text.",
        "max_results": "Maximum number of results to return (optional, default 50).",
        "name": "Class or function name for explain_class or explain_function.",
    }

    def execute(
        self,
        operation: str,
        path: Optional[str] = None,
        pattern: Optional[str] = None,
        query: Optional[str] = None,
        max_results: int = 50,
        name: Optional[str] = None,
    ) -> ToolResult:
        """Execute a read-only code inspection or analysis operation."""
        try:
            if operation == "read_file":
                return self._read_file(path)
            if operation == "list_dir":
                return self._list_dir(path)
            if operation == "search_files":
                return self._search_files(path, pattern, max_results)
            if operation == "search_text":
                return self._search_text(path, query, max_results)
            if operation == "detect_language":
                return self._detect_language(path)
            if operation == "summarize_file":
                return self._summarize_file(path)
            if operation == "explain_class":
                return self._explain_class(path, name)
            if operation == "explain_function":
                return self._explain_function(path, name)
            if operation == "list_imports":
                return self._list_imports(path)
            if operation == "detect_todos":
                return self._detect_todos(path, max_results)
            if operation == "detect_large_functions":
                return self._detect_large_functions(path, max_results)
            if operation == "detect_duplicates":
                return self._detect_duplicates(path, max_results)
            if operation == "summarize_project":
                return self._summarize_project(path, max_results)
            if operation == "analyze_module":
                return self._analyze_module(path)

            return ToolResult(
                success=False,
                error=f"Unknown coding operation: '{operation}'.",
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Coding operation failed: {e}",
            )

    def _read_file(self, path: Optional[str]) -> ToolResult:
        if not path:
            return ToolResult(success=False, error="'path' is required for read_file.")
        target = Path(path)
        if not target.exists():
            return ToolResult(success=False, error=f"Path not found: {path}")
        if not target.is_file():
            return ToolResult(success=False, error=f"Not a file: {path}")
        content = target.read_text(encoding="utf-8", errors="replace")
        return ToolResult(success=True, data={"content": content, "path": str(target)})

    def _list_dir(self, path: Optional[str]) -> ToolResult:
        if not path:
            return ToolResult(success=False, error="'path' is required for list_dir.")
        target = Path(path)
        if not target.exists():
            return ToolResult(success=False, error=f"Path not found: {path}")
        if not target.is_dir():
            return ToolResult(success=False, error=f"Not a directory: {path}")
        entries = []
        for child in target.iterdir():
            entries.append({
                "name": child.name,
                "type": "directory" if child.is_dir() else "file",
                "path": str(child),
            })
        return ToolResult(success=True, data={"entries": entries, "path": str(target)})

    def _search_files(
        self, path: Optional[str], pattern: Optional[str], max_results: int
    ) -> ToolResult:
        if not path:
            return ToolResult(success=False, error="'path' is required for search_files.")
        if not pattern:
            return ToolResult(success=False, error="'pattern' is required for search_files.")
        base = Path(path)
        if not base.exists():
            return ToolResult(success=False, error=f"Path not found: {path}")
        matches = []
        for root, _, files in os.walk(base):
            for f in files:
                if Path(f).match(pattern):
                    matches.append(os.path.join(root, f))
        matches = matches[:max_results]
        return ToolResult(success=True, data={"matches": matches, "path": str(base)})

    def _search_text(
        self, path: Optional[str], query: Optional[str], max_results: int
    ) -> ToolResult:
        if not path:
            return ToolResult(success=False, error="'path' is required for search_text.")
        if not query:
            return ToolResult(success=False, error="'query' is required for search_text.")
        base = Path(path)
        if not base.exists():
            return ToolResult(success=False, error=f"Path not found: {path}")
        matches = []
        for root, _, files in os.walk(base):
            for f in files:
                full = Path(root) / f
                try:
                    text = full.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    continue
                if query in text:
                    matches.append(str(full))
        matches = matches[:max_results]
        return ToolResult(success=True, data={"matches": matches, "query": query})

    def _detect_language(self, path: Optional[str]) -> ToolResult:
        if not path:
            return ToolResult(success=False, error="'path' is required for detect_language.")
        target = Path(path)
        if not target.exists():
            return ToolResult(success=False, error=f"Path not found: {path}")
        if not target.is_file():
            return ToolResult(success=False, error=f"Not a file: {path}")
        ext = target.suffix.lower()
        language_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".java": "Java",
            ".c": "C",
            ".cpp": "C++",
            ".h": "C/C++ Header",
            ".cs": "C#",
            ".go": "Go",
            ".rs": "Rust",
            ".rb": "Ruby",
            ".php": "PHP",
            ".swift": "Swift",
            ".kt": "Kotlin",
            ".json": "JSON",
            ".yaml": "YAML",
            ".yml": "YAML",
            ".md": "Markdown",
            ".html": "HTML",
            ".css": "CSS",
            ".sql": "SQL",
            ".sh": "Shell",
            ".bat": "Batch",
            ".ps1": "PowerShell",
            ".xml": "XML",
        }
        language = language_map.get(ext, "Unknown")
        return ToolResult(success=True, data={"path": str(target), "extension": ext, "language": language})

    def _summarize_file(self, path: Optional[str]) -> ToolResult:
        if not path:
            return ToolResult(success=False, error="'path' is required for summarize_file.")
        result = self._read_file(path)
        if not result.success:
            return result
        content = result.data["content"]
        lines = content.splitlines()
        return ToolResult(
            success=True,
            data={
                "path": str(path),
                "lines": len(lines),
                "size": len(content),
                "preview": "\n".join(lines[:50]),
            },
        )

    def _explain_class(self, path: Optional[str], name: Optional[str]) -> ToolResult:
        if not path:
            return ToolResult(success=False, error="'path' is required for explain_class.")
        if not name:
            return ToolResult(success=False, error="'name' is required for explain_class.")
        result = self._read_file(path)
        if not result.success:
            return result
        content = result.data["content"]
        matches = []
        for i, line in enumerate(content.splitlines(), 1):
            if f"class {name}" in line:
                matches.append({"line": i, "content": line.strip()})
        return ToolResult(success=True, data={"path": str(path), "class_name": name, "matches": matches})

    def _explain_function(self, path: Optional[str], name: Optional[str]) -> ToolResult:
        if not path:
            return ToolResult(success=False, error="'path' is required for explain_function.")
        if not name:
            return ToolResult(success=False, error="'name' is required for explain_function.")
        result = self._read_file(path)
        if not result.success:
            return result
        content = result.data["content"]
        matches = []
        for i, line in enumerate(content.splitlines(), 1):
            if f"def {name}" in line:
                matches.append({"line": i, "content": line.strip()})
                if i < len(content.splitlines()):
                    next_line = content.splitlines()[i]
                    if '"""' in next_line or "'''" in next_line:
                        matches.append({"line": i + 1, "content": next_line.strip()})
        return ToolResult(success=True, data={"path": str(path), "function_name": name, "matches": matches})

    def _list_imports(self, path: Optional[str]) -> ToolResult:
        if not path:
            return ToolResult(success=False, error="'path' is required for list_imports.")
        result = self._read_file(path)
        if not result.success:
            return result
        imports = []
        for line in result.data["content"].splitlines():
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                imports.append(stripped)
        return ToolResult(success=True, data={"path": str(path), "imports": imports})

    def _detect_todos(self, path: Optional[str], max_results: int) -> ToolResult:
        if not path:
            return ToolResult(success=False, error="'path' is required for detect_todos.")
        result = self._read_file(path)
        if not result.success:
            return result
        todos = []
        for i, line in enumerate(result.data["content"].splitlines(), 1):
            if "TODO" in line or "FIXME" in line:
                todos.append({"line": i, "content": line.strip()})
                if len(todos) >= max_results:
                    break
        return ToolResult(success=True, data={"path": str(path), "todos": todos})

    def _detect_large_functions(self, path: Optional[str], max_results: int) -> ToolResult:
        if not path:
            return ToolResult(success=False, error="'path' is required for detect_large_functions.")
        result = self._read_file(path)
        if not result.success:
            return result
        try:
            tree = ast.parse(result.data["content"])
        except Exception:
            return ToolResult(success=True, data={"path": str(path), "large_functions": []})
        large = []
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef):
                start = node.lineno
                end = node.end_lineno or start
                size = end - start + 1
                if size > 50:
                    large.append({"name": node.name, "start_line": start, "end_line": end, "size": size})
                    if len(large) >= max_results:
                        break
        return ToolResult(success=True, data={"path": str(path), "large_functions": large})

    def _detect_duplicates(self, path: Optional[str], max_results: int) -> ToolResult:
        if not path:
            return ToolResult(success=False, error="'path' is required for detect_duplicates.")
        target = Path(path)
        if not target.exists() or not target.is_dir():
            return ToolResult(success=False, error=f"Not a directory: {path}")
        size_map: dict[int, list[str]] = {}
        duplicates = []
        for f in target.rglob("*"):
            if f.is_file():
                size_map.setdefault(f.stat().st_size, []).append(str(f))
        for paths in size_map.values():
            if len(paths) > 1:
                for p in paths:
                    duplicates.append(p)
        return ToolResult(success=True, data={"path": str(path), "duplicates": duplicates[:max_results]})

    def _summarize_project(self, path: Optional[str], max_results: int) -> ToolResult:
        if not path:
            return ToolResult(success=False, error="'path' is required for summarize_project.")
        target = Path(path)
        if not target.exists() or not target.is_dir():
            return ToolResult(success=False, error=f"Not a directory: {path}")
        skip = {".git", "node_modules", "__pycache__", ".venv"}
        entries = []
        for child in target.iterdir():
            if child.is_dir() and child.name in skip:
                continue
            entries.append({"name": child.name, "type": "directory" if child.is_dir() else "file"})
        return ToolResult(success=True, data={"path": str(path), "entries": entries[:max_results]})

    def _analyze_module(self, path: Optional[str]) -> ToolResult:
        if not path:
            return ToolResult(success=False, error="'path' is required for analyze_module.")
        result = self._read_file(path)
        if not result.success:
            return result
        content = result.data["content"]
        lines = content.splitlines()
        imports = self._list_imports(path).data.get("imports", [])
        todos = self._detect_todos(path, 50).data.get("todos", [])
        return ToolResult(
            success=True,
            data={
                "path": str(path),
                "lines": len(lines),
                "imports": imports,
                "todos": todos,
                "preview": "\n".join(lines[:80]),
            },
        )