from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class ToolResult:
    """
    A structured result returned by every Tool execution.

    Attributes:
        success: Whether the tool operation completed successfully.
        data: The structured data produced by the tool, if any.
        error: A human-readable error message if the operation failed.
    """

    success: bool = True
    data: Any = None
    error: Optional[str] = None


class Tool(ABC):
    """
    Abstract Base Class for all JARVIS tools.

    A Tool encapsulates a single, focused business-logic operation.
    Tools are stateless, AI-agnostic, and know nothing about:
    - JarvisBrain
    - FastAPI
    - Commands
    - Ollama or any AI provider

    Tools receive typed inputs and return structured ToolResult objects.
    They never format conversational responses — that is the Command's
    responsibility.
    """

    name: str = ""
    description: str = ""
    parameters: Dict[str, str] = {}

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """
        Executes the tool's primary operation.

        Args:
            **kwargs: Typed keyword arguments matching the tool's
                      declared parameters.

        Returns:
            A ToolResult containing structured data or error information.
        """