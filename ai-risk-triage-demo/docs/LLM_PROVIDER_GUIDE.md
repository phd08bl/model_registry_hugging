# LLM Provider Configuration and Extension Guide

This guide explains the implemented provider-neutral LLM architecture, how to switch between
the built-in runtimes, and how to add another API without changing the governed workflow.

The provider layer is intentionally narrow. Changing a model transport must not change the
model's authority: LLM output remains typed, bounded and advisory, while materiality, 2LoD
routing, autonomy, Human Gates, approval and publication remain deterministic or human-owned.

## 1. Implemented architecture

The Coordinator, router and tool registry depend only on `LLMClient` in
[`app/llm/base.py`](../app/llm/base.py). The provider layer is:

```text
app/llm/
  base.py       LLMClient and reusable StructuredLLMClient
  prompts.py    shared governed prompt builders
  factory.py    explicit provider registry, builders and generic fallback
  ollama.py     Ollama structured-output transport
  openai.py     OpenAI Responses API transport
  mock.py       deterministic test and demonstration runtime
```

The call path is:

```text
Coordinator / approved tool
  -> LLMClient method
  -> shared governed prompt builder
  -> selected provider's _structured transport
  -> provider schema enforcement
  -> local Pydantic validation
  -> deterministic verifier and policy controls
```

`StructuredLLMClient` implements the three governed operations:

| Method | Output model | Purpose |
| --- | --- | --- |
| `extract_evidence()` | `EvidenceExtraction` | Extract evidence-linked facts and advisory issues |
| `challenge()` | `ChallengeResult` | Identify unsupported assumptions and questions |
| `propose_action()` | `ActionProposal` | Select one action and tool from supplied allowlists |

A new structured provider normally implements only:

- `health()`;
- `_structured(system, user, response_model)`; and
- `runtime_metadata()`.

The graph, coordinator, approved tools, verifier and deterministic engines must not contain
provider-specific branches.

## 2. Built-in provider modes

`LLM_MODE` is normalized to lowercase and treats hyphens as underscores. The built-in
registry accepts:

| Mode | Implementation | Required configuration |
| --- | --- | --- |
| `mock` | `MockLLMClient` | None |
| `ollama` | `OllamaLLMClient` | Ollama URL and installed model |
| `openai` | `OpenAILLMClient` | `OPENAI_API_KEY`, `OPENAI_MODEL` |
| `openai_compatible` | `OpenAILLMClient` with custom base URL | API key, model and `OPENAI_BASE_URL` |

An unknown value fails during startup. It never silently falls back to Ollama or another
provider. This is important because silent provider substitution could send evidence to an
unintended service and create incorrect audit metadata.

## 3. Environment configuration

Copy `.env.example` to `.env`, then set only the fields for the selected provider. Real API
keys must be supplied through a protected environment or secret store and must never be
committed.

### Ollama

```dotenv
LLM_MODE=ollama
ALLOW_MOCK_FALLBACK=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
OLLAMA_TIMEOUT_SECONDS=120
```

Start and prepare Ollama before starting the application:

```powershell
ollama serve
ollama pull llama3.2:3b
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### OpenAI

Choose a governed model ID that supports Structured Outputs. Do not put a model described as
"latest" directly into source code; keep it configurable and evaluate model changes against
the repository's test and evaluation set.

```dotenv
LLM_MODE=openai
ALLOW_MOCK_FALLBACK=true
OPENAI_API_KEY=replace-through-a-secret-store
OPENAI_MODEL=your-approved-model-id
OPENAI_TIMEOUT_SECONDS=120
OPENAI_STORE_RESPONSES=false
```

The adapter uses the OpenAI Responses API parsing helper with the existing Pydantic response
models. It sends the shared system instructions and input, requests the requested typed
format, and sets the API `store` option from `OPENAI_STORE_RESPONSES`. Storage is disabled by
default.

Current request fields and model capabilities must be checked in the official OpenAI
documentation:

- [Create a model response](https://developers.openai.com/api/reference/cli/resources/responses/methods/create)
- [OpenAI model catalogue](https://developers.openai.com/api/docs/models)

`OPENAI_STORE_RESPONSES=false` is a request setting, not a complete data-governance control.
Before transmitting real evidence, separately approve retention, training-use, regional
processing, privacy, security, redaction and contractual requirements.

### OpenAI-compatible Responses endpoint

Use this mode only if the exact provider and model have been tested with the Responses API
and strict structured output:

```dotenv
LLM_MODE=openai_compatible
ALLOW_MOCK_FALLBACK=true
OPENAI_API_KEY=provider-key
OPENAI_MODEL=provider-model-id
OPENAI_BASE_URL=https://provider.example/v1
OPENAI_TIMEOUT_SECONDS=120
OPENAI_STORE_RESPONSES=false
```

An endpoint advertising "OpenAI compatibility" may support only part of the API. Verify:

- Responses API support rather than only Chat Completions;
- the SDK `responses.parse` request shape;
- strict JSON Schema behavior;
- system/developer instructions;
- refusal and content-filter responses;
- model retrieval used by `health()`;
- authentication and base URL format; and
- rate-limit, timeout and retry error behavior.

If the provider does not implement these behaviors, create a separate adapter rather than
adding provider conditionals to `OpenAILLMClient`.

### Deterministic mock

```dotenv
LLM_MODE=mock
```

Mock mode uses the same workflow, policy, tool, verifier and typed result contracts without a
network call. It is the default mode for automated tests and architecture demonstrations.

## 4. Provider selection and fallback

[`app/llm/factory.py`](../app/llm/factory.py) owns an explicit
`LLMProviderRegistry`. Each mode maps to a builder that validates provider-specific settings
and creates an `LLMClient`.

`build_llm_client()` performs this sequence:

1. normalize `LLM_MODE`;
2. create the registered primary provider;
3. return the mock directly for `mock` mode;
4. return the primary directly when fallback is disabled; or
5. wrap a live primary in `FallbackLLMClient` when fallback is enabled.

`FallbackLLMClient` catches only `LLMRuntimeError`, then delegates the same operation to the
governed mock. Programming errors are not hidden as provider failures.

Runtime metadata records:

- wrapper runtime;
- configured primary provider and model;
- selected runtime (`not_called`, primary provider, or `mock_fallback`);
- whether fallback is enabled; and
- a sanitized fallback error.

Health remains degraded if the primary is unavailable, even when mock fallback is enabled.
This prevents the fallback from making an unavailable configured provider look healthy.

## 5. Health API and UI contract

`GET /api/health` uses provider-neutral fields:

```json
{
  "status": "ok",
  "llm_mode": "openai",
  "provider": "openai",
  "model": "configured-model-id",
  "available": true,
  "selected_runtime": "not_called",
  "fallback_enabled": true,
  "message": "openai model 'configured-model-id' is available."
}
```

The UI displays `provider` and `model`; it does not assume every live provider is Ollama.
Secrets, evidence, prompts and full provider errors must never appear in this response.

## 6. Add a provider with a different API

Use these steps when an endpoint cannot use the existing Ollama or OpenAI transports.

### Step 1: Add settings

Add narrowly scoped fields to `Settings` in [`app/config.py`](../app/config.py). Store secrets
as `SecretStr`:

```python
from pydantic import SecretStr


class Settings(BaseSettings):
    # Existing settings...
    vendor_api_key: SecretStr | None = None
    vendor_model: str = ""
    vendor_base_url: str = "https://api.vendor.example"
    vendor_timeout_seconds: float = 120.0
```

Add empty or non-secret placeholders to `.env.example`:

```dotenv
VENDOR_API_KEY=
VENDOR_MODEL=
VENDOR_BASE_URL=https://api.vendor.example
VENDOR_TIMEOUT_SECONDS=120
```

Do not add real keys to source, fixtures, documentation or screenshots.

### Step 2: Implement the transport adapter

Create `app/llm/vendor.py` and inherit `StructuredLLMClient`:

```python
from __future__ import annotations

from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from app.llm.base import LLMRuntimeError, StructuredLLMClient

T = TypeVar("T", bound=BaseModel)


class VendorLLMClient(StructuredLLMClient):
    runtime_name = "vendor"

    def __init__(self, api_key: str, model: str, timeout_seconds: float):
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.client = build_vendor_client(
            api_key=api_key,
            timeout=timeout_seconds,
        )

    def health(self) -> tuple[bool, str]:
        try:
            self.client.retrieve_model(self.model)
            return True, f"Vendor model '{self.model}' is available."
        except EXPECTED_VENDOR_ERRORS as exc:
            return False, f"Vendor is unavailable: {type(exc).__name__}"

    def _structured(
        self,
        system: str,
        user: str,
        response_model: type[T],
    ) -> T:
        try:
            raw_json = self.client.generate_structured(
                model=self.model,
                system=system,
                user=user,
                json_schema=response_model.model_json_schema(),
            )
            return response_model.model_validate_json(raw_json)
        except (EXPECTED_VENDOR_ERRORS, ValidationError, TypeError, ValueError) as exc:
            raise LLMRuntimeError(
                f"Vendor structured-output call failed: {type(exc).__name__}"
            ) from exc

    def runtime_metadata(self) -> dict[str, Any]:
        return {
            "runtime": self.runtime_name,
            "model": self.model,
            "structured_output": True,
        }
```

Replace the placeholder SDK calls and exception tuple with the provider's documented API.
Catch expected provider and validation failures, not `Exception`. Programming defects should
remain visible during development.

The adapter does not implement `extract_evidence`, `challenge`, or `propose_action` because
`StructuredLLMClient` already supplies those methods using `app/llm/prompts.py`.

### Step 3: Add the dependency

Add the official provider SDK to `pyproject.toml`, then refresh the editable environment:

```powershell
python -m pip install -e ".[dev]"
```

Resolve and lock the tested dependency version according to the deployment's dependency
management process.

### Step 4: Register a builder

Import the adapter in `app/llm/factory.py`, add one builder, and register it. No factory
branch is needed:

```python
from app.llm.vendor import VendorLLMClient


def _build_vendor(settings: Settings) -> LLMClient:
    if settings.vendor_api_key is None:
        raise ValueError("VENDOR_API_KEY is required for LLM_MODE=vendor.")
    if not settings.vendor_model.strip():
        raise ValueError("VENDOR_MODEL is required for LLM_MODE=vendor.")
    return VendorLLMClient(
        api_key=settings.vendor_api_key.get_secret_value(),
        model=settings.vendor_model,
        timeout_seconds=settings.vendor_timeout_seconds,
    )


DEFAULT_LLM_PROVIDER_REGISTRY.register("vendor", _build_vendor)
```

Alternatively, an explicitly imported extension module can call
`register_llm_provider("vendor", builder)`. The module must be imported during application
startup before `build_llm_client()` runs. Registration is explicit by design; arbitrary class
paths from environment variables are not loaded.

### Step 5: Configure the mode

```dotenv
LLM_MODE=vendor
ALLOW_MOCK_FALLBACK=true
VENDOR_API_KEY=replace-through-a-secret-store
VENDOR_MODEL=approved-vendor-model
```

### Step 6: Add tests

Tests must inject a fake SDK client or monkeypatch the provider transport. They must not
require a real key or internet access.

At minimum, test:

- successful typed parsing for all three operations;
- the shared prompt and supplied allowlists reach the provider request;
- missing or malformed structured output raises `LLMRuntimeError`;
- authentication, rate-limit, timeout and refusal failures are sanitized;
- `health()` success and failure;
- runtime metadata contains provider/model but no secret;
- factory creation, missing settings and unknown mode;
- generic mock fallback; and
- existing governance tests still prevent prohibited actions and decisions.

A registry unit test can avoid changing global state:

```python
registry = LLMProviderRegistry()
registry.register("vendor", build_test_vendor)
client = build_llm_client(settings, registry=registry)
```

## 7. Structured-output requirements

Provider output is untrusted even when the provider advertises schema enforcement. Every
adapter must perform local Pydantic validation before returning a value.

Do not:

- return arbitrary dictionaries from a live adapter;
- weaken schemas to accept unexpected fields;
- treat plain JSON mode as equivalent to strict schema output;
- parse prose by stripping Markdown fences;
- silently fill model-selected actions or tools; or
- allow a provider response to mutate case state directly.

If a provider offers no reliable schema-constrained output, it is not a drop-in transport for
this application. A separate, carefully tested adapter may request JSON and validate it
locally, but malformed results must fail safely.

## 8. Prompt and governance requirements

All structured providers reuse [`app/llm/prompts.py`](../app/llm/prompts.py). Do not copy the
prompts into a provider adapter.

The shared prompts preserve these controls:

- evidence is untrusted source material, not instructions;
- facts require supplied line references;
- uncertainty must be retained;
- the router selects only from provided action/tool allowlists;
- the router does not execute tools or mutate state; and
- the LLM cannot set risk rules, outcomes, autonomy, Gates, approval or publication.

A prompt change therefore affects every live provider and requires governance regression
testing. Record prompt versions and evaluate model-specific behavior before deployment.

## 9. Error handling and secret safety

Adapters translate expected transport and structured-output failures into `LLMRuntimeError`.
The OpenAI adapter records only exception class and HTTP status when available; it does not
copy the provider's error message because that message can contain request details.

Apply the same rule to new adapters:

- never include API keys or authorization headers;
- never include full prompts, evidence or provider responses;
- avoid returning raw SDK exception strings through health endpoints;
- keep detailed protected telemetry separate from user-facing errors; and
- confirm logging and tracing libraries do not capture request bodies by default.

`FallbackLLMClient` retains the sanitized `LLMRuntimeError` in case runtime metadata. That
error must therefore already be safe to store and display.

## 10. Test and verification commands

Run all checks after adding or changing a provider:

```powershell
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check app tests
python -m compileall -q app tests
```

The repository's provider tests cover OpenAI request construction through an injected fake
client, error sanitization, registry selection, configuration failure and generic fallback.
They make no live API calls.

An optional live smoke test should be separate from the default suite and must use:

- synthetic non-sensitive evidence;
- an explicitly approved model;
- a small request and cost budget;
- no automatic retries beyond the approved limit; and
- explicit opt-in environment configuration.

## 11. Operational approval checklist

Before enabling a hosted provider outside development, confirm:

- provider and exact model ID approval;
- Structured Outputs compatibility;
- prompt and schema evaluation results;
- permitted data classifications and redaction;
- retention, training-use, residency and deletion terms;
- secret storage, access and rotation;
- outbound network allowlisting;
- timeout, concurrency, request-size and retry limits;
- cost, latency, rate-limit, validation, refusal and fallback monitoring;
- model/version change approval and rollback;
- accurate health and audit metadata; and
- a tested return to a safer provider or mock mode.

## 12. Completion criteria

A provider addition is complete only when:

- it implements `StructuredLLMClient` or the full `LLMClient` contract;
- it returns the existing typed output models;
- it uses the shared governed prompts;
- it is explicitly registered and unknown modes still fail;
- configuration is documented without secrets;
- health and runtime metadata are provider-neutral and accurate;
- fallback behavior is tested;
- error messages are sanitized;
- all unit and governance tests pass; and
- no provider-specific logic was added to the graph, coordinator or tools.

Following this contract keeps a provider change local to the LLM layer while preserving the
demo's deterministic controls and human accountability.
