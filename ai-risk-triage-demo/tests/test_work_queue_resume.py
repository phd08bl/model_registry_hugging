from app.config import Settings
from app.coordinator import CaseCoordinator
from app.llm.mock import MockLLMClient
from app.samples import SAMPLES
from app.schemas import HumanDecision


def test_pending_case_can_resume_after_coordinator_restart(tmp_path):
    settings = Settings(
        llm_mode="mock",
        case_db_path=str(tmp_path / "cases.db"),
        checkpoint_db_path=str(tmp_path / "checkpoints.db"),
    )
    first = CaseCoordinator(settings, MockLLMClient())
    created = first.create_demo_case(SAMPLES["human_full_review"])
    case_id = created["case_id"]
    paused = first.start(case_id)

    assert paused["pending_gate"]["gate_id"] == "input_confirmation"
    assert paused["status"] == "AWAITING_INPUT_CONFIRMATION"
    first._checkpoint_connection.close()

    restarted = CaseCoordinator(settings, MockLLMClient())
    try:
        restored = restarted.get_case(case_id)
        assert restored["pending_gate"]["gate_id"] == "input_confirmation"
        assert restored["state"]["current_gate"] == "input_confirmation"
        assert restored["state"]["agent_action_trace"]

        resumed = restarted.resume(
            case_id,
            HumanDecision(
                action="confirm",
                rationale="Restored inputs reviewed and confirmed.",
                reviewer="AIRO restart test",
            ),
        )
        assert resumed["pending_gate"]["gate_id"] == "final_triage"
        assert resumed["status"] == "AWAITING_FINAL_DECISION"
        assert resumed["state"]["human_decisions"][-1]["reviewer"] == "AIRO restart test"
        assert resumed["state"]["confirmed_facts"]
    finally:
        restarted._checkpoint_connection.close()


def test_terminal_case_is_viewable_but_cannot_resume(coordinator):
    created = coordinator.create_demo_case(SAMPLES["human_full_review"])
    case_id = created["case_id"]
    coordinator.start(case_id)
    cancelled = coordinator.resume(
        case_id,
        HumanDecision(
            action="cancel_case",
            rationale="Case withdrawn by the owner.",
            reviewer="AIRO queue test",
        ),
    )

    restored = coordinator.get_case(case_id)
    assert cancelled["status"] == "CANCELLED"
    assert restored["pending_gate"] is None
    assert restored["state"]["current_gate"] is None

    try:
        coordinator.resume(
            case_id,
            HumanDecision(action="confirm", rationale="Should not resume."),
        )
    except ValueError as exc:
        assert "not waiting at a Human Gate" in str(exc)
    else:
        raise AssertionError("A terminal Case must not be resumable.")
