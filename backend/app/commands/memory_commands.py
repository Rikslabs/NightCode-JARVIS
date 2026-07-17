from ..memory.base import Command
from ..memory.registry import register_command
from ..tools.registry import get_tool


@register_command("remember_name")
class RememberNameCommand(Command):
    """
    Stores the user's name in persistent memory.
    """

    description = "Stores the user's name in persistent memory."
    parameters = {
        "name": "The user's name to remember.",
    }

    def execute(self, params: dict) -> str:
        """
        Executes the remember name command.

        Delegates storage to MemoryTool and formats the result.

        Args:
            params: A dictionary of parameters. Expected key: "name" (string)
                    containing the user's name as extracted by the LLM.

        Returns:
            A confirmation string with the remembered name.
        """
        name = params.get("name", "").strip()

        if not name:
            return "I couldn't determine your name. Please tell me your name."

        tool = get_tool("memory")
        result = tool.execute(operation="set", key="name", value=name)

        if not result.success:
            return f"Sorry, I couldn't remember your name. {result.error}"

        return f"I'll remember that. Hello, {name}."


@register_command("get_name")
class GetNameCommand(Command):
    """
    Retrieves the user's name from persistent memory and returns it.
    """

    description = "Retrieves the user's name from persistent memory."

    def execute(self, params: dict) -> str:
        """
        Executes the get name command.

        Delegates retrieval to MemoryTool and formats the result.

        Args:
            params: A dictionary of parameters (not used for this command).

        Returns:
            A string containing the user's name, or a message indicating
            that the name is unknown.
        """
        tool = get_tool("memory")
        result = tool.execute(operation="get", key="name")

        if not result.success:
            return f"Sorry, I couldn't retrieve your name. {result.error}"

        if result.data:
            return f"Your name is {result.data}."

        return "I don't know your name yet."
