from ..memory.base import Command
from ..memory.registry import register_command
from ..tools.registry import get_tool


def _get_coding_tool():
    return get_tool("coding")


@register_command("explain_file")
class ExplainFileCommand(Command):
    """Returns a structured understanding of a source file."""

    description = "Analyze and summarize a source file."
    parameters = {
        "path": "Path to the source file to analyze.",
    }

    def execute(self, params: dict) -> str:
        path = params.get("path", "").strip()
        if not path:
            return "Please provide a file path to explain."

        tool = _get_coding_tool()
        summary = tool.execute(operation="summarize_file", path=path)
        if not summary.success:
            return summary.error

        imports = tool.execute(operation="list_imports", path=path)
        import_count = len(imports.data.get("imports", [])) if imports.success else 0

        todos = tool.execute(operation="detect_todos", path=path, max_results=10)
        todo_count = len(todos.data.get("todos", [])) if todos.success else 0

        language = tool.execute(operation="detect_language", path=path)
        language_name = language.data.get("language", "Unknown") if language.success else "Unknown"

        lines = summary.data.get("lines", 0)
        size = summary.data.get("size", 0)

        response = (
            f"File: {path}\n"
            f"Language: {language_name}\n"
            f"Lines: {lines}\n"
            f"Size: {size} bytes\n"
            f"Imports: {import_count}\n"
            f"TODOs/FIXMEs: {todo_count}\n"
        )

        if todo_count:
            response += "\nTODOs/FIXMEs:\n"
            for item in todos.data.get("todos", []):
                response += f"  Line {item['line']}: {item['content']}\n"

        return response


@register_command("list_project")
class ListProjectCommand(Command):
    """Lists the top-level structure of a project directory."""

    description = "List the top-level files and directories of a project."
    parameters = {
        "path": "Path to the project directory.",
    }

    def execute(self, params: dict) -> str:
        path = params.get("path", "").strip()
        if not path:
            return "Please provide a project directory path."

        tool = _get_coding_tool()
        result = tool.execute(operation="summarize_project", path=path, max_results=50)
        if not result.success:
            return result.error

        entries = result.data.get("entries", [])
        if not entries:
            return f"No entries found in {path}."

        lines = [f"Project: {path}", "Entries:"]
        for entry in entries:
            prefix = "[DIR] " if entry["type"] == "directory" else "      "
            lines.append(f"{prefix}{entry['name']}")

        return "\n".join(lines)


@register_command("analyze_module")
class AnalyzeModuleCommand(Command):
    """Provides module-level analysis including imports, TODOs, and preview."""

    description = "Analyze a Python module for imports, TODOs, and structure."
    parameters = {
        "path": "Path to the Python module file.",
    }

    def execute(self, params: dict) -> str:
        path = params.get("path", "").strip()
        if not path:
            return "Please provide a module path to analyze."

        tool = _get_coding_tool()
        result = tool.execute(operation="analyze_module", path=path)
        if not result.success:
            return result.error

        data = result.data
        lines = [
            f"Module: {path}",
            f"Lines: {data.get('lines', 0)}",
            "",
            "Imports:",
        ]
        imports = data.get("imports", [])
        if imports:
            for imp in imports:
                lines.append(f"  {imp}")
        else:
            lines.append("  None")

        todos = data.get("todos", [])
        if todos:
            lines.extend(["", "TODOs/FIXMEs:"])
            for item in todos:
                lines.append(f"  Line {item['line']}: {item['content']}")

        preview = data.get("preview", "")
        if preview:
            lines.extend(["", "Preview:", preview])

        return "\n".join(lines)