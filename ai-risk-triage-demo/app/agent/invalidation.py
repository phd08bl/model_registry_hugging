from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from app.schemas import StateInvalidation

RISK_ENGINE_FIELDS = {
    "customer_facing",
    "customer_decisioning",
    "personal_data",
    "sensitive_data",
    "external_model_or_supplier",
    "autonomous_actions",
    "critical_process_dependency",
    "human_review_of_outputs",
    "financial_impact",
}


def invalidation_update(
    state: dict[str, Any],
    *,
    answer_updates: dict[str, Any] | None = None,
    evidence_changed: bool = False,
    trigger_reason: str | None = None,
) -> dict[str, Any]:
    """Invalidate only outputs that depend on changed evidence or answers."""

    changed_fields = {
        key
        for key, value in (answer_updates or {}).items()
        if state.get("questionnaire", {}).get(key) != value
    }
    affected = {
        "evidence_extraction",
        "evidence_claims",
        "confirmed_facts",
        "mandatory_evidence_gaps",
        "challenge_summary",
        "follow_up_questions",
        "exceptions",
        "confirmed_exceptions",
        "review_pack",
    }
    material_change = bool(changed_fields & RISK_ENGINE_FIELDS)
    if changed_fields & RISK_ENGINE_FIELDS:
        affected.update(
            {
                "materiality_result",
                "lod2_result",
                "proposed_outcome",
                "final_outcome",
                "publication_draft",
            }
        )
    elif changed_fields or evidence_changed:
        affected.update({"final_outcome", "publication_draft"})

    now = datetime.now(UTC).isoformat()
    invalidations = list(state.get("invalidations", []))
    superseded = list(state.get("superseded_results", []))
    updates: dict[str, Any] = {}
    trigger = trigger_reason or ", ".join(sorted(changed_fields)) or "submitted evidence changed"
    for key in sorted(affected):
        previous = state.get(key)
        if not previous:
            continue
        version = previous.get("rule_version") if isinstance(previous, dict) else None
        invalidations.append(
            StateInvalidation(
                invalidation_id=f"INV-{uuid.uuid4().hex[:10].upper()}",
                invalidated_result=key,
                previous_version=version,
                reason="A dependency changed; stale output must not remain authoritative.",
                triggering_change=trigger,
                material_change=material_change,
                previous_approval_remains_effective=key != "final_outcome",
                invalidated_at=now,
            ).model_dump()
        )
        superseded.append(
            {
                "result_type": key,
                "value": previous,
                "superseded_at": now,
                "trigger": trigger,
            }
        )
        if isinstance(previous, list):
            updates[key] = []
        elif isinstance(previous, str):
            updates[key] = ""
        else:
            updates[key] = {}

    updates.update(
        {
            "invalidations": invalidations,
            "superseded_results": superseded,
            "current_authoritative_results": {
                key: value
                for key, value in state.get("current_authoritative_results", {}).items()
                if key not in affected
            },
            "material_change_requires_airo_review": material_change
            or bool(state.get("final_outcome")),
        }
    )

    # completed_nodes is an audit-friendly workflow marker, but it must not make
    # invalidated downstream stages look current in the UI. Deterministic engines
    # remain current when only evidence changes because their questionnaire inputs
    # have not changed; challenge/review/publication stages do not.
    stale_nodes = {
        "input_gate",
        "challenge_assessment",
        "exception_gate",
        "review_pack",
        "final_gate",
        "publication_gate",
        "publish",
    }
    if material_change:
        stale_nodes.add("decision_engines")
    updates["completed_nodes"] = [
        node for node in state.get("completed_nodes", []) if node not in stale_nodes
    ]

    # Challenge observations are advisory, but observations derived from stale
    # inputs must not continue to be displayed as if they describe the current case.
    updates["advisory_observations"] = [
        item
        for item in state.get("advisory_observations", [])
        if item.get("source_tool") != "challenge_assessor"
    ]
    return updates
