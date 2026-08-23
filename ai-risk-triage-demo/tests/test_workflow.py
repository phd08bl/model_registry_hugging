import pytest

from app.samples import SAMPLES
from app.schemas import ActionProposal, HumanDecision


def decision(action: str, rationale: str = "Reviewed for automated test", **kwargs):
    return HumanDecision(action=action, rationale=rationale, reviewer="AIRO tester", **kwargs)


def test_human_governed_case_pauses_and_resumes_to_completion(coordinator):
    case = coordinator.create_demo_case(SAMPLES["human_full_review"])
    case_id = case["case_id"]

    case = coordinator.start(case_id)
    assert case["pending_gate"]["gate_id"] == "input_confirmation"

    case = coordinator.resume(case_id, decision("confirm"))
    assert case["pending_gate"]["gate_id"] == "exception_resolution"

    case = coordinator.resume(case_id, decision("proceed"))
    assert case["pending_gate"]["gate_id"] == "final_triage"
    assert "input_gate" in case["state"]["completed_nodes"]
    assert case["state"]["confirmed_exceptions"]
    assert case["state"]["confirmed_exceptions"][0]["status"] == "accepted"

    case = coordinator.resume(case_id, decision("confirm"))
    assert case["pending_gate"]["gate_id"] == "publication"

    case = coordinator.resume(case_id, decision("approve"))
    assert case["status"] == "CLOSED"
    assert case["state"]["final_outcome"]["status"] == "AIRO_CONFIRMED"
    assert case["state"]["publication_status"] == "PUBLISHED_LOCAL_DEMO"
    assert len(case["audit"]) >= 9


def test_evidence_conflict_creates_targeted_human_gate(coordinator):
    case = coordinator.create_demo_case(SAMPLES["human_evidence_conflict"])
    case = coordinator.start(case["case_id"])

    assert case["pending_gate"]["gate_id"] == "evidence_request"
    assert case["state"]["inconsistencies"]
    assert case["state"]["evidence_request"]


def test_added_evidence_and_answer_update_reenter_extraction(coordinator):
    case = coordinator.create_demo_case(SAMPLES["human_evidence_conflict"])
    case_id = case["case_id"]
    coordinator.start(case_id)

    case = coordinator.resume(
        case_id,
        decision(
            "add_evidence",
            additional_evidence="Privacy assessment confirms employee name and email processing.",
            answer_updates={"personal_data": True},
        ),
    )

    assert case["state"]["evidence_cycle"] == 1
    assert case["state"]["questionnaire"]["personal_data"] is True
    assert case["pending_gate"]["gate_id"] == "input_confirmation"
    assert not case["state"]["missing_information"]
    assert not case["state"]["inconsistencies"]
    assert not [
        issue
        for issue in case["state"]["open_issues"]
        if issue["category"] in {"mandatory_evidence_gap", "inconsistency"}
        and issue["status"] == "open"
    ]
    assert "advisory_evidence_summary" in case["pending_gate"]["context"]
    assert "evidence_summary" not in case["pending_gate"]["context"]


def test_evidence_conflict_gate_statuses_stay_current_through_completion(coordinator):
    """Each resume must expose the next Gate's state, not stale prior-Gate state."""

    case = coordinator.create_demo_case(SAMPLES["human_evidence_conflict"])
    case_id = case["case_id"]

    case = coordinator.start(case_id)
    assert case["status"] == "AWAITING_INFORMATION"
    assert case["state"]["current_gate"] == "evidence_request"

    case = coordinator.resume(
        case_id,
        decision(
            "add_evidence",
            additional_evidence=(
                "Privacy assessment confirms employee names and corporate email are "
                "authorised. Supplier due diligence, contract, assurance and model-change "
                "responsibilities are approved."
            ),
            answer_updates={"personal_data": True},
        ),
    )
    assert case["status"] == "AWAITING_INPUT_CONFIRMATION"
    assert case["pending_gate"]["gate_id"] == "input_confirmation"
    assert case["state"]["current_gate"] == "input_confirmation"
    assert not [
        issue
        for issue in case["state"]["open_issues"]
        if issue["status"] == "open"
        and issue["category"] in {"mandatory_evidence_gap", "inconsistency"}
    ]

    case = coordinator.resume(case_id, decision("confirm", "Inputs are confirmed."))
    assert case["status"] == "AWAITING_EXCEPTION_DECISION"
    assert case["pending_gate"]["gate_id"] == "exception_resolution"
    assert case["state"]["confirmed_facts"]
    assert case["state"]["confirmed_facts"][0]["confirmed_by"] == "AIRO tester"

    case = coordinator.resume(case_id, decision("proceed", "Exception accepted for triage."))
    assert case["status"] == "AWAITING_FINAL_DECISION"
    assert case["pending_gate"]["gate_id"] == "final_triage"
    assert "exception_gate" in case["state"]["completed_nodes"]
    assert all(item["status"] == "accepted" for item in case["state"]["confirmed_exceptions"])

    case = coordinator.resume(case_id, decision("confirm", "Proposal confirmed by AIRO."))
    assert case["status"] == "READY_TO_PUBLISH"
    assert case["pending_gate"]["gate_id"] == "publication"
    assert case["state"]["final_outcome"]["status"] == "AIRO_CONFIRMED"
    assert "final_gate" in case["state"]["completed_nodes"]

    case = coordinator.resume(case_id, decision("approve", "Local demo record approved."))
    assert case["status"] == "CLOSED"
    assert case["pending_gate"] is None
    assert case["state"]["current_gate"] is None
    assert case["state"]["publication_status"] == "PUBLISHED_LOCAL_DEMO"
    assert {"publication_gate", "publish"} <= set(case["state"]["completed_nodes"])


def test_proceed_with_gap_marks_current_issue_accepted_not_resolved(coordinator):
    case = coordinator.create_demo_case(SAMPLES["human_evidence_conflict"])
    case_id = case["case_id"]
    case = coordinator.start(case_id)
    current_issues = {
        issue["summary"]
        for issue in case["state"]["open_issues"]
        if issue["status"] == "open" and not issue["advisory"]
    }
    assert current_issues

    case = coordinator.resume(
        case_id,
        decision("proceed_with_gap", "AIRO accepts the residual evidence risk for triage."),
    )

    assert case["pending_gate"]["gate_id"] == "input_confirmation"
    accepted = {
        issue["summary"] for issue in case["state"]["open_issues"] if issue["status"] == "accepted"
    }
    assert current_issues <= accepted
    assert not case["pending_gate"]["context"]["remaining_gaps"]
    assert not case["pending_gate"]["context"]["remaining_conflicts"]
    assert case["pending_gate"]["context"]["airo_accepted_evidence_issues"]


def test_return_for_evidence_invalidates_later_stages_but_reuses_current_engines(
    coordinator,
):
    case = coordinator.create_demo_case(SAMPLES["selective_replanning"])
    case_id = case["case_id"]
    case = coordinator.start(case_id)
    case = coordinator.resume(case_id, decision("confirm", "Inputs confirmed."))
    assert case["pending_gate"]["gate_id"] == "exception_resolution"
    materiality = case["state"]["materiality_result"]
    lod2 = case["state"]["lod2_result"]

    case = coordinator.resume(
        case_id,
        decision("return_for_evidence", "Provide additional attendee-control evidence."),
    )
    assert case["pending_gate"]["gate_id"] == "evidence_request"
    assert case["state"]["materiality_result"] == materiality
    assert case["state"]["lod2_result"] == lod2
    assert "decision_engines" in case["state"]["completed_nodes"]
    assert "challenge_assessment" not in case["state"]["completed_nodes"]
    assert not case["state"].get("challenge_summary")
    assert not case["state"].get("confirmed_facts")

    case = coordinator.resume(
        case_id,
        decision(
            "add_evidence",
            "Additional evidence received.",
            additional_evidence=(
                "Meeting-summary controls confirm authorised internal access and mandatory "
                "reviewer sign-off before use."
            ),
        ),
    )
    assert case["pending_gate"]["gate_id"] == "input_confirmation"
    case = coordinator.resume(case_id, decision("confirm", "Refreshed inputs confirmed."))
    assert case["pending_gate"]["gate_id"] == "exception_resolution"
    assert case["state"]["materiality_result"] == materiality
    assert case["state"]["lod2_result"] == lod2


def test_ollama_style_router_fields_cannot_break_evidence_resume(coordinator, monkeypatch):
    def incomplete_contract(state, allowed_actions, allowed_tools):
        del state
        action = allowed_actions[0]
        wrong_tool = allowed_tools[-1]
        return ActionProposal(
            selected_action=action,
            selected_tool=wrong_tool,
            reason="Local model selected an allowed evidence action.",
            inputs_required=[],
            confidence=0.91,
            human_review_required=True,
        )

    monkeypatch.setattr(coordinator.llm, "propose_action", incomplete_contract)
    case = coordinator.create_demo_case(SAMPLES["human_evidence_conflict"])
    case_id = case["case_id"]
    case = coordinator.start(case_id)
    assert case["pending_gate"]["gate_id"] == "evidence_request"
    assert case["state"]["latest_tool_result"]["status"] == "succeeded"

    case = coordinator.resume(
        case_id,
        decision(
            "add_evidence",
            additional_evidence=(
                "Privacy assessment confirms employee names and corporate email are "
                "authorised. Supplier due diligence, contract, assurance and model-change "
                "responsibilities are approved."
            ),
            answer_updates={"personal_data": True},
        ),
    )

    assert case["pending_gate"]["gate_id"] == "input_confirmation"
    assert case["state"]["latest_verification"]["disposition"] in {"accepted", "advisory"}
    assert not case["state"]["failed_actions"]
    assert all(
        item["result"]["status"] == "succeeded"
        for item in case["state"]["agent_action_trace"]
        if item.get("result")
    )


def test_invalid_gate_action_is_rejected(coordinator):
    case = coordinator.create_demo_case(SAMPLES["human_full_review"])
    case_id = case["case_id"]
    coordinator.start(case_id)

    with pytest.raises(ValueError, match="not permitted"):
        coordinator.resume(case_id, decision("approve"))


def test_exception_proceed_requires_airo_rationale(coordinator):
    case = coordinator.create_demo_case(SAMPLES["human_full_review"])
    case_id = case["case_id"]
    coordinator.start(case_id)
    case = coordinator.resume(case_id, decision("confirm"))
    assert case["pending_gate"]["gate_id"] == "exception_resolution"

    with pytest.raises(ValueError, match="requires a decision rationale"):
        coordinator.resume(case_id, HumanDecision(action="proceed", rationale=""))


def test_save_draft_returns_to_publication_gate(coordinator):
    case = coordinator.create_demo_case(SAMPLES["human_full_review"])
    case_id = case["case_id"]
    coordinator.start(case_id)
    coordinator.resume(case_id, decision("confirm"))
    coordinator.resume(case_id, decision("proceed"))
    coordinator.resume(case_id, decision("confirm"))

    case = coordinator.resume(case_id, decision("save_draft"))
    assert case["state"]["publication_status"] == "DRAFT_SAVED"
    assert case["pending_gate"]["gate_id"] == "publication"


def test_workflow_failure_is_stored_without_internal_exception_text(coordinator, monkeypatch):
    case = coordinator.create_demo_case(SAMPLES["human_full_review"])
    secret = "sensitive internal evidence or connection detail"

    def fail_closed(*args, **kwargs):
        raise RuntimeError(secret)

    monkeypatch.setattr(coordinator.graph, "invoke", fail_closed)
    with pytest.raises(RuntimeError, match=secret):
        coordinator.start(case["case_id"])

    stored = coordinator.get_case(case["case_id"])
    serialized = str(stored)
    assert stored["status"] == "ERROR"
    assert "failed closed" in stored["state"]["error"]
    assert secret not in serialized
    graph_error = next(item for item in stored["audit"] if item["action"] == "GRAPH_ERROR")
    assert graph_error["details"] == {
        "error_type": "RuntimeError",
        "details_exposed": False,
    }
