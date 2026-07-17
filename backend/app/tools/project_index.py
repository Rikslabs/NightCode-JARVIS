import os
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, field

from app.tools.coding import CodingTool


@dataclass
class FileMetadata:
    path: str
    language: str
    size: int
    lines: int
    category: str  # source, test, config, docs, asset, unknown
    imports: list[str] = field(default_factory=list)


class ProjectIndex:
    """Read-only project intelligence engine."""

    SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".next", ".turbo"}

    def __init__(self, root_path: str):
        self.root = Path(root_path).resolve()
        self.files: dict[str, FileMetadata] = {}
        self.modules: dict[str, list[str]] = {}
        self.dependencies: dict[str, list[str]] = {}
        self.project_type: Optional[str] = None
        self.package_manager: Optional[str] = None
        self.entry_points: list[str] = []
        self._coding = CodingTool()

    def build_index(self) -> dict[str, Any]:
        self._detect_project_type()
        self._scan_directory(self.root)
        return self.get_project_summary()

    def refresh_index(self) -> dict[str, Any]:
        self.files.clear()
        self.modules.clear()
        self.dependencies.clear()
        self.entry_points.clear()
        return self.build_index()

    def get_project_summary(self) -> dict[str, Any]:
        stats = {
            "total_files": len(self.files),
            "by_language": {},
            "by_category": {},
            "project_type": self.project_type,
            "package_manager": self.package_manager,
            "entry_points": self.entry_points,
            "modules": list(self.modules.keys()),
        }
        for meta in self.files.values():
            stats["by_language"][meta.language] = stats["by_language"].get(meta.language, 0) + 1
            stats["by_category"][meta.category] = stats["by_category"].get(meta.category, 0) + 1
        return stats

    def get_file_metadata(self, path: str) -> Optional[dict[str, Any]]:
        meta = self.files.get(path)
        if not meta:
            return None
        return {
            "path": meta.path,
            "language": meta.language,
            "size": meta.size,
            "lines": meta.lines,
            "category": meta.category,
            "imports": meta.imports,
        }

    def get_dependencies(self, path: str) -> list[str]:
        return self.dependencies.get(path, [])

    def find_entry_points(self) -> list[str]:
        return self.entry_points

    def list_modules(self) -> list[str]:
        return list(self.modules.keys())

    def search_module(self, name: str) -> list[str]:
        name_lower = name.lower()
        return [p for mod, paths in self.modules.items() for p in paths if name_lower in mod.lower()]

    def _detect_project_type(self) -> None:
        if (self.root / "package.json").exists():
            self.project_type = "Node.js"
            self.package_manager = "npm"
        elif (self.root / "pyproject.toml").exists() or (self.root / "setup.py").exists():
            self.project_type = "Python"
            self.package_manager = "pip"
        elif (self.root / "pom.xml").exists():
            self.project_type = "Java"
            self.package_manager = "maven"
        elif (self.root / "go.mod").exists():
            self.project_type = "Go"
            self.package_manager = "go modules"
        elif (self.root / "Cargo.toml").exists():
            self.project_type = "Rust"
            self.package_manager = "cargo"

    def _scan_directory(self, directory: Path) -> None:
        if not directory.exists() or not directory.is_dir():
            return
        for child in sorted(directory.iterdir()):
            if child.is_dir():
                if child.name in self.SKIP_DIRS:
                    continue
                if child.name == "src":
                    self._scan_source_tree(child)
                    continue
                self._scan_directory(child)
            elif child.is_file():
                self._index_file(child)

    def _scan_source_tree(self, directory: Path) -> None:
        if not directory.exists() or not directory.is_dir():
            return
        for child in sorted(directory.rglob("*")):
            if child.is_dir():
                if child.name in self.SKIP_DIRS:
                    continue
                continue
            if child.is_file():
                self._index_file(child)

    def _index_file(self, path: Path) -> None:
        rel = str(path.relative_to(self.root))
        meta = self._coding.execute(operation="detect_language", path=str(path))
        language = meta.data.get("language", "Unknown") if meta.success else "Unknown"

        size = path.stat().st_size if path.exists() else 0
        lines = 0
        content = ""
        if path.is_file():
            try:
                content = path.read_text(encoding="utf-8", errors="replace")
                lines = len(content.splitlines())
            except Exception:
                pass

        category = self._categorize(path, language)
        imports = self._extract_imports(content, language) if language == "Python" else []

        self.files[rel] = FileMetadata(
            path=rel,
            language=language,
            size=size,
            lines=lines,
            category=category,
            imports=imports,
        )

        if language == "Python" and path.stem != "__init__":
            module_name = path.stem.replace("-", "_")
            self.modules.setdefault(module_name, []).append(rel)

        self.dependencies[rel] = imports

        if category in {"entry", "test"}:
            self.entry_points.append(rel)

    def _categorize(self, path: Path, language: str) -> str:
        name = path.name
        parent = path.parent.name
        if language in {"Python"} and (name.startswith("test_") or name.endswith("_test.py") or parent == "tests"):
            return "test"
        if parent in {"__tests__", "tests", "test"}:
            return "test"
        if language in {"JSON", "YAML", "Markdown", "HTML", "CSS"}:
            return "config" if parent in {"config", "configs"} else "docs"
        if path.suffix.lower() in {".png", ".jpg", ".svg", ".gif", ".ico", ".woff", ".ttf"}:
            return "asset"
        if language == "Unknown" and path.suffix.lower() in {".env", ".gitignore", ".dockerignore"}:
            return "config"
        if parent in {"docs", "documentation", "wiki"}:
            return "docs"
        if language == "Python" and path.name in {"app.py", "main.py", "manage.py"}:
            return "entry"
        if name in {"index.js", "index.ts", "main.js", "main.ts", "app.js", "app.ts"}:
            return "entry"
        if path.suffix.lower() == ".jsx" or path.suffix.lower() == ".tsx":
            return "source"
        return "source"

    def _extract_imports(self, content: str, language: str) -> list[str]:
        if language != "Python":
            return []
        imports = []
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                imports.append(stripped)
        return imports