import pytest

from app.samples import SAMPLE_CATEGORIES, SAMPLES
from app.schemas import HumanDecision


def decision(action: str):
    return HumanDecision(action=action, rationale="Reviewed by AIRO tester")


def start_sample(coordinator, sample_name: str) -> tuple[str, dict]:
    created = coordinator.create_demo_case(SAMPLES[sample_name])
    return created["case_id"], coordinator.start(created["case_id"])


def test_catalogue_uses_typed_metadata_and_covers_all_profiles():
    assert len(SAMPLES) == 15
    assert {sample.category for sample in SAMPLES.values()} == set(SAMPLE_CATEGORIES)
    assert {sample.expected_assigned_profile for sample in SAMPLES.values()} == {
        "human_governed",
        "conditional_review",
        "exception_based",
        "straight_through_demo",
    }
    assert all(sample.sample_id == name for name, sample in SAMPLES.items())
    assert all(sample.learning_objectives for sample in SAMPLES.values())
    assert all(sample.interactive_steps for sample in SAMPLES.values())


@pytest.mark.parametrize(
    ("sample_name", "initial_gate"),
    [
        ("human_evidence_conflict", "evidence_request"),
        ("human_full_review", "input_confirmation"),
        ("agentic_ai_autonomy", "input_confirmation"),
        ("conditional_clean_final", "final_triage"),
        ("conditional_exception", "exception_resolution"),
        ("exception_based_eligible", "input_confirmation"),
        ("exception_based_sampled", "input_confirmation"),
        ("exception_based_triggered", "input_confirmation"),
        ("straight_through_eligible", "input_confirmation"),
        ("straight_through_ineligible", "input_confirmation"),
    ],
)
def test_primary_samples_follow_policy_owned_initial_route(
    coordinator, sample_name: str, initial_gate: str
):
    _, case = start_sample(coordinator, sample_name)
    assert case["pending_gate"]["gate_id"] == initial_gate


def test_exception_sampling_is_repeatable_and_explained(coordinator):
    case_id, _ = start_sample(coordinator, "exception_based_sampled")
    case = coordinator.resume(case_id, decision("confirm"))
    assert case["pending_gate"]["gate_id"] == "final_triage"
    assert "sampling" in case["pending_gate"]["reason"].lower()


def test_non_sampled_exception_case_skips_final_triage(coordinator):
    case_id, _ = start_sample(coordinator, "exception_based_eligible")
    case = coordinator.resume(case_id, decision("confirm"))
    assert case["pending_gate"]["gate_id"] == "publication"
    final_event = next(
        item for item in case["state"]["autonomy_log"] if item["gate_id"] == "final_triage"
    )
    assert final_event["required"] is False


def test_straight_through_demo_is_system_assigned_and_local_only(coordinator):
    case_id, case = start_sample(coordinator, "straight_through_eligible")
    assert case["state"]["autonomy_profile"] == "straight_through_demo"
    case = coordinator.resume(case_id, decision("confirm"))
    assert case["status"] == "CLOSED"
    assert case["state"]["publication_status"] == "PUBLISHED_LOCAL_DEMO"


def test_ineligible_straight_through_attempt_is_downgraded(coordinator):
    _, case = start_sample(coordinator, "straight_through_ineligible")
    assignment = case["state"]["autonomy_assignment"]
    assert assignment["approved_maximum_profile"] == "straight_through_demo"
    assert assignment["effective_profile"] == "human_governed"
    assert assignment["downgraded"] is True


def test_agentic_case_runs_bounded_autonomy_check(coordinator):
    _, case = start_sample(coordinator, "agentic_ai_autonomy")
    assert any(
        item["proposal"]["selected_action"] == "check_agentic_ai_autonomy"
        for item in case["state"]["agent_action_trace"]
    )
