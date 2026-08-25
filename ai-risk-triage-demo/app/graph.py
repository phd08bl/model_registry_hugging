from __future__ import annotations

import hashlib
import json
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, Literal

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from app.agent.authorizer import ActionAuthoriser
from app.agent.completion import CompletionPolicy
from app.agent.interrupts import AIROInterruptController
from app.agent.invalidation import invalidation_update
from app.agent.policy import ACTION_INPUTS, PolicySupervisor
from app.agent.readiness import ReadinessPolicy
from app.agent.router import BoundedActionRouter
from app.agent.tools import ToolRegistry
from app.agent.verifier import ResultVerifier
from app.engines.autonomy import GateEvaluation
from app.llm.base import LLMClient
from app.schemas import (
    ActionAuthorisation,
    ActionProposal,
    ActionType,
    AgentActionTrace,
    ControlException,
    DomainPhase,
    ExternalEventExpectation,
    ExternalEventSubmission,
    GovernanceLoop,
    HumanDecision,
    LifecycleStatus,
    OpenIssue,
    SupervisorDecision,
    ToolIdentifier,
    ToolInvocation,
    VerificationResult,
    VerificationStatus,
)
from app.services.evidence import (
    build_targeted_questions,
)
from app.state import TriageState
from app.versions import (
    EXTERNAL_EVENT_SCHEMA_VERSION,
    PROMPT_VERSION,
    QUESTIONNAIRE_VERSION,
    RULESET_VERSION,
    WORKFLOW_VERSION,
)


def now() -> str:
    return datetime.now(UTC).isoformat()


def _append_unique(values: list[str] | None, value: str) -> list[str]:
    result = list(values or [])
    if value not in result:
        result.append(value)
    return result


def _merge_unique(*groups: list[str] | None) -> list[str]:
    return sorted({item for group in groups for item in (group or []) if item})


def _transition_record(
    state: TriageState,
    node: str,
    decision: str,
    *,
    state_changes: list[str] | None = None,
) -> list[dict[str, Any]]:
    history = list(state.get("transition_history", []))
    history.append(
        {
            "transition_id": f"TRANS-{uuid.uuid4().hex[:12].upper()}",
            "occurred_at": now(),
            "node": node,
            "lifecycle_status": state.get("lifecycle_status"),
            "domain_phase": state.get("domain_phase"),
            "decision": decision,
            "state_changes": state_changes or [],
            "case_state_version": state.get("case_state_version", 1),
        }
    )
    return history


def _state_diff(
    state: TriageState, updates: dict[str, Any], *, include: list[str] | None = None
) -> dict[str, dict[str, Any]]:
    """Build a compact structured diff for the educational audit trace."""

    ignored = {"updated_at", "transition_history", "agent_action_trace"}
    keys = include or sorted(set(updates) - ignored)
    return {
        key: {"before": state.get(key), "after": updates.get(key)}
        for key in keys
        if key not in ignored and state.get(key) != updates.get(key)
    }


def _authoritative_state_fingerprint(state: TriageState) -> str:
    """Bind an invocation to the governed inputs that can affect its result."""

    governed = {
        "case_id": state.get("case_id"),
        "case_state_version": state.get("case_state_version", 1),
        "lifecycle_status": state.get("lifecycle_status"),
        "domain_phase": state.get("domain_phase"),
        "case_objective": state.get("case_objective"),
        "questionnaire": state.get("questionnaire"),
        "evidence_text": state.get("evidence_text"),
        "confirmed_facts": state.get("confirmed_facts"),
        "open_issues": state.get("open_issues"),
        "exceptions": state.get("exceptions"),
        "materiality_result": state.get("materiality_result"),
        "lod2_result": state.get("lod2_result"),
        "proposed_outcome": state.get("proposed_outcome"),
        "final_outcome": state.get("final_outcome"),
        "rule_version": state.get("rule_version"),
        "policy_version": state.get("policy_version"),
        "tool_contract_version": state.get("tool_contract_version"),
    }
    return hashlib.sha256(
        json.dumps(governed, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()


class TriageGraphFactory:
    def __init__(
        self,
        llm: LLMClient,
        supervisor: PolicySupervisor | None = None,
        router: BoundedActionRouter | None = None,
        registry: ToolRegistry | None = None,
        verifier: ResultVerifier | None = None,
    ):
        self.llm = llm
        self.supervisor = supervisor or PolicySupervisor()
        self.router = router or BoundedActionRouter(llm)
        self.registry = registry or ToolRegistry(llm)
        self.verifier = verifier or ResultVerifier()
        self.authoriser = ActionAuthoriser()
        self.readiness_policy = ReadinessPolicy()
        self.completion_policy = CompletionPolicy()
        self.interrupt_controller = AIROInterruptController()

    def _gate_payload(
        self,
        state: TriageState,
        evaluation: GateEvaluation,
        title: str,
        summary: str,
        allowed_actions: list[str],
        context: dict[str, Any],
        effects: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        payload = self.interrupt_controller.build_payload(
            state,
            evaluation,
            title=title,
            decision_required=summary,
            reason=evaluation.rationale,
            allowed_actions=allowed_actions,
            effects=effects
            or {action: f"Apply the governed '{action}' transition." for action in allowed_actions},
            context=context,
        )
        governance_loop = {
            "evidence_request": GovernanceLoop.EVIDENCE_RESOLUTION,
            "input_confirmation": GovernanceLoop.MATERIAL_FACT_CONFIRMATION,
            "exception_resolution": GovernanceLoop.EXCEPTION_INTERPRETATION,
            "final_triage": GovernanceLoop.FINAL_TRIAGE_DECISION,
            "publication": GovernanceLoop.PUBLICATION_APPROVAL,
            "control_exception_review": GovernanceLoop.CONTROL_EXCEPTION_REVIEW,
        }.get(evaluation.gate_id)
        payload.update(
            {
                "interrupt_kind": "human_governance",
                "governance_loop": governance_loop.value if governance_loop else None,
                "case_state_version": state.get("case_state_version", 1),
                "rule_version": state.get("rule_version"),
            }
        )
        return payload

    @staticmethod
    def _decision_update(state: TriageState, decision: HumanDecision) -> dict[str, Any]:
        decisions = list(state.get("human_decisions", []))
        decisions.append(decision.model_dump(mode="json"))
        return {
            "human_decisions": decisions,
            "processed_decision_ids": _append_unique(
                state.get("processed_decision_ids"), decision.decision_id
            ),
            "case_state_version": state.get("case_state_version", 1) + 1,
            "active_governance_loop": None,
            "updated_at": now(),
        }

    @staticmethod
    def _accept_current_evidence_issues(
        state: TriageState, decision: HumanDecision
    ) -> list[dict[str, Any]]:
        """Record that AIRO knowingly accepted a current gap; do not call it resolved."""

        current = {
            *state.get("missing_information", []),
            *state.get("inconsistencies", []),
        }
        issues = [dict(item) for item in state.get("open_issues", [])]
        for issue in issues:
            if (
                (issue.get("summary") in current or issue.get("category") == "verification")
                and issue.get("category")
                in {"mandatory_evidence_gap", "inconsistency", "verification"}
                and issue.get("status") == "open"
            ):
                issue["status"] = "accepted"
                issue["owner"] = decision.reviewer
        return issues

    @staticmethod
    def _confirmed_input_facts(state: TriageState, decision: HumanDecision) -> list[dict[str, Any]]:
        """Snapshot the facts AIRO confirmed at Gate 2 for later Gate payloads."""

        confirmed = [
            {
                "claim": (
                    "AIRO confirmed the structured questionnaire as the input to the "
                    "illustrative deterministic materiality and 2LoD engines."
                ),
                "source": f"questionnaire:{state.get('questionnaire_version', 'unknown')}",
                "line_refs": [],
                "confidence": 1.0,
                "questionnaire_snapshot": dict(state.get("questionnaire", {})),
                "confirmed_by": decision.reviewer,
                "confirmed_at": decision.decided_at,
            }
        ]
        confirmed.extend(
            {
                **dict(fact),
                "confirmed_by": decision.reviewer,
                "confirmed_at": decision.decided_at,
            }
            for fact in state.get("evidence_claims", [])
        )
        return confirmed

    @staticmethod
    def _route_after_confirmed_inputs(state: TriageState) -> str:
        """Reuse current deterministic engine results when their inputs did not change."""

        if state.get("materiality_result") and state.get("lod2_result"):
            return "challenge_assessment"
        return "run_engines"

    def _autonomy_update(self, state: TriageState, evaluation: GateEvaluation) -> list[dict]:
        values = list(state.get("autonomy_log", []))
        assignment = self.supervisor.effective_autonomy_profile(state)
        sampled = (
            self.supervisor.gate_policy._sample_selected(
                state.get("sampling_key") or state["case_id"]
            )
            if evaluation.gate_id == "final_triage"
            and assignment.effective_profile == "exception_based"
            else None
        )
        values.append(
            {
                **evaluation.to_dict(),
                "evaluated_at": now(),
                "effective_profile": assignment.effective_profile,
                "assignment_policy_version": assignment.policy_version,
                "eligibility_result": assignment.eligible,
                "assignment_rationale": assignment.rationale,
                "risk_conditions": {
                    "materiality_band": state.get("materiality_result", {}).get(
                        "proposed_materiality_band"
                    ),
                    "exceptions": bool(state.get("exceptions")),
                },
                "evidence_conditions": {
                    "gaps": bool(state.get("missing_information")),
                    "inconsistencies": bool(state.get("inconsistencies")),
                },
                "sampling_result": sampled,
            }
        )
        return values

    @staticmethod
    def _build_control_exception(
        state: TriageState,
        *,
        code: str,
        reason: str,
        failed_action: str | None = None,
        failed_tool: str | None = None,
        recoverable: bool = True,
    ) -> dict[str, Any]:
        return ControlException(
            exception_id=f"CTRL-{uuid.uuid4().hex[:12].upper()}",
            code=code,
            reason=reason,
            failed_action=failed_action,
            failed_tool=failed_tool,
            recoverable=recoverable,
            retry_count=sum(int(value) for value in state.get("retry_counts", {}).values()),
            budget_state={
                "remaining_tool_calls": int(state.get("remaining_tool_calls", 0)),
                "remaining_evidence_cycles": max(
                    0,
                    int(state.get("max_evidence_cycles", 0)) - int(state.get("evidence_cycle", 0)),
                ),
                "remaining_total_loops": int(state.get("remaining_total_loops", 0)),
            },
            allowed_recovery_actions=(
                ["retry", "deterministic_fallback", "wait_external", "cancel", "fail_safe"]
                if recoverable
                else ["cancel", "fail_safe"]
            ),
            timestamp=now(),
        ).model_dump(mode="json")

    def normalise_intake(self, state: TriageState) -> dict[str, Any]:
        questionnaire = dict(state.get("questionnaire", {}))
        if questionnaire.get("sensitive_data"):
            questionnaire["personal_data"] = True
        return {
            "questionnaire": questionnaire,
            "lifecycle_status": LifecycleStatus.OPEN.value,
            "domain_phase": DomainPhase.INTAKE.value,
            "status": "INGESTING",
            "evidence_cycle": state.get("evidence_cycle", 0),
            "questionnaire_version": state.get("questionnaire_version", QUESTIONNAIRE_VERSION),
            "rule_version": RULESET_VERSION,
            "workflow_version": WORKFLOW_VERSION,
            "prompt_version": PROMPT_VERSION,
            "completed_nodes": _append_unique(state.get("completed_nodes"), "normalise_intake"),
            "transition_history": _transition_record(
                state,
                "normalise_intake",
                "Validated and normalised the submitted questionnaire.",
                state_changes=["questionnaire", "lifecycle_status", "domain_phase"],
            ),
            "updated_at": now(),
        }

    def plan_evidence_actions(self, state: TriageState) -> dict[str, Any]:
        """Create a bounded evidence plan from facts, never from model-selected authority."""

        questionnaire = state.get("questionnaire", {})
        searchable = " ".join(
            [questionnaire.get("use_case_name", ""), questionnaire.get("purpose", "")]
        ).lower()
        if state.get("rework_actions"):
            actions = [ActionType(item) for item in state["rework_actions"]]
        else:
            actions = [
                ActionType.EXTRACT_SUBMITTED_EVIDENCE,
                ActionType.CHECK_QUESTIONNAIRE_EVIDENCE_CONSISTENCY,
            ]
            if "rag" in searchable or "retriev" in searchable or "policy" in searchable:
                actions.append(ActionType.CHECK_RAG_EVIDENCE)
            if questionnaire.get("external_model_or_supplier"):
                actions.append(ActionType.CHECK_SUPPLIER_EVIDENCE)
            if questionnaire.get("autonomous_actions"):
                actions.append(ActionType.CHECK_AGENTIC_AI_AUTONOMY)
            actions.append(ActionType.VERIFY_CITATIONS)
        action_values = {action.value for action in actions}
        return {
            "action_plan": [
                {
                    "action": action.value,
                    "status": "pending",
                    "reason": "Required by the illustrative deterministic evidence policy.",
                }
                for action in actions
            ],
            "pending_actions": [action.value for action in actions],
            "open_objectives": [
                {
                    "objective_id": f"EVIDENCE-{index + 1}",
                    "action": action.value,
                    "status": "OPEN",
                    "reason": "Required by deterministic illustrative evidence policy.",
                }
                for index, action in enumerate(actions)
            ],
            "completed_actions": [
                item for item in state.get("completed_actions", []) if item not in action_values
            ],
            "completed_objectives": state.get("completed_objectives", []),
            "failed_actions": [
                item for item in state.get("failed_actions", []) if item not in action_values
            ],
            "prohibited_actions": [
                item for item in state.get("prohibited_actions", []) if item not in action_values
            ],
            "tool_call_count": state.get("tool_call_count", 0),
            "remaining_tool_calls": max(
                0,
                state.get("max_tool_calls", self.supervisor.max_tool_calls)
                - state.get("tool_call_count", 0),
            ),
            "rework_actions": [],
            "lifecycle_status": LifecycleStatus.WORKING.value,
            "domain_phase": DomainPhase.EVIDENCE_REVIEW.value,
            "status": "EVIDENCE_REVIEW",
            "updated_at": now(),
        }

    @staticmethod
    def observe_case(state: TriageState) -> dict[str, Any]:
        pending = [
            item["action"]
            for item in state.get("action_plan", [])
            if item.get("status") == "pending"
        ]
        loop_count = state.get("total_loop_count", 0) + 1
        remaining_loops = max(0, state.get("max_total_loops", 24) - loop_count)
        return {
            "pending_actions": pending,
            "recommended_next_action": {
                "action": pending[0] if pending else "reassess_case",
                "reason": "Next unresolved governed evidence objective.",
            },
            "completed_nodes": _append_unique(state.get("completed_nodes"), "observe_case"),
            "total_loop_count": loop_count,
            "remaining_total_loops": remaining_loops,
            "transition_history": _transition_record(
                state,
                "observe_case",
                "Observed authoritative Case State and unresolved objectives.",
                state_changes=["pending_actions", "recommended_next_action"],
            ),
            "updated_at": now(),
        }

    def supervise_actions(self, state: TriageState) -> dict[str, Any]:
        assignment = self.supervisor.effective_autonomy_profile(state)
        decision = self.supervisor.supervise(state)
        return {
            "autonomy_profile": assignment.effective_profile,
            "autonomy_assignment": assignment.model_dump(),
            "policy_assessment": {
                "permitted_actions": [item.value for item in decision.allowed_actions],
                "permitted_tools": [item.value for item in decision.allowed_tools],
                "mandatory_checks": ["schema", "identity_version", "citations", "authority"],
                "router_permitted": decision.llm_recommender_permitted,
                "max_tool_calls": self.supervisor.max_tool_calls,
                "max_evidence_cycles": self.supervisor.max_evidence_cycles,
                "minimum_confidence": self.supervisor.minimum_confidence,
                "fail_closed": decision.control_exception,
                "rationale": decision.rationale,
                "policy_version": decision.policy_version,
            },
            "supervisor_decision": decision.model_dump(mode="json"),
            "execution_budgets": {
                "maximum_tool_calls": state.get("max_tool_calls", self.supervisor.max_tool_calls),
                "remaining_tool_calls": decision.remaining_tool_calls,
                "maximum_retries": self.supervisor.max_retries,
                "remaining_retries": decision.remaining_retries,
                "maximum_evidence_cycles": state.get(
                    "max_evidence_cycles", self.supervisor.max_evidence_cycles
                ),
                "remaining_evidence_cycles": decision.remaining_evidence_cycles,
                "maximum_total_loops": state.get(
                    "max_total_loops", self.supervisor.max_total_loops
                ),
                "remaining_total_loops": decision.remaining_total_loops,
            },
            "updated_at": now(),
        }

    @staticmethod
    def route_after_supervision(
        state: TriageState,
    ) -> Literal[
        "select_required_action",
        "recommend_evidence_action",
        "enter_control_exception",
    ]:
        decision = SupervisorDecision.model_validate(state["supervisor_decision"])
        if decision.control_exception:
            return "enter_control_exception"
        if decision.mandatory_action is not None:
            return "select_required_action"
        if decision.llm_recommender_permitted:
            return "recommend_evidence_action"
        return "enter_control_exception"

    def select_required_action(self, state: TriageState) -> dict[str, Any]:
        decision = SupervisorDecision.model_validate(state["supervisor_decision"])
        actions = [decision.mandatory_action] if decision.mandatory_action else []
        proposal, router_invoked = self.router.recommend(state, actions, decision.allowed_tools)
        return {
            "current_action_proposal": proposal.model_dump(mode="json"),
            "router_invoked": router_invoked,
            "deterministic_fallback_requested": False,
            "transition_history": _transition_record(
                state,
                "select_required_action",
                "Selected the single mandatory action without calling an LLM.",
                state_changes=["current_action_proposal"],
            ),
            "updated_at": now(),
        }

    def recommend_evidence_action(self, state: TriageState) -> dict[str, Any]:
        actions = [ActionType(item) for item in state["policy_assessment"]["permitted_actions"]]
        tools = [ToolIdentifier(item) for item in state["policy_assessment"]["permitted_tools"]]
        proposal, router_invoked = self.router.recommend(state, actions, tools)
        return {
            "current_action_proposal": proposal.model_dump(mode="json"),
            "router_invoked": router_invoked,
            "transition_history": _transition_record(
                state,
                "recommend_evidence_action",
                "Requested one bounded recommendation from the allowlisted evidence actions.",
                state_changes=["current_action_proposal"],
            ),
            "updated_at": now(),
        }

    def authorise_action(self, state: TriageState) -> dict[str, Any]:
        proposal = ActionProposal.model_validate(state["current_action_proposal"])
        decision = SupervisorDecision.model_validate(state["supervisor_decision"])
        contract = None
        if proposal.selected_tool:
            try:
                contract = self.registry.get(proposal.selected_tool)
            except ValueError:
                contract = None
        authorisation = self.authoriser.authorise(proposal, state, decision, contract)
        valid = authorisation.decision == "AUTHORISED"
        rationale = authorisation.reason
        prohibited = list(state.get("prohibited_actions", []))
        if not valid:
            prohibited.append(proposal.selected_action.value)
        return {
            "action_validation": {"valid": valid, "rationale": rationale},
            "current_action_authorisation": authorisation.model_dump(mode="json"),
            "action_authorisations": [
                *state.get("action_authorisations", []),
                authorisation.model_dump(mode="json"),
            ],
            "prohibited_actions": prohibited,
            "transition_history": _transition_record(
                state,
                "authorise_action",
                authorisation.reason,
                state_changes=["current_action_authorisation", "action_authorisations"],
            ),
            "updated_at": now(),
        }

    @staticmethod
    def route_after_authorisation(
        state: TriageState,
    ) -> Literal["execute_tool", "record_rejected_action"]:
        proposal = state.get("current_action_proposal", {})
        valid = state.get("action_validation", {}).get("valid")
        executable = bool(valid and proposal.get("selected_tool"))
        return "execute_tool" if executable else "record_rejected_action"

    def record_rejected_action(self, state: TriageState) -> dict[str, Any]:
        """Preserve fail-closed proposals in the audit trace without invoking a tool."""

        proposal = ActionProposal.model_validate(state["current_action_proposal"])
        valid = bool(state.get("action_validation", {}).get("valid"))
        rationale = state.get("current_action_authorisation", {}).get(
            "rationale", "Policy escalation requires AIRO review."
        )
        if rationale == "Policy escalation requires AIRO review.":
            rationale = state.get("current_action_authorisation", {}).get(
                "reason", state.get("action_validation", {}).get("rationale", rationale)
            )
        disposition = "escalate" if valid else "rejected"
        verification = VerificationResult(
            verified=False,
            disposition=disposition,
            checks={"policy_authorised": valid, "tool_not_invoked": True},
            limitations=["No tool result exists because policy stopped execution."],
            issues=[rationale],
            label="Unverified or rejected result—AIRO confirmation required.",
        )
        trace = list(state.get("agent_action_trace", []))
        contract = self.registry.get(proposal.selected_tool) if proposal.selected_tool else None
        trace.append(
            AgentActionTrace(
                trace_id=f"TRACE-{uuid.uuid4().hex[:12].upper()}",
                occurred_at=now(),
                proposal=proposal,
                verification=verification,
                authorisation=state.get("current_action_authorisation") or None,
                observed_state={
                    "lifecycle_status": state.get("lifecycle_status"),
                    "domain_phase": state.get("domain_phase"),
                    "open_objectives": state.get("open_objectives", []),
                },
                supervisor_decision=state.get("supervisor_decision", {}),
                policy_version=self.supervisor.policy_version,
                autonomy_profile=state["autonomy_profile"],
                remaining_tool_calls=state.get("remaining_tool_calls", 0),
                rationale=rationale,
                selection_source=(
                    "llm_router" if state.get("router_invoked") else "deterministic_policy"
                ),
                state_changes=["failed_actions", "control_exception"],
                transition_decision="CONTROL_EXCEPTION",
                stategraph_node="record_rejected_action",
                tool_contract=contract,
                state_diff={
                    "lifecycle_status": {
                        "before": state.get("lifecycle_status"),
                        "after": LifecycleStatus.CONTROL_EXCEPTION.value,
                    },
                    "active_governance_loop": {
                        "before": state.get("active_governance_loop"),
                        "after": GovernanceLoop.CONTROL_EXCEPTION_REVIEW.value,
                    },
                },
                next_transition="control_exception_gate",
            ).model_dump(mode="json")
        )
        issue = OpenIssue(
            issue_id=f"ISS-{uuid.uuid4().hex[:10].upper()}",
            category="verification",
            summary=rationale,
            advisory=False,
        ).model_dump()
        failed = _append_unique(state.get("failed_actions"), proposal.selected_action.value)
        plan = [
            {
                **item,
                "status": "failed"
                if item.get("action") == proposal.selected_action.value
                else item.get("status"),
            }
            for item in state.get("action_plan", [])
        ]
        control_exception = self._build_control_exception(
            state,
            code=("UNAUTHORISED_ACTION_PROPOSAL" if not valid else "NO_EXECUTABLE_TOOL"),
            reason=rationale,
            failed_action=proposal.selected_action.value,
            failed_tool=proposal.selected_tool.value if proposal.selected_tool else None,
        )
        return {
            "latest_verification": verification.model_dump(mode="json"),
            "agent_action_trace": trace,
            # The rejected attempt is historical once its trace has been written.
            # Keeping it in a field named ``current`` makes paused Gate screens
            # incorrectly present it as work that is still executing.
            "current_action_proposal": {},
            "current_action_authorisation": {},
            "current_tool_invocation": {},
            "action_validation": {},
            "router_invoked": False,
            "failed_actions": failed,
            "action_plan": plan,
            "open_issues": [*state.get("open_issues", []), issue],
            "control_exception": control_exception,
            "control_exception_history": [
                *state.get("control_exception_history", []),
                control_exception,
            ],
            "lifecycle_status": LifecycleStatus.CONTROL_EXCEPTION.value,
            "active_governance_loop": GovernanceLoop.CONTROL_EXCEPTION_REVIEW.value,
            "updated_at": now(),
        }

    def enter_control_exception(self, state: TriageState) -> dict[str, Any]:
        decision = SupervisorDecision.model_validate(state.get("supervisor_decision", {}))
        reason = decision.control_exception_reason or "No safe permitted transition exists."
        code = "NO_PERMITTED_ACTION"
        if "tool-call budget" in reason.lower():
            code = "TOOL_BUDGET_EXHAUSTED"
        elif "evidence-loop budget" in reason.lower():
            code = "EVIDENCE_LOOP_BUDGET_EXHAUSTED"
        elif "total coordinator loop" in reason.lower():
            code = "TOTAL_LOOP_BUDGET_EXHAUSTED"
        elif "unknown lifecycle" in reason.lower():
            code = "UNKNOWN_STATE"
        exception = self._build_control_exception(state, code=code, reason=reason)
        return {
            "control_exception": exception,
            "control_exception_history": [
                *state.get("control_exception_history", []),
                exception,
            ],
            "lifecycle_status": LifecycleStatus.CONTROL_EXCEPTION.value,
            "active_governance_loop": GovernanceLoop.CONTROL_EXCEPTION_REVIEW.value,
            "transition_history": _transition_record(
                state,
                "enter_control_exception",
                reason,
                state_changes=["control_exception", "lifecycle_status"],
            ),
            "updated_at": now(),
        }

    def execute_tool(self, state: TriageState) -> dict[str, Any]:
        proposal = ActionProposal.model_validate(state["current_action_proposal"])
        if proposal.selected_action == ActionType.ESCALATE_TO_AIRO or not proposal.selected_tool:
            return {
                "failed_actions": _append_unique(
                    state.get("failed_actions"), proposal.selected_action.value
                ),
                "updated_at": now(),
            }
        contract = self.registry.get(proposal.selected_tool)
        if ACTION_INPUTS[proposal.selected_action] == ["questionnaire", "evidence_text"]:
            inputs = {
                "questionnaire": state.get("questionnaire", {}),
                "evidence_text": state.get("evidence_text", ""),
            }
        else:
            inputs = {"state": dict(state)}
        state_fingerprint = _authoritative_state_fingerprint(state)
        fingerprint = hashlib.sha256(
            (
                state["case_id"]
                + str(state.get("evidence_cycle", 0))
                + proposal.selected_action.value
                + str(state.get("questionnaire", {}))
                + state.get("evidence_text", "")
                + state_fingerprint
            ).encode("utf-8")
        ).hexdigest()
        invocation = ToolInvocation(
            invocation_id=f"CALL-{uuid.uuid4().hex[:12].upper()}",
            case_id=state["case_id"],
            action=proposal.selected_action,
            tool_id=proposal.selected_tool,
            tool_version=contract.version,
            case_state_version=state.get("case_state_version", 1),
            rule_version=state.get("rule_version", "unknown"),
            inputs=inputs,
            input_references=[
                f"questionnaire:{state.get('questionnaire_version')}",
                f"evidence-cycle:{state.get('evidence_cycle', 0)}",
            ],
            idempotency_key=fingerprint,
            state_fingerprint=state_fingerprint,
        )
        result = self.registry.invoke(invocation, state["autonomy_profile"])
        if (
            state.get("demo_controls", {}).get("tool_result_mode") == "malformed_output"
            and proposal.selected_action == ActionType.EXTRACT_SUBMITTED_EVIDENCE
        ):
            result = result.model_copy(
                update={
                    "output": {
                        "summary": "Protected demonstration of an unsupported tool payload.",
                        "facts": "not-a-list",
                    }
                }
            )
        retries = dict(state.get("retry_counts", {}))
        retries[proposal.selected_tool.value] = max(
            retries.get(proposal.selected_tool.value, 0), result.retry_count
        )
        timeouts = dict(state.get("timeouts", {}))
        timeouts[proposal.selected_tool.value] = contract.timeout_seconds
        return {
            "current_tool_invocation": invocation.model_dump(mode="json"),
            "latest_tool_result": result.model_dump(mode="json"),
            "tool_results": [
                *state.get("tool_results", []),
                result.model_dump(mode="json"),
            ],
            "tool_call_count": state.get("tool_call_count", 0) + 1,
            "retry_counts": retries,
            "timeouts": timeouts,
            "remaining_tool_calls": max(
                0,
                state.get("max_tool_calls", self.supervisor.max_tool_calls)
                - state.get("tool_call_count", 0)
                - 1,
            ),
            "transition_history": _transition_record(
                state,
                "execute_tool",
                f"Executed registered tool {proposal.selected_tool.value}.",
                state_changes=["latest_tool_result", "tool_results", "remaining_tool_calls"],
            ),
            "updated_at": now(),
        }

    def verify_tool_result(self, state: TriageState) -> dict[str, Any]:
        result = self.registry.get(ToolIdentifier(state["latest_tool_result"]["tool_id"]))
        from app.schemas import ToolResult

        tool_result = ToolResult.model_validate(state["latest_tool_result"])
        verification = self.verifier.verify(
            tool_result,
            result,
            state,
            state.get("policy_assessment", {}).get(
                "minimum_confidence", self.supervisor.minimum_confidence
            ),
        )
        retries = dict(state.get("retry_counts", {}))
        retry_key = result.tool_id.value
        if (
            not verification.checks.get("output_schema_valid", True)
            and retries.get(retry_key, 0) < result.max_retries
        ):
            retries[retry_key] = retries.get(retry_key, 0) + 1
            verification = verification.model_copy(
                update={
                    "disposition": "retry",
                    "status": VerificationStatus.EXECUTION_FAILED,
                    "issues": [
                        *verification.issues,
                        "Malformed output exhausted this attempt; applying the bounded retry budget.",
                    ],
                }
            )
        dumped = verification.model_dump(mode="json")
        return {
            "latest_verification": dumped,
            "verification_results": [*state.get("verification_results", []), dumped],
            "retry_counts": retries,
            "transition_history": _transition_record(
                state,
                "verify_tool_result",
                f"Result verification status: {dumped['status']}.",
                state_changes=["latest_verification", "verification_results"],
            ),
            "updated_at": now(),
        }

    @staticmethod
    def route_after_tool_verification(
        state: TriageState,
    ) -> Literal["execute_tool", "update_case_state"]:
        return (
            "execute_tool"
            if state.get("latest_verification", {}).get("disposition") == "retry"
            else "update_case_state"
        )

    def update_case_state(self, state: TriageState) -> dict[str, Any]:
        proposal = ActionProposal.model_validate(state["current_action_proposal"])
        result = state["latest_tool_result"]
        verification = state["latest_verification"]
        updates: dict[str, Any] = {}
        open_issues = list(state.get("open_issues", []))
        advisory = list(state.get("advisory_observations", []))

        for issue_text in verification.get("issues", []):
            if "prompt-injection" in issue_text.lower() and not any(
                item.get("category") == "security" and item.get("summary") == issue_text
                for item in open_issues
            ):
                open_issues.append(
                    OpenIssue(
                        issue_id=f"ISS-{uuid.uuid4().hex[:10].upper()}",
                        category="security",
                        summary=issue_text,
                        advisory=True,
                    ).model_dump()
                )

        if verification["disposition"] in {"accepted", "advisory"}:
            for issue in open_issues:
                if (
                    issue.get("category") == "verification"
                    and issue.get("status") == "open"
                    and issue.get("summary")
                    in {
                        "The proposed tool does not match the approved action contract.",
                        "Tool result failed verification and requires AIRO review.",
                    }
                ):
                    issue["status"] = "resolved"
            output = result.get("output", {})
            if proposal.selected_action == ActionType.EXTRACT_SUBMITTED_EVIDENCE:
                extraction = {
                    key: value
                    for key, value in output.items()
                    if key not in {"source_references", "confidence"}
                }
                updates["evidence_extraction"] = extraction
                updates["evidence_claims"] = extraction.get("facts", [])
                updates["candidate_facts"] = extraction.get("facts", [])
                updates["llm_runtime"] = self.llm.runtime_metadata()
            elif proposal.selected_action == ActionType.CHECK_QUESTIONNAIRE_EVIDENCE_CONSISTENCY:
                missing = output.get("mandatory_evidence_gaps", [])
                conflicts = output.get("inconsistencies", [])
                updates["missing_information"] = missing
                updates["inconsistencies"] = conflicts
                updates["evidence_conflicts"] = [
                    {"summary": item, "source": "questionnaire_evidence_consistency"}
                    for item in conflicts
                ]
                updates["mandatory_evidence_gaps"] = [
                    {"summary": item, "source": "illustrative deterministic evidence policy"}
                    for item in missing
                ]
                current_issues = {
                    "mandatory_evidence_gap": set(missing),
                    "inconsistency": set(conflicts),
                }
                for issue in open_issues:
                    category = issue.get("category")
                    if (
                        category in current_issues
                        and issue.get("status") == "open"
                        and issue.get("summary") not in current_issues[category]
                    ):
                        issue["status"] = "resolved"
                for category, values in (
                    ("mandatory_evidence_gap", missing),
                    ("inconsistency", conflicts),
                ):
                    for item in values:
                        if not any(
                            issue.get("category") == category
                            and issue.get("summary") == item
                            and issue.get("status") == "open"
                            for issue in open_issues
                        ):
                            open_issues.append(
                                OpenIssue(
                                    issue_id=f"ISS-{uuid.uuid4().hex[:10].upper()}",
                                    category=category,
                                    summary=item,
                                    advisory=False,
                                ).model_dump()
                            )
            elif proposal.selected_action == ActionType.VERIFY_CITATIONS:
                if not result.get("output", {}).get("valid", True):
                    open_issues.append(
                        OpenIssue(
                            issue_id=f"ISS-{uuid.uuid4().hex[:10].upper()}",
                            category="verification",
                            summary="One or more evidence citations do not exist.",
                        ).model_dump()
                    )
            else:
                advisory.extend(
                    {
                        "observation": item,
                        "source_tool": result.get("tool_id"),
                        "label": "Advisory observation—AIRO confirmation required.",
                    }
                    for item in result.get("output", {}).get("observations", [])
                )
                updates["llm_advisory_observations"] = advisory
        else:
            failure_summary = "Tool result failed verification and requires AIRO review."
            if not any(
                issue.get("category") == "verification"
                and issue.get("status") == "open"
                and issue.get("summary") == failure_summary
                for issue in open_issues
            ):
                open_issues.append(
                    OpenIssue(
                        issue_id=f"ISS-{uuid.uuid4().hex[:10].upper()}",
                        category="verification",
                        summary=failure_summary,
                    ).model_dump()
                )

        plan = []
        for item in state.get("action_plan", []):
            item = dict(item)
            if item.get("action") == proposal.selected_action.value:
                item["status"] = (
                    "completed"
                    if verification["disposition"] in {"accepted", "advisory"}
                    else "failed"
                )
            plan.append(item)
        completed = list(state.get("completed_actions", []))
        failed = list(state.get("failed_actions", []))
        if verification["disposition"] in {"accepted", "advisory"}:
            completed = _append_unique(completed, proposal.selected_action.value)
        else:
            failed = _append_unique(failed, proposal.selected_action.value)
        trace = list(state.get("agent_action_trace", []))
        contract = self.registry.get(proposal.selected_tool)
        trace.append(
            AgentActionTrace(
                trace_id=f"TRACE-{uuid.uuid4().hex[:12].upper()}",
                occurred_at=now(),
                proposal=proposal,
                invocation=ToolInvocation.model_validate(state.get("current_tool_invocation")),
                result=state.get("latest_tool_result"),
                verification=verification,
                authorisation=state.get("current_action_authorisation") or None,
                observed_state={
                    "lifecycle_status": state.get("lifecycle_status"),
                    "domain_phase": state.get("domain_phase"),
                    "open_objectives": state.get("open_objectives", []),
                },
                supervisor_decision=state.get("supervisor_decision", {}),
                policy_version=self.supervisor.policy_version,
                autonomy_profile=state["autonomy_profile"],
                remaining_tool_calls=state.get("remaining_tool_calls", 0),
                rationale=state.get("action_validation", {}).get("rationale", ""),
                selection_source=(
                    "fallback"
                    if "fallback" in proposal.reason.lower()
                    else "llm_router"
                    if state.get("router_invoked")
                    else "deterministic_policy"
                ),
                state_changes=sorted(updates),
                invalidated_outputs=list(state.get("stale_outputs", [])),
                transition_decision=(
                    "CONTINUE"
                    if verification["disposition"] in {"accepted", "advisory"}
                    else "CONTROL_EXCEPTION"
                ),
                stategraph_node="update_case_state",
                tool_contract=contract,
                state_diff=_state_diff(state, updates),
                next_transition="reassess_case",
            ).model_dump(mode="json")
        )
        open_objectives = []
        completed_objectives = list(state.get("completed_objectives", []))
        for objective in state.get("open_objectives", []):
            if objective.get("action") == proposal.selected_action.value:
                completed_objectives.append({**objective, "status": "COMPLETED"})
            else:
                open_objectives.append(objective)
        updates.update(
            {
                "action_plan": plan,
                "completed_actions": completed,
                "failed_actions": failed,
                "open_issues": open_issues,
                "advisory_observations": advisory,
                "agent_action_trace": trace,
                "open_objectives": open_objectives,
                "completed_objectives": completed_objectives,
                "transition_history": _transition_record(
                    state,
                    "update_case_state",
                    "Applied only verified or explicitly advisory tool output to governed state.",
                    state_changes=sorted(updates),
                ),
                "stale_outputs": [
                    item for item in state.get("stale_outputs", []) if item not in set(updates)
                ],
                # The connected trace above is the authoritative history for this
                # completed cycle. These fields describe only in-flight work.
                "current_action_proposal": {},
                "current_action_authorisation": {},
                "current_tool_invocation": {},
                "action_validation": {},
                "router_invoked": False,
                "updated_at": now(),
            }
        )
        return updates

    def reassess_case(self, state: TriageState) -> dict[str, Any]:
        remaining = [
            item for item in state.get("action_plan", []) if item.get("status") == "pending"
        ]
        failed = bool(state.get("failed_actions") or state.get("prohibited_actions"))
        assignment = self.supervisor.effective_autonomy_profile(state)
        return {
            "autonomy_profile": assignment.effective_profile,
            "autonomy_assignment": assignment.model_dump(),
            "reassessment": {
                "continue": bool(remaining) and not failed,
                "fail_closed": failed,
                "remaining_objectives": [item["action"] for item in remaining],
            },
            "pending_actions": [item["action"] for item in remaining],
            "transition_history": _transition_record(
                state,
                "reassess_case",
                (
                    "Continue bounded work."
                    if remaining and not failed
                    else "Stop for a governed transition."
                ),
                state_changes=["reassessment"],
            ),
            "updated_at": now(),
        }

    @staticmethod
    def route_after_reassessment(
        state: TriageState,
    ) -> Literal[
        "observe_case",
        "draft_evidence_request",
        "prepare_external_event_wait",
        "enter_control_exception",
        "input_gate",
    ]:
        if state.get("reassessment", {}).get("continue"):
            return "observe_case"
        if state.get("reassessment", {}).get("fail_closed"):
            return "enter_control_exception"
        supplier_gap = any(
            "supplier" in str(item).lower() for item in state.get("missing_information", [])
        ) and state.get("questionnaire", {}).get("external_model_or_supplier")
        if supplier_gap:
            return "prepare_external_event_wait"
        if state.get("missing_information") or state.get("inconsistencies"):
            return "draft_evidence_request"
        return "input_gate"

    def draft_evidence_request(self, state: TriageState) -> dict[str, Any]:
        questions = build_targeted_questions(
            state.get("missing_information", []), state.get("inconsistencies", [])
        )
        if state.get("reassessment", {}).get("fail_closed") and not questions:
            questions.append(
                "AIRO review is required because an action or result failed policy validation."
            )
        return {
            "evidence_request": questions,
            "lifecycle_status": LifecycleStatus.AWAITING_HUMAN.value,
            "domain_phase": DomainPhase.EVIDENCE_REVIEW.value,
            "active_governance_loop": GovernanceLoop.EVIDENCE_RESOLUTION.value,
            "status": "AWAITING_INFORMATION",
            "completed_nodes": _append_unique(
                state.get("completed_nodes"), "draft_evidence_request"
            ),
            "updated_at": now(),
        }

    def prepare_external_event_wait(self, state: TriageState) -> dict[str, Any]:
        existing = state.get("active_external_event")
        if existing and existing.get("status") == "WAITING":
            expectation = existing
        else:
            expectation = ExternalEventExpectation(
                event_type="stakeholder_evidence_received",
                case_id=state["case_id"],
                correlation_id=f"CORR-{uuid.uuid4().hex[:12].upper()}",
                expected_source="business_owner",
                schema_version=EXTERNAL_EVENT_SCHEMA_VERSION,
                due_at=(datetime.now(UTC) + timedelta(days=7)).isoformat(),
                timeout_action="escalate_to_control_exception",
                case_state_version=state.get("case_state_version", 1),
            ).model_dump(mode="json")
        questions = build_targeted_questions(
            state.get("missing_information", []), state.get("inconsistencies", [])
        )
        if not questions:
            questions = [
                "Provide the required supplier contract, due-diligence and foundation-model assurance evidence."
            ]
        return {
            "evidence_request": questions,
            "active_external_event": expectation,
            "expected_external_events": [
                *[
                    item
                    for item in state.get("expected_external_events", [])
                    if item.get("correlation_id") != expectation["correlation_id"]
                ],
                expectation,
            ],
            "lifecycle_status": LifecycleStatus.AWAITING_EXTERNAL_EVENT.value,
            "domain_phase": DomainPhase.EVIDENCE_REVIEW.value,
            "active_governance_loop": None,
            "status": "AWAITING_EXTERNAL_EVENT",
            "transition_history": _transition_record(
                state,
                "prepare_external_event_wait",
                "Created a targeted evidence request and durable wait for stakeholder evidence.",
                state_changes=["evidence_request", "active_external_event", "lifecycle_status"],
            ),
            "updated_at": now(),
        }

    def external_event_wait(self, state: TriageState) -> Command:
        expectation = ExternalEventExpectation.model_validate(state["active_external_event"])
        payload = {
            "interrupt_kind": "external_event",
            "title": "External event wait â€” stakeholder evidence",
            "case_id": state["case_id"],
            "event_contract": expectation.model_dump(mode="json"),
            "decision_required": (
                "Submit the expected stakeholder evidence event or a governed timeout event."
            ),
            "allowed_event_types": [
                expectation.event_type,
                "external_response_received",
                "timeout",
            ],
            "governance_message": (
                "The Coordinator is durably paused. No risk engine or publication action runs "
                "until a valid correlated event is received."
            ),
        }
        event = ExternalEventSubmission.model_validate(interrupt(payload))
        processed = [*state.get("processed_external_events", []), event.model_dump(mode="json")]
        if event.event_type == "timeout":
            exception = self._build_control_exception(
                state,
                code="EXTERNAL_EVENT_TIMEOUT",
                reason="The expected stakeholder evidence event reached its demo timeout.",
            )
            return Command(
                update={
                    "processed_external_events": processed,
                    "active_external_event": {
                        **expectation.model_dump(mode="json"),
                        "status": "TIMED_OUT",
                    },
                    "control_exception": exception,
                    "control_exception_history": [
                        *state.get("control_exception_history", []),
                        exception,
                    ],
                    "lifecycle_status": LifecycleStatus.CONTROL_EXCEPTION.value,
                    "active_governance_loop": GovernanceLoop.CONTROL_EXCEPTION_REVIEW.value,
                    "case_state_version": state.get("case_state_version", 1) + 1,
                    "updated_at": now(),
                },
                goto="control_exception_gate",
            )

        updates = invalidation_update(
            state,
            evidence_changed=True,
            trigger_reason=f"Validated external event {event.event_id}",
        )
        updates.update(
            {
                "evidence_text": (
                    f"{state.get('evidence_text', '').rstrip()}\n{event.artifact_text.strip()}"
                ).strip(),
                "evidence_cycle": state.get("evidence_cycle", 0) + 1,
                "processed_external_events": processed,
                "active_external_event": None,
                "lifecycle_status": LifecycleStatus.WORKING.value,
                "domain_phase": DomainPhase.EVIDENCE_REVIEW.value,
                "status": "EVIDENCE_REVIEW",
                "case_state_version": state.get("case_state_version", 1) + 1,
                "transition_history": _transition_record(
                    state,
                    "external_event_wait",
                    "Validated the correlated stakeholder event and resumed selective evidence work.",
                    state_changes=["evidence_text", "evidence_cycle", "active_external_event"],
                ),
                "updated_at": now(),
            }
        )
        return Command(update=updates, goto="plan_evidence_actions")

    def evidence_gate(self, state: TriageState) -> Command:
        evaluation = self.supervisor.gate_requirement("evidence_request", state)
        verification_failure = state.get("latest_verification", {}).get("disposition") in {
            "escalate",
            "rejected",
        }
        payload = self._gate_payload(
            state,
            evaluation,
            "AIRO Gate 1 — Evidence request",
            (
                "A governed action or tool result failed verification. Review the recorded "
                "failure and decide whether to retry with evidence or proceed with the gap."
                if verification_failure
                else "Evidence is missing or inconsistent. Obtain information through normal "
                "channels, then resume this case."
            ),
            ["add_evidence", "proceed_with_gap", "cancel_case"],
            {
                "missing_information": state.get("missing_information", []),
                "inconsistencies": state.get("inconsistencies", []),
                "draft_questions": state.get("evidence_request", []),
            },
            effects={
                "add_evidence": (
                    "Add evidence and/or correct questionnaire facts, invalidate affected "
                    "outputs and rerun the bounded evidence checks."
                ),
                "proceed_with_gap": (
                    "Record the unresolved issue as knowingly accepted by AIRO and continue "
                    "to input confirmation; it remains a risk condition, not a resolution."
                ),
                "cancel_case": "Close the case without a risk approval.",
            },
        )
        decision = HumanDecision.model_validate(interrupt(payload))
        updates = self._decision_update(state, decision)
        updates["autonomy_log"] = self._autonomy_update(state, evaluation)

        if decision.action == "add_evidence":
            questionnaire = {**state["questionnaire"], **decision.answer_updates}
            if questionnaire.get("sensitive_data"):
                questionnaire["personal_data"] = True
            updates.update(
                invalidation_update(
                    state,
                    answer_updates=decision.answer_updates,
                    evidence_changed=bool(decision.additional_evidence.strip()),
                )
            )
            updates.update(
                {
                    "questionnaire": questionnaire,
                    "evidence_text": (
                        state.get("evidence_text", "").rstrip()
                        + "\n\nADDITIONAL EVIDENCE:\n"
                        + decision.additional_evidence.strip()
                    ).strip(),
                    "evidence_cycle": state.get("evidence_cycle", 0) + 1,
                    "status": "EVIDENCE_REVIEW",
                }
            )
            return Command(update=updates, goto="plan_evidence_actions")

        if decision.action == "proceed_with_gap":
            accepted_control_gaps = [
                issue.get("summary")
                for issue in state.get("open_issues", [])
                if issue.get("status") == "open" and issue.get("category") == "verification"
            ]
            updates.update(
                {
                    "exceptions": _merge_unique(
                        state.get("exceptions", []),
                        [
                            *state.get("missing_information", []),
                            *state.get("inconsistencies", []),
                            *accepted_control_gaps,
                        ],
                    ),
                    "open_issues": self._accept_current_evidence_issues(state, decision),
                    "status": "AWAITING_INPUT_CONFIRMATION",
                    "completed_nodes": _append_unique(
                        state.get("completed_nodes"), "evidence_gate"
                    ),
                }
            )
            return Command(update=updates, goto="input_gate")

        return Command(update=updates, goto="cancel_case")

    def control_exception_gate(self, state: TriageState) -> Command:
        exception = ControlException.model_validate(state["control_exception"])
        evaluation = GateEvaluation(
            gate_id="control_exception_review",
            required=True,
            mode="MANDATORY_REVIEW",
            rationale="A safe automated continuation is unavailable.",
        )
        allowed_actions = list(exception.allowed_recovery_actions)
        if exception.budget_state.get("remaining_tool_calls", 0) <= 0:
            allowed_actions = [
                action
                for action in allowed_actions
                if action not in {"retry", "deterministic_fallback"}
            ]
        recovery_effects = {
            "retry": "Retry the failed governed objective within remaining budgets.",
            "deterministic_fallback": (
                "Use the first supervisor-prioritised action without an LLM recommendation."
            ),
            "wait_external": "Pause for external remediation evidence.",
            "cancel": "Cancel the Case without a risk decision.",
            "fail_safe": "Close workflow execution as failed safe; this is not a risk rejection.",
        }
        payload = self._gate_payload(
            state,
            evaluation,
            "AIRO Governance Loop â€” Control Exception review",
            "Choose an explicitly permitted recovery or terminal action.",
            allowed_actions,
            {"control_exception": exception.model_dump(mode="json")},
            effects={action: recovery_effects[action] for action in allowed_actions},
        )
        decision = HumanDecision.model_validate(interrupt(payload))
        updates = self._decision_update(state, decision)
        recovered = {**exception.model_dump(mode="json"), "status": "RECOVERED"}
        updates.update(
            {
                "control_exception": None,
                "control_exception_history": [
                    *state.get("control_exception_history", []),
                    recovered,
                ],
                "active_governance_loop": None,
            }
        )
        if decision.action == "cancel":
            return Command(update=updates, goto="cancel_case")
        if decision.action == "fail_safe":
            return Command(update=updates, goto="fail_safe")
        if decision.action == "wait_external":
            return Command(update=updates, goto="prepare_external_event_wait")

        failed_action = exception.failed_action
        action_plan = [
            {
                **item,
                "status": "pending" if item.get("action") == failed_action else item.get("status"),
            }
            for item in state.get("action_plan", [])
        ]
        updates.update(
            {
                "action_plan": action_plan,
                "failed_actions": [
                    item for item in state.get("failed_actions", []) if item != failed_action
                ],
                "prohibited_actions": [
                    item for item in state.get("prohibited_actions", []) if item != failed_action
                ],
                "open_objectives": [
                    *state.get("open_objectives", []),
                    *(
                        [
                            {
                                "objective_id": f"RECOVERY-{uuid.uuid4().hex[:8].upper()}",
                                "action": failed_action,
                                "status": "OPEN",
                                "reason": f"AIRO authorised {decision.action} recovery.",
                            }
                        ]
                        if failed_action
                        else []
                    ),
                ],
                "deterministic_fallback_requested": (decision.action == "deterministic_fallback"),
                "lifecycle_status": LifecycleStatus.WORKING.value,
                "domain_phase": DomainPhase.EVIDENCE_REVIEW.value,
                "status": "EVIDENCE_REVIEW",
            }
        )
        return Command(update=updates, goto="observe_case")

    @staticmethod
    def fail_safe(state: TriageState) -> dict[str, Any]:
        return {
            "lifecycle_status": LifecycleStatus.FAILED_SAFE.value,
            "status": "FAILED_SAFE",
            "active_governance_loop": None,
            "updated_at": now(),
        }

    def input_gate(self, state: TriageState) -> Command:
        evaluation = self.supervisor.gate_requirement("input_confirmation", state)
        autonomy_log = self._autonomy_update(state, evaluation)
        if not evaluation.required:
            return Command(
                update={
                    "autonomy_log": autonomy_log,
                    "lifecycle_status": LifecycleStatus.WORKING.value,
                    "domain_phase": DomainPhase.INPUT_CONFIRMATION.value,
                    "status": "CALCULATING_TRIAGE",
                    "completed_nodes": _append_unique(state.get("completed_nodes"), "input_gate"),
                    "updated_at": now(),
                },
                goto="readiness_check",
            )

        payload = self._gate_payload(
            state,
            evaluation,
            "AIRO Gate 2 — Confirm material inputs",
            "Confirm or amend the structured facts before deterministic risk engines run.",
            ["confirm", "edit_answers", "return_for_evidence", "cancel_case"],
            {
                "questionnaire": state.get("questionnaire", {}),
                "advisory_evidence_summary": state.get("evidence_extraction", {}).get("summary"),
                "advisory_summary_notice": (
                    "LLM-prepared summary—AIRO confirmation required. Deterministic current "
                    "gap/conflict fields below remain authoritative for routing."
                ),
                "remaining_gaps": [
                    item
                    for item in state.get("missing_information", [])
                    if not any(
                        issue.get("summary") == item and issue.get("status") == "accepted"
                        for issue in state.get("open_issues", [])
                    )
                ],
                "remaining_conflicts": [
                    item
                    for item in state.get("inconsistencies", [])
                    if not any(
                        issue.get("summary") == item and issue.get("status") == "accepted"
                        for issue in state.get("open_issues", [])
                    )
                ],
                "airo_accepted_evidence_issues": [
                    issue
                    for issue in state.get("open_issues", [])
                    if issue.get("status") == "accepted"
                    and issue.get("category")
                    in {"mandatory_evidence_gap", "inconsistency", "verification"}
                ],
            },
            effects={
                "confirm": (
                    "Record the current structured inputs as AIRO-confirmed, then run only "
                    "deterministic engines whose inputs are not already current."
                ),
                "edit_answers": (
                    "Change questionnaire facts, invalidate dependent outputs and return "
                    "to bounded evidence preparation."
                ),
                "return_for_evidence": (
                    "Invalidate the input confirmation and create a new Gate 1 evidence request."
                ),
                "cancel_case": "Close the case without a risk approval.",
            },
        )
        decision = HumanDecision.model_validate(interrupt(payload))
        updates = self._decision_update(state, decision)
        updates["autonomy_log"] = autonomy_log

        if decision.action == "edit_answers":
            questionnaire = {**state["questionnaire"], **decision.answer_updates}
            if questionnaire.get("sensitive_data"):
                questionnaire["personal_data"] = True
            updates.update(invalidation_update(state, answer_updates=decision.answer_updates))
            updates.update({"questionnaire": questionnaire, "status": "EVIDENCE_REVIEW"})
            return Command(update=updates, goto="plan_evidence_actions")
        if decision.action == "return_for_evidence":
            updates.update(
                invalidation_update(
                    state,
                    evidence_changed=True,
                    trigger_reason="AIRO returned the inputs for further evidence",
                )
            )
            updates.update(
                {
                    "missing_information": _merge_unique(
                        state.get("missing_information", []),
                        [decision.rationale or "AIRO requested further evidence"],
                    ),
                    "status": "AWAITING_INFORMATION",
                }
            )
            return Command(update=updates, goto="draft_evidence_request")
        if decision.action == "cancel_case":
            return Command(update=updates, goto="cancel_case")
        updates["status"] = "CALCULATING_TRIAGE"
        updates["lifecycle_status"] = LifecycleStatus.WORKING.value
        updates["domain_phase"] = DomainPhase.ASSESSMENT.value
        updates["completed_nodes"] = _append_unique(state.get("completed_nodes"), "input_gate")
        updates["confirmed_facts"] = self._confirmed_input_facts(state, decision)
        updates["stale_outputs"] = [
            item for item in state.get("stale_outputs", []) if item != "confirmed_facts"
        ]
        return Command(update=updates, goto="readiness_check")

    def readiness_check(self, state: TriageState) -> dict[str, Any]:
        result = self.readiness_policy.evaluate(state)
        return {
            "readiness_result": result.model_dump(mode="json"),
            "lifecycle_status": LifecycleStatus.WORKING.value,
            "domain_phase": DomainPhase.ASSESSMENT.value,
            "transition_history": _transition_record(
                state,
                "readiness_check",
                result.rationale,
                state_changes=["readiness_result", "domain_phase"],
            ),
            "updated_at": now(),
        }

    @staticmethod
    def route_after_readiness(
        state: TriageState,
    ) -> Literal[
        "run_engines",
        "challenge_assessment",
        "draft_evidence_request",
        "input_gate",
        "enter_control_exception",
    ]:
        readiness = state.get("readiness_result", {})
        if readiness.get("ready_for_engines"):
            if state.get("materiality_result") and state.get("lod2_result"):
                return "challenge_assessment"
            return "run_engines"
        if readiness.get("blocking_gaps") or readiness.get("blocking_conflicts"):
            return "draft_evidence_request"
        if readiness.get("facts_requiring_confirmation"):
            return "input_gate"
        return "enter_control_exception"

    def run_engines(self, state: TriageState) -> dict[str, Any]:
        return {
            "lifecycle_status": LifecycleStatus.WORKING.value,
            "domain_phase": DomainPhase.ASSESSMENT.value,
            "status": "CALCULATING_TRIAGE",
            "updated_at": now(),
        }

    def _invoke_governed_tool(
        self,
        state: TriageState,
        tool_id: ToolIdentifier,
        action: ActionType,
        *,
        next_transition: str,
    ) -> dict[str, Any]:
        """Authorize, invoke and verify one fixed workflow capability."""

        decision = self.supervisor.supervise_capability(state, action)
        contract = self.registry.get(tool_id)
        proposal = ActionProposal(
            selected_action=action,
            selected_tool=tool_id,
            reason="The deterministic workflow identified the next governed capability.",
            inputs_required=ACTION_INPUTS[action],
            confidence=1.0,
        )
        authorisation = self.authoriser.authorise(proposal, state, decision, contract)
        invocation: ToolInvocation | None = None
        result = None
        state_fingerprint = _authoritative_state_fingerprint(state)
        tool_count = int(state.get("tool_call_count", 0))
        loop_count = int(state.get("total_loop_count", 0))
        retries = dict(state.get("retry_counts", {}))
        timeouts = dict(state.get("timeouts", {}))

        if authorisation.decision != "AUTHORISED":
            verification = VerificationResult(
                verified=False,
                disposition="rejected",
                checks={"policy_authorised": False, "tool_not_invoked": True},
                issues=[authorisation.reason],
                limitations=["The capability was blocked before registry invocation."],
                label="Rejected capability—no tool result was applied.",
            )
        else:
            fingerprint = hashlib.sha256(
                (state["case_id"] + action.value + state_fingerprint).encode("utf-8")
            ).hexdigest()
            invocation = ToolInvocation(
                invocation_id=f"CALL-{uuid.uuid4().hex[:12].upper()}",
                case_id=state["case_id"],
                action=action,
                tool_id=tool_id,
                tool_version=contract.version,
                case_state_version=state.get("case_state_version", 1),
                rule_version=state.get("rule_version", "unknown"),
                inputs={"state": dict(state)},
                input_references=[
                    f"questionnaire:{state.get('questionnaire_version')}",
                    f"state-fingerprint:{state_fingerprint}",
                ],
                idempotency_key=fingerprint,
                state_fingerprint=state_fingerprint,
            )
            result = self.registry.invoke(invocation, state["autonomy_profile"])
            verification = self.verifier.verify(
                result,
                contract,
                {**state, "current_tool_invocation": invocation.model_dump(mode="json")},
                self.supervisor.minimum_confidence,
            )
            tool_count += 1
            loop_count += 1
            retries[tool_id.value] = max(retries.get(tool_id.value, 0), result.retry_count)
            timeouts[tool_id.value] = contract.timeout_seconds

        succeeded = bool(
            result is not None
            and result.status == "succeeded"
            and verification.disposition in {"accepted", "advisory"}
        )
        remaining_tool_calls = max(
            0, int(state.get("max_tool_calls", self.supervisor.max_tool_calls)) - tool_count
        )
        remaining_total_loops = max(
            0, int(state.get("max_total_loops", self.supervisor.max_total_loops)) - loop_count
        )
        trace = AgentActionTrace(
            trace_id=f"TRACE-{uuid.uuid4().hex[:12].upper()}",
            occurred_at=now(),
            proposal=proposal,
            invocation=invocation,
            result=result,
            verification=verification,
            authorisation=authorisation,
            observed_state={
                "lifecycle_status": state.get("lifecycle_status"),
                "domain_phase": state.get("domain_phase"),
                "open_objectives": state.get("open_objectives", []),
                "state_fingerprint": state_fingerprint,
            },
            supervisor_decision=decision.model_dump(mode="json"),
            policy_version=self.supervisor.policy_version,
            autonomy_profile=state["autonomy_profile"],
            remaining_tool_calls=remaining_tool_calls,
            rationale=authorisation.reason,
            selection_source="deterministic_policy",
            invalidated_outputs=list(state.get("stale_outputs", [])),
            transition_decision="CONTINUE" if succeeded else "CONTROL_EXCEPTION",
            stategraph_node=action.value,
            tool_contract=contract,
            next_transition=next_transition if succeeded else "control_exception_gate",
        ).model_dump(mode="json")
        updates: dict[str, Any] = {
            "supervisor_decision": decision.model_dump(mode="json"),
            "action_authorisations": [
                *state.get("action_authorisations", []),
                authorisation.model_dump(mode="json"),
            ],
            "verification_results": [
                *state.get("verification_results", []),
                verification.model_dump(mode="json"),
            ],
            "latest_verification": verification.model_dump(mode="json"),
            "agent_action_trace": [*state.get("agent_action_trace", []), trace],
            "tool_call_count": tool_count,
            "remaining_tool_calls": remaining_tool_calls,
            "total_loop_count": loop_count,
            "remaining_total_loops": remaining_total_loops,
            "retry_counts": retries,
            "timeouts": timeouts,
            "current_action_proposal": {},
            "current_action_authorisation": {},
            "current_tool_invocation": {},
            "updated_at": now(),
        }
        if result is not None:
            updates["tool_results"] = [
                *state.get("tool_results", []),
                result.model_dump(mode="json"),
            ]
        error = (
            authorisation.reason
            if authorisation.decision != "AUTHORISED"
            else result.error
            if result and result.error
            else "; ".join(verification.issues) or "Capability verification failed."
        )
        return {
            "succeeded": succeeded,
            "output": result.output if succeeded and result is not None else {},
            "invocation": invocation.model_dump(mode="json") if invocation else None,
            "result": result.model_dump(mode="json") if result else None,
            "verification": verification.model_dump(mode="json"),
            "authorisation": authorisation.model_dump(mode="json"),
            "updates": updates,
            "error": error,
        }

    def _capability_failure_command(
        self,
        state: TriageState,
        record: dict[str, Any],
        *,
        action: ActionType,
        tool_id: ToolIdentifier,
    ) -> Command:
        projected = {**state, **record["updates"]}
        exception = self._build_control_exception(
            projected,
            code="GOVERNED_CAPABILITY_FAILURE",
            reason=record["error"],
            failed_action=action.value,
            failed_tool=tool_id.value,
        )
        issue = OpenIssue(
            issue_id=f"ISS-{uuid.uuid4().hex[:10].upper()}",
            category="verification",
            summary="A governed capability was blocked or failed verification.",
            advisory=False,
        ).model_dump()
        return Command(
            update={
                **record["updates"],
                "open_issues": [*state.get("open_issues", []), issue],
                "control_exception": exception,
                "control_exception_history": [
                    *state.get("control_exception_history", []),
                    exception,
                ],
                "lifecycle_status": LifecycleStatus.CONTROL_EXCEPTION.value,
                "active_governance_loop": GovernanceLoop.CONTROL_EXCEPTION_REVIEW.value,
                "transition_history": _transition_record(
                    state,
                    action.value,
                    record["error"],
                    state_changes=["control_exception", "lifecycle_status"],
                ),
            },
            goto="control_exception_gate",
        )

    def materiality_engine(self, state: TriageState) -> Command:
        action = ActionType.RUN_MATERIALITY_ENGINE
        tool_id = ToolIdentifier.MATERIALITY_ENGINE
        record = self._invoke_governed_tool(
            state, tool_id, action, next_transition="lod2_engine"
        )
        if not record["succeeded"]:
            return self._capability_failure_command(
                state, record, action=action, tool_id=tool_id
            )
        return Command(
            update={
                **record["updates"],
                "materiality_result": record["output"],
                "materiality_tool_record": record,
            },
            goto="lod2_engine",
        )

    def lod2_engine(self, state: TriageState) -> Command:
        action = ActionType.RUN_2LOD_ENGINE
        tool_id = ToolIdentifier.LOD2_TRIGGER_ENGINE
        record = self._invoke_governed_tool(
            state, tool_id, action, next_transition="combine_proposal"
        )
        if not record["succeeded"]:
            return self._capability_failure_command(
                state, record, action=action, tool_id=tool_id
            )
        return Command(
            update={
                **record["updates"],
                "lod2_result": record["output"],
                "lod2_tool_record": record,
            },
            goto="combine_proposal",
        )

    def combine_proposal(self, state: TriageState) -> dict[str, Any]:
        materiality = state["materiality_result"]
        lod2 = state["lod2_result"]
        materiality_hash = hashlib.sha256(
            json.dumps(materiality, sort_keys=True).encode("utf-8")
        ).hexdigest()
        lod2_hash = hashlib.sha256(json.dumps(lod2, sort_keys=True).encode("utf-8")).hexdigest()
        engine_records = [state["materiality_tool_record"], state["lod2_tool_record"]]
        return {
            "proposed_outcome": {
                "materiality_band": materiality["proposed_materiality_band"],
                "validation_requirement": materiality["proposed_validation_requirement"],
                "materiality_drivers": materiality.get("score_details", []),
                "dealbreakers": materiality.get("dealbreakers", []),
                "minimum_route_rules": materiality.get("minimum_route_rules", []),
                "triggered_2lod_teams": lod2["teams"],
                "second_line_triggers": lod2.get("triggers", []),
                "evidence_references": [
                    reference
                    for result in state.get("tool_results", [])
                    for reference in result.get("source_references", [])
                ],
                "rule_versions": {
                    "materiality": materiality.get("rule_version"),
                    "2lod": lod2.get("rule_version"),
                },
                "result_hashes": {
                    "materiality": materiality_hash,
                    "2lod": lod2_hash,
                },
                "current": True,
                "stale": False,
                "status": "PROPOSED_NOT_APPROVED",
            },
            "tool_results": [
                *state.get("tool_results", []),
                *[record["result"] for record in engine_records],
            ],
            "verification_results": [
                *state.get("verification_results", []),
                *[record["verification"] for record in engine_records],
            ],
            "current_authoritative_results": {
                **state.get("current_authoritative_results", {}),
                "materiality_result": materiality,
                "lod2_result": lod2,
            },
            "stale_outputs": [
                item
                for item in state.get("stale_outputs", [])
                if item not in {"materiality_result", "lod2_result", "proposed_outcome"}
            ],
            "completed_nodes": _append_unique(state.get("completed_nodes"), "decision_engines"),
            "updated_at": now(),
        }

    def challenge_assessment(self, state: TriageState) -> Command:
        action = ActionType.CHALLENGE_ASSESSMENT
        tool_id = ToolIdentifier.CHALLENGE_ASSESSOR
        record = self._invoke_governed_tool(
            state, tool_id, action, next_transition="exception_gate"
        )
        if not record["succeeded"]:
            return self._capability_failure_command(
                state, record, action=action, tool_id=tool_id
            )
        challenge = record["output"]
        questionnaire = state.get("questionnaire", {})
        proposed_band = state.get("materiality_result", {}).get("proposed_materiality_band")
        rule_supported_exceptions: list[str] = []
        if proposed_band in {"negligible", "minor"} and not questionnaire.get("approved_pattern"):
            rule_supported_exceptions.append(
                "The low proposed band is not supported by an explicitly approved pattern."
            )

        # Free-form LLM challenge findings are advisory. Only existing exceptions,
        # confirmed inconsistencies and transparent rule-supported exceptions may
        # control the conditional-review gate.
        exceptions = _merge_unique(
            state.get("exceptions", []),
            state.get("inconsistencies", []),
            rule_supported_exceptions,
        )
        advisory_observations = [
            f"LLM challenge observation: {item}" for item in challenge.get("exceptions", [])
        ]
        return {
            "exceptions": exceptions,
            "follow_up_questions": _merge_unique(
                state.get("follow_up_questions", []),
                advisory_observations,
                challenge.get("follow_up_questions", []),
            ),
            "challenge_summary": challenge.get("challenge_summary"),
            "advisory_observations": [
                *state.get("advisory_observations", []),
                *[
                    {
                        "observation": item,
                        "source_tool": "challenge_assessor",
                        "label": "Advisory observation—AIRO confirmation required.",
                    }
                    for item in challenge.get("exceptions", [])
                ],
            ],
            "llm_runtime": self.llm.runtime_metadata(),
            "action_authorisations": [
                *state.get("action_authorisations", []),
                authorisation,
            ],
            "tool_results": [*state.get("tool_results", []), record["result"]],
            "verification_results": [
                *state.get("verification_results", []),
                record["verification"],
            ],
            "domain_phase": DomainPhase.CHALLENGE.value,
            "status": "AWAITING_EXCEPTION_DECISION",
            "completed_nodes": _append_unique(state.get("completed_nodes"), "challenge_assessment"),
            "updated_at": now(),
        }

    def exception_gate(self, state: TriageState) -> Command:
        evaluation = self.supervisor.gate_requirement("exception_resolution", state)
        autonomy_log = self._autonomy_update(state, evaluation)
        if not evaluation.required:
            return Command(
                update={
                    "autonomy_log": autonomy_log,
                    "completed_nodes": _append_unique(
                        state.get("completed_nodes"), "exception_gate"
                    ),
                    "updated_at": now(),
                },
                goto="generate_review_pack",
            )

        payload = self._gate_payload(
            state,
            evaluation,
            "AIRO Gate 3 — Challenge and exception review",
            "Review challenge findings and determine whether the case may proceed.",
            ["proceed", "edit_answers", "return_for_evidence", "cancel_case"],
            {
                "exceptions": state.get("exceptions", []),
                "follow_up_questions": state.get("follow_up_questions", []),
                "challenge_summary": state.get("challenge_summary"),
                "proposed_outcome": state.get("proposed_outcome", {}),
            },
            effects={
                "proceed": (
                    "AIRO completes challenge review and accepts any recorded exceptions "
                    "for continued triage; this does not approve the final outcome."
                ),
                "edit_answers": (
                    "Correct a material questionnaire fact, invalidate dependent results "
                    "and rerun affected checks and engines."
                ),
                "return_for_evidence": (
                    "Create a new evidence requirement and return the case to Gate 1."
                ),
                "cancel_case": "Close the case without a risk approval.",
            },
        )
        decision = HumanDecision.model_validate(interrupt(payload))
        updates = self._decision_update(state, decision)
        updates["autonomy_log"] = autonomy_log

        if decision.action == "edit_answers":
            questionnaire = {**state["questionnaire"], **decision.answer_updates}
            if questionnaire.get("sensitive_data"):
                questionnaire["personal_data"] = True
            updates.update(invalidation_update(state, answer_updates=decision.answer_updates))
            updates.update({"questionnaire": questionnaire, "status": "EVIDENCE_REVIEW"})
            return Command(update=updates, goto="plan_evidence_actions")
        if decision.action == "return_for_evidence":
            updates.update(
                invalidation_update(
                    state,
                    evidence_changed=True,
                    trigger_reason="AIRO requested evidence after challenge",
                )
            )
            updates.update(
                {
                    "missing_information": _merge_unique(
                        state.get("missing_information", []),
                        [decision.rationale or "AIRO requested evidence after challenge"],
                    ),
                    "status": "AWAITING_INFORMATION",
                }
            )
            return Command(update=updates, goto="draft_evidence_request")
        if decision.action == "cancel_case":
            return Command(update=updates, goto="cancel_case")
        confirmed = list(state.get("confirmed_exceptions", []))
        existing_summaries = {item.get("summary") for item in confirmed}
        confirmed.extend(
            OpenIssue(
                issue_id=f"ISS-{uuid.uuid4().hex[:10].upper()}",
                category="confirmed_exception",
                summary=exception,
                status="accepted",
                owner=decision.reviewer,
                advisory=False,
            ).model_dump()
            for exception in state.get("exceptions", [])
            if exception not in existing_summaries
        )
        updates["confirmed_exceptions"] = confirmed
        updates["completed_nodes"] = _append_unique(state.get("completed_nodes"), "exception_gate")
        return Command(update=updates, goto="generate_review_pack")

    def generate_review_pack(self, state: TriageState) -> dict[str, Any]:
        authorisation = self._direct_tool_authorisation(
            state, ToolIdentifier.REVIEW_PACK_GENERATOR, "generate_review_pack"
        )
        record = self._invoke_governed_tool(
            state, ToolIdentifier.REVIEW_PACK_GENERATOR, "generate_review_pack"
        )
        pack = record["output"]
        current = dict(state.get("current_authoritative_results", {}))
        current["review_pack"] = pack
        return {
            "review_pack": pack,
            "action_authorisations": [
                *state.get("action_authorisations", []),
                authorisation,
            ],
            "tool_results": [*state.get("tool_results", []), record["result"]],
            "verification_results": [
                *state.get("verification_results", []),
                record["verification"],
            ],
            "current_authoritative_results": current,
            "stale_outputs": [
                item for item in state.get("stale_outputs", []) if item != "review_pack"
            ],
            "domain_phase": DomainPhase.FINAL_DECISION.value,
            "status": "AWAITING_FINAL_DECISION",
            "completed_nodes": _append_unique(state.get("completed_nodes"), "review_pack"),
            "updated_at": now(),
        }

    def final_gate(self, state: TriageState) -> Command:
        evaluation = self.supervisor.gate_requirement("final_triage", state)
        autonomy_log = self._autonomy_update(state, evaluation)
        proposed = state["proposed_outcome"]
        if not evaluation.required:
            final = {
                **proposed,
                "status": "AUTO_CONFIRMED_WITHIN_DEMO_POLICY",
                "decision_rationale": evaluation.rationale,
            }
            return Command(
                update={
                    "autonomy_log": autonomy_log,
                    "final_outcome": final,
                    "current_authoritative_results": {
                        **state.get("current_authoritative_results", {}),
                        "final_outcome": final,
                    },
                    "completed_nodes": _append_unique(state.get("completed_nodes"), "final_gate"),
                    "updated_at": now(),
                },
                goto="prepare_publication",
            )

        payload = self._gate_payload(
            state,
            evaluation,
            "AIRO Gate 4 — Final triage decision",
            "Confirm, amend or override the proposed materiality and 2LoD engagement.",
            ["confirm", "override", "return_for_review", "cancel_case"],
            {
                "proposed_outcome": proposed,
                "materiality": state.get("materiality_result", {}),
                "lod2": state.get("lod2_result", {}),
                "exceptions": state.get("exceptions", []),
            },
            effects={
                "confirm": (
                    "AIRO confirms the deterministic proposal as the final triage outcome; "
                    "the Coordinator then prepares a local publication draft."
                ),
                "override": (
                    "AIRO records an accountable materiality and/or 2LoD override before "
                    "publication preparation."
                ),
                "return_for_review": "Return to Gate 3 without approving a final outcome.",
                "cancel_case": "Close the case without a risk approval.",
            },
        )
        decision = HumanDecision.model_validate(interrupt(payload))
        updates = self._decision_update(state, decision)
        updates["autonomy_log"] = autonomy_log

        if decision.action == "return_for_review":
            return Command(update=updates, goto="exception_gate")
        if decision.action == "cancel_case":
            return Command(update=updates, goto="cancel_case")

        final = dict(proposed)
        if decision.action == "override":
            if decision.override_band:
                final["materiality_band"] = decision.override_band
            if decision.confirmed_teams is not None:
                final["triggered_2lod_teams"] = decision.confirmed_teams
            final["status"] = "AIRO_OVERRIDDEN"
        else:
            final["status"] = "AIRO_CONFIRMED"
        final["decision_rationale"] = decision.rationale
        final["reviewer"] = decision.reviewer
        final["decided_at"] = decision.decided_at
        updates["final_outcome"] = final
        updates["current_authoritative_results"] = {
            **state.get("current_authoritative_results", {}),
            "final_outcome": final,
        }
        updates["completed_nodes"] = _append_unique(state.get("completed_nodes"), "final_gate")
        return Command(update=updates, goto="prepare_publication")

    def prepare_publication(self, state: TriageState) -> dict[str, Any]:
        authorisation = self._direct_tool_authorisation(
            state, ToolIdentifier.REVIEW_PACK_GENERATOR, "generate_review_pack"
        )
        record = self._invoke_governed_tool(
            state, ToolIdentifier.REVIEW_PACK_GENERATOR, "generate_review_pack"
        )
        refreshed_pack = record["output"]
        draft = {
            "target": "Local demo publication record",
            "title": refreshed_pack["title"],
            "body": refreshed_pack,
            "formal_external_write": False,
        }
        return {
            "review_pack": refreshed_pack,
            "action_authorisations": [
                *state.get("action_authorisations", []),
                authorisation,
            ],
            "tool_results": [*state.get("tool_results", []), record["result"]],
            "verification_results": [
                *state.get("verification_results", []),
                record["verification"],
            ],
            "publication_draft": draft,
            "current_authoritative_results": {
                **state.get("current_authoritative_results", {}),
                "review_pack": refreshed_pack,
                "publication_draft": draft,
            },
            "publication_status": "DRAFT",
            "domain_phase": DomainPhase.PUBLICATION.value,
            "status": "READY_TO_PUBLISH",
            "updated_at": now(),
        }

    def publication_gate(self, state: TriageState) -> Command:
        evaluation = self.supervisor.gate_requirement("publication", state)
        autonomy_log = self._autonomy_update(state, evaluation)
        if not evaluation.required:
            return Command(
                update={
                    "autonomy_log": autonomy_log,
                    "publication_status": "AUTO_APPROVED_LOCAL_DEMO_ONLY",
                    "completed_nodes": _append_unique(
                        state.get("completed_nodes"), "publication_gate"
                    ),
                    "updated_at": now(),
                },
                goto="publish",
            )

        payload = self._gate_payload(
            state,
            evaluation,
            "AIRO Gate 5 — Publication approval",
            "Approve the local demo publication record. Production Confluence writes must use a separately governed adapter.",
            ["approve", "save_draft", "amend_material_fact", "cancel_case"],
            {
                "publication_draft": state.get("publication_draft", {}),
                "current_final_outcome": state.get("final_outcome", {}),
            },
            effects={
                "approve": "Approve and publish the local demonstration record only.",
                "save_draft": (
                    "Save the local draft and remain at Gate 5; no publication approval is recorded."
                ),
                "amend_material_fact": (
                    "Record new evidence and/or a corrected questionnaire fact, invalidate the "
                    "prior AIRO decision and only its dependent outputs, then selectively replan."
                ),
                "cancel_case": "Close the case without publishing the draft.",
            },
        )
        decision = HumanDecision.model_validate(interrupt(payload))
        updates = self._decision_update(state, decision)
        updates["autonomy_log"] = autonomy_log
        if decision.action == "amend_material_fact":
            if not decision.answer_updates and not decision.additional_evidence.strip():
                raise ValueError(
                    "A material-fact amendment requires answer updates or additional evidence."
                )
            questionnaire = {**state["questionnaire"], **decision.answer_updates}
            if questionnaire.get("sensitive_data"):
                questionnaire["personal_data"] = True
            evidence_changed = bool(decision.additional_evidence.strip())
            updates.update(
                invalidation_update(
                    state,
                    answer_updates=decision.answer_updates,
                    evidence_changed=evidence_changed,
                    trigger_reason=(
                        decision.rationale
                        or "AIRO recorded a material-fact amendment before publication"
                    ),
                )
            )
            evidence_text = state.get("evidence_text", "")
            if evidence_changed:
                evidence_text = (
                    evidence_text.rstrip()
                    + "\n\nADDITIONAL EVIDENCE AFTER FINAL DECISION:\n"
                    + decision.additional_evidence.strip()
                ).strip()
            updates.update(
                {
                    "questionnaire": questionnaire,
                    "evidence_text": evidence_text,
                    "evidence_cycle": state.get("evidence_cycle", 0) + 1,
                    "publication_status": "INVALIDATED_PENDING_REASSESSMENT",
                    "lifecycle_status": LifecycleStatus.WORKING.value,
                    "domain_phase": DomainPhase.EVIDENCE_REVIEW.value,
                    "status": "EVIDENCE_REVIEW",
                }
            )
            return Command(update=updates, goto="plan_evidence_actions")
        if decision.action == "save_draft":
            return Command(update=updates, goto="save_draft")
        if decision.action == "cancel_case":
            return Command(update=updates, goto="cancel_case")
        updates["publication_status"] = "AIRO_APPROVED"
        updates["completed_nodes"] = _append_unique(
            state.get("completed_nodes"), "publication_gate"
        )
        return Command(update=updates, goto="publish")

    @staticmethod
    def publish(state: TriageState) -> dict[str, Any]:
        draft = dict(state.get("publication_draft", {}))
        draft["local_demo_reference"] = f"local-demo://review-pack/{state['case_id']}"
        return {
            "publication_draft": draft,
            "publication_status": "PUBLISHED_LOCAL_DEMO",
            "lifecycle_status": LifecycleStatus.WORKING.value,
            "domain_phase": DomainPhase.PUBLICATION.value,
            "status": "COMPLETION_CHECK",
            "completed_nodes": _append_unique(state.get("completed_nodes"), "publish"),
            "updated_at": now(),
        }

    def evaluate_completion(self, state: TriageState) -> dict[str, Any]:
        evaluation = self.completion_policy.evaluate(state)
        updates: dict[str, Any] = {
            "completion_evaluation": evaluation.model_dump(mode="json"),
            "transition_history": _transition_record(
                state,
                "evaluate_completion",
                (
                    "All deterministic completion criteria are met."
                    if evaluation.complete
                    else "Completion is blocked and requires a Control Exception review."
                ),
                state_changes=["completion_evaluation"],
            ),
            "updated_at": now(),
        }
        if evaluation.complete:
            updates.update(
                {
                    "lifecycle_status": LifecycleStatus.COMPLETED.value,
                    "status": "CLOSED",
                    "completed_nodes": _append_unique(
                        state.get("completed_nodes"), "evaluate_completion"
                    ),
                }
            )
        else:
            exception = self._build_control_exception(
                state,
                code="COMPLETION_CRITERIA_NOT_MET",
                reason="Completion blockers: " + ", ".join(evaluation.blockers),
            )
            updates.update(
                {
                    "control_exception": exception,
                    "control_exception_history": [
                        *state.get("control_exception_history", []),
                        exception,
                    ],
                    "lifecycle_status": LifecycleStatus.CONTROL_EXCEPTION.value,
                    "active_governance_loop": GovernanceLoop.CONTROL_EXCEPTION_REVIEW.value,
                }
            )
        return updates

    @staticmethod
    def route_after_completion(
        state: TriageState,
    ) -> Literal["control_exception_gate", "__end__"]:
        return (
            "__end__"
            if state.get("completion_evaluation", {}).get("complete")
            else "control_exception_gate"
        )

    @staticmethod
    def save_draft(state: TriageState) -> dict[str, Any]:
        return {
            "publication_status": "DRAFT_SAVED",
            "status": "READY_TO_PUBLISH",
            "updated_at": now(),
        }

    @staticmethod
    def cancel_case(state: TriageState) -> dict[str, Any]:
        return {
            "lifecycle_status": LifecycleStatus.CANCELLED.value,
            "status": "CANCELLED",
            "active_governance_loop": None,
            "updated_at": now(),
        }

    def build(self, checkpointer):
        graph = StateGraph(TriageState)
        graph.add_node("normalise_intake", self.normalise_intake)
        graph.add_node("plan_evidence_actions", self.plan_evidence_actions)
        graph.add_node("observe_case", self.observe_case)
        graph.add_node("supervise_actions", self.supervise_actions)
        graph.add_node("select_required_action", self.select_required_action)
        graph.add_node("recommend_evidence_action", self.recommend_evidence_action)
        graph.add_node("authorise_action", self.authorise_action)
        graph.add_node("record_rejected_action", self.record_rejected_action)
        graph.add_node("enter_control_exception", self.enter_control_exception)
        graph.add_node("control_exception_gate", self.control_exception_gate)
        graph.add_node("fail_safe", self.fail_safe)
        graph.add_node("execute_tool", self.execute_tool)
        graph.add_node("verify_tool_result", self.verify_tool_result)
        graph.add_node("update_case_state", self.update_case_state)
        graph.add_node("reassess_case", self.reassess_case)
        graph.add_node("draft_evidence_request", self.draft_evidence_request)
        graph.add_node("prepare_external_event_wait", self.prepare_external_event_wait)
        graph.add_node("external_event_wait", self.external_event_wait)
        graph.add_node("evidence_gate", self.evidence_gate)
        graph.add_node("input_gate", self.input_gate)
        graph.add_node("readiness_check", self.readiness_check)
        graph.add_node("run_engines", self.run_engines)
        graph.add_node("materiality_engine", self.materiality_engine)
        graph.add_node("lod2_engine", self.lod2_engine)
        graph.add_node("combine_proposal", self.combine_proposal)
        graph.add_node("challenge_assessment", self.challenge_assessment)
        graph.add_node("exception_gate", self.exception_gate)
        graph.add_node("generate_review_pack", self.generate_review_pack)
        graph.add_node("final_gate", self.final_gate)
        graph.add_node("prepare_publication", self.prepare_publication)
        graph.add_node("publication_gate", self.publication_gate)
        graph.add_node("publish", self.publish)
        graph.add_node("evaluate_completion", self.evaluate_completion)
        graph.add_node("save_draft", self.save_draft)
        graph.add_node("cancel_case", self.cancel_case)

        graph.add_edge(START, "normalise_intake")
        graph.add_edge("normalise_intake", "plan_evidence_actions")
        graph.add_edge("plan_evidence_actions", "observe_case")
        graph.add_edge("observe_case", "supervise_actions")
        graph.add_conditional_edges("supervise_actions", self.route_after_supervision)
        graph.add_edge("select_required_action", "authorise_action")
        graph.add_edge("recommend_evidence_action", "authorise_action")
        graph.add_conditional_edges("authorise_action", self.route_after_authorisation)
        graph.add_edge("record_rejected_action", "control_exception_gate")
        graph.add_edge("enter_control_exception", "control_exception_gate")
        graph.add_edge("execute_tool", "verify_tool_result")
        graph.add_conditional_edges(
            "verify_tool_result",
            self.route_after_tool_verification,
            {
                "execute_tool": "execute_tool",
                "update_case_state": "update_case_state",
            },
        )
        graph.add_edge("update_case_state", "reassess_case")
        graph.add_conditional_edges("reassess_case", self.route_after_reassessment)
        graph.add_edge("draft_evidence_request", "evidence_gate")
        graph.add_edge("prepare_external_event_wait", "external_event_wait")
        graph.add_conditional_edges("readiness_check", self.route_after_readiness)
        graph.add_edge("run_engines", "materiality_engine")
        graph.add_edge("run_engines", "lod2_engine")
        graph.add_edge(["materiality_engine", "lod2_engine"], "combine_proposal")
        graph.add_edge("combine_proposal", "challenge_assessment")
        graph.add_edge("challenge_assessment", "exception_gate")
        graph.add_edge("generate_review_pack", "final_gate")
        graph.add_edge("prepare_publication", "publication_gate")
        graph.add_edge("publish", "evaluate_completion")
        graph.add_conditional_edges("evaluate_completion", self.route_after_completion)
        # Saving a draft is a durable pause, not an approval. Re-enter the
        # publication gate so a later explicit AIRO decision can complete it.
        graph.add_edge("save_draft", "publication_gate")
        graph.add_edge("cancel_case", END)
        graph.add_edge("fail_safe", END)
        return graph.compile(checkpointer=checkpointer)
