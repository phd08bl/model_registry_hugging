import pytest

from app.samples import SAMPLES
from app.schemas import HumanDecision

GATE_STATUSES = {
    "evidence_request": "AWAITING_INFORMATION",
    "input_confirmation": "AWAITING_INPUT_CONFIRMATION",
    "exception_resolution": "AWAITING_EXCEPTION_DECISION",
    "final_triage": "AWAITING_FINAL_DECISION",
    "publication": "READY_TO_PUBLISH",
}

PRIMARY_SAMPLE_IDS = [
    sample_id for sample_id, sample in SAMPLES.items() if sample.category != "advanced_controls"
]


def _decision_for(gate_id: str) -> HumanDecision:
    common = {
        "rationale": f"AIRO reviewed and completed {gate_id} in the mock journey.",
        "reviewer": "AIRO mock journey test",
    }
    if gate_id == "evidence_request":
        return HumanDecision(
            action="add_evidence",
            additional_evidence=(
                "Privacy assessment confirms employee names and corporate email are "
                "authorised. Supplier due diligence, contract, assurance and model-change "
                "responsibilities are approved."
            ),
            answer_updates={"personal_data": True},
            **common,
        )
    return HumanDecision(
        action={
            "input_confirmation": "confirm",
            "exception_resolution": "proceed",
            "final_triage": "confirm",
            "publication": "approve",
        }[gate_id],
        **common,
    )


def _assert_pause_is_ui_complete(case: dict) -> None:
    gate = case["pending_gate"]
    state = case["state"]
    gate_id = gate["gate_id"]

    assert case["status"] == GATE_STATUSES[gate_id]
    assert state["status"] == case["status"]
    assert state["current_gate"] == gate_id
    assert gate["title"].startswith("AIRO Gate")
    assert gate["gate_version"]
    assert gate["decision_required"]
    assert gate["reason"]
    assert gate["decision_authority"] == "AI Risk Oversight (AIRO)"
    assert gate["allowed_actions"]
    assert set(gate["allowed_actions"]) == set(gate["action_effects"])
    assert set(gate["allowed_actions"]) == set(gate["rationale_required"])
    assert isinstance(gate["context"], dict)
    assert isinstance(state.get("open_issues", []), list)
    assert isinstance(state.get("advisory_observations", []), list)
    assert isinstance(state.get("confirmed_exceptions", []), list)
    assert isinstance(state.get("invalidations", []), list)
    assert isinstance(state.get("superseded_results", []), list)

    if gate_id == "input_confirmation":
        assert "questionnaire" in gate["context"]
        assert "remaining_gaps" in gate["context"]
        assert "remaining_conflicts" in gate["context"]
    elif gate_id == "exception_resolution":
        assert state["materiality_result"]
        assert state["lod2_result"]
        assert state["proposed_outcome"]["status"] == "PROPOSED_NOT_APPROVED"
    elif gate_id == "final_triage":
        assert state["review_pack"]
        assert state["proposed_outcome"]
        assert not state.get("final_outcome")
    elif gate_id == "publication":
        assert state["final_outcome"]
        assert state["publication_draft"]
        assert state["publication_status"] == "DRAFT"


@pytest.mark.parametrize("sample_id", PRIMARY_SAMPLE_IDS)
def test_every_primary_mock_sample_matches_its_documented_gate_path(coordinator, sample_id):
    sample = SAMPLES[sample_id]
    created = coordinator.create_demo_case(sample)
    case_id = created["case_id"]
    case = coordinator.start(case_id)
    observed_gates: list[str] = []

    for _ in range(8):
        if not case["pending_gate"]:
            break
        _assert_pause_is_ui_complete(case)
        gate_id = case["pending_gate"]["gate_id"]
        observed_gates.append(gate_id)
        decision = _decision_for(gate_id)
        case = coordinator.resume(case_id, decision)
        assert case["state"]["human_decisions"][-1]["action"] == decision.action
    else:
        raise AssertionError(f"{sample_id} exceeded the bounded demonstration Gate journey")

    assert observed_gates == sample.expected_gates
    assert case["pending_gate"] is None
    assert case["status"] == "CLOSED"
    assert case["state"]["status"] == "CLOSED"
    assert case["state"]["current_gate"] is None
    assert case["state"]["publication_status"] == "PUBLISHED_LOCAL_DEMO"
    assert case["state"]["final_outcome"]


@pytest.mark.parametrize(
    "sample_id",
    [
        "low_confidence_router",
        "invalid_tool_proposal",
        "prompt_injection_evidence",
        "action_budget_exhaustion",
    ],
)
def test_advanced_mock_fail_closed_cases_expose_a_complete_gate_state(coordinator, sample_id):
    created = coordinator.create_demo_case(SAMPLES[sample_id])
    case = coordinator.start(created["case_id"])

    _assert_pause_is_ui_complete(case)
    assert case["pending_gate"]["gate_id"] == "evidence_request"
    assert case["state"]["latest_verification"]["disposition"] in {
        "escalate",
        "rejected",
    }
    assert any(
        issue["status"] == "open" and not issue["advisory"]
        for issue in case["state"]["open_issues"]
    )
