import pytest

from app.agent.policy import DEMO_PATTERN_MAXIMUMS
from app.engines.lod2 import calculate_2lod_triggers
from app.engines.materiality import calculate_materiality
from app.samples import SAMPLES
from app.schemas import ActionType, HumanDecision, ToolIdentifier


def _start(coordinator, sample_id: str) -> dict:
    created = coordinator.create_demo_case(SAMPLES[sample_id])
    return coordinator.start(created["case_id"])


@pytest.mark.parametrize("sample_id", SAMPLES)
def test_every_demonstration_case_is_created_by_governed_policy(coordinator, sample_id):
    sample = SAMPLES[sample_id]
    created = coordinator.create_demo_case(sample)
    state = created["state"]
    assignment = state["autonomy_assignment"]

    assert state["demo_scenario_id"] == sample_id
    assert assignment["effective_profile"] == sample.expected_assigned_profile
    assert assignment["approved_maximum_profile"] == sample.expected_approved_maximum_profile
    assert assignment["governed_pattern_id"] == sample.governed_pattern_id
    assert assignment["policy_version"].startswith("illustrative-demo")


def test_governed_pattern_registry_exactly_matches_sample_catalogue():
    assert set(DEMO_PATTERN_MAXIMUMS) == set(SAMPLES)


def test_expected_metadata_cannot_force_runtime_outcomes(coordinator):
    altered = SAMPLES["human_full_review"].model_copy(
        update={"expected_materiality_band": "severe", "expected_final_status": "APPROVED"}
    )
    case = coordinator.create_demo_case(altered)
    assert "materiality_result" not in case["state"]
    assert "final_outcome" not in case["state"]


@pytest.mark.parametrize(
    "sample_id",
    [
        sample_id
        for sample_id, sample in SAMPLES.items()
        if sample.expected_materiality_band is not None
    ],
)
def test_documented_risk_expectations_match_approved_deterministic_engines(sample_id):
    sample = SAMPLES[sample_id]
    questionnaire = sample.questionnaire.model_dump()
    assert (
        calculate_materiality(questionnaire)["proposed_materiality_band"]
        == sample.expected_materiality_band
    )
    assert calculate_2lod_triggers(questionnaire)["teams"] == sample.expected_2lod_teams


@pytest.mark.parametrize(
    ("sample_id", "mode"),
    [
        ("low_confidence_router", "low_confidence"),
        ("invalid_tool_proposal", "non_allowlisted_tool"),
    ],
)
def test_router_rejections_fail_closed_without_tool_execution(coordinator, sample_id, mode):
    case = _start(coordinator, sample_id)
    state = case["state"]
    trace = state["agent_action_trace"][-1]

    assert state["demo_controls"]["router_mode"] == mode
    assert case["pending_gate"]["gate_id"] == "evidence_request"
    assert state["tool_call_count"] == 0
    assert trace["invocation"] is None
    assert trace["result"] is None
    assert trace["verification"]["disposition"] == "rejected"


def test_non_allowlisted_proposal_cannot_invoke_materiality_engine(coordinator):
    case = _start(coordinator, "invalid_tool_proposal")
    trace = case["state"]["agent_action_trace"][-1]
    assert trace["proposal"]["selected_tool"] == ToolIdentifier.MATERIALITY_ENGINE.value
    assert trace["proposal"]["selected_action"] == ActionType.EXTRACT_SUBMITTED_EVIDENCE.value
    assert trace["verification"]["checks"]["tool_not_invoked"] is True


def test_prompt_injection_and_invalid_citation_are_preserved_as_security_issues(coordinator):
    case = _start(coordinator, "prompt_injection_evidence")
    state = case["state"]
    extraction_trace = next(
        item
        for item in state["agent_action_trace"]
        if item["proposal"]["selected_action"] == "extract_submitted_evidence"
    )

    assert extraction_trace["verification"]["disposition"] == "escalate"
    assert extraction_trace["verification"]["checks"]["citations_exist"] is False
    assert any(item["category"] == "security" for item in state["open_issues"])
    assert case["pending_gate"]["gate_id"] == "evidence_request"
    assert not state.get("final_outcome")


def test_action_budget_exhaustion_stops_and_records_escalation(coordinator):
    case = _start(coordinator, "action_budget_exhaustion")
    state = case["state"]

    assert state["max_tool_calls"] == 1
    assert state["tool_call_count"] == 1
    assert state["remaining_tool_calls"] == 0
    assert len(state["agent_action_trace"]) == 2
    assert state["agent_action_trace"][-1]["proposal"]["selected_action"] == "escalate_to_airo"
    assert state["agent_action_trace"][-1]["verification"]["disposition"] == "escalate"
    assert case["pending_gate"]["gate_id"] == "evidence_request"


def test_selective_replanning_invalidates_engines_and_preserves_history(coordinator):
    case = _start(coordinator, "selective_replanning")
    case_id = case["case_id"]
    case = coordinator.resume(
        case_id, HumanDecision(action="confirm", rationale="Inputs confirmed")
    )
    assert case["pending_gate"]["gate_id"] == "exception_resolution"
    previous_materiality = case["state"]["materiality_result"]
    trace_count = len(case["state"]["agent_action_trace"])

    case = coordinator.resume(
        case_id,
        HumanDecision(
            action="edit_answers",
            answer_updates={"personal_data": True},
            rationale="Attendee identifiers are now in scope.",
        ),
    )
    state = case["state"]
    invalidated = {item["invalidated_result"] for item in state["invalidations"]}

    assert {"materiality_result", "lod2_result"} <= invalidated
    assert state["superseded_results"]
    assert any(
        item.get("value") == previous_materiality
        for item in state["superseded_results"]
        if item["result_type"] == "materiality_result"
    )
    assert state["materiality_result"] != previous_materiality
    assert len(state["agent_action_trace"]) > trace_count
    assert state["material_change_requires_airo_review"] is True
    assert case["pending_gate"] is not None


def test_sample_suite_covers_each_ui_suitable_agent_control():
    controls = {
        objective for sample in SAMPLES.values() for objective in sample.learning_objectives
    }
    required = {
        "Bounded evidence routing",
        "Citation verification",
        "System profile assignment",
        "Agentic-AI checker",
        "Confidence threshold",
        "Tool allowlist",
        "Prompt-injection detection",
        "Dependency-aware invalidation",
        "Maximum action budget",
    }
    assert required <= controls
