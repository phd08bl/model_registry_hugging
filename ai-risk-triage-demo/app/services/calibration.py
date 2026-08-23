from __future__ import annotations

from typing import Any

from app.engines.materiality import BAND_ORDER, DEMO_RULE_VERSION, calculate_materiality
from app.schemas import HistoricalAssessment, Questionnaire

SENSITIVITY_FIELDS = (
    "approved_pattern",
    "customer_facing",
    "customer_decisioning",
    "personal_data",
    "sensitive_data",
    "external_model_or_supplier",
    "autonomous_actions",
    "critical_process_dependency",
    "human_review_of_outputs",
)


def _index(band: str) -> int:
    return BAND_ORDER.index(band)


def run_backtest(cases: list[HistoricalAssessment]) -> dict[str, Any]:
    """Compare the demo rules with historical expert labels.

    This is diagnostic evidence for rule owners. It never updates rules automatically.
    """

    details: list[dict[str, Any]] = []
    false_low = 0
    false_high = 0
    exact = 0
    absolute_distance = 0

    for historical in cases:
        result = calculate_materiality(historical.questionnaire.model_dump())
        predicted = result["proposed_materiality_band"]
        expected = historical.expert_materiality_band
        distance = _index(predicted) - _index(expected)
        exact += int(distance == 0)
        false_low += int(distance < 0)
        false_high += int(distance > 0)
        absolute_distance += abs(distance)
        details.append(
            {
                "case_reference": historical.case_reference,
                "predicted_band": predicted,
                "expert_band": expected,
                "distance_in_bands": distance,
                "classification": (
                    "exact" if distance == 0 else "false_low" if distance < 0 else "false_high"
                ),
                "raw_score": result["raw_score"],
                "dealbreakers": result["dealbreakers"],
                "minimum_route_rules": result["minimum_route_rules"],
            }
        )

    total = len(cases)
    return {
        "rule_version": DEMO_RULE_VERSION,
        "dataset_size": total,
        "metrics": {
            "exact_match_rate": round(exact / total, 3),
            "false_low_count": false_low,
            "false_high_count": false_high,
            "mean_absolute_band_error": round(absolute_distance / total, 3),
        },
        "cases": details,
        "governance_message": (
            "Backtesting informs AIRO rule-owner review. No score, threshold or route is "
            "changed automatically. False-low cases should receive priority investigation."
        ),
    }


def run_sensitivity(questionnaire: Questionnaire) -> dict[str, Any]:
    """Flip one Boolean answer at a time and report the deterministic effect."""

    baseline_answers = questionnaire.model_dump()
    baseline = calculate_materiality(baseline_answers)
    rows: list[dict[str, Any]] = []
    for field in SENSITIVITY_FIELDS:
        changed = dict(baseline_answers)
        changed[field] = not bool(changed[field])
        if field == "personal_data" and changed.get("sensitive_data"):
            # The schema invariant would restore personal_data=True.
            continue
        candidate = calculate_materiality(changed)
        rows.append(
            {
                "field": field,
                "from": baseline_answers[field],
                "to": changed[field],
                "new_score": candidate["raw_score"],
                "score_delta": candidate["raw_score"] - baseline["raw_score"],
                "new_band": candidate["proposed_materiality_band"],
                "band_delta": _index(candidate["proposed_materiality_band"])
                - _index(baseline["proposed_materiality_band"]),
            }
        )

    return {
        "rule_version": baseline["rule_version"],
        "baseline": {
            "score": baseline["raw_score"],
            "band": baseline["proposed_materiality_band"],
        },
        "one_at_a_time_changes": rows,
        "governance_message": (
            "Sensitivity analysis exposes brittle thresholds and influential answers. "
            "AIRO must assess any rule change through controlled calibration and approval."
        ),
    }


DEMO_HISTORY = [
    HistoricalAssessment(
        case_reference="HIST-001",
        questionnaire=Questionnaire(
            use_case_name="Historical internal summary",
            purpose="Summarise non-sensitive internal notes for mandatory human review.",
            business_owner="Operations",
            approved_pattern=True,
        ),
        expert_materiality_band="negligible",
    ),
    HistoricalAssessment(
        case_reference="HIST-002",
        questionnaire=Questionnaire(
            use_case_name="Historical policy RAG",
            purpose="Answer colleague policy questions using a hosted external model.",
            business_owner="People Operations",
            external_model_or_supplier=True,
            financial_impact="medium",
        ),
        # Intentionally differs from the demo rules to illustrate a false-low review.
        expert_materiality_band="moderate",
    ),
    HistoricalAssessment(
        case_reference="HIST-003",
        questionnaire=Questionnaire(
            use_case_name="Historical autonomous credit action",
            purpose="Make autonomous customer credit actions in a critical process.",
            business_owner="Credit Operations",
            customer_facing=True,
            customer_decisioning=True,
            personal_data=True,
            sensitive_data=True,
            external_model_or_supplier=True,
            autonomous_actions=True,
            critical_process_dependency=True,
            human_review_of_outputs=False,
            financial_impact="high",
        ),
        expert_materiality_band="severe",
    ),
]
