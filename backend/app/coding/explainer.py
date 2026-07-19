"""Read-only Python code explanations."""

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Union

from .reader import FileReader
from .symbols import PythonSymbolIndex


@dataclass(frozen=True)
class FileExplanation:
    """Structural summary of a source file."""

    module_name: str
    imports: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    async_functions: List[str] = field(default_factory=list)
    public_api_count: int = 0
    private_member_count: int = 0
    line_count: int = 0
    has_docstring: bool = False
    detected_language: str = "Unknown"


@dataclass(frozen=True)
class SymbolExplanation:
    """Source-level details for a named symbol."""

    name: str
    symbol_type: str
    location: str
    parent: Optional[str] = None
    signature: Optional[str] = None
    docstring: Optional[str] = None


class CodeExplainer:
    """Explain Python files and symbols without importing or executing them."""

    def __init__(
        self,
        project_root: Union[str, Path],
        reader: Optional[FileReader] = None,
        symbol_index: Optional[PythonSymbolIndex] = None,
    ) -> None:
        self._project_root = Path(project_root).expanduser()
        self._reader = reader or FileReader(self._project_root)
        self._symbol_index = symbol_index or PythonSymbolIndex(self._project_root)

    def explain_file(self, path: Union[str, Path]) -> FileExplanation:
        """Return a structural explanation of a source file."""
        relative_path = Path(path)
        source = self._reader.read_text(relative_path)
        module_name = relative_path.with_suffix("").as_posix().replace("/", ".")
        language = "Python" if relative_path.suffix.lower() == ".py" else "Unknown"
        line_count = len(source.splitlines())

        if language != "Python":
            return FileExplanation(
                module_name=module_name,
                line_count=line_count,
                detected_language=language,
            )

        try:
            tree = ast.parse(source, filename=relative_path.as_posix())
        except SyntaxError:
            return FileExplanation(
                module_name=module_name,
                line_count=line_count,
                detected_language=language,
            )

        imports: List[str] = []
        classes: List[str] = []
        functions: List[str] = []
        async_functions: List[str] = []

        for node in tree.body:
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module or "")
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, ast.FunctionDef):
                functions.append(node.name)
            elif isinstance(node, ast.AsyncFunctionDef):
                async_functions.append(node.name)

        public_names = classes + functions + async_functions
        private_count = sum(
            1
            for node in ast.walk(tree)
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name.startswith("_")
        )
        return FileExplanation(
            module_name=module_name,
            imports=[name for name in imports if name],
            classes=classes,
            functions=functions,
            async_functions=async_functions,
            public_api_count=sum(not name.startswith("_") for name in public_names),
            private_member_count=private_count,
            line_count=line_count,
            has_docstring=ast.get_docstring(tree) is not None,
            detected_language=language,
        )

    def explain_symbol(self, name: str) -> SymbolExplanation:
        """Return source details for the first exact symbol match."""
        matches = self._symbol_index.search(name, exact=True)
        if not matches:
            raise KeyError(f"Symbol not found: {name}")
        symbol = matches[0]
        source = self._reader.read_text(symbol.relative_file_path)
        try:
            tree = ast.parse(source, filename=symbol.relative_file_path)
        except SyntaxError as exc:
            raise ValueError(f"Cannot explain malformed Python file: {symbol.relative_file_path}") from exc

        node = self._find_node(tree, symbol.name, symbol.line_number)
        signature = self._signature(node) if node is not None else None
        docstring = ast.get_docstring(node) if isinstance(
            node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
        ) else None
        return SymbolExplanation(
            name=symbol.name,
            symbol_type=symbol.symbol_type,
            location=f"{symbol.relative_file_path}:{symbol.line_number}",
            parent=symbol.parent_symbol,
            signature=signature,
            docstring=docstring,
        )

    @staticmethod
    def _find_node(tree: ast.Module, name: str, line_number: int) -> Optional[ast.AST]:
        for node in ast.walk(tree):
            if getattr(node, "lineno", None) == line_number and getattr(node, "name", None) == name:
                return node
        return tree if line_number == 1 else None

    @staticmethod
    def _signature(node: ast.AST) -> Optional[str]:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return None
        signature = f"{node.name}({ast.unparse(node.args)})"
        if node.returns is not None:
            signature += f" -> {ast.unparse(node.returns)}"
        return signature
