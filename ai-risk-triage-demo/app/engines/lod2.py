from __future__ import annotations

from typing import Any

DEMO_TRIGGER_VERSION = "demo-2lod-1.0"


def calculate_2lod_triggers(questionnaire: dict[str, Any]) -> dict[str, Any]:
    """Apply answer-based specialist triggers independent of materiality score."""

    triggers: list[dict[str, str]] = []

    def trigger(team: str, condition: bool, rule: str, rationale: str) -> None:
        if condition:
            triggers.append(
                {
                    "team": team,
                    "rule": rule,
                    "rationale": rationale,
                    "source": "confirmed questionnaire answer",
                }
            )

    trigger(
        "Data & Privacy",
        bool(questionnaire.get("personal_data") or questionnaire.get("sensitive_data")),
        "TR-DATA-01",
        "Personal or sensitive data is processed.",
    )
    trigger(
        "Third-party / Supplier Risk",
        bool(questionnaire.get("external_model_or_supplier")),
        "TR-TPRM-01",
        "An external model, service or supplier is used.",
    )
    trigger(
        "Conduct / Customer Risk",
        bool(questionnaire.get("customer_facing") or questionnaire.get("customer_decisioning")),
        "TR-CONDUCT-01",
        "The use case interacts with or influences customers.",
    )
    trigger(
        "Operational Risk",
        bool(questionnaire.get("autonomous_actions")),
        "TR-OPRISK-01",
        "The system can perform autonomous actions.",
    )
    trigger(
        "Technology / Cyber",
        bool(
            questionnaire.get("autonomous_actions")
            or questionnaire.get("critical_process_dependency")
            or questionnaire.get("external_model_or_supplier")
        ),
        "TR-TECH-01",
        "Technology, autonomy, criticality or supplier dependency is present.",
    )
    trigger(
        "Business Continuity",
        bool(questionnaire.get("critical_process_dependency")),
        "TR-BCM-01",
        "The AI use case supports a critical process.",
    )
    trigger(
        "Model Risk / AI IVT",
        bool(
            questionnaire.get("customer_decisioning")
            or questionnaire.get("autonomous_actions")
            or questionnaire.get("critical_process_dependency")
        ),
        "TR-MODEL-01",
        "The declared use presents features that may require validation judgement.",
    )

    teams = sorted({item["team"] for item in triggers})
    return {
        "rule_version": DEMO_TRIGGER_VERSION,
        "demo_warning": "Illustrative triggers only — not approved PwC or MRO routing.",
        "teams": teams,
        "triggers": triggers,
    }
