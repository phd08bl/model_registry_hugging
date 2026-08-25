from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.config import PROJECT_ROOT, get_settings
from app.coordinator import CaseCoordinator
from app.llm import build_llm_client
from app.samples import PROFILE_UI_DEFINITIONS, SAMPLE_CATEGORIES, SAMPLES
from app.schemas import (
    BacktestRequest,
    ControlRecoveryRequest,
    CreateCaseRequest,
    ExternalEventSubmission,
    HealthResponse,
    HumanDecision,
    SensitivityRequest,
)
from app.services.calibration import DEMO_HISTORY, run_backtest, run_sensitivity
from app.versions import APP_VERSION, UI_ASSET_VERSION

settings = get_settings()
llm_client = build_llm_client(settings)
coordinator = CaseCoordinator(settings, llm_client)

app = FastAPI(
    title=settings.app_name,
    version=APP_VERSION,
    description=(
        "Demonstration of a human-governed, stateful AIRO Case Coordinator. "
        "All risk rules are illustrative and not approved MRO or PwC methodology."
    ),
)

STATIC_DIR = PROJECT_ROOT / "app" / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.middleware("http")
async def prevent_stale_demo_assets(request: Request, call_next):
    """Keep the local demo's HTML, CSS and JavaScript on the same UI release."""

    response = await call_next(request)
    if request.url.path == "/" or request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-store, max-age=0"
        response.headers["Pragma"] = "no-cache"
    return response


@app.get("/", include_in_schema=False)
def index() -> HTMLResponse:
    html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    return HTMLResponse(
        html.replace("__UI_ASSET_VERSION__", UI_ASSET_VERSION),
        headers={"Cache-Control": "no-store, max-age=0", "Pragma": "no-cache"},
    )


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
        selected_runtime=str(metadata.get("selected_runtime", metadata.get("runtime", provider))),
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
            "featured_case_number": sample.featured_case_number,
            "featured_case_name": sample.featured_case_name,
            "learning_objectives": sample.learning_objectives,
            "expected_assigned_profile": sample.expected_assigned_profile,
            "expected_approved_maximum_profile": sample.expected_approved_maximum_profile,
            "profile_summary": PROFILE_UI_DEFINITIONS[sample.expected_assigned_profile],
            "likely_airo_attention": sample.likely_airo_attention,
            "expected_router_actions": [item.value for item in sample.expected_router_actions],
            "expected_tools": [item.value for item in sample.expected_tools],
            "expected_verification_statuses": sample.expected_verification_statuses,
            "expected_gates": sample.expected_gates,
            "expected_governance_loops": sample.expected_governance_loops,
            "expected_external_event_type": sample.expected_external_event_type,
            "expected_exceptions": sample.expected_exceptions,
            "expected_path": sample.expected_path,
            "expected_materiality_band": sample.expected_materiality_band,
            "expected_2lod_teams": sample.expected_2lod_teams,
            "expected_final_status": sample.expected_final_status,
            "teaching_controls": sample.demo_controls.model_dump(mode="json"),
            "teaching_controls_notice": (
                "Protected fixture controls only; they do not override the policy-assigned profile."
            ),
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


@app.post("/api/cases/{case_id}/resume")
def resume_case(case_id: str, decision: HumanDecision) -> dict:
    try:
        return coordinator.resume(case_id, decision)
    except KeyError:
        raise HTTPException(status_code=404, detail="Case not found") from None
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/api/cases/{case_id}/events")
def submit_external_event(case_id: str, event: ExternalEventSubmission) -> dict:
    try:
        return coordinator.submit_external_event(case_id, event)
    except KeyError:
        raise HTTPException(status_code=404, detail="Case not found") from None
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/api/cases/{case_id}/recover")
def recover_control_exception(case_id: str, recovery: ControlRecoveryRequest) -> dict:
    try:
        return coordinator.recover_control_exception(case_id, recovery)
    except KeyError:
        raise HTTPException(status_code=404, detail="Case not found") from None
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.get("/api/cases/{case_id}/history")
def get_action_history(case_id: str) -> dict:
    try:
        return coordinator.action_history(case_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Case not found") from None


@app.get("/api/cases/{case_id}/supervisor")
def get_supervisor_decision(case_id: str) -> dict:
    try:
        return coordinator.supervisor_decision(case_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Case not found") from None


@app.get("/api/cases/{case_id}/results")
def get_result_status(case_id: str) -> dict:
    try:
        return coordinator.result_status(case_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Case not found") from None


@app.get("/api/tools")
def get_tool_registry() -> list[dict]:
    return coordinator.tool_metadata()


@app.post("/api/calibration/backtest")
def backtest(request: BacktestRequest) -> dict:
    return run_backtest(request.cases)


@app.get("/api/calibration/demo-backtest")
def demo_backtest() -> dict:
    return run_backtest(DEMO_HISTORY)


@app.post("/api/calibration/sensitivity")
def sensitivity(request: SensitivityRequest) -> dict:
    return run_sensitivity(request.questionnaire)
