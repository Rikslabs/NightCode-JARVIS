from typing import Optional

from app.brain.matcher import CommandMatcher
from app.memory import registry


class CommandDispatcher:
    """
    Orchestrates command detection, lookup, and execution.

    This class is the link between the JarvisBrain and the command framework.
    It uses a swappable "matcher" to determine if a message is a command,
    then retrieves the command from the registry and executes it.
    """

    def __init__(self, matcher: CommandMatcher):
        """
        Initializes the dispatcher.

        Args:
            matcher: A swappable component for matching user input to commands.
        """
        self._matcher = matcher
        self._registry = registry

    def dispatch(self, message: str) -> Optional[str]:
        """
        Attempts to map a user message to a command and execute it.

        If a command is found and executed, its response is returned.
        If no command is matched, it returns None, signaling the caller
        to proceed with standard conversational AI.

        Args:
            message: The user's input message.

        Returns:
            The command's string response if executed, otherwise None.
        """
        command_details = self._registry.get_command_details()
        if not command_details:
            return None

        # Pass the original message (preserving case) to the matcher.
        # The matcher handles lowercasing internally for keyword matching.
        match_result = self._matcher.match(message, command_details)

        if match_result:
            intent = match_result.get("intent")
            params = match_result.get("params", {})
            command = self._registry.get_command(intent)

            if command:
                try:
                    # Execute the command and return its result
                    return command.execute(params)
                except Exception as e:
                    # Basic error handling for production
                    print(f"ERROR: Command execution failed for intent '{intent}': {e}")
                    return f"Sorry, I encountered an error executing that command."

        # No command was matched
        return None
