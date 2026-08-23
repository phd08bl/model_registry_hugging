from __future__ import annotations

from types import SimpleNamespace

import pytest
from openai import OpenAIError

from app.config import Settings
from app.llm.base import LLMRuntimeError
from app.llm.factory import (
    FallbackLLMClient,
    LLMProviderRegistry,
    build_llm_client,
)
from app.llm.mock import MockLLMClient
from app.llm.ollama import OllamaLLMClient
from app.llm.openai import OpenAILLMClient
from app.schemas import EvidenceExtraction


class FakeResponses:
    def __init__(self, parsed=None, error: Exception | None = None):
        self.parsed = parsed
        self.error = error
        self.last_request = None

    def parse(self, **kwargs):
        self.last_request = kwargs
        if self.error is not None:
            raise self.error
        return SimpleNamespace(output_parsed=self.parsed)


class FakeModels:
    def __init__(self, error: Exception | None = None):
        self.error = error
        self.retrieved_model = None

    def retrieve(self, model):
        self.retrieved_model = model
        if self.error is not None:
            raise self.error
        return SimpleNamespace(id=model)


class FakeOpenAI:
    def __init__(self, parsed=None, response_error=None, model_error=None):
        self.responses = FakeResponses(parsed, response_error)
        self.models = FakeModels(model_error)


def test_openai_adapter_reuses_governed_prompts_and_parses_typed_output():
    expected = EvidenceExtraction(summary="Supported summary")
    sdk = FakeOpenAI(parsed=expected)
    client = OpenAILLMClient(
        api_key="unused-in-test",
        model="approved-test-model",
        client=sdk,
    )

    result = client.extract_evidence(
        {"personal_data": False},
        "1: Human review is documented.",
    )

    assert result is expected
    request = sdk.responses.last_request
    assert request["model"] == "approved-test-model"
    assert request["text_format"] is EvidenceExtraction
    assert request["store"] is False
    assert "do not\nmake the final materiality" in request["instructions"]
    assert "1: Human review is documented." in request["input"]


def test_openai_adapter_rejects_missing_or_invalid_structured_output():
    missing = OpenAILLMClient(
        api_key="unused-in-test",
        model="approved-test-model",
        client=FakeOpenAI(parsed=None),
    )
    with pytest.raises(LLMRuntimeError, match="no parsed structured output"):
        missing.challenge({})

    secret = "sensitive-provider-response"
    invalid = OpenAILLMClient(
        api_key="unused-in-test",
        model="approved-test-model",
        client=FakeOpenAI(response_error=ValueError(secret)),
    )
    with pytest.raises(LLMRuntimeError) as captured:
        invalid.challenge({})
    assert "ValueError" in str(captured.value)
    assert secret not in str(captured.value)


def test_openai_health_and_metadata_are_provider_neutral_and_sanitized():
    sdk = FakeOpenAI(parsed=EvidenceExtraction(summary="ok"))
    client = OpenAILLMClient(
        api_key="unused-in-test",
        model="provider-model",
        base_url="https://provider.example/v1/",
        provider_name="example_provider",
        client=sdk,
    )

    available, message = client.health()
    assert available is True
    assert "provider-model" in message
    assert sdk.models.retrieved_model == "provider-model"
    assert client.runtime_metadata() == {
        "runtime": "example_provider",
        "model": "provider-model",
        "endpoint_type": "openai_compatible",
        "structured_output": True,
        "response_storage_requested": False,
    }

    secret = "key-or-provider-body"
    broken = OpenAILLMClient(
        api_key="unused-in-test",
        model="provider-model",
        client=FakeOpenAI(model_error=OpenAIError(secret)),
    )
    available, message = broken.health()
    assert available is False
    assert "OpenAIError" in message
    assert secret not in message


def test_factory_selects_explicit_modes_and_rejects_invalid_configuration():
    mock = build_llm_client(Settings(llm_mode="mock"))
    assert isinstance(mock, MockLLMClient)

    ollama = build_llm_client(
        Settings(llm_mode="ollama", allow_mock_fallback=False)
    )
    assert isinstance(ollama, OllamaLLMClient)

    openai = build_llm_client(
        Settings(
            llm_mode="openai",
            allow_mock_fallback=False,
            openai_api_key="test-key",
            openai_model="approved-test-model",
        )
    )
    assert isinstance(openai, OpenAILLMClient)
    assert openai.runtime_name == "openai"

    compatible = build_llm_client(
        Settings(
            llm_mode="openai-compatible",
            allow_mock_fallback=False,
            openai_api_key="test-key",
            openai_model="provider-model",
            openai_base_url="https://provider.example/v1",
        )
    )
    assert isinstance(compatible, OpenAILLMClient)
    assert compatible.runtime_name == "openai_compatible"

    with pytest.raises(ValueError, match="Unsupported LLM_MODE"):
        build_llm_client(Settings(llm_mode="misspelled-provider"))
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        build_llm_client(Settings(llm_mode="openai", openai_model="model"))
    with pytest.raises(ValueError, match="OPENAI_MODEL"):
        build_llm_client(Settings(llm_mode="openai", openai_api_key="key"))
    with pytest.raises(ValueError, match="OPENAI_BASE_URL"):
        build_llm_client(
            Settings(
                llm_mode="openai_compatible",
                openai_api_key="key",
                openai_model="model",
            )
        )


def test_provider_registry_allows_explicit_extensions_without_factory_branching():
    registry = LLMProviderRegistry()
    registry.register("custom-provider", lambda settings: MockLLMClient())

    client = build_llm_client(
        Settings(llm_mode="custom_provider", allow_mock_fallback=False),
        registry=registry,
    )

    assert isinstance(client, MockLLMClient)
    assert registry.names() == ("custom_provider",)
    with pytest.raises(ValueError, match="already registered"):
        registry.register("custom_provider", lambda settings: MockLLMClient())


def test_fallback_records_generic_primary_metadata(monkeypatch):
    primary = OllamaLLMClient("http://127.0.0.1:1", "missing-model", 0.01)

    def unavailable(*args, **kwargs):
        raise LLMRuntimeError("Primary provider unavailable for test")

    monkeypatch.setattr(primary, "challenge", unavailable)
    fallback = FallbackLLMClient(primary, MockLLMClient())
    fallback.challenge({})

    metadata = fallback.runtime_metadata()
    assert metadata["selected_runtime"] == "mock_fallback"
    assert metadata["primary"]["runtime"] == "ollama"
    assert metadata["primary"]["model"] == "missing-model"
    assert metadata["fallback_enabled"] is True
