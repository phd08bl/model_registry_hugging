from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, datetime
from typing import Any, Literal

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from app.agent.interrupts import AIROInterruptController
from app.agent.invalidation import invalidation_update
from app.agent.policy import ACTION_INPUTS, PolicySupervisor
from app.agent.router import BoundedActionRouter
from app.agent.tools import ToolRegistry
from app.agent.verifier import ResultVerifier
from app.engines.autonomy import GateEvaluation
from app.llm.base import LLMClient
from app.schemas import (
    ActionProposal,
    ActionType,
    AgentActionTrace,
    HumanDecision,
    OpenIssue,
    ToolIdentifier,
    ToolInvocation,
    VerificationResult,
)
from app.services.evidence import (
    build_targeted_questions,
)
from app.state import TriageState

WORKFLOW_VERSION = "airo-case-coordinator-0.2"
PROMPT_VERSION = "demo-prompts-0.2"


def now() -> str:
    return datetime.now(UTC).isoformat()


def _append_unique(values: list[str] | None, value: str) -> list[str]:
    result = list(values or [])
    if value not in result:
        result.append(value)
    return result


def _merge_unique(*groups: list[str] | None) -> list[str]:
    return sorted({item for group in groups for item in (group or []) if item})


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
        return self.interrupt_controller.build_payload(
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

    @staticmethod
    def _decision_update(state: TriageState, decision: HumanDecision) -> dict[str, Any]:
        decisions = list(state.get("human_decisions", []))
        decisions.append(decision.model_dump())
        return {"human_decisions": decisions, "updated_at": now()}

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

    def normalise_intake(self, state: TriageState) -> dict[str, Any]:
        questionnaire = dict(state.get("questionnaire", {}))
        if questionnaire.get("sensitive_data"):
            questionnaire["personal_data"] = True
        return {
            "questionnaire": questionnaire,
            "status": "INGESTING",
            "evidence_cycle": state.get("evidence_cycle", 0),
            "questionnaire_version": state.get("questionnaire_version", "demo-questionnaire-1.0"),
            "rule_version": "demo-rules-1.0",
            "workflow_version": WORKFLOW_VERSION,
            "prompt_version": PROMPT_VERSION,
            "completed_nodes": _append_unique(state.get("completed_nodes"), "normalise_intake"),
            "updated_at": now(),
        }

    def plan_evidence_actions(self, state: TriageState) -> dict[str, Any]:
        """Create a bounded evidence plan from facts, never from model-selected authority."""

        questionnaire = state.get("questionnaire", {})
        searchable = " ".join(
            [questionnaire.get("use_case_name", ""), questionnaire.get("purpose", "")]
        ).lower()
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
            "completed_actions": [],
            "failed_actions": [],
            "prohibited_actions": [],
            "tool_call_count": 0,
            "remaining_tool_calls": state.get("max_tool_calls", self.supervisor.max_tool_calls),
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
        return {
            "pending_actions": pending,
            "recommended_next_action": {
                "action": pending[0] if pending else "reassess_case",
                "reason": "Next unresolved governed evidence objective.",
            },
            "completed_nodes": _append_unique(state.get("completed_nodes"), "observe_case"),
            "updated_at": now(),
        }

    def supervise_actions(self, state: TriageState) -> dict[str, Any]:
        assignment = self.supervisor.effective_autonomy_profile(state)
        assessment = self.supervisor.assess_state(state)
        return {
            "autonomy_profile": assignment.effective_profile,
            "autonomy_assignment": assignment.model_dump(),
            "policy_assessment": {
                "permitted_actions": [item.value for item in assessment.permitted_actions],
                "permitted_tools": [item.value for item in assessment.permitted_tools],
                "mandatory_checks": list(assessment.mandatory_checks),
                "router_permitted": assessment.router_permitted,
                "max_tool_calls": assessment.max_tool_calls,
                "max_evidence_cycles": assessment.max_evidence_cycles,
                "minimum_confidence": assessment.minimum_confidence,
                "fail_closed": assessment.fail_closed,
                "rationale": assessment.rationale,
                "policy_version": assessment.policy_version,
            },
            "updated_at": now(),
        }

    def route_evidence_action(self, state: TriageState) -> dict[str, Any]:
        actions = [ActionType(item) for item in state["policy_assessment"]["permitted_actions"]]
        tools = [ToolIdentifier(item) for item in state["policy_assessment"]["permitted_tools"]]
        proposal, router_invoked = self.router.recommend(state, actions, tools)
        return {
            "current_action_proposal": proposal.model_dump(mode="json"),
            "router_invoked": router_invoked,
            "updated_at": now(),
        }

    def validate_action(self, state: TriageState) -> dict[str, Any]:
        proposal = ActionProposal.model_validate(state["current_action_proposal"])
        valid, rationale = self.supervisor.validate_action_proposal(proposal, state)
        prohibited = list(state.get("prohibited_actions", []))
        if not valid:
            prohibited.append(proposal.selected_action.value)
        return {
            "action_validation": {"valid": valid, "rationale": rationale},
            "prohibited_actions": prohibited,
            "updated_at": now(),
        }

    @staticmethod
    def route_after_validation(
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
        rationale = state.get("action_validation", {}).get(
            "rationale", "Policy escalation requires AIRO review."
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
        trace.append(
            AgentActionTrace(
                trace_id=f"TRACE-{uuid.uuid4().hex[:12].upper()}",
                occurred_at=now(),
                proposal=proposal,
                verification=verification,
                policy_version=self.supervisor.policy_version,
                autonomy_profile=state["autonomy_profile"],
                remaining_tool_calls=state.get("remaining_tool_calls", 0),
                rationale=rationale,
                selection_source=(
                    "llm_router" if state.get("router_invoked") else "deterministic_policy"
                ),
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
        return {
            "latest_verification": verification.model_dump(),
            "agent_action_trace": trace,
            "failed_actions": failed,
            "action_plan": plan,
            "open_issues": [*state.get("open_issues", []), issue],
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
        fingerprint = hashlib.sha256(
            (
                state["case_id"]
                + str(state.get("evidence_cycle", 0))
                + proposal.selected_action.value
                + str(state.get("questionnaire", {}))
                + state.get("evidence_text", "")
            ).encode("utf-8")
        ).hexdigest()
        invocation = ToolInvocation(
            invocation_id=f"CALL-{uuid.uuid4().hex[:12].upper()}",
            case_id=state["case_id"],
            action=proposal.selected_action,
            tool_id=proposal.selected_tool,
            tool_version=contract.version,
            inputs=inputs,
            input_references=[
                f"questionnaire:{state.get('questionnaire_version')}",
                f"evidence-cycle:{state.get('evidence_cycle', 0)}",
            ],
            idempotency_key=fingerprint,
        )
        result = self.registry.invoke(invocation, state["autonomy_profile"])
        retries = dict(state.get("retry_counts", {}))
        retries[proposal.selected_tool.value] = result.retry_count
        timeouts = dict(state.get("timeouts", {}))
        timeouts[proposal.selected_tool.value] = contract.timeout_seconds
        return {
            "current_tool_invocation": invocation.model_dump(mode="json"),
            "latest_tool_result": result.model_dump(mode="json"),
            "tool_call_count": state.get("tool_call_count", 0) + 1,
            "retry_counts": retries,
            "timeouts": timeouts,
            "remaining_tool_calls": max(
                0,
                state.get("max_tool_calls", self.supervisor.max_tool_calls)
                - state.get("tool_call_count", 0)
                - 1,
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
        return {"latest_verification": verification.model_dump(), "updated_at": now()}

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
                updates["llm_runtime"] = self.llm.runtime_metadata()
            elif proposal.selected_action == ActionType.CHECK_QUESTIONNAIRE_EVIDENCE_CONSISTENCY:
                missing = output.get("mandatory_evidence_gaps", [])
                conflicts = output.get("inconsistencies", [])
                updates["missing_information"] = missing
                updates["inconsistencies"] = conflicts
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
        trace.append(
            AgentActionTrace(
                trace_id=f"TRACE-{uuid.uuid4().hex[:12].upper()}",
                occurred_at=now(),
                proposal=proposal,
                invocation=ToolInvocation.model_validate(state.get("current_tool_invocation")),
                result=state.get("latest_tool_result"),
                verification=verification,
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
            ).model_dump(mode="json")
        )
        updates.update(
            {
                "action_plan": plan,
                "completed_actions": completed,
                "failed_actions": failed,
                "open_issues": open_issues,
                "advisory_observations": advisory,
                "agent_action_trace": trace,
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
            "updated_at": now(),
        }

    @staticmethod
    def route_after_reassessment(
        state: TriageState,
    ) -> Literal["observe_case", "draft_evidence_request", "input_gate"]:
        if state.get("reassessment", {}).get("continue"):
            return "observe_case"
        if (
            state.get("reassessment", {}).get("fail_closed")
            or state.get("missing_information")
            or state.get("inconsistencies")
        ):
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
            "status": "AWAITING_INFORMATION",
            "completed_nodes": _append_unique(
                state.get("completed_nodes"), "draft_evidence_request"
            ),
            "updated_at": now(),
        }

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

    def input_gate(self, state: TriageState) -> Command:
        evaluation = self.supervisor.gate_requirement("input_confirmation", state)
        autonomy_log = self._autonomy_update(state, evaluation)
        if not evaluation.required:
            return Command(
                update={
                    "autonomy_log": autonomy_log,
                    "status": "CALCULATING_TRIAGE",
                    "completed_nodes": _append_unique(state.get("completed_nodes"), "input_gate"),
                    "updated_at": now(),
                },
                goto=self._route_after_confirmed_inputs(state),
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
        updates["completed_nodes"] = _append_unique(state.get("completed_nodes"), "input_gate")
        updates["confirmed_facts"] = self._confirmed_input_facts(state, decision)
        return Command(update=updates, goto=self._route_after_confirmed_inputs(state))

    @staticmethod
    def run_engines(state: TriageState) -> dict[str, Any]:
        return {"status": "CALCULATING_TRIAGE", "updated_at": now()}

    def _invoke_governed_tool(
        self, state: TriageState, tool_id: ToolIdentifier, action: str
    ) -> dict[str, Any]:
        contract = self.registry.get(tool_id)
        fingerprint = hashlib.sha256(
            (
                state["case_id"]
                + action
                + str(state.get("questionnaire", {}))
                + str(state.get("final_outcome", {}))
                + str(state.get("exceptions", []))
                + str(state.get("human_decisions", []))
            ).encode("utf-8")
        ).hexdigest()
        invocation = ToolInvocation(
            invocation_id=f"CALL-{uuid.uuid4().hex[:12].upper()}",
            case_id=state["case_id"],
            action=action,
            tool_id=tool_id,
            tool_version=contract.version,
            inputs={"state": dict(state)},
            input_references=[f"questionnaire:{state.get('questionnaire_version')}"],
            idempotency_key=fingerprint,
        )
        result = self.registry.invoke(invocation, state["autonomy_profile"])
        verification = self.verifier.verify(
            result, contract, state, self.supervisor.minimum_confidence
        )
        if result.status != "succeeded" or verification.disposition in {"rejected", "escalate"}:
            raise RuntimeError(f"Governed tool failed closed: {tool_id.value}: {result.error}")
        return result.output

    def materiality_engine(self, state: TriageState) -> dict[str, Any]:
        result = self._invoke_governed_tool(
            state, ToolIdentifier.MATERIALITY_ENGINE, "run_materiality_engine"
        )
        return {"materiality_result": result}

    def lod2_engine(self, state: TriageState) -> dict[str, Any]:
        result = self._invoke_governed_tool(
            state, ToolIdentifier.LOD2_TRIGGER_ENGINE, "run_2lod_engine"
        )
        return {"lod2_result": result}

    def combine_proposal(self, state: TriageState) -> dict[str, Any]:
        materiality = state["materiality_result"]
        lod2 = state["lod2_result"]
        return {
            "proposed_outcome": {
                "materiality_band": materiality["proposed_materiality_band"],
                "validation_requirement": materiality["proposed_validation_requirement"],
                "triggered_2lod_teams": lod2["teams"],
                "status": "PROPOSED_NOT_APPROVED",
            },
            "current_authoritative_results": {
                **state.get("current_authoritative_results", {}),
                "materiality_result": materiality,
                "lod2_result": lod2,
            },
            "completed_nodes": _append_unique(state.get("completed_nodes"), "decision_engines"),
            "updated_at": now(),
        }

    def challenge_assessment(self, state: TriageState) -> dict[str, Any]:
        challenge = self._invoke_governed_tool(
            state, ToolIdentifier.CHALLENGE_ASSESSOR, "challenge_assessment"
        )
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
        pack = self._invoke_governed_tool(
            state, ToolIdentifier.REVIEW_PACK_GENERATOR, "generate_review_pack"
        )
        current = dict(state.get("current_authoritative_results", {}))
        current["review_pack"] = pack
        return {
            "review_pack": pack,
            "current_authoritative_results": current,
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
        refreshed_pack = self._invoke_governed_tool(
            state, ToolIdentifier.REVIEW_PACK_GENERATOR, "generate_review_pack"
        )
        draft = {
            "target": "Local demo publication record",
            "title": refreshed_pack["title"],
            "body": refreshed_pack,
            "formal_external_write": False,
        }
        return {
            "review_pack": refreshed_pack,
            "publication_draft": draft,
            "current_authoritative_results": {
                **state.get("current_authoritative_results", {}),
                "review_pack": refreshed_pack,
                "publication_draft": draft,
            },
            "publication_status": "DRAFT",
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
            ["approve", "save_draft", "cancel_case"],
            {"publication_draft": state.get("publication_draft", {})},
            effects={
                "approve": "Approve and publish the local demonstration record only.",
                "save_draft": (
                    "Save the local draft and remain at Gate 5; no publication approval is recorded."
                ),
                "cancel_case": "Close the case without publishing the draft.",
            },
        )
        decision = HumanDecision.model_validate(interrupt(payload))
        updates = self._decision_update(state, decision)
        updates["autonomy_log"] = autonomy_log
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
            "status": "CLOSED",
            "completed_nodes": _append_unique(state.get("completed_nodes"), "publish"),
            "updated_at": now(),
        }

    @staticmethod
    def save_draft(state: TriageState) -> dict[str, Any]:
        return {
            "publication_status": "DRAFT_SAVED",
            "status": "READY_TO_PUBLISH",
            "updated_at": now(),
        }

    @staticmethod
    def cancel_case(state: TriageState) -> dict[str, Any]:
        return {"status": "CANCELLED", "updated_at": now()}

    def build(self, checkpointer):
        graph = StateGraph(TriageState)
        graph.add_node("normalise_intake", self.normalise_intake)
        graph.add_node("plan_evidence_actions", self.plan_evidence_actions)
        graph.add_node("observe_case", self.observe_case)
        graph.add_node("supervise_actions", self.supervise_actions)
        graph.add_node("route_evidence_action", self.route_evidence_action)
        graph.add_node("validate_action", self.validate_action)
        graph.add_node("record_rejected_action", self.record_rejected_action)
        graph.add_node("execute_tool", self.execute_tool)
        graph.add_node("verify_tool_result", self.verify_tool_result)
        graph.add_node("update_case_state", self.update_case_state)
        graph.add_node("reassess_case", self.reassess_case)
        graph.add_node("draft_evidence_request", self.draft_evidence_request)
        graph.add_node("evidence_gate", self.evidence_gate)
        graph.add_node("input_gate", self.input_gate)
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
        graph.add_node("save_draft", self.save_draft)
        graph.add_node("cancel_case", self.cancel_case)

        graph.add_edge(START, "normalise_intake")
        graph.add_edge("normalise_intake", "plan_evidence_actions")
        graph.add_edge("plan_evidence_actions", "observe_case")
        graph.add_edge("observe_case", "supervise_actions")
        graph.add_edge("supervise_actions", "route_evidence_action")
        graph.add_edge("route_evidence_action", "validate_action")
        graph.add_conditional_edges("validate_action", self.route_after_validation)
        graph.add_edge("record_rejected_action", "reassess_case")
        graph.add_edge("execute_tool", "verify_tool_result")
        graph.add_edge("verify_tool_result", "update_case_state")
        graph.add_edge("update_case_state", "reassess_case")
        graph.add_conditional_edges("reassess_case", self.route_after_reassessment)
        graph.add_edge("draft_evidence_request", "evidence_gate")
        graph.add_edge("run_engines", "materiality_engine")
        graph.add_edge("run_engines", "lod2_engine")
        graph.add_edge(["materiality_engine", "lod2_engine"], "combine_proposal")
        graph.add_edge("combine_proposal", "challenge_assessment")
        graph.add_edge("challenge_assessment", "exception_gate")
        graph.add_edge("generate_review_pack", "final_gate")
        graph.add_edge("prepare_publication", "publication_gate")
        graph.add_edge("publish", END)
        # Saving a draft is a durable pause, not an approval. Re-enter the
        # publication gate so a later explicit AIRO decision can complete it.
        graph.add_edge("save_draft", "publication_gate")
        graph.add_edge("cancel_case", END)
        return graph.compile(checkpointer=checkpointer)
