"""Minimal client for Ollama discovery and non-streaming generation."""

import json
from contextlib import closing
from typing import Any, Callable, Dict, List, Optional, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .exceptions import OllamaConnectionError, OllamaTimeoutError


class HttpResponse(Protocol):
    def read(self) -> bytes: ...

    def close(self) -> None: ...


class OllamaClient:
    """Discover local models and request one non-streaming response."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:11434",
        timeout_seconds: float = 2.0,
        generation_timeout_seconds: float = 60.0,
        opener: Callable[..., HttpResponse] = urlopen,
    ) -> None:
        if timeout_seconds <= 0 or generation_timeout_seconds <= 0:
            raise ValueError("timeout values must be greater than zero")
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._generation_timeout_seconds = generation_timeout_seconds
        self._opener = opener

    def list_models(self) -> List[str]:
        """Return locally installed model names from ``/api/tags``."""
        payload = self._request_json("/api/tags")
        models = payload.get("models", [])
        if not isinstance(models, list):
            raise OllamaConnectionError("Ollama returned an invalid model list.")
        return [
            str(item.get("name") or item.get("model"))
            for item in models
            if isinstance(item, dict) and (item.get("name") or item.get("model"))
        ]

    def generate(self, model: str, prompt: str) -> str:
        """Request one non-streaming response from a selected local model."""
        payload = self._request_json(
            "/api/generate",
            {"model": model, "prompt": prompt, "stream": False},
            self._generation_timeout_seconds,
        )
        response = payload.get("response")
        if not isinstance(response, str):
            raise OllamaConnectionError("Ollama returned an invalid generation response.")
        return response

    def _request_json(
        self,
        path: str,
        body: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        data = json.dumps(body).encode("utf-8") if body is not None else None
        request = Request(
            f"{self._base_url}{path}",
            data=data,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            method="POST" if data is not None else "GET",
        )
        try:
            with closing(self._opener(
                request,
                timeout=timeout or self._timeout_seconds,
            )) as response:
                decoded: Any = json.loads(response.read().decode("utf-8"))
        except TimeoutError as exc:
            raise OllamaTimeoutError("Ollama request timed out.") from exc
        except (HTTPError, URLError, OSError) as exc:
            raise OllamaConnectionError("Ollama server is unavailable.") from exc
        except (UnicodeDecodeError, json.JSONDecodeError, AttributeError, TypeError) as exc:
            raise OllamaConnectionError("Ollama returned an invalid response.") from exc

        if not isinstance(decoded, dict):
            raise OllamaConnectionError("Ollama returned an invalid response.")
        return decoded
