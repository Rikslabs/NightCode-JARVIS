"""Provider connection errors safe for CLI presentation."""


class OllamaConnectionError(RuntimeError):
    """Raised when the local Ollama API cannot be reached or decoded."""


class OllamaTimeoutError(OllamaConnectionError, TimeoutError):
    """Raised when the local Ollama API exceeds its configured timeout."""
