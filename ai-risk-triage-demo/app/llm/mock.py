from __future__ import annotations

import re
from typing import Any

from app.agent.policy import ACTION_TO_TOOL
from app.llm.base import LLMClient
from app.schemas import (
    ActionProposal,
    ActionType,
    ChallengeResult,
    EvidenceExtraction,
    EvidenceItem,
    ToolIdentifier,
)


class MockLLMClient(LLMClient):
    """Deterministic demonstration fallback used for tests and model-free demos."""

    runtime_name = "mock-llm"

    def health(self) -> tuple[bool, str]:
        return True, "Deterministic mock LLM is available."

    def extract_evidence(
        self, questionnaire: dict[str, Any], numbered_evidence: str
    ) -> EvidenceExtraction:
        raw_lines = numbered_evidence.splitlines()
        facts: list[EvidenceItem] = []
        signals: list[str] = []
        inconsistencies: list[str] = []

        keywords = {
            "personal data": "Personal-data processing is referenced.",
            "employee name": "Employee names are referenced.",
            "email": "Email data is referenced.",
            "supplier": "A supplier dependency is referenced.",
            "autonomous": "Autonomous operation is referenced.",
            "human review": "Human review is referenced.",
            "continuity": "Business-continuity controls are referenced.",
            "kill switch": "A kill-switch control is referenced.",
            "customer": "Customer interaction or impact is referenced.",
        }

        for line in raw_lines:
            match = re.match(r"(\d+):\s?(.*)", line)
            if not match:
                continue
            line_no = int(match.group(1))
            content = match.group(2).strip()
            lower = content.lower()
            for keyword, claim in keywords.items():
                if keyword in lower:
                    facts.append(
                        EvidenceItem(
                            claim=f"{claim} Evidence: {content[:180]}",
                            line_refs=[line_no],
                            confidence=0.82,
                        )
                    )
                    signals.append(keyword)

        joined = numbered_evidence.lower()
        if not questionnaire.get("personal_data") and any(
            term in joined for term in ("employee name", "email", "personal data")
        ):
            inconsistencies.append(
                "Evidence references possible personal data although the questionnaire answer is false."
            )

        summary_source = " ".join(line.split(":", 1)[-1].strip() for line in raw_lines)
        summary = summary_source[:500] or "No supporting evidence was supplied."
        if "[DEMO:INVALID_CITATION]" in numbered_evidence:
            # Protected mock fixture: exercise citation rejection without changing
            # production/Ollama behaviour or teaching the verifier to trust a marker.
            facts.append(
                EvidenceItem(
                    claim="Untrusted document instruction was preserved as submitted data.",
                    line_refs=[999],
                    confidence=0.82,
                )
            )
        return EvidenceExtraction(
            summary=summary,
            facts=facts[:12],
            potential_inconsistencies=inconsistencies,
            risk_signals=sorted(set(signals)),
        )

    def challenge(self, state: dict[str, Any]) -> ChallengeResult:
        materiality = state.get("materiality_result", {})
        exceptions = list(state.get("inconsistencies", []))
        questions: list[str] = []
        questionnaire = state.get("questionnaire", {})

        if materiality.get("proposed_materiality_band") in {
            "negligible",
            "minor",
        } and not questionnaire.get("approved_pattern"):
            exceptions.append(
                "The low proposed band is not supported by an explicitly approved pattern."
            )
            questions.append(
                "Is this use case within an approved and sufficiently comparable pattern?"
            )

        if questionnaire.get("external_model_or_supplier"):
            questions.append(
                "Has the supplier, contract and model-change responsibility been confirmed?"
            )

        if questionnaire.get("autonomous_actions"):
            questions.append(
                "Are action limits, human approval, pause and rollback controls evidenced?"
            )

        return ChallengeResult(
            exceptions=sorted(set(exceptions)),
            follow_up_questions=sorted(set(questions)),
            challenge_summary=(
                "The deterministic mock challenge identified items requiring AIRO attention."
                if exceptions or questions
                else "No additional challenge was identified by the deterministic mock."
            ),
        )

    def propose_action(
        self,
        state: dict[str, Any],
        allowed_actions: list[ActionType],
        allowed_tools: list[ToolIdentifier],
    ) -> ActionProposal:
        """Deterministically emulate a bounded structured router for demos and tests."""

        del allowed_tools
        mode = state.get("demo_controls", {}).get("router_mode", "normal")
        action = allowed_actions[0]
        selected_tool = ACTION_TO_TOOL[action]
        confidence = 0.95
        reason = "The governed mock selected the first supervisor-prioritised objective."
        if mode == "low_confidence":
            confidence = 0.20
            reason = "Protected demo response is intentionally below the policy threshold."
        elif mode == "non_allowlisted_tool":
            selected_tool = ToolIdentifier.MATERIALITY_ENGINE
            reason = "Protected demo response intentionally proposes a prohibited tool."
        return ActionProposal(
            selected_action=action,
            selected_tool=selected_tool,
            reason=reason,
            inputs_required=(
                ["questionnaire", "evidence_text"]
                if action
                in {
                    ActionType.EXTRACT_SUBMITTED_EVIDENCE,
                    ActionType.CHECK_QUESTIONNAIRE_EVIDENCE_CONSISTENCY,
                }
                else ["state"]
            ),
            confidence=confidence,
            human_review_required=False,
        )
