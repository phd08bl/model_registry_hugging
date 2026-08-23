from __future__ import annotations

import json
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel

from app.llm.base import LLMRuntimeError, StructuredLLMClient

T = TypeVar("T", bound=BaseModel)


class OllamaLLMClient(StructuredLLMClient):
    """Small governed adapter around Ollama's local /api/chat endpoint."""

    runtime_name = "ollama"

    def __init__(self, base_url: str, model: str, timeout_seconds: float = 120.0):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    @staticmethod
    def _error_summary(exc: Exception) -> str:
        response = getattr(exc, "response", None)
        status_code = getattr(response, "status_code", None)
        status = f" (HTTP {status_code})" if status_code is not None else ""
        return f"{type(exc).__name__}{status}"

    def health(self) -> tuple[bool, str]:
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=3.0)
            response.raise_for_status()
            models = [item.get("name", "") for item in response.json().get("models", [])]
            if any(name == self.model or name.startswith(f"{self.model}:") for name in models):
                return True, f"Ollama is available and model '{self.model}' is installed."
            return False, f"Ollama is available but model '{self.model}' is not installed."
        except (httpx.HTTPError, KeyError, ValueError) as exc:  # pragma: no cover
            return False, f"Ollama is unavailable: {self._error_summary(exc)}"

    def _structured(self, system: str, user: str, response_model: type[T]) -> T:
        schema = response_model.model_json_schema()
        grounded_user = (
            f"{user}\n\nReturn only JSON matching this schema:\n"
            f"{json.dumps(schema, ensure_ascii=False)}"
        )
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": grounded_user},
            ],
            "format": schema,
            "stream": False,
            "options": {"temperature": 0},
        }
        try:
            response = httpx.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            content = response.json()["message"]["content"]
            return response_model.model_validate_json(content)
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            raise LLMRuntimeError(
                f"Ollama structured-output call failed: {self._error_summary(exc)}"
            ) from exc

    def runtime_metadata(self) -> dict[str, Any]:
        return {
            "runtime": self.runtime_name,
            "base_url": self.base_url,
            "model": self.model,
            "structured_output": True,
        }
