from app.engines.lod2 import calculate_2lod_triggers
from app.samples import SAMPLES


def test_2lod_triggers_are_answer_based():
    answers = SAMPLES["human_evidence_conflict"].questionnaire.model_dump()
    result = calculate_2lod_triggers(answers)

    assert "Third-party / Supplier Risk" in result["teams"]
    assert "Technology / Cyber" in result["teams"]
    assert "Conduct / Customer Risk" not in result["teams"]
    assert all(item["rule"].startswith("TR-") for item in result["triggers"])


def test_materiality_score_is_not_an_input_to_2lod_engine():
    answers = SAMPLES["human_full_review"].questionnaire.model_dump()
    answers["personal_data"] = True
    result = calculate_2lod_triggers(answers)

    assert result["teams"] == ["Data & Privacy"]
