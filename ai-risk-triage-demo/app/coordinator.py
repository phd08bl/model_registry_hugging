from __future__ import annotations

import hashlib
import sqlite3
import threading
import uuid
from datetime import UTC, datetime
from typing import Any

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command
from pydantic import ValidationError

from app.agent.policy import PolicySupervisor
from app.agent.router import BoundedActionRouter
from app.agent.tools import ToolRegistry
from app.agent.verifier import ResultVerifier
from app.config import Settings
from app.database import CaseRepository
from app.graph import TriageGraphFactory
from app.llm.base import LLMClient
from app.schemas import (
    CASE_COMPLETION_CRITERIA,
    CASE_OBJECTIVE_STATEMENT,
    CaseObjective,
    ControlException,
    ControlRecoveryRequest,
    CreateCaseRequest,
    DemonstrationCase,
    DomainPhase,
    ExternalEventSubmission,
    GovernanceLoop,
    HumanDecision,
    LifecycleStatus,
    Questionnaire,
)
from app.versions import (
    AGENT_POLICY_VERSION,
    CASE_STATE_SCHEMA_VERSION,
    PROMPT_VERSION,
    QUESTIONNAIRE_VERSION,
    RULESET_VERSION,
    TOOL_CONTRACT_VERSION,
    WORKFLOW_VERSION,
)

CASE_OBJECTIVE = CaseObjective(
    statement=CASE_OBJECTIVE_STATEMENT,
    completion_criteria=CASE_COMPLETION_CRITERIA,
)


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class CaseCoordinator:
    """Application service wrapping the graph, checkpoints, case store and audit."""

    def __init__(self, settings: Settings, llm: LLMClient):
        self.settings = settings
        self.llm = llm
        self.repository = CaseRepository(settings.absolute_case_db_path)
        self.policy_supervisor = PolicySupervisor()
        self.tool_registry = ToolRegistry(llm)
        self.router = BoundedActionRouter(llm)
        self.verifier = ResultVerifier()
        settings.absolute_checkpoint_db_path.parent.mkdir(parents=True, exist_ok=True)
        self._checkpoint_connection = sqlite3.connect(
            settings.absolute_checkpoint_db_path,
            check_same_thread=False,
        )
        self.checkpointer = SqliteSaver(self._checkpoint_connection)
        self.graph = TriageGraphFactory(
            llm,
            supervisor=self.policy_supervisor,
            router=self.router,
            registry=self.tool_registry,
            verifier=self.verifier,
        ).build(self.checkpointer)
        self._run_lock = threading.RLock()

    @staticmethod
    def _config(case_id: str) -> dict[str, Any]:
        return {"configurable": {"thread_id": case_id}}

    def create_case(self, request: CreateCaseRequest) -> dict[str, Any]:
        """Create a production-style case; creators cannot select autonomy."""

        return self._create_case(request, governed_pattern_id=None)

    def create_demo_case(self, fixture: DemonstrationCase) -> dict[str, Any]:
        """Create a case using a governed illustrative pattern fixture."""

        expected = self.policy_supervisor.assign_autonomy(
            fixture.questionnaire.model_dump(), fixture.governed_pattern_id
        )
        if (
            expected.approved_maximum_profile != fixture.expected_approved_maximum_profile
            or expected.effective_profile != fixture.expected_assigned_profile
        ):
            raise ValueError(
                "Demonstration expectation does not match the governed policy assignment."
            )
        controls = fixture.demo_controls
        return self._create_case(
            fixture.initial_submission,
            governed_pattern_id=fixture.governed_pattern_id,
            demonstration={
                "sample_id": fixture.sample_id,
                "router_mode": controls.router_mode,
                "tool_result_mode": controls.tool_result_mode,
                "sampling_key": controls.sampling_key,
                "max_tool_calls": controls.max_tool_calls,
            },
        )

    def _create_case(
        self,
        request: CreateCaseRequest,
        governed_pattern_id: str | None,
        demonstration: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        case_id = f"AIRO-{uuid.uuid4().hex[:8].upper()}"
        created = utc_now()
        assignment = self.policy_supervisor.assign_autonomy(
            request.questionnaire.model_dump(), governed_pattern_id
        )
        demo = demonstration or {}
        max_tool_calls = demo.get("max_tool_calls") or self.policy_supervisor.max_tool_calls
        state = {
            "case_id": case_id,
            "thread_id": case_id,
            "case_state_version": 1,
            "lifecycle_status": LifecycleStatus.NEW.value,
            "domain_phase": DomainPhase.INTAKE.value,
            "status": "DRAFT",
            "autonomy_profile": assignment.effective_profile,
            "autonomy_assignment": assignment.model_dump(),
            "demo_scenario_id": demo.get("sample_id"),
            "demo_controls": (
                {
                    "router_mode": demo.get("router_mode", "normal"),
                    "tool_result_mode": demo.get("tool_result_mode", "normal"),
                }
                if demonstration
                else {}
            ),
            "sampling_key": demo.get("sampling_key"),
            "case_objective": CASE_OBJECTIVE.model_dump(),
            "completion_criteria": list(CASE_OBJECTIVE.completion_criteria),
            "created_at": created,
            "updated_at": created,
            "questionnaire": request.questionnaire.model_dump(),
            "evidence_text": request.evidence_text,
            "evidence_cycle": 0,
            "submitted_facts": [],
            "candidate_facts": [],
            "evidence_claims": [],
            "mandatory_evidence_gaps": [],
            "evidence_conflicts": [],
            "llm_advisory_observations": [],
            "advisory_observations": [],
            "confirmed_exceptions": [],
            "open_issues": [],
            "missing_information": [],
            "inconsistencies": [],
            "exceptions": [],
            "follow_up_questions": [],
            "human_decisions": [],
            "autonomy_log": [],
            "completed_nodes": [],
            "task_plan": [],
            "open_objectives": [],
            "completed_objectives": [],
            "action_plan": [],
            "pending_actions": [],
            "completed_actions": [],
            "failed_actions": [],
            "prohibited_actions": [],
            "agent_action_trace": [],
            "deterministic_fallback_requested": False,
            "rework_actions": [],
            "supervisor_decision": {},
            "current_action_authorisation": {},
            "action_authorisations": [],
            "tool_results": [],
            "verification_results": [],
            "tool_call_count": 0,
            "max_tool_calls": max_tool_calls,
            "remaining_tool_calls": max_tool_calls,
            "max_evidence_cycles": self.policy_supervisor.max_evidence_cycles,
            "total_loop_count": 0,
            "max_total_loops": self.policy_supervisor.max_total_loops,
            "remaining_total_loops": self.policy_supervisor.max_total_loops,
            "execution_budgets": {
                "maximum_tool_calls": max_tool_calls,
                "remaining_tool_calls": max_tool_calls,
                "maximum_retries": self.policy_supervisor.max_retries,
                "remaining_retries": self.policy_supervisor.max_retries,
                "maximum_evidence_cycles": self.policy_supervisor.max_evidence_cycles,
                "remaining_evidence_cycles": self.policy_supervisor.max_evidence_cycles,
                "maximum_total_loops": self.policy_supervisor.max_total_loops,
                "remaining_total_loops": self.policy_supervisor.max_total_loops,
            },
            "retry_counts": {},
            "timeouts": {},
            "readiness_result": {},
            "active_governance_loop": None,
            "processed_decision_ids": [],
            "expected_external_events": [],
            "active_external_event": None,
            "processed_external_events": [],
            "control_exception": None,
            "control_exception_history": [],
            "invalidations": [],
            "superseded_results": [],
            "current_authoritative_results": {},
            "stale_outputs": [],
            "dependency_metadata": {
                "questionnaire.personal_data": [
                    "evidence_consistency",
                    "materiality_result",
                    "lod2_result",
                    "proposed_outcome",
                    "review_pack",
                    "final_outcome",
                    "publication_draft",
                ],
                "rule_version": [
                    "materiality_result",
                    "lod2_result",
                    "proposed_outcome",
                    "review_pack",
                    "final_outcome",
                ],
            },
            "material_change_requires_airo_review": False,
            "completion_evaluation": {},
            "transition_history": [],
            "decision_authority": "AI Risk Oversight (AIRO)",
            "questionnaire_version": QUESTIONNAIRE_VERSION,
            "rule_version": RULESET_VERSION,
            "workflow_version": WORKFLOW_VERSION,
            "prompt_version": PROMPT_VERSION,
            "policy_version": AGENT_POLICY_VERSION,
            "tool_contract_version": TOOL_CONTRACT_VERSION,
            "model_version": str(self.llm.runtime_metadata().get("model", "mock-or-configured")),
            "version_manifest": {
                "case_state": CASE_STATE_SCHEMA_VERSION,
                "questionnaire": QUESTIONNAIRE_VERSION,
                "rules": RULESET_VERSION,
                "workflow": WORKFLOW_VERSION,
                "prompt": PROMPT_VERSION,
                "policy": AGENT_POLICY_VERSION,
                "tools": TOOL_CONTRACT_VERSION,
            },
            "publication_status": "NOT_STARTED",
        }
        self.repository.create(state)
        self.repository.add_audit(
            case_id,
            "human",
            "AIRO demo user",
            "CASE_CREATED",
            {
                "autonomy_assignment": assignment.model_dump(),
                "case_objective_version": CASE_OBJECTIVE.version,
            },
        )
        return self.get_case(case_id)

    def _save_snapshot(self, case_id: str, action: str) -> dict[str, Any]:
        snapshot = self.graph.get_state(self._config(case_id))
        state = dict(snapshot.values)
        pending_interrupt = snapshot.interrupts[0].value if snapshot.interrupts else None
        pending_gate = (
            pending_interrupt
            if pending_interrupt
            and pending_interrupt.get("interrupt_kind", "human_governance") == "human_governance"
            else None
        )
        state["current_gate"] = pending_gate.get("gate_id") if pending_gate else None
        if pending_gate:
            state["active_governance_loop"] = pending_gate.get("governance_loop")
            state["status"] = {
                "evidence_request": "AWAITING_INFORMATION",
                "input_confirmation": "AWAITING_INPUT_CONFIRMATION",
                "exception_resolution": "AWAITING_EXCEPTION_DECISION",
                "final_triage": "AWAITING_FINAL_DECISION",
                "publication": "READY_TO_PUBLISH",
                "control_exception_review": "CONTROL_EXCEPTION",
            }.get(pending_gate.get("gate_id"), state.get("status", "AWAITING_HUMAN"))
            if pending_gate.get("gate_id") == "control_exception_review":
                state["lifecycle_status"] = LifecycleStatus.CONTROL_EXCEPTION.value
            else:
                state["lifecycle_status"] = LifecycleStatus.AWAITING_HUMAN.value
            state["domain_phase"] = {
                "evidence_request": DomainPhase.EVIDENCE_REVIEW.value,
                "input_confirmation": DomainPhase.INPUT_CONFIRMATION.value,
                "exception_resolution": DomainPhase.CHALLENGE.value,
                "final_triage": DomainPhase.FINAL_DECISION.value,
                "publication": DomainPhase.PUBLICATION.value,
            }.get(pending_gate.get("gate_id"), state.get("domain_phase"))
        elif pending_interrupt and pending_interrupt.get("interrupt_kind") == "external_event":
            state["current_gate"] = None
            state["active_governance_loop"] = None
            state["lifecycle_status"] = LifecycleStatus.AWAITING_EXTERNAL_EVENT.value
            state["domain_phase"] = DomainPhase.EVIDENCE_REVIEW.value
            state["status"] = "AWAITING_EXTERNAL_EVENT"
        # The graph's last supervisor record describes the action cycle that led
        # here. Recompute after applying the interrupt so the API/UI receives the
        # policy decision for the authoritative paused Case State.
        state["supervisor_decision"] = self.policy_supervisor.supervise(state).model_dump(
            mode="json"
        )
        latest_trace = (state.get("agent_action_trace") or [{}])[-1]
        self.repository.save(case_id, state, pending_gate)
        self.repository.add_audit(
            case_id,
            "system",
            "AIRO Case Coordinator",
            action,
            {
                "status": state.get("status"),
                "pending_gate": pending_gate.get("gate_id") if pending_gate else None,
                "pending_event": (
                    state.get("active_external_event", {}).get("event_type")
                    if state.get("active_external_event")
                    else None
                ),
                "next_nodes": list(snapshot.next),
                "llm_runtime": state.get("llm_runtime", {}),
                "autonomy_assignment": state.get("autonomy_assignment", {}),
                "latest_action": state.get("current_action_proposal")
                or latest_trace.get("proposal", {}),
                "latest_verification": state.get("latest_verification", {}),
                "remaining_tool_calls": state.get("remaining_tool_calls"),
            },
        )
        return self.get_case(case_id)

    def start(self, case_id: str) -> dict[str, Any]:
        existing = self.repository.get(case_id)
        if not existing:
            raise KeyError(case_id)
        if existing["status"] != "DRAFT":
            return self.get_case(case_id)
        with self._run_lock:
            try:
                self.graph.invoke(existing["state"], self._config(case_id))
                return self._save_snapshot(case_id, "GRAPH_STARTED_OR_PAUSED")
            except Exception as exc:
                state = existing["state"]
                control_exception = ControlException(
                    exception_id=f"CTRL-{uuid.uuid4().hex[:12].upper()}",
                    code="UNHANDLED_WORKFLOW_FAILURE",
                    reason="Workflow execution failed closed. Review protected service telemetry.",
                    recoverable=False,
                    retry_count=0,
                    budget_state={
                        "remaining_tool_calls": state.get("remaining_tool_calls", 0),
                        "remaining_total_loops": state.get("remaining_total_loops", 0),
                    },
                    allowed_recovery_actions=["cancel", "fail_safe"],
                    timestamp=utc_now(),
                    status="FAILED_SAFE",
                ).model_dump(mode="json")
                state["lifecycle_status"] = LifecycleStatus.FAILED_SAFE.value
                state["status"] = "FAILED_SAFE"
                state["error"] = (
                    "Workflow execution failed closed. Review protected service telemetry."
                )
                state["control_exception"] = control_exception
                state["control_exception_history"] = [
                    *state.get("control_exception_history", []),
                    control_exception,
                ]
                self.repository.save(case_id, state, None)
                self.repository.add_audit(
                    case_id,
                    "system",
                    "AIRO Case Coordinator",
                    "GRAPH_ERROR",
                    {"error_type": type(exc).__name__, "details_exposed": False},
                )
                raise

    def resume(self, case_id: str, decision: HumanDecision) -> dict[str, Any]:
        existing = self.repository.get(case_id)
        if not existing:
            raise KeyError(case_id)
        if not existing.get("pending_gate"):
            raise ValueError("The case is not waiting at a Human Gate.")
        state = existing["state"]
        pending_gate = existing["pending_gate"]
        if decision.decision_id in state.get("processed_decision_ids", []):
            raise ValueError("This human decision ID has already been processed.")
        if decision.case_id not in {None, case_id}:
            raise ValueError("Human decision Case ID does not match the active Case.")
        if decision.gate_id not in {None, pending_gate.get("gate_id")}:
            raise ValueError("Human decision Gate ID is stale or does not match.")
        current_version = int(state.get("case_state_version", 1))
        if decision.case_state_version not in {None, current_version}:
            raise ValueError("Human decision Case State version is stale.")
        if decision.rule_version not in {None, state.get("rule_version")}:
            raise ValueError("Human decision rule version is stale.")
        if decision.decision_authority != "AI Risk Oversight (AIRO)":
            raise ValueError("Human decision authority is not permitted.")
        decision.case_id = case_id
        decision.gate_id = pending_gate.get("gate_id")
        decision.governance_loop = (
            GovernanceLoop(pending_gate["governance_loop"])
            if pending_gate.get("governance_loop")
            else None
        )
        decision.case_state_version = current_version
        decision.rule_version = state.get("rule_version")
        allowed_actions = existing["pending_gate"].get("allowed_actions", [])
        if decision.action not in allowed_actions:
            raise ValueError(
                f"Action '{decision.action}' is not permitted at this gate. "
                f"Allowed actions: {', '.join(allowed_actions)}"
            )
        rationale_required = (
            existing["pending_gate"].get("rationale_required", {}).get(decision.action, False)
        )
        if rationale_required and not decision.rationale.strip():
            raise ValueError("This AIRO action requires a decision rationale.")
        if decision.action == "add_evidence" and not (
            decision.additional_evidence.strip() or decision.answer_updates
        ):
            raise ValueError("Add evidence or amend at least one questionnaire answer.")
        if decision.action == "edit_answers" and not decision.answer_updates:
            raise ValueError("Edit at least one questionnaire answer.")
        if decision.action == "amend_material_fact" and not (
            decision.additional_evidence.strip() or decision.answer_updates
        ):
            raise ValueError("Amend evidence or at least one questionnaire answer.")
        if decision.action == "override" and not (
            decision.override_band or decision.confirmed_teams is not None
        ):
            raise ValueError("An override must change the materiality band or 2LoD teams.")
        if decision.answer_updates:
            try:
                validated = Questionnaire.model_validate(
                    {**existing["state"].get("questionnaire", {}), **decision.answer_updates}
                )
                normalised = validated.model_dump()
                decision.answer_updates = {key: normalised[key] for key in decision.answer_updates}
            except ValidationError as exc:
                raise ValueError("Questionnaire updates are invalid.") from exc
        rationale_required = {
            "proceed_with_gap",
            "return_for_evidence",
            "return_for_review",
            "amend_material_fact",
            "override",
            "cancel_case",
        }
        if decision.action in rationale_required and not decision.rationale.strip():
            raise ValueError(f"A rationale is required for '{decision.action}'.")
        self.repository.add_audit(
            case_id,
            "human",
            decision.reviewer,
            "HUMAN_DECISION_SUBMITTED",
            {
                "gate_id": existing["pending_gate"].get("gate_id"),
                "action": decision.action,
                "rationale": decision.rationale,
                "answer_updates": decision.answer_updates,
                "override_band": decision.override_band,
                "confirmed_teams": decision.confirmed_teams,
            },
        )
        with self._run_lock:
            self.graph.invoke(
                Command(resume=decision.model_dump(mode="json")), self._config(case_id)
            )
            return self._save_snapshot(case_id, "GRAPH_RESUMED_OR_COMPLETED")

    def submit_external_event(self, case_id: str, event: ExternalEventSubmission) -> dict[str, Any]:
        existing = self.repository.get(case_id)
        if not existing:
            raise KeyError(case_id)
        state = existing["state"]
        for processed in state.get("processed_external_events", []):
            if processed.get("event_id") == event.event_id:
                result = self.get_case(case_id)
                result["event_submission"] = {
                    "status": "IDEMPOTENT_REPLAY",
                    "event_id": event.event_id,
                }
                return result
        expected = state.get("active_external_event")
        if not expected or expected.get("status") != "WAITING":
            raise ValueError("The Case is not waiting for an external event.")
        if event.case_id != case_id:
            raise ValueError("External event Case ID does not match.")
        if event.correlation_id != expected.get("correlation_id"):
            raise ValueError("External event correlation ID does not match.")
        permitted_event_types = {
            expected.get("event_type"),
            "external_response_received",
            "timeout",
        }
        if event.event_type not in permitted_event_types:
            raise ValueError("External event type is not expected.")
        if event.schema_version != expected.get("schema_version"):
            raise ValueError("External event schema version does not match.")
        if event.case_state_version != state.get("case_state_version", 1):
            raise ValueError("External event Case State version is stale.")
        if event.event_type != "timeout" and event.source != expected.get("expected_source"):
            raise ValueError("External event source is not expected.")
        if event.artifact_hash:
            calculated = hashlib.sha256(event.artifact_text.encode("utf-8")).hexdigest()
            if event.artifact_hash.lower() != calculated:
                raise ValueError("External event artifact integrity check failed.")
        self.repository.add_audit(
            case_id,
            "external_event",
            event.source,
            "EXTERNAL_EVENT_VALIDATED",
            {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "correlation_id": event.correlation_id,
                "schema_version": event.schema_version,
                "case_state_version": event.case_state_version,
            },
        )
        with self._run_lock:
            self.graph.invoke(Command(resume=event.model_dump()), self._config(case_id))
            result = self._save_snapshot(case_id, "GRAPH_RESUMED_BY_EXTERNAL_EVENT")
            result["event_submission"] = {
                "status": "ACCEPTED",
                "event_id": event.event_id,
            }
            return result

    def recover_control_exception(
        self, case_id: str, recovery: ControlRecoveryRequest
    ) -> dict[str, Any]:
        existing = self.repository.get(case_id)
        if not existing:
            raise KeyError(case_id)
        pending = existing.get("pending_gate") or {}
        if pending.get("gate_id") != "control_exception_review":
            raise ValueError("The Case is not waiting for Control Exception review.")
        if recovery.case_state_version != existing["state"].get("case_state_version", 1):
            raise ValueError("Control recovery Case State version is stale.")
        return self.resume(
            case_id,
            HumanDecision(
                decision_id=recovery.recovery_id,
                action=recovery.action,
                rationale=recovery.rationale,
                reviewer=recovery.reviewer,
                reviewer_role="AIRO Control Exception reviewer",
                case_id=case_id,
                gate_id="control_exception_review",
                governance_loop=GovernanceLoop.CONTROL_EXCEPTION_REVIEW,
                case_state_version=recovery.case_state_version,
                rule_version=existing["state"].get("rule_version"),
            ),
        )

    def get_case(self, case_id: str) -> dict[str, Any]:
        case = self.repository.get(case_id)
        if not case:
            raise KeyError(case_id)
        case["audit"] = self.repository.audit(case_id)
        return case

    def list_cases(self) -> list[dict[str, Any]]:
        return self.repository.list()

    def supervisor_decision(self, case_id: str) -> dict[str, Any]:
        case = self.get_case(case_id)
        # Always evaluate the authoritative state. A stored decision is retained
        # for audit/trace purposes but can predate a Gate or external-event pause.
        return self.policy_supervisor.supervise(case["state"]).model_dump(mode="json")

    def action_history(self, case_id: str) -> dict[str, Any]:
        case = self.get_case(case_id)
        state = case["state"]
        return {
            "case_id": case_id,
            "action_trace": state.get("agent_action_trace", []),
            "authorisations": state.get("action_authorisations", []),
            "tool_results": state.get("tool_results", []),
            "verification_results": state.get("verification_results", []),
            "transitions": state.get("transition_history", []),
            "human_decisions": state.get("human_decisions", []),
            "external_events": state.get("processed_external_events", []),
            "audit": case.get("audit", []),
        }

    def result_status(self, case_id: str) -> dict[str, Any]:
        state = self.get_case(case_id)["state"]
        return {
            "case_id": case_id,
            "current": state.get("current_authoritative_results", {}),
            "stale_outputs": state.get("stale_outputs", []),
            "superseded": state.get("superseded_results", []),
            "invalidations": state.get("invalidations", []),
        }

    def tool_metadata(self) -> list[dict[str, Any]]:
        return [item.model_dump(mode="json") for item in self.tool_registry.contracts()]

    def health(self) -> tuple[bool, str]:
        return self.llm.health()
