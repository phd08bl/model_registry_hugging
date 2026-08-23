from app.engines.materiality import calculate_materiality
from app.samples import SAMPLES


def _answers(sample_name: str) -> dict:
    return SAMPLES[sample_name].questionnaire.model_dump()


def test_low_risk_sample_is_negligible():
    result = calculate_materiality(_answers("human_full_review"))

    assert result["raw_score"] == 0
    assert result["proposed_materiality_band"] == "negligible"
    assert result["dealbreakers"] == []


def test_critical_autonomous_customer_case_is_severe():
    result = calculate_materiality(_answers("straight_through_ineligible"))

    assert result["proposed_materiality_band"] == "severe"
    assert "Autonomous customer decision/action" in result["dealbreakers"]
    assert "Autonomous action in a critical process" in result["dealbreakers"]


def test_minimum_route_can_override_score_threshold():
    answers = _answers("human_full_review")
    answers["critical_process_dependency"] = True
    result = calculate_materiality(answers)

    assert result["threshold_band"] == "minor"
    assert result["proposed_materiality_band"] == "material"
    assert result["minimum_route_rules"]
