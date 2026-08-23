from __future__ import annotations

from typing import Any, TypeVar

from openai import OpenAI, OpenAIError
from pydantic import BaseModel, ValidationError

from app.llm.base import LLMRuntimeError, StructuredLLMClient

T = TypeVar("T", bound=BaseModel)


class OpenAILLMClient(StructuredLLMClient):
    """Governed adapter for OpenAI and tested Responses-compatible endpoints."""

    runtime_name = "openai"

    def __init__(
        self,
        api_key: str,
        model: str,
        timeout_seconds: float = 120.0,
        base_url: str | None = None,
        store_responses: bool = False,
        provider_name: str = "openai",
        client: OpenAI | None = None,
    ):
        if not model.strip():
            raise ValueError("An OpenAI model ID is required.")
        if not provider_name.strip():
            raise ValueError("A provider name is required.")

        self.runtime_name = provider_name.strip().lower()
        self.model = model.strip()
        self.base_url = base_url.rstrip("/") if base_url else None
        self.timeout_seconds = timeout_seconds
        self.store_responses = store_responses
        self.client = client or OpenAI(
            api_key=api_key,
            base_url=self.base_url,
            timeout=timeout_seconds,
        )

    @staticmethod
    def _error_summary(exc: Exception) -> str:
        status_code = getattr(exc, "status_code", None)
        status = f" (HTTP {status_code})" if status_code is not None else ""
        return f"{type(exc).__name__}{status}"

    def health(self) -> tuple[bool, str]:
        try:
            self.client.models.retrieve(self.model)
            return True, f"{self.runtime_name} model '{self.model}' is available."
        except OpenAIError as exc:  # pragma: no cover - requires a live service
            return False, (
                f"{self.runtime_name} is unavailable: {self._error_summary(exc)}"
            )

    def _structured(self, system: str, user: str, response_model: type[T]) -> T:
        try:
            response = self.client.responses.parse(
                model=self.model,
                instructions=system,
                input=user,
                text_format=response_model,
                store=self.store_responses,
            )
            parsed = response.output_parsed
            if parsed is None:
                raise LLMRuntimeError(
                    f"{self.runtime_name} returned no parsed structured output."
                )
            return parsed
        except LLMRuntimeError:
            raise
        except (OpenAIError, ValidationError, TypeError, ValueError) as exc:
            raise LLMRuntimeError(
                f"{self.runtime_name} structured-output call failed: "
                f"{self._error_summary(exc)}"
            ) from exc

    def runtime_metadata(self) -> dict[str, Any]:
        return {
            "runtime": self.runtime_name,
            "model": self.model,
            "endpoint_type": "openai" if self.base_url is None else "openai_compatible",
            "structured_output": True,
            "response_storage_requested": self.store_responses,
        }
