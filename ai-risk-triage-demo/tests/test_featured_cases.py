from app.samples import SAMPLES
from app.schemas import HumanDecision

FEATURED_CASES = {
    1: "human_full_review",
    2: "multiple_evidence_actions",
    3: "human_evidence_conflict",
    4: "missing_supplier_evidence",
    5: "agentic_ai_autonomy",
    6: "selective_replanning",
    7: "malformed_tool_result",
    8: "straight_through_ineligible",
}


def _start(coordinator, sample_id: str) -> dict:
    created = coordinator.create_demo_case(SAMPLES[sample_id])
    return coordinator.start(created["case_id"])


def test_featured_case_numbers_and_teaching_contract_are_complete():
    numbered = {
        sample.featured_case_number: sample_id
        for sample_id, sample in SAMPLES.items()
        if sample.featured_case_number is not None
    }
    assert numbered == FEATURED_CASES

    for number, sample_id in FEATURED_CASES.items():
        sample = SAMPLES[sample_id]
        assert sample.category == "featured_cases"
        assert sample.featured_case_number == number
        assert sample.featured_case_name
        assert sample.learning_objectives
        assert sample.expected_path
        assert sample.expected_router_actions
        assert sample.expected_tools
        assert sample.expected_verification_statuses
        assert sample.expected_final_status
        assert sample.interactive_steps


def test_case_1_standard_low_risk_runs_engines_and_controlled_publication(coordinator):
    case = _start(coordinator, "human_full_review")
    case_id = case["case_id"]
    state = case["state"]

    assert case["pending_gate"]["gate_id"] == "input_confirmation"
    assert not state["missing_information"]
    assert not state["inconsistencies"]
    assert any(
        item["selection_source"] == "deterministic_policy" for item in state["agent_action_trace"]
    )

    case = coordinator.resume(
        case_id,
        HumanDecision(action="confirm", rationale="AIRO confirms the complete inputs."),
    )
    state = case["state"]
    assert state["readiness_result"]["ready_for_engines"] is True
    assert state["materiality_result"]["proposed_materiality_band"] == "negligible"
    assert state["lod2_result"]["teams"] == []
    assert case["pending_gate"]["gate_id"] == "final_triage"

    case = coordinator.resume(
        case_id,
        HumanDecision(action="confirm", rationale="AIRO confirms final triage."),
    )
    assert case["pending_gate"]["gate_id"] == "publication"
    assert case["state"]["publication_draft"]
    case = coordinator.resume(
        case_id,
        HumanDecision(action="approve", rationale="AIRO approves the local demo record."),
    )
    assert case["status"] == "CLOSED"
    assert case["state"]["publication_status"] == "PUBLISHED_LOCAL_DEMO"


def test_case_2_records_bounded_recommendation_authorisation_and_continuation(coordinator):
    case = _start(coordinator, "multiple_evidence_actions")
    traces = case["state"]["agent_action_trace"]
    recommended_index = next(
        index
        for index, item in enumerate(traces)
        if item["selection_source"] == "llm_router"
        and len(item["supervisor_decision"]["allowed_actions"]) > 1
    )
    recommended = traces[recommended_index]

    assert (
        recommended["proposal"]["selected_action"]
        in recommended["supervisor_decision"]["allowed_actions"]
    )
    assert recommended["authorisation"]["decision"] == "AUTHORISED"
    assert recommended["invocation"]
    assert recommended["result"]["status"] == "succeeded"
    assert recommended["verification"]["disposition"] in {"accepted", "advisory"}
    assert recommended["next_transition"] == "reassess_case"
    assert len(traces) > recommended_index + 1
    assert any(item["selection_source"] == "deterministic_policy" for item in traces)
    assert case["pending_gate"]["gate_id"] == "input_confirmation"


def test_case_3_amendment_reruns_only_affected_evidence_work(coordinator):
    case = _start(coordinator, "human_evidence_conflict")
    case_id = case["case_id"]
    before = case["state"]["agent_action_trace"]
    extraction_count = sum(
        item["proposal"]["selected_action"] == "extract_submitted_evidence" for item in before
    )

    case = coordinator.resume(
        case_id,
        HumanDecision(
            action="add_evidence",
            answer_updates={"personal_data": True},
            additional_evidence=(
                "Privacy assessment classifies employee names and corporate email addresses "
                "as personal data authorised for this internal purpose."
            ),
            rationale="AIRO corrects the confirmed material fact and supplies assurance.",
        ),
    )
    state = case["state"]
    after = state["agent_action_trace"]
    rerun_actions = [item["proposal"]["selected_action"] for item in after[len(before) :]]

    assert case["pending_gate"]["gate_id"] == "input_confirmation"
    assert not state["inconsistencies"]
    assert (
        sum(item["proposal"]["selected_action"] == "extract_submitted_evidence" for item in after)
        == extraction_count + 1
    )
    assert set(rerun_actions) <= {
        "extract_submitted_evidence",
        "check_questionnaire_evidence_consistency",
        "verify_citations",
    }
    assert "check_rag_evidence" not in rerun_actions
    assert "check_supplier_evidence" not in rerun_actions
    assert rerun_actions


def test_case_8_downgrade_cannot_bypass_elevated_proposals_or_lod2(coordinator):
    case = _start(coordinator, "straight_through_ineligible")
    case_id = case["case_id"]
    assignment = case["state"]["autonomy_assignment"]
    assert assignment["approved_maximum_profile"] == "straight_through_demo"
    assert assignment["effective_profile"] == "human_governed"
    assert assignment["downgraded"] is True

    case = coordinator.resume(
        case_id,
        HumanDecision(action="confirm", rationale="AIRO confirms the elevated inputs."),
    )
    state = case["state"]
    assert state["materiality_result"]["proposed_materiality_band"] == "severe"
    assert state["lod2_result"]["teams"]
    assert "Model Risk / AI IVT" in state["lod2_result"]["teams"]
    assert case["pending_gate"]["gate_id"] == "exception_resolution"
    assert state["active_governance_loop"] == "EXCEPTION_INTERPRETATION"
