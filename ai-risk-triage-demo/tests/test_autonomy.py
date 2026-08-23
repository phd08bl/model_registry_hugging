from app.engines.autonomy import AutonomyPolicyEngine
from app.engines.materiality import calculate_materiality
from app.samples import SAMPLES


def _eligible_state(profile: str) -> dict:
    questionnaire = SAMPLES["exception_based_eligible"].questionnaire.model_dump()
    return {
        "case_id": "AIRO-DEMO-ELIGIBLE",
        "autonomy_profile": profile,
        "questionnaire": questionnaire,
        "materiality_result": calculate_materiality(questionnaire),
        "exceptions": [],
        "missing_information": [],
        "inconsistencies": [],
    }


def test_human_governed_requires_final_gate():
    evaluation = AutonomyPolicyEngine().evaluate("final_triage", _eligible_state("human_governed"))
    assert evaluation.required is True


def test_exception_based_can_skip_non_sampled_low_risk_gate():
    engine = AutonomyPolicyEngine()
    state = _eligible_state("exception_based")
    evaluation = engine.evaluate("exception_resolution", state)

    assert evaluation.required is False
    assert evaluation.mode == "EXCEPTION_REVIEW"


def test_exception_forces_review():
    engine = AutonomyPolicyEngine()
    state = _eligible_state("exception_based")
    state["exceptions"] = ["Unsupported low-risk assumption"]

    assert engine.evaluate("exception_resolution", state).required is True


def test_evidence_request_is_mandatory_for_every_profile():
    engine = AutonomyPolicyEngine()
    for profile in (
        "human_governed",
        "conditional_review",
        "exception_based",
        "straight_through",
    ):
        assert engine.evaluate("evidence_request", _eligible_state(profile)).required is True


def test_human_governed_requires_every_decision_gate():
    engine = AutonomyPolicyEngine()
    state = _eligible_state("human_governed")

    assert all(
        engine.evaluate(gate_id, state).required
        for gate_id in (
            "input_confirmation",
            "exception_resolution",
            "final_triage",
            "publication",
        )
    )


def test_conditional_review_skips_clean_preparation_but_requires_final_and_publication():
    engine = AutonomyPolicyEngine()
    state = _eligible_state("conditional_review")

    assert engine.evaluate("input_confirmation", state).required is False
    assert engine.evaluate("exception_resolution", state).required is False
    assert engine.evaluate("final_triage", state).required is True
    assert engine.evaluate("publication", state).required is True


def test_conditional_review_restores_exception_review_when_needed():
    engine = AutonomyPolicyEngine()
    state = _eligible_state("conditional_review")
    state["exceptions"] = ["Review required"]

    assert engine.evaluate("exception_resolution", state).required is True


def test_exception_based_requires_initial_governance_then_applies_sampling():
    engine = AutonomyPolicyEngine()
    state = _eligible_state("exception_based")
    state.pop("materiality_result")
    assert engine.evaluate("input_confirmation", state).required is True

    state = _eligible_state("exception_based")
    assert engine.evaluate("exception_resolution", state).required is False
    assert engine.evaluate("final_triage", state).required is engine._sample_selected(
        state["case_id"]
    )
    assert engine.evaluate("publication", state).required is True


def test_exception_based_requires_review_for_elevated_risk():
    engine = AutonomyPolicyEngine()
    questionnaire = SAMPLES["straight_through_ineligible"].questionnaire.model_dump()
    state = {
        **_eligible_state("exception_based"),
        "questionnaire": questionnaire,
        "materiality_result": calculate_materiality(questionnaire),
    }

    assert engine.evaluate("exception_resolution", state).required is True
    assert engine.evaluate("final_triage", state).required is True


def test_straight_through_requires_input_then_skips_later_gates_when_eligible():
    engine = AutonomyPolicyEngine()
    state = _eligible_state("straight_through")
    state.pop("materiality_result")
    assert engine.evaluate("input_confirmation", state).required is True

    state = _eligible_state("straight_through")
    assert all(
        engine.evaluate(gate_id, state).required is False
        for gate_id in ("exception_resolution", "final_triage", "publication")
    )


def test_straight_through_fails_safely_when_ineligible():
    engine = AutonomyPolicyEngine()
    questionnaire = SAMPLES["straight_through_ineligible"].questionnaire.model_dump()
    state = {
        **_eligible_state("straight_through"),
        "questionnaire": questionnaire,
        "materiality_result": calculate_materiality(questionnaire),
    }

    assert all(
        engine.evaluate(gate_id, state).required
        for gate_id in ("exception_resolution", "final_triage", "publication")
    )


def test_legacy_straight_through_profile_remains_compatible():
    engine = AutonomyPolicyEngine()
    canonical = _eligible_state("straight_through_demo")
    legacy = _eligible_state("straight_through")

    for gate_id in ("input_confirmation", "exception_resolution", "final_triage", "publication"):
        assert (
            engine.evaluate(gate_id, canonical).required
            is engine.evaluate(gate_id, legacy).required
        )
