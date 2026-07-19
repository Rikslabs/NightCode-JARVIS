"""Read-only Python symbol discovery."""

import ast
from pathlib import Path
from typing import List, Optional, Tuple, Union

from .explorer import RepositoryExplorer
from .models import PythonSymbol


class _SymbolVisitor(ast.NodeVisitor):
    """Collect named symbols while tracking lexical parents."""

    def __init__(self, relative_file_path: str) -> None:
        self.symbols: List[PythonSymbol] = []
        self._relative_file_path = relative_file_path
        self._parents: List[Tuple[str, str]] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._add(node.name, "class", node.lineno)
        self._visit_children(node, node.name, "class")

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        symbol_type = "method" if self._inside_class() else "function"
        self._add(node.name, symbol_type, node.lineno)
        self._visit_children(node, node.name, symbol_type)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        symbol_type = "method" if self._inside_class() else "async_function"
        self._add(node.name, symbol_type, node.lineno)
        self._visit_children(node, node.name, symbol_type)

    def _add(self, name: str, symbol_type: str, line_number: int) -> None:
        self.symbols.append(PythonSymbol(
            name=name,
            symbol_type=symbol_type,
            relative_file_path=self._relative_file_path,
            line_number=line_number,
            parent_symbol=self._parents[-1][0] if self._parents else None,
        ))

    def _visit_children(self, node: ast.AST, name: str, symbol_type: str) -> None:
        self._parents.append((name, symbol_type))
        self.generic_visit(node)
        self._parents.pop()

    def _inside_class(self) -> bool:
        return bool(self._parents and self._parents[-1][1] == "class")


class PythonSymbolIndex:
    """Discover and search Python symbols under a project root."""

    def __init__(
        self,
        project_root: Union[str, Path],
        explorer: Optional[RepositoryExplorer] = None,
    ) -> None:
        self._project_root = Path(project_root).expanduser()
        self._explorer = explorer or RepositoryExplorer(self._project_root)
        self._symbols: List[PythonSymbol] = []
        self._indexed = False

    def index(self) -> List[PythonSymbol]:
        """Build and return a fresh in-memory symbol index."""
        root = self._project_root.resolve()
        symbols: List[PythonSymbol] = []

        for file_entry in self._explorer.list_files(".py"):
            path = root / file_entry.relative_path
            try:
                source = path.read_text(encoding="utf-8")
                tree = ast.parse(source, filename=file_entry.relative_path)
            except (OSError, UnicodeError, SyntaxError):
                continue

            module_name = Path(file_entry.relative_path).with_suffix("").as_posix().replace("/", ".")
            symbols.append(PythonSymbol(
                name=module_name,
                symbol_type="module",
                relative_file_path=file_entry.relative_path,
                line_number=1,
            ))
            visitor = _SymbolVisitor(file_entry.relative_path)
            visitor.visit(tree)
            symbols.extend(visitor.symbols)

        self._symbols = symbols
        self._indexed = True
        return list(symbols)

    def search(self, name: str, exact: bool = False) -> List[PythonSymbol]:
        """Search indexed symbol names exactly or by case-insensitive substring."""
        if not self._indexed:
            self.index()
        query = name.casefold()
        if exact:
            return [symbol for symbol in self._symbols if symbol.name.casefold() == query]
        return [symbol for symbol in self._symbols if query in symbol.name.casefold()]
