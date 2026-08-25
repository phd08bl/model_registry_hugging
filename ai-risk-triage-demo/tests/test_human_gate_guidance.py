from app.samples import SAMPLES
from app.schemas import HumanDecision


def _start(coordinator, sample_id: str) -> dict:
    created = coordinator.create_demo_case(SAMPLES[sample_id])
    return coordinator.start(created["case_id"])


def _assert_guidance_contract(gate: dict) -> None:
    assert gate["required_inputs"]
    assert gate["blocking_item_count"] == sum(
        bool(item["blocking"]) for item in gate["required_inputs"]
    )
    assert set(gate["action_impacts"]) == set(gate["allowed_actions"])
    if gate["recommended_action"] is not None:
        assert gate["recommended_action"] in gate["allowed_actions"]
    for action in gate["allowed_actions"]:
        impact = gate["action_impacts"][action]
        assert impact["effect"] == gate["action_effects"][action]
        assert impact["next_step"]
        assert isinstance(impact["required_fields"], list)
        assert isinstance(impact["will_change"], list)
        assert isinstance(impact["will_rerun"], list)
        assert isinstance(impact["will_remain_current"], list)


def test_evidence_gate_explains_the_exact_questionnaire_conflict(coordinator):
    case = _start(coordinator, "human_evidence_conflict")
    gate = case["pending_gate"]

    _assert_guidance_contract(gate)
    assert gate["gate_id"] == "evidence_request"
    assert gate["recommended_action"] == "add_evidence"
    assert gate["blocking_item_count"] == 1
    requirement = gate["required_inputs"][0]
    assert requirement["kind"] == "evidence_conflict"
    assert requirement["field"] == "personal_data"
    assert requirement["current_value"] is False
    assert requirement["evidence_supported_value"] is True
    assert requirement["suggested_value"] is True
    assert requirement["required_artifacts"]
    assert requirement["citations"]
    assert gate["action_impacts"]["add_evidence"]["required_fields"] == [
        "additional_evidence_or_questionnaire_update"
    ]


def test_every_human_governance_gate_has_specific_tasks_and_impacts(coordinator):
    input_case = _start(coordinator, "human_full_review")
    _assert_guidance_contract(input_case["pending_gate"])
    assert input_case["pending_gate"]["gate_id"] == "input_confirmation"
    assert input_case["pending_gate"]["required_inputs"][0]["kind"] == "fact_confirmation"

    case_id = input_case["case_id"]
    final_case = coordinator.resume(
        case_id,
        HumanDecision(action="confirm", rationale="AIRO confirms the material inputs."),
    )
    _assert_guidance_contract(final_case["pending_gate"])
    assert final_case["pending_gate"]["gate_id"] == "final_triage"
    assert len(final_case["pending_gate"]["required_inputs"]) == 2

    publication_case = coordinator.resume(
        case_id,
        HumanDecision(action="confirm", rationale="AIRO confirms final triage."),
    )
    _assert_guidance_contract(publication_case["pending_gate"])
    assert publication_case["pending_gate"]["gate_id"] == "publication"
    assert publication_case["pending_gate"]["required_inputs"][0]["kind"] == (
        "publication_approval"
    )

    exception_case = _start(coordinator, "agentic_ai_autonomy")
    exception_case = coordinator.resume(
        exception_case["case_id"],
        HumanDecision(action="confirm", rationale="AIRO confirms the elevated inputs."),
    )
    _assert_guidance_contract(exception_case["pending_gate"])
    assert exception_case["pending_gate"]["gate_id"] == "exception_resolution"
    assert all(
        item["kind"] == "exception_judgement"
        for item in exception_case["pending_gate"]["required_inputs"]
    )

    control_case = _start(coordinator, "malformed_tool_result")
    _assert_guidance_contract(control_case["pending_gate"])
    assert control_case["pending_gate"]["gate_id"] == "control_exception_review"
    assert control_case["pending_gate"]["required_inputs"][0]["kind"] == "control_recovery"


def test_edit_answers_requires_an_actual_questionnaire_change(coordinator):
    case = _start(coordinator, "human_full_review")

    try:
        coordinator.resume(
            case["case_id"],
            HumanDecision(action="edit_answers", rationale="AIRO selected edit answers."),
        )
    except ValueError as exc:
        assert str(exc) == "Edit at least one questionnaire answer."
    else:
        raise AssertionError("Empty Edit Answers must fail before the graph resumes")
