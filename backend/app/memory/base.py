from abc import ABC, abstractmethod
from typing import Dict, Optional


class Command(ABC):
    """
    Abstract Base Class for all JARVIS commands.

    This class defines a common interface for all commands, ensuring that the
    JarvisBrain can execute any command in a uniform way. Each concrete command
    must implement the `execute` method.

    Subclasses may set:
        description (str): A human-readable description of what the command
            does. Used by the LLM intent engine for classification. Falls back
            to the class docstring if not set.
        parameters (Dict[str, str]): A mapping of parameter names to their
            descriptions. Used by the LLM intent engine to extract structured
            parameters from user messages.
    """

    description: Optional[str] = None
    parameters: Optional[Dict[str, str]] = None

    @abstractmethod
    def execute(self, params: dict) -> str:
        """
        Executes the command's primary logic.

        Args:
            params: A dictionary of parameters extracted by the LLM from the
                    user's query (e.g., {'location': 'San Francisco'}).

        Returns:
            A string response to be communicated back to the user.
        """
