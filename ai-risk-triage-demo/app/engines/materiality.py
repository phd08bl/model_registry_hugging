from __future__ import annotations

from typing import Any

DEMO_RULE_VERSION = "demo-materiality-1.0"

BAND_ORDER = ["negligible", "minor", "moderate", "material", "severe"]

VALIDATION_REQUIREMENT = {
    "negligible": "None proposed",
    "minor": "Optional / proportionate review",
    "moderate": "Standard or light validation — AIRO/IVT judgement required",
    "material": "Extended or standard validation — AIRO/IVT judgement required",
    "severe": "Extended independent validation proposed",
}


def _score_band(score: int) -> str:
    if score <= 3:
        return "negligible"
    if score <= 7:
        return "minor"
    if score <= 12:
        return "moderate"
    if score <= 18:
        return "material"
    return "severe"


def _max_band(current: str, minimum: str) -> str:
    return BAND_ORDER[max(BAND_ORDER.index(current), BAND_ORDER.index(minimum))]


def calculate_materiality(questionnaire: dict[str, Any]) -> dict[str, Any]:
    """Apply transparent demo scoring, thresholds and minimum-route rules.

    These are intentionally illustrative and must not be treated as PwC or MRO policy.
    """

    scores: list[dict[str, Any]] = []

    def add(factor: str, active: bool, points: int, rationale: str) -> None:
        awarded = points if active else 0
        scores.append(
            {
                "factor": factor,
                "active": active,
                "available_points": points,
                "awarded_points": awarded,
                "rationale": rationale,
            }
        )

    add("Customer-facing", bool(questionnaire.get("customer_facing")), 2, "Direct exposure")
    add(
        "Customer decisioning",
        bool(questionnaire.get("customer_decisioning")),
        4,
        "Influences customer outcomes",
    )
    add("Personal data", bool(questionnaire.get("personal_data")), 2, "Data risk")
    add("Sensitive data", bool(questionnaire.get("sensitive_data")), 4, "Elevated data risk")
    add(
        "External model or supplier",
        bool(questionnaire.get("external_model_or_supplier")),
        2,
        "Third-party dependency",
    )
    add(
        "Autonomous actions",
        bool(questionnaire.get("autonomous_actions")),
        5,
        "System may act without prior approval",
    )
    add(
        "Critical process dependency",
        bool(questionnaire.get("critical_process_dependency")),
        5,
        "Operational resilience impact",
    )
    add(
        "No human review of outputs",
        not bool(questionnaire.get("human_review_of_outputs", True)),
        3,
        "Reduced preventative oversight",
    )

    impact_points = {"low": 0, "medium": 2, "high": 5}.get(
        str(questionnaire.get("financial_impact", "low")), 0
    )
    scores.append(
        {
            "factor": "Financial or business impact",
            "active": impact_points > 0,
            "available_points": 5,
            "awarded_points": impact_points,
            "rationale": f"Declared impact: {questionnaire.get('financial_impact', 'low')}",
        }
    )

    raw_score = sum(item["awarded_points"] for item in scores)
    threshold_band = _score_band(raw_score)
    final_band = threshold_band
    uplift_reasons: list[str] = []
    dealbreakers: list[str] = []
    minimum_routes: list[str] = []

    if questionnaire.get("sensitive_data"):
        minimum_routes.append("Sensitive data sets a minimum route of moderate")
        final_band = _max_band(final_band, "moderate")

    if questionnaire.get("critical_process_dependency"):
        minimum_routes.append("Critical-process dependency sets a minimum route of material")
        final_band = _max_band(final_band, "material")

    if questionnaire.get("autonomous_actions") and questionnaire.get("customer_decisioning"):
        dealbreakers.append("Autonomous customer decision/action")
        uplift_reasons.append("Dealbreaker uplift to at least material")
        final_band = _max_band(final_band, "material")

    if questionnaire.get("autonomous_actions") and questionnaire.get("critical_process_dependency"):
        dealbreakers.append("Autonomous action in a critical process")
        uplift_reasons.append("Dealbreaker uplift to severe")
        final_band = "severe"

    return {
        "rule_version": DEMO_RULE_VERSION,
        "demo_warning": "Illustrative rules only — not approved PwC or MRO methodology.",
        "score_details": scores,
        "raw_score": raw_score,
        "threshold_band": threshold_band,
        "dealbreakers": dealbreakers,
        "minimum_route_rules": minimum_routes,
        "uplift_reasons": uplift_reasons,
        "proposed_materiality_band": final_band,
        "proposed_validation_requirement": VALIDATION_REQUIREMENT[final_band],
    }
