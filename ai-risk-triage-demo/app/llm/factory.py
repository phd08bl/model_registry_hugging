from __future__ import annotations

from app.config import Settings
from app.llm.base import LLMClient, LLMRuntimeError
from app.llm.mock import MockLLMClient
from app.llm.ollama import OllamaLLMClient


class FallbackLLMClient(LLMClient):
    """Uses Ollama when available and records any explicit fallback to the mock."""

    runtime_name = "ollama-with-mock-fallback"

    def __init__(self, primary: OllamaLLMClient, fallback: MockLLMClient):
        self.primary = primary
        self.fallback = fallback
        self.last_runtime = "not_called"
        self.last_error = ""

    def health(self) -> tuple[bool, str]:
        available, message = self.primary.health()
        if available:
            return True, message
        return False, f"{message} The governed mock fallback is enabled."

    def _call(self, method: str, *args):
        try:
            result = getattr(self.primary, method)(*args)
            self.last_runtime = "ollama"
            self.last_error = ""
            return result
        except LLMRuntimeError as exc:  # pragma: no cover - requires service failure
            self.last_runtime = "mock_fallback"
            self.last_error = str(exc)
            return getattr(self.fallback, method)(*args)

    def extract_evidence(self, questionnaire, numbered_evidence):
        return self._call("extract_evidence", questionnaire, numbered_evidence)

    def challenge(self, state):
        return self._call("challenge", state)

    def propose_action(self, state, allowed_actions, allowed_tools):
        return self._call("propose_action", state, allowed_actions, allowed_tools)

    def runtime_metadata(self):
        return {
            "runtime": self.runtime_name,
            "selected_runtime": self.last_runtime,
            "ollama_model": self.primary.model,
            "fallback_error": self.last_error,
        }


def build_llm_client(settings: Settings) -> LLMClient:
    if settings.llm_mode.lower() == "mock":
        return MockLLMClient()

    primary = OllamaLLMClient(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        timeout_seconds=settings.ollama_timeout_seconds,
    )
    if settings.allow_mock_fallback:
        return FallbackLLMClient(primary, MockLLMClient())
    return primary
