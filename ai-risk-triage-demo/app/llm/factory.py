from __future__ import annotations

from collections.abc import Callable

from app.config import Settings
from app.llm.base import LLMClient, LLMRuntimeError
from app.llm.mock import MockLLMClient
from app.llm.ollama import OllamaLLMClient
from app.llm.openai import OpenAILLMClient

ProviderBuilder = Callable[[Settings], LLMClient]


class LLMProviderRegistry:
    """Explicit allowlist of configured LLM provider builders."""

    def __init__(self) -> None:
        self._builders: dict[str, ProviderBuilder] = {}

    @staticmethod
    def normalise(name: str) -> str:
        return name.strip().lower().replace("-", "_")

    def register(
        self,
        name: str,
        builder: ProviderBuilder,
        *,
        replace: bool = False,
    ) -> None:
        normalised = self.normalise(name)
        if not normalised:
            raise ValueError("An LLM provider name is required.")
        if normalised in self._builders and not replace:
            raise ValueError(f"LLM provider '{normalised}' is already registered.")
        self._builders[normalised] = builder

    def create(self, name: str, settings: Settings) -> LLMClient:
        normalised = self.normalise(name)
        try:
            builder = self._builders[normalised]
        except KeyError as exc:
            available = ", ".join(self.names())
            raise ValueError(
                f"Unsupported LLM_MODE '{name}'. Registered providers: {available}."
            ) from exc
        return builder(settings)

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._builders))


class FallbackLLMClient(LLMClient):
    """Uses a configured primary provider and records fallback to the governed mock."""

    runtime_name = "llm-with-mock-fallback"

    def __init__(self, primary: LLMClient, fallback: MockLLMClient):
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
            self.last_runtime = self.primary.runtime_name
            self.last_error = ""
            return result
        except LLMRuntimeError as exc:  # pragma: no cover - live provider failure
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
            "primary": self.primary.runtime_metadata(),
            "fallback_enabled": True,
            "fallback_error": self.last_error,
        }


def _build_mock(settings: Settings) -> LLMClient:
    del settings
    return MockLLMClient()


def _build_ollama(settings: Settings) -> LLMClient:
    return OllamaLLMClient(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        timeout_seconds=settings.ollama_timeout_seconds,
    )


def _openai_credentials(settings: Settings, mode: str) -> tuple[str, str]:
    if settings.openai_api_key is None:
        raise ValueError(f"OPENAI_API_KEY is required for LLM_MODE={mode}.")
    model = settings.openai_model.strip()
    if not model:
        raise ValueError(f"OPENAI_MODEL is required for LLM_MODE={mode}.")
    return settings.openai_api_key.get_secret_value(), model


def _build_openai(settings: Settings) -> LLMClient:
    api_key, model = _openai_credentials(settings, "openai")
    return OpenAILLMClient(
        api_key=api_key,
        model=model,
        timeout_seconds=settings.openai_timeout_seconds,
        store_responses=settings.openai_store_responses,
    )


def _build_openai_compatible(settings: Settings) -> LLMClient:
    api_key, model = _openai_credentials(settings, "openai_compatible")
    if not settings.openai_base_url:
        raise ValueError(
            "OPENAI_BASE_URL is required for LLM_MODE=openai_compatible."
        )
    return OpenAILLMClient(
        api_key=api_key,
        model=model,
        base_url=settings.openai_base_url,
        timeout_seconds=settings.openai_timeout_seconds,
        store_responses=settings.openai_store_responses,
        provider_name="openai_compatible",
    )


DEFAULT_LLM_PROVIDER_REGISTRY = LLMProviderRegistry()
DEFAULT_LLM_PROVIDER_REGISTRY.register("mock", _build_mock)
DEFAULT_LLM_PROVIDER_REGISTRY.register("ollama", _build_ollama)
DEFAULT_LLM_PROVIDER_REGISTRY.register("openai", _build_openai)
DEFAULT_LLM_PROVIDER_REGISTRY.register("openai_compatible", _build_openai_compatible)


def register_llm_provider(
    name: str,
    builder: ProviderBuilder,
    *,
    replace: bool = False,
) -> None:
    """Register an explicitly imported provider builder for application startup."""

    DEFAULT_LLM_PROVIDER_REGISTRY.register(name, builder, replace=replace)


def build_llm_client(
    settings: Settings,
    registry: LLMProviderRegistry = DEFAULT_LLM_PROVIDER_REGISTRY,
) -> LLMClient:
    mode = registry.normalise(settings.llm_mode)
    primary = registry.create(mode, settings)
    if mode == "mock" or not settings.allow_mock_fallback:
        return primary
    return FallbackLLMClient(primary, MockLLMClient())
