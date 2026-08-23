from __future__ import annotations

from typing import Any

REQUIREMENTS: list[tuple[str, tuple[str, ...], str]] = [
    (
        "personal_data",
        ("data classification", "privacy", "personal data"),
        "Data classification or privacy evidence",
    ),
    (
        "sensitive_data",
        ("sensitive", "special category", "classification"),
        "Sensitive-data classification and controls",
    ),
    (
        "external_model_or_supplier",
        ("supplier", "contract", "third-party", "vendor"),
        "Supplier, contract or due-diligence evidence",
    ),
    (
        "autonomous_actions",
        ("human approval", "pause", "kill switch", "failsafe"),
        "Autonomy limits, human approval and pause controls",
    ),
    (
        "critical_process_dependency",
        ("continuity", "recovery", "fallback", "resilience"),
        "Continuity, recovery and fallback evidence",
    ),
    (
        "customer_decisioning",
        ("customer", "decision", "appeal", "human review"),
        "Customer-outcome, review and recourse evidence",
    ),
]

PERSONAL_DATA_TERMS = (
    "employee name",
    "customer name",
    "email address",
    "personal data",
    "customer record",
    "employee identifier",
)


def numbered_text(text: str) -> str:
    lines = text.splitlines() or [""]
    return "\n".join(f"{index + 1}: {line}" for index, line in enumerate(lines))


def deterministic_evidence_checks(
    questionnaire: dict[str, Any], evidence_text: str
) -> tuple[list[str], list[str]]:
    lower = evidence_text.lower()
    missing: list[str] = []
    inconsistencies: list[str] = []

    if not evidence_text.strip():
        missing.append("A supporting evidence narrative or document extract")

    for field, keywords, description in REQUIREMENTS:
        if questionnaire.get(field) and not any(keyword in lower for keyword in keywords):
            missing.append(description)

    if not questionnaire.get("personal_data") and any(
        term in lower for term in PERSONAL_DATA_TERMS
    ):
        inconsistencies.append(
            "The questionnaire states that personal data is not used, but the evidence references names, email, identifiers or personal records."
        )

    if questionnaire.get("human_review_of_outputs") and (
        "fully automated" in lower or "no human review" in lower
    ):
        inconsistencies.append(
            "The questionnaire states that outputs receive human review, but the evidence suggests fully automated operation."
        )

    return sorted(set(missing)), sorted(set(inconsistencies))


def build_targeted_questions(missing: list[str], inconsistencies: list[str]) -> list[str]:
    questions = [f"Please provide or identify: {item}." for item in missing]
    questions.extend(
        f"Please clarify and evidence this inconsistency: {item}" for item in inconsistencies
    )
    return questions
