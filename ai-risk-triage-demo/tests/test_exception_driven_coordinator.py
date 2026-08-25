import pytest

from app.agent.completion import CompletionPolicy
from app.agent.readiness import ReadinessPolicy
from app.samples import SAMPLES
from app.schemas import (
    ControlRecoveryRequest,
    ExternalEventSubmission,
    HumanDecision,
)


def _external_event(case: dict, **changes) -> ExternalEventSubmission:
    expected = case["pending_event"]
    values = {
        "event_type": expected["event_type"],
        "case_id": case["case_id"],
        "correlation_id": expected["correlation_id"],
        "source": expected["expected_source"],
        "schema_version": expected["schema_version"],
        "case_state_version": case["state"]["case_state_version"],
        "artifact_text": (
            "Supplier due diligence, contract, assurance and model-change "
            "responsibilities are approved."
        ),
    }
    values.update(changes)
    return ExternalEventSubmission(**values)


def test_lifecycle_phase_and_supervisor_decision_are_explicit(coordinator):
    created = coordinator.create_demo_case(SAMPLES["human_full_review"])
    assert created["state"]["lifecycle_status"] == "NEW"
    assert created["state"]["domain_phase"] == "INTAKE"

    case = coordinator.start(created["case_id"])
    state = case["state"]
    decision = state["supervisor_decision"]

    assert state["lifecycle_status"] == "AWAITING_HUMAN"
    assert state["domain_phase"] == "INPUT_CONFIRMATION"
    assert decision["policy_version"]
    assert decision["allowed_actions"] == []
    assert decision["human_decision_required"] is True
    assert decision["external_write_permitted"] is False
    assert {"approve_case", "select_materiality", "select_2lod", "bypass_gate"} <= set(
        decision["prohibited_actions"]
    )


def test_external_event_validation_resume_and_idempotency(coordinator):
    created = coordinator.create_demo_case(SAMPLES["missing_supplier_evidence"])
    waiting = coordinator.start(created["case_id"])

    assert waiting["status"] == "AWAITING_EXTERNAL_EVENT"
    assert waiting["pending_gate"] is None
    assert waiting["pending_event"]["status"] == "WAITING"

    with pytest.raises(ValueError, match="correlation ID"):
        coordinator.submit_external_event(
            waiting["case_id"],
            _external_event(waiting, correlation_id="CORR-WRONG"),
        )
    with pytest.raises(ValueError, match="source"):
        coordinator.submit_external_event(
            waiting["case_id"],
            _external_event(waiting, source="untrusted_source"),
        )
    with pytest.raises(ValueError, match="version is stale"):
        coordinator.submit_external_event(
            waiting["case_id"],
            _external_event(
                waiting,
                case_state_version=waiting["state"]["case_state_version"] + 1,
            ),
        )

    event = _external_event(waiting)
    resumed = coordinator.submit_external_event(waiting["case_id"], event)
    assert resumed["event_submission"]["status"] == "ACCEPTED"
    assert resumed["pending_gate"]["gate_id"] == "input_confirmation"
    assert resumed["state"]["processed_external_events"][-1]["event_id"] == event.event_id
    assert "check_supplier_evidence" in resumed["state"]["completed_actions"]
    assert resumed["state"]["agent_action_trace"][-1]["proposal"]["selected_action"]
    assert resumed["state"]["current_action_proposal"] == {}
    assert resumed["state"]["current_action_authorisation"] == {}
    assert resumed["state"]["current_tool_invocation"] == {}
    assert resumed["state"]["supervisor_decision"]["allowed_actions"] == []
    assert resumed["state"]["supervisor_decision"]["human_decision_required"] is True

    replayed = coordinator.submit_external_event(waiting["case_id"], event)
    assert replayed["event_submission"]["status"] == "IDEMPOTENT_REPLAY"
    assert len(replayed["state"]["processed_external_events"]) == 1


def test_external_event_timeout_enters_control_exception(coordinator):
    created = coordinator.create_demo_case(SAMPLES["missing_supplier_evidence"])
    waiting = coordinator.start(created["case_id"])
    timed_out = coordinator.submit_external_event(
        waiting["case_id"],
        _external_event(waiting, event_type="timeout", artifact_text=""),
    )

    assert timed_out["pending_gate"]["gate_id"] == "control_exception_review"
    assert timed_out["state"]["control_exception"]["code"] == "EXTERNAL_EVENT_TIMEOUT"
    assert timed_out["state"]["lifecycle_status"] == "CONTROL_EXCEPTION"


def test_external_response_event_resumes_the_same_waiting_case(coordinator):
    created = coordinator.create_demo_case(SAMPLES["missing_supplier_evidence"])
    waiting = coordinator.start(created["case_id"])
    resumed = coordinator.submit_external_event(
        waiting["case_id"],
        _external_event(waiting, event_type="external_response_received"),
    )

    assert resumed["case_id"] == waiting["case_id"]
    assert resumed["event_submission"]["status"] == "ACCEPTED"
    assert resumed["state"]["processed_external_events"][-1]["event_type"] == (
        "external_response_received"
    )
    assert resumed["pending_gate"]["gate_id"] == "input_confirmation"


def test_control_exception_supports_versioned_deterministic_recovery(coordinator):
    created = coordinator.create_demo_case(SAMPLES["invalid_tool_proposal"])
    failed = coordinator.start(created["case_id"])
    assert failed["state"]["tool_call_count"] == 0
    assert failed["pending_gate"]["gate_id"] == "control_exception_review"

    with pytest.raises(ValueError, match="version is stale"):
        coordinator.recover_control_exception(
            failed["case_id"],
            ControlRecoveryRequest(
                action="deterministic_fallback",
                rationale="Use the safe deterministic fallback.",
                reviewer="AIRO tester",
                case_state_version=failed["state"]["case_state_version"] + 1,
            ),
        )

    recovered = coordinator.recover_control_exception(
        failed["case_id"],
        ControlRecoveryRequest(
            action="deterministic_fallback",
            rationale="Use the safe deterministic fallback.",
            reviewer="AIRO tester",
            case_state_version=failed["state"]["case_state_version"],
        ),
    )
    assert recovered["state"]["control_exception"] is None
    assert recovered["state"]["tool_call_count"] > 0
    assert recovered["pending_gate"]["gate_id"] == "input_confirmation"
    assert recovered["state"]["agent_action_trace"][-1]["selection_source"] == (
        "deterministic_policy"
    )
    assert recovered["state"]["human_decisions"][-1]["action"] == ("deterministic_fallback")


def test_readiness_and_completion_are_deterministic_guards(coordinator):
    created = coordinator.create_demo_case(SAMPLES["human_full_review"])
    blocked = ReadinessPolicy().evaluate(created["state"])
    assert not blocked.ready_for_engines
    assert blocked.facts_requiring_confirmation

    incomplete = CompletionPolicy().evaluate(created["state"])
    assert not incomplete.complete
    assert "final_decision_present" in incomplete.blockers

    case = coordinator.start(created["case_id"])
    for action in ("confirm", "confirm", "approve"):
        case = coordinator.resume(
            case["case_id"],
            HumanDecision(action=action, rationale="AIRO test decision."),
        )
    assert case["state"]["lifecycle_status"] == "COMPLETED"
    assert case["state"]["completion_evaluation"]["complete"] is True
    assert all(case["state"]["completion_evaluation"]["criteria"].values())


def test_tool_contracts_results_and_authorisations_are_auditable(coordinator):
    tools = coordinator.tool_metadata()
    assert tools
    for contract in tools:
        assert contract["authority_class"]
        assert contract["data_permissions"]
        assert contract["result_verifier"]
        assert contract["owner"]

    created = coordinator.create_demo_case(SAMPLES["human_full_review"])
    case = coordinator.start(created["case_id"])
    history = coordinator.action_history(case["case_id"])
    assert history["authorisations"]
    assert history["tool_results"]
    assert history["verification_results"]
    assert all(item["status"] for item in history["verification_results"])


def test_human_decisions_reject_stale_context_and_replay(coordinator):
    created = coordinator.create_demo_case(SAMPLES["human_full_review"])
    case = coordinator.start(created["case_id"])
    stale = HumanDecision(
        decision_id="DEC-STALE-CONTEXT",
        action="confirm",
        rationale="Stale test.",
        case_id=case["case_id"],
        gate_id="input_confirmation",
        case_state_version=case["state"]["case_state_version"] + 1,
        rule_version=case["state"]["rule_version"],
    )
    with pytest.raises(ValueError, match="version is stale"):
        coordinator.resume(case["case_id"], stale)

    accepted = HumanDecision(
        decision_id="DEC-IDEMPOTENCY-TEST",
        action="confirm",
        rationale="Current test.",
    )
    coordinator.resume(case["case_id"], accepted)
    with pytest.raises(ValueError, match="already been processed"):
        coordinator.resume(case["case_id"], accepted)
