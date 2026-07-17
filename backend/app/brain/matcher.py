import json
from typing import Any, Dict, Optional

from app.ai.provider import AIProvider


class CommandMatcher:
    """
    Matches user messages to registered commands.

    This implementation uses a two-tier strategy:
    1. Fast keyword-based matching as the first pass.
    2. LLM-based intent classification as the second pass (if an AI provider
       is configured).

    Keyword matching is cheap and handles explicit command-like phrases
    (e.g., "system status"). The LLM pass handles natural language variations
    and parameter extraction (e.g., "my name is Vikash" → remember_name).

    This class is the Stage 4A LLM Intent Engine entry point.
    """

    def __init__(self, ai_provider: Optional[AIProvider] = None):
        """
        Initializes the matcher.

        Args:
            ai_provider: An optional AI provider for LLM-based intent
                         classification. If None, only keyword matching
                         is used.
        """
        self._ai_provider = ai_provider

    def match(
        self, message: str, command_details: Dict[str, Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Matches a message against available commands.

        Execution order:
        1. Keyword matching (fast path, no LLM call).
        2. LLM intent classification (slow path, calls AI provider).

        Args:
            message: The user's input message (original case preserved).
            command_details: A dictionary mapping intent names to their
                             metadata (description, parameters).

        Returns:
            A dictionary with 'intent' and 'params' if a command is matched,
            otherwise None.
        """
        # Step 1: Keyword matching — fast path, no LLM call
        result = self._keyword_match(message, command_details)
        if result is not None:
            return result

        # Step 2: LLM intent classification — slow path
        if self._ai_provider is not None:
            return self._llm_match(message, command_details)

        return None

    def _llm_match(
        self, message: str, command_details: Dict[str, Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Uses the AI provider to classify the user's intent.

        Constructs a system prompt listing all available commands with their
        descriptions and expected parameters, then asks the LLM to return a
        JSON object with the matched intent and any extracted parameters.

        Args:
            message: The user's input message (original case preserved).
            command_details: A dictionary of available command metadata.

        Returns:
            A dictionary with 'intent' and 'params' if the LLM successfully
            identified a command, otherwise None.
        """
        if not command_details:
            return None

        # Build the intent list for the prompt with parameter schemas
        intent_lines = []
        for intent, meta in command_details.items():
            description = meta.get("description", "")
            parameters = meta.get("parameters", {})
            line = f"- {intent}: {description}"
            if parameters:
                param_desc = ", ".join(
                    f"{name}: {desc}" for name, desc in parameters.items()
                )
                line += f"  Parameters: {param_desc}"
            intent_lines.append(line)

        intent_list = "\n".join(intent_lines)

        prompt = (
            "You are an intent classification system. Your task is to "
            "analyse the user's message and determine which registered "
            "command (if any) they want to execute.\n\n"
            "Available commands:\n"
            f"{intent_list}\n\n"
            "Respond with a JSON object in exactly this format:\n"
            '{"intent": "command_name", "params": {"key": "value"}}\n\n'
            'If no command matches, respond with: {"intent": null, "params": {}}\n\n'
            "Extract parameters from the message where applicable. "
            "For example, if a command requires a 'name' parameter, "
            "extract the name from the user's message preserving its "
            "original capitalisation.\n\n"
            f"User message: {message}"
        )

        try:
            raw_response = self._ai_provider.generate(prompt)
        except Exception:
            # If the LLM call fails, return None
            return None

        return self._parse_llm_response(raw_response, command_details)

    def _parse_llm_response(
        self, raw_response: str, command_details: Dict[str, Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Parses the LLM's response into a structured intent result.

        Handles cases where the LLM wraps JSON in markdown code blocks
        or includes additional text around the JSON.

        Args:
            raw_response: The raw string response from the AI provider.
            command_details: A dictionary of available command metadata.

        Returns:
            A validated dictionary with 'intent' and 'params', or None if
            parsing fails or the intent is not recognised.
        """
        # Strip markdown code blocks if present
        text = raw_response.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines).strip()

        try:
            parsed = json.loads(text)
        except (json.JSONDecodeError, ValueError):
            return None

        intent = parsed.get("intent")
        params = parsed.get("params", {})

        if not intent or intent not in command_details:
            return None

        return {"intent": intent, "params": params}

    def _keyword_match(
        self, message: str, command_details: Dict[str, Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Performs case-insensitive keyword matching.

        Args:
            message: The user's input message (original case preserved).
            command_details: A dictionary of available command metadata.

        Returns:
            A dictionary with 'intent' and 'params' if a keyword match is
            found, otherwise None.
        """
        lower_message = message.lower()
        for intent in command_details.keys():
            trigger_phrase = intent.replace("_", " ")
            if trigger_phrase in lower_message:
                return {"intent": intent, "params": {}}
        return None
