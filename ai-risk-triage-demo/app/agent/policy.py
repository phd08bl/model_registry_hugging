from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from app.engines.autonomy import AutonomyPolicyEngine, GateEvaluation
from app.schemas import (
    CASE_COMPLETION_CRITERIA,
    CASE_OBJECTIVE_STATEMENT,
    ActionProposal,
    ActionType,
    AutonomyAssignment,
    AutonomyProfile,
    CaseObjective,
    ToolIdentifier,
)
from app.versions import AGENT_POLICY_VERSION

DEMO_POLICY_VERSION = AGENT_POLICY_VERSION
PROFILE_RANK: dict[str, int] = {
    "human_governed": 0,
    "conditional_review": 1,
    "exception_based": 2,
    "straight_through": 3,
    "straight_through_demo": 3,
}

# These are demonstration fixtures, not PwC or MRO policy. Normal case creation
# never consults this registry and therefore always receives human_governed.
DEMO_PATTERN_MAXIMUMS: dict[str, AutonomyProfile] = {
    "human_evidence_conflict": "human_governed",
    "human_full_review": "human_governed",
    "agentic_ai_autonomy": "human_governed",
    "conditional_clean_final": "conditional_review",
    "conditional_exception": "conditional_review",
    "exception_based_eligible": "exception_based",
    "exception_based_triggered": "exception_based",
    "straight_through_eligible": "straight_through_demo",
    "straight_through_ineligible": "straight_through_demo",
    "exception_based_sampled": "exception_based",
    "low_confidence_router": "human_governed",
    "invalid_tool_proposal": "human_governed",
    "prompt_injection_evidence": "human_governed",
    "selective_replanning": "human_governed",
    "action_budget_exhaustion": "human_governed",
}

ACTION_TO_TOOL: dict[ActionType, ToolIdentifier | None] = {
    ActionType.EXTRACT_SUBMITTED_EVIDENCE: ToolIdentifier.EVIDENCE_EXTRACTOR,
    ActionType.CHECK_QUESTIONNAIRE_EVIDENCE_CONSISTENCY: (
        ToolIdentifier.EVIDENCE_CONSISTENCY_CHECKER
    ),
    ActionType.CHECK_RAG_EVIDENCE: ToolIdentifier.RAG_EVIDENCE_CHECKER,
    ActionType.CHECK_AGENTIC_AI_AUTONOMY: ToolIdentifier.AGENTIC_AUTONOMY_CHECKER,
    ActionType.CHECK_SUPPLIER_EVIDENCE: ToolIdentifier.SUPPLIER_EVIDENCE_CHECKER,
    ActionType.VERIFY_CITATIONS: ToolIdentifier.CITATION_VERIFIER,
    ActionType.ESCALATE_TO_AIRO: None,
}

ACTION_INPUTS: dict[ActionType, list[str]] = {
    action: (
        ["questionnaire", "evidence_text"]
        if action
        in {
            ActionType.EXTRACT_SUBMITTED_EVIDENCE,
            ActionType.CHECK_QUESTIONNAIRE_EVIDENCE_CONSISTENCY,
        }
        else ["state"]
    )
    for action in ActionType
}
ACTION_INPUTS[ActionType.ESCALATE_TO_AIRO] = []


@dataclass(frozen=True)
class PolicyAssessment:
    permitted_actions: tuple[ActionType, ...]
    permitted_tools: tuple[ToolIdentifier, ...]
    mandatory_checks: tuple[str, ...]
    router_permitted: bool
    max_tool_calls: int
    max_evidence_cycles: int
    minimum_confidence: float
    fail_closed: bool
    rationale: str
    policy_version: str = DEMO_POLICY_VERSION


class PolicySupervisor:
    """Deterministic authority boundary for the single Coordinator.

    The supervisor decides permissions and budgets. It never asks the LLM to
    decide autonomy, risk outcomes, gate requirements, or external authority.
    """

    policy_version = DEMO_POLICY_VERSION
    max_tool_calls = 8
    max_evidence_cycles = 3
    minimum_confidence = 0.70

    def __init__(self, gate_policy: AutonomyPolicyEngine | None = None):
        self.gate_policy = gate_policy or AutonomyPolicyEngine()

    def assign_autonomy(
        self, questionnaire: dict[str, Any], governed_pattern_id: str | None = None
    ) -> AutonomyAssignment:
        maximum: AutonomyProfile = (
            DEMO_PATTERN_MAXIMUMS.get(governed_pattern_id, "human_governed")
            if governed_pattern_id
            else "human_governed"
        )
        eligible = governed_pattern_id in DEMO_PATTERN_MAXIMUMS if governed_pattern_id else False
        effective = maximum
        reasons = [
            f"Maximum profile assigned by {self.policy_version}",
            "Normal unmatched cases default to human_governed"
            if not governed_pattern_id
            else f"Governed illustrative fixture: {governed_pattern_id}",
        ]

        elevated = bool(
            questionnaire.get("sensitive_data")
            or questionnaire.get("customer_decisioning")
            or questionnaire.get("autonomous_actions")
            or questionnaire.get("critical_process_dependency")
        )
        if elevated and PROFILE_RANK[effective] > PROFILE_RANK["human_governed"]:
            effective = "human_governed"
            reasons.append("Elevated declared risk downgraded the effective profile")

        return AutonomyAssignment(
            effective_profile=effective,
            approved_maximum_profile=maximum,
            rationale="; ".join(reasons),
            policy_version=self.policy_version,
            governed_pattern_id=governed_pattern_id,
            eligible=eligible,
            downgraded=effective != maximum,
        )

    def effective_autonomy_profile(self, state: dict[str, Any]) -> AutonomyAssignment:
        raw = state.get("autonomy_assignment") or {}
        try:
            assignment = AutonomyAssignment.model_validate(raw)
        except (ValidationError, TypeError):
            return self.assign_autonomy(state.get("questionnaire", {}))

        if (
            state.get("missing_information") or state.get("inconsistencies")
        ) and assignment.effective_profile != "human_governed":
            return assignment.model_copy(
                update={
                    "effective_profile": "human_governed",
                    "rationale": assignment.rationale
                    + "; unresolved evidence issue requires human governance",
                    "downgraded": True,
                }
            )
        return assignment

    @staticmethod
    def _planned_actions(state: dict[str, Any]) -> list[ActionType]:
        pending = []
        for item in state.get("action_plan", []):
            if item.get("status") == "pending":
                try:
                    pending.append(ActionType(item["action"]))
                except (KeyError, ValueError):
                    return [ActionType.ESCALATE_TO_AIRO]
        completed = {ActionType(item) for item in state.get("completed_actions", [])}
        foundations = {
            ActionType.EXTRACT_SUBMITTED_EVIDENCE,
            ActionType.CHECK_QUESTIONNAIRE_EVIDENCE_CONSISTENCY,
        }
        foundation_pending = [item for item in pending if item in foundations]
        if foundation_pending:
            return foundation_pending
        if ActionType.EXTRACT_SUBMITTED_EVIDENCE not in completed:
            return [ActionType.ESCALATE_TO_AIRO]
        return pending

    def allowed_actions(self, state: dict[str, Any]) -> list[ActionType]:
        if state.get("tool_call_count", 0) >= state.get("max_tool_calls", self.max_tool_calls):
            return [ActionType.ESCALATE_TO_AIRO]
        if state.get("evidence_cycle", 0) > state.get(
            "max_evidence_cycles", self.max_evidence_cycles
        ):
            return [ActionType.ESCALATE_TO_AIRO]
        pending = self._planned_actions(state)
        return pending or []

    def allowed_tools(self, state: dict[str, Any]) -> list[ToolIdentifier]:
        return [
            tool
            for action in self.allowed_actions(state)
            if (tool := ACTION_TO_TOOL.get(action)) is not None
        ]

    def assess_state(self, state: dict[str, Any]) -> PolicyAssessment:
        actions = self.allowed_actions(state)
        try:
            objective = CaseObjective.model_validate(state.get("case_objective", {}))
            objective_valid = (
                objective.statement == CASE_OBJECTIVE_STATEMENT
                and objective.completion_criteria == CASE_COMPLETION_CRITERIA
            )
        except (ValidationError, TypeError):
            objective_valid = False
        unknown_status = state.get("status") not in {
            "INGESTING",
            "EVIDENCE_REVIEW",
            "AWAITING_INFORMATION",
            "DRAFT",
        }
        fail_closed = (
            unknown_status or not objective_valid or actions == [ActionType.ESCALATE_TO_AIRO]
        )
        assessed_actions = [ActionType.ESCALATE_TO_AIRO] if fail_closed else actions
        return PolicyAssessment(
            permitted_actions=tuple(assessed_actions),
            permitted_tools=() if fail_closed else tuple(self.allowed_tools(state)),
            mandatory_checks=("schema", "identity_version", "citations", "authority"),
            router_permitted=len(actions) > 1 and not fail_closed,
            max_tool_calls=self.max_tool_calls,
            max_evidence_cycles=self.max_evidence_cycles,
            minimum_confidence=self.minimum_confidence,
            fail_closed=fail_closed,
            rationale=(
                "Unknown state or exhausted budget fails closed to AIRO review."
                if fail_closed
                else "Actions are limited to pending evidence-preparation objectives."
            ),
        )

    def validate_action_proposal(
        self, proposal: ActionProposal, state: dict[str, Any]
    ) -> tuple[bool, str]:
        allowed_actions = self.allowed_actions(state)
        allowed_tools = self.allowed_tools(state)
        if proposal.selected_action not in allowed_actions:
            return False, "Action is not permitted in the current case state."
        expected_tool = ACTION_TO_TOOL.get(proposal.selected_action)
        if expected_tool != proposal.selected_tool:
            return False, "The proposed tool does not match the approved action contract."
        if proposal.selected_tool and proposal.selected_tool not in allowed_tools:
            return False, "Tool is not allowlisted for the current case state."
        if proposal.confidence < self.minimum_confidence:
            return False, "Proposal confidence is below the deterministic policy threshold."
        return True, "Proposal satisfies deterministic action policy."

    def gate_requirement(self, gate_id: str, state: dict[str, Any]) -> GateEvaluation:
        safe_state = dict(state)
        assignment = self.effective_autonomy_profile(state)
        safe_state["autonomy_profile"] = assignment.effective_profile
        return self.gate_policy.evaluate(gate_id, safe_state)
