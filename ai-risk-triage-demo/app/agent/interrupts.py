from __future__ import annotations

from typing import Any

from app.engines.autonomy import GateEvaluation


class AIROInterruptController:
    """Builds consistent, evidence-linked governance interrupt contracts."""

    gate_version = "airo-gates-1.0"

    def build_payload(
        self,
        state: dict[str, Any],
        evaluation: GateEvaluation,
        *,
        title: str,
        decision_required: str,
        reason: str,
        allowed_actions: list[str],
        effects: dict[str, str],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        extraction = state.get("evidence_extraction", {})
        return {
            "gate_id": evaluation.gate_id,
            "gate_version": self.gate_version,
            "title": title,
            "case_id": state["case_id"],
            "decision_required": decision_required,
            "summary": decision_required,
            "reason": reason,
            "supporting_facts": state.get("confirmed_facts", []),
            "evidence": extraction.get("facts", []),
            "citations": [
                {
                    "claim": fact.get("claim"),
                    "source": fact.get("source"),
                    "line_refs": fact.get("line_refs", []),
                }
                for fact in extraction.get("facts", [])
            ],
            "relevant_deterministic_rule": evaluation.to_dict(),
            "coordinator_recommendation": state.get("recommended_next_action", {}),
            "uncertainty_and_verification": {
                "latest_verification": state.get("latest_verification"),
                "open_issues": state.get("open_issues", []),
            },
            "allowed_actions": allowed_actions,
            "action_effects": effects,
            "rationale_required": {
                action: action
                in {
                    "proceed_with_gap",
                    "proceed",
                    "return_for_evidence",
                    "return_for_review",
                    "override",
                    "cancel_case",
                }
                for action in allowed_actions
            },
            "decision_authority": "AI Risk Oversight (AIRO)",
            "context": context,
            "autonomy": evaluation.to_dict(),
            "governance_message": (
                "The Coordinator is paused. AIRO must record the accountable decision."
            ),
        }
