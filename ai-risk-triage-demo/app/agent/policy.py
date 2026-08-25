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
    GovernanceLoop,
    LifecycleStatus,
    SupervisorDecision,
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
    "multiple_evidence_actions": "human_governed",
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
    "malformed_tool_result": "human_governed",
    "prompt_injection_evidence": "human_governed",
    "selective_replanning": "human_governed",
    "action_budget_exhaustion": "human_governed",
    "missing_supplier_evidence": "human_governed",
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
    ActionType.RUN_MATERIALITY_ENGINE: ToolIdentifier.MATERIALITY_ENGINE,
    ActionType.RUN_2LOD_ENGINE: ToolIdentifier.LOD2_TRIGGER_ENGINE,
    ActionType.CHALLENGE_ASSESSMENT: ToolIdentifier.CHALLENGE_ASSESSOR,
    ActionType.GENERATE_REVIEW_PACK: ToolIdentifier.REVIEW_PACK_GENERATOR,
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

DIRECT_CAPABILITY_ACTIONS = {
    ActionType.RUN_MATERIALITY_ENGINE,
    ActionType.RUN_2LOD_ENGINE,
    ActionType.CHALLENGE_ASSESSMENT,
    ActionType.GENERATE_REVIEW_PACK,
}


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
    # Covers evidence preparation and all later governed capabilities. Individual
    # demonstration fixtures can deliberately lower this to exercise exhaustion.
    max_tool_calls = 16
    max_evidence_cycles = 3
    max_retries = 3
    max_total_loops = 24
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

    @staticmethod
    def _capability_prerequisite(
        state: dict[str, Any], action: ActionType
    ) -> tuple[bool, str | None]:
        if action in {
            ActionType.RUN_MATERIALITY_ENGINE,
            ActionType.RUN_2LOD_ENGINE,
        } and not state.get("readiness_result", {}).get("ready_for_engines"):
            return False, "Deterministic engine readiness has not been established."
        if action == ActionType.CHALLENGE_ASSESSMENT and not state.get("proposed_outcome"):
            return False, "The combined deterministic risk proposal is not available."
        if action == ActionType.GENERATE_REVIEW_PACK and not state.get("proposed_outcome"):
            return False, "The combined deterministic risk proposal is not available."
        return True, None

    def supervise_capability(
        self, state: dict[str, Any], action: ActionType
    ) -> SupervisorDecision:
        """Apply the whole-Case policy envelope to a fixed workflow capability.

        Workflow routing may identify a deterministic next capability, but it does
        not grant execution authority. This method produces the same typed
        SupervisorDecision used by the bounded evidence selector immediately before
        every non-router capability invocation.
        """

        if action not in DIRECT_CAPABILITY_ACTIONS:
            raise ValueError(f"'{action.value}' is not a direct governed capability.")
        base = self.supervise(state)
        prerequisite_ok, prerequisite_reason = self._capability_prerequisite(state, action)
        budget_ok = base.remaining_tool_calls > 0 and base.remaining_total_loops > 0
        version_ok = (
            state.get("policy_version") == self.policy_version
            and state.get("rule_version") is not None
        )
        paused = bool(base.human_decision_required or base.external_event_required)
        permitted = bool(
            not base.control_exception
            and prerequisite_ok
            and budget_ok
            and version_ok
            and not paused
        )
        tool = ACTION_TO_TOOL[action]
        reason = None
        if base.control_exception:
            reason = base.control_exception_reason or base.rationale
        elif not prerequisite_ok:
            reason = prerequisite_reason
        elif not budget_ok:
            reason = "A governed execution budget is exhausted."
        elif not version_ok:
            reason = "Policy or rule version is not current."
        elif paused:
            reason = "Human authority or an external event is pending."
        return base.model_copy(
            update={
                "allowed_actions": [action] if permitted else [],
                "allowed_tools": [tool] if permitted and tool else [],
                "mandatory_action": action if permitted else None,
                "llm_recommender_permitted": False,
                "control_exception": not permitted,
                "control_exception_reason": reason,
                "rationale": (
                    "The deterministic policy authorised the next fixed workflow capability."
                    if permitted
                    else reason or "The capability is not permitted."
                ),
            }
        )

    def supervise(self, state: dict[str, Any]) -> SupervisorDecision:
        """Evaluate the full current Case State without calling an LLM."""

        assignment = self.effective_autonomy_profile(state)
        actions = self.allowed_actions(state)
        tools = self.allowed_tools(state)
        has_pending_executable = any(
            ACTION_TO_TOOL.get(action) for action in self._planned_actions(state)
        )
        remaining_tool_calls = max(
            0,
            int(state.get("max_tool_calls", self.max_tool_calls))
            - int(state.get("tool_call_count", 0)),
        )
        remaining_evidence_cycles = max(
            0,
            int(state.get("max_evidence_cycles", self.max_evidence_cycles))
            - int(state.get("evidence_cycle", 0)),
        )
        remaining_retries = max(
            0,
            self.max_retries - sum(int(value) for value in state.get("retry_counts", {}).values()),
        )
        remaining_total_loops = max(
            0,
            int(state.get("max_total_loops", self.max_total_loops))
            - int(state.get("total_loop_count", 0)),
        )

        lifecycle = state.get("lifecycle_status")
        known_lifecycle = (
            lifecycle in {item.value for item in LifecycleStatus}
            if lifecycle is not None
            else state.get("status")
            in {"DRAFT", "INGESTING", "EVIDENCE_REVIEW", "AWAITING_INFORMATION"}
        )
        existing_exception = state.get("control_exception") or {}
        budget_exception = bool(
            (not remaining_tool_calls and has_pending_executable)
            or not remaining_total_loops
            or int(state.get("evidence_cycle", 0))
            > int(state.get("max_evidence_cycles", self.max_evidence_cycles))
        )
        objective_valid = True
        try:
            objective = CaseObjective.model_validate(state.get("case_objective", {}))
            objective_valid = (
                objective.statement == CASE_OBJECTIVE_STATEMENT
                and objective.completion_criteria == CASE_COMPLETION_CRITERIA
            )
        except (ValidationError, TypeError):
            objective_valid = False

        escalation_only = actions == [ActionType.ESCALATE_TO_AIRO]
        control_exception = bool(
            existing_exception.get("status") == "OPEN"
            or not known_lifecycle
            or not objective_valid
            or budget_exception
            or escalation_only
        )
        if control_exception:
            actions = []
            tools = []

        active_loop = None
        raw_loop = state.get("active_governance_loop")
        if raw_loop:
            try:
                active_loop = GovernanceLoop(raw_loop)
            except ValueError:
                control_exception = True

        active_event = state.get("active_external_event") or {}
        external_required = active_event.get("status") == "WAITING"
        human_required = bool(
            active_loop
            or state.get("current_gate")
            or lifecycle == LifecycleStatus.AWAITING_HUMAN.value
        )
        if human_required or external_required:
            # No router/tool action is executable while the Coordinator is paused
            # for a protected human decision or a correlated external event.
            actions = []
            tools = []
        ready_for_engines = bool(state.get("readiness_result", {}).get("ready_for_engines"))
        completion_candidate = bool(
            state.get("final_outcome")
            and state.get("review_pack")
            and not state.get("open_objectives")
            and not state.get("pending_actions")
        )
        reason = None
        if not known_lifecycle:
            reason = "Unknown lifecycle state."
        elif not objective_valid:
            reason = "Case objective or completion criteria do not match the governed version."
        elif not remaining_total_loops:
            reason = "Total Coordinator loop budget is exhausted."
        elif not remaining_tool_calls and has_pending_executable:
            reason = "Tool-call budget is exhausted while executable objectives remain."
        elif int(state.get("evidence_cycle", 0)) > int(
            state.get("max_evidence_cycles", self.max_evidence_cycles)
        ):
            reason = "Evidence-loop budget is exhausted."
        elif escalation_only:
            reason = "No permitted executable action remains."
        elif existing_exception.get("status") == "OPEN":
            reason = str(existing_exception.get("reason", "A Control Exception is open."))

        deterministic_fallback = bool(state.get("deterministic_fallback_requested"))
        return SupervisorDecision(
            policy_version=self.policy_version,
            allowed_actions=actions,
            prohibited_actions=sorted(
                {
                    *state.get("prohibited_actions", []),
                    "approve_case",
                    "select_materiality",
                    "select_2lod",
                    "change_profile",
                    "bypass_gate",
                    "publish_external",
                }
            ),
            allowed_tools=tools,
            mandatory_action=(
                actions[0] if actions and (len(actions) == 1 or deterministic_fallback) else None
            ),
            llm_recommender_permitted=(
                len(actions) > 1 and not control_exception and not deterministic_fallback
            ),
            human_decision_required=human_required,
            active_governance_loop=active_loop,
            governance_reason=(
                "The active Governance Loop reserves this judgement to AIRO."
                if human_required
                else None
            ),
            external_event_required=external_required,
            expected_event_type=active_event.get("event_type") if external_required else None,
            ready_for_deterministic_engines=ready_for_engines,
            external_write_permitted=False,
            remaining_tool_calls=remaining_tool_calls,
            remaining_retries=remaining_retries,
            remaining_evidence_cycles=remaining_evidence_cycles,
            remaining_total_loops=remaining_total_loops,
            effective_automation_profile=assignment.effective_profile,
            completion_candidate=completion_candidate,
            control_exception=control_exception,
            control_exception_reason=reason,
            rationale=(
                reason
                or "The deterministic policy evaluated objectives, permissions, versions, "
                "budgets, Governance Loops, events and completion readiness."
            ),
        )

    def assess_state(self, state: dict[str, Any]) -> PolicyAssessment:
        """Compatibility view retained for existing callers during state migration."""

        decision = self.supervise(state)
        assessed_actions = (
            [ActionType.ESCALATE_TO_AIRO]
            if decision.control_exception
            else decision.allowed_actions
        )
        return PolicyAssessment(
            permitted_actions=tuple(assessed_actions),
            permitted_tools=tuple(decision.allowed_tools),
            mandatory_checks=("schema", "identity_version", "citations", "authority"),
            router_permitted=decision.llm_recommender_permitted,
            max_tool_calls=self.max_tool_calls,
            max_evidence_cycles=self.max_evidence_cycles,
            minimum_confidence=self.minimum_confidence,
            fail_closed=decision.control_exception,
            rationale=decision.rationale,
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
