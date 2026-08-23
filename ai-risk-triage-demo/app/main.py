from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import PROJECT_ROOT, get_settings
from app.coordinator import CaseCoordinator
from app.llm import build_llm_client
from app.samples import PROFILE_UI_DEFINITIONS, SAMPLE_CATEGORIES, SAMPLES
from app.schemas import (
    BacktestRequest,
    CreateCaseRequest,
    HealthResponse,
    HumanDecision,
    SensitivityRequest,
)
from app.services.calibration import DEMO_HISTORY, run_backtest, run_sensitivity

settings = get_settings()
llm_client = build_llm_client(settings)
coordinator = CaseCoordinator(settings, llm_client)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description=(
        "Demonstration of a human-governed, stateful AIRO Case Coordinator. "
        "All risk rules are illustrative and not approved MRO or PwC methodology."
    ),
)

STATIC_DIR = PROJECT_ROOT / "app" / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    available, message = coordinator.health()
    metadata = llm_client.runtime_metadata()
    primary = metadata.get("primary", metadata)
    provider = str(primary.get("runtime", settings.llm_mode))
    model = str(primary.get("model") or "deterministic demonstration runtime")
    return HealthResponse(
        status="ok" if available else "degraded",
        llm_mode=settings.llm_mode,
        provider=provider,
        model=model,
        available=available,
        selected_runtime=str(
            metadata.get("selected_runtime", metadata.get("runtime", provider))
        ),
        fallback_enabled=bool(metadata.get("fallback_enabled", False)),
        message=message,
    )


@app.get("/api/samples")
def list_samples() -> dict:
    return {
        name: {
            "sample_id": sample.sample_id,
            "title": sample.title,
            "short_description": sample.short_description,
            "category": sample.category,
            "category_name": SAMPLE_CATEGORIES[sample.category],
            "learning_objectives": sample.learning_objectives,
            "expected_assigned_profile": sample.expected_assigned_profile,
            "expected_approved_maximum_profile": sample.expected_approved_maximum_profile,
            "profile_summary": PROFILE_UI_DEFINITIONS[sample.expected_assigned_profile],
            "likely_airo_attention": sample.likely_airo_attention,
            "expected_router_actions": [item.value for item in sample.expected_router_actions],
            "expected_tools": [item.value for item in sample.expected_tools],
            "expected_verification_statuses": sample.expected_verification_statuses,
            "expected_gates": sample.expected_gates,
            "expected_materiality_band": sample.expected_materiality_band,
            "expected_2lod_teams": sample.expected_2lod_teams,
            "expected_final_status": sample.expected_final_status,
            "interactive_steps": sample.interactive_steps,
        }
        for name, sample in SAMPLES.items()
    }


@app.post("/api/samples/{sample_name}")
def create_sample(sample_name: str) -> dict:
    sample = SAMPLES.get(sample_name)
    if not sample:
        raise HTTPException(status_code=404, detail="Unknown sample")
    return coordinator.create_demo_case(sample.model_copy(deep=True))


@app.post("/api/cases")
def create_case(request: CreateCaseRequest) -> dict:
    return coordinator.create_case(request)


@app.get("/api/cases")
def list_cases() -> list[dict]:
    return coordinator.list_cases()


@app.get("/api/cases/{case_id}")
def get_case(case_id: str) -> dict:
    try:
        return coordinator.get_case(case_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Case not found") from None


@app.post("/api/cases/{case_id}/start")
def start_case(case_id: str) -> dict:
    try:
        return coordinator.start(case_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Case not found") from None
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/cases/{case_id}/resume")
def resume_case(case_id: str, decision: HumanDecision) -> dict:
    try:
        return coordinator.resume(case_id, decision)
    except KeyError:
        raise HTTPException(status_code=404, detail="Case not found") from None
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/design")
def design() -> dict:
    return {
        "product": "AIRO Human-Governed Agentic Case Coordinator",
        "governance_framework": "MRO Risk-Based Progressive Automation and Oversight Framework",
        "orchestration": "LangGraph StateGraph",
        "classification": (
            "An agent with deterministic orchestration, constrained decision authority, "
            "constrained action authority and mandatory AIRO oversight"
        ),
        "direct_user": "AI Risk Oversight Team",
        "activity_types": {
            "D": "Deterministic approved rules",
            "L": "Bounded LLM evidence capability",
            "A": "Agentic case coordination",
            "H": "Human judgement and accountability",
        },
        "principles": [
            "The Coordinator manages the case.",
            "Deterministic rules calculate the proposal.",
            "The LLM processes and challenges evidence.",
            "AIRO owns reserved decisions.",
            "A deterministic policy controls autonomy.",
            "Every tool result is verified and traced.",
            "Changed inputs invalidate dependent stale results.",
        ],
        "normal_case_profile_assignment": "system_assigned_human_governed",
        "warning": "All demo scoring and trigger rules are illustrative.",
    }


@app.post("/api/calibration/backtest")
def backtest(request: BacktestRequest) -> dict:
    return run_backtest(request.cases)


@app.get("/api/calibration/demo-backtest")
def demo_backtest() -> dict:
    return run_backtest(DEMO_HISTORY)


@app.post("/api/calibration/sensitivity")
def sensitivity(request: SensitivityRequest) -> dict:
    return run_sensitivity(request.questionnaire)
