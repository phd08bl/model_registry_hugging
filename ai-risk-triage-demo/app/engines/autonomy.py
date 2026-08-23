from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from typing import Any

from app.versions import AUTONOMY_POLICY_VERSION

STRAIGHT_THROUGH_PROFILES = {"straight_through", "straight_through_demo"}


@dataclass(frozen=True)
class GateEvaluation:
    gate_id: str
    required: bool
    mode: str
    rationale: str
    policy_version: str = AUTONOMY_POLICY_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class AutonomyPolicyEngine:
    """Deterministic gate policy. The LLM never decides whether a gate is skipped."""

    policy_version = AUTONOMY_POLICY_VERSION

    @staticmethod
    def _sample_selected(case_id: str, rate: float = 0.25) -> bool:
        bucket = int(hashlib.sha256(case_id.encode("utf-8")).hexdigest()[:8], 16) / 0xFFFFFFFF
        return bucket < rate

    @staticmethod
    def _low_risk_eligible(state: dict[str, Any]) -> bool:
        questionnaire = state.get("questionnaire", {})
        materiality = state.get("materiality_result", {})
        band = materiality.get("proposed_materiality_band")
        return bool(
            band in {"negligible", "minor"}
            and questionnaire.get("approved_pattern")
            and not questionnaire.get("sensitive_data")
            and not questionnaire.get("customer_decisioning")
            and not questionnaire.get("autonomous_actions")
            and not questionnaire.get("critical_process_dependency")
            and not state.get("exceptions")
            and not state.get("missing_information")
            and not state.get("inconsistencies")
        )

    def evaluate(self, gate_id: str, state: dict[str, Any]) -> GateEvaluation:
        profile = state.get("autonomy_profile", "human_governed")
        exceptions = bool(
            state.get("exceptions")
            or state.get("missing_information")
            or state.get("inconsistencies")
        )
        band = state.get("materiality_result", {}).get("proposed_materiality_band")
        elevated = band in {"material", "severe"}
        eligible = self._low_risk_eligible(state)

        if gate_id == "evidence_request":
            verification_failure = bool(
                state.get("failed_actions")
                or state.get("prohibited_actions")
                or state.get("latest_verification", {}).get("disposition")
                in {"escalate", "rejected"}
            )
            return GateEvaluation(
                gate_id,
                True,
                "MANDATORY_REVIEW",
                (
                    "A failed or unverified governed action requires an AIRO decision."
                    if verification_failure
                    else "Missing or conflicting evidence requires an AIRO decision."
                ),
            )

        if profile == "human_governed":
            return GateEvaluation(
                gate_id,
                True,
                "MANDATORY_REVIEW",
                "The human-governed profile requires every configured decision gate.",
            )

        if gate_id == "publication" and profile not in STRAIGHT_THROUGH_PROFILES:
            return GateEvaluation(
                gate_id,
                True,
                "MANDATORY_REVIEW",
                "Formal write actions require explicit approval in this demo.",
            )

        if profile == "conditional_review":
            required = gate_id == "final_triage" or exceptions or elevated
            return GateEvaluation(
                gate_id,
                required,
                "CONDITIONAL_REVIEW",
                "Review is required for final triage, exceptions or elevated materiality."
                if required
                else "Complete non-exception input may proceed to the next mandatory gate.",
            )

        if profile == "exception_based":
            # Demo sampling is stable and policy-owned. Normal cases fall back to
            # their immutable case identifier; protected fixtures may provide a
            # non-user-editable key to make a teaching journey repeatable.
            sampling_key = state.get("sampling_key") or state["case_id"]
            sampled = gate_id == "final_triage" and self._sample_selected(sampling_key)
            required = exceptions or elevated or not eligible or sampled
            reason = (
                "Exception, elevated risk, ineligibility or deterministic sampling requires review."
                if required
                else "Approved low-risk pattern is eligible for exception-based processing."
            )
            return GateEvaluation(gate_id, required, "EXCEPTION_REVIEW", reason)

        if profile in STRAIGHT_THROUGH_PROFILES:
            required = not eligible and gate_id in {
                "input_confirmation",
                "exception_resolution",
                "final_triage",
            }
            if gate_id == "publication":
                required = not eligible
            return GateEvaluation(
                gate_id,
                required,
                "STRAIGHT_THROUGH",
                "Only eligible low-risk demo cases may proceed automatically."
                if not required
                else "The case is outside the approved straight-through demo boundary.",
            )

        return GateEvaluation(
            gate_id,
            True,
            "MANDATORY_REVIEW",
            "Unknown profile fails safely to mandatory human review.",
        )
