from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.schemas import CompletionEvaluation
from app.versions import AGENT_POLICY_VERSION


class CompletionPolicy:
    """Deterministic final guard; incomplete or stale Cases cannot become completed."""

    def evaluate(self, state: dict[str, Any]) -> CompletionEvaluation:
        open_blocking_issues = [
            item
            for item in state.get("open_issues", [])
            if item.get("status") == "open" and not item.get("advisory", False)
        ]
        criteria = {
            "no_open_objectives": not bool(state.get("open_objectives")),
            "no_pending_actions": not bool(state.get("pending_actions")),
            "no_blocking_issues": not bool(open_blocking_issues),
            "risk_proposals_current": bool(
                state.get("materiality_result") and state.get("lod2_result")
            )
            and not bool(
                {"materiality_result", "lod2_result"} & set(state.get("stale_outputs", []))
            ),
            "final_decision_present": bool(state.get("final_outcome")),
            "review_pack_current": bool(state.get("review_pack"))
            and "review_pack" not in state.get("stale_outputs", []),
            "publication_reconciled": state.get("publication_status")
            in {"PUBLISHED_LOCAL_DEMO", "NOT_REQUIRED"},
            "no_open_control_exception": not bool(
                state.get("control_exception", {}).get("status") == "OPEN"
                if state.get("control_exception")
                else False
            ),
        }
        blockers = [name for name, met in criteria.items() if not met]
        return CompletionEvaluation(
            complete=all(criteria.values()),
            criteria=criteria,
            blockers=blockers,
            evaluated_at=datetime.now(UTC).isoformat(),
            policy_version=AGENT_POLICY_VERSION,
        )
