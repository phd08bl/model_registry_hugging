from app.samples import SAMPLES
from app.schemas import HistoricalAssessment
from app.services.calibration import DEMO_HISTORY, run_backtest, run_sensitivity


def test_backtest_reports_false_lows_without_changing_rules():
    result = run_backtest(DEMO_HISTORY)

    assert result["dataset_size"] == 3
    assert result["metrics"]["false_low_count"] == 1
    assert result["rule_version"] == "demo-materiality-1.0"


def test_sensitivity_reports_answer_influence():
    result = run_sensitivity(SAMPLES["human_full_review"].questionnaire)

    autonomous = next(
        row for row in result["one_at_a_time_changes"] if row["field"] == "autonomous_actions"
    )
    assert autonomous["score_delta"] == 5
    assert autonomous["new_band"] == "minor"


def test_backtest_accepts_team_supplied_history():
    item = HistoricalAssessment(
        case_reference="TEAM-001",
        questionnaire=SAMPLES["human_full_review"].questionnaire,
        expert_materiality_band="negligible",
    )
    assert run_backtest([item])["metrics"]["exact_match_rate"] == 1.0
