from __future__ import annotations

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
    CreateCaseRequest,
    DemonstrationCase,
    HumanDecision,
    Questionnaire,
)
from app.versions import PROMPT_VERSION, QUESTIONNAIRE_VERSION, RULESET_VERSION, WORKFLOW_VERSION

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
            "status": "DRAFT",
            "autonomy_profile": assignment.effective_profile,
            "autonomy_assignment": assignment.model_dump(),
            "demo_scenario_id": demo.get("sample_id"),
            "demo_controls": (
                {"router_mode": demo.get("router_mode", "normal")} if demonstration else {}
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
            "evidence_claims": [],
            "mandatory_evidence_gaps": [],
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
            "action_plan": [],
            "pending_actions": [],
            "completed_actions": [],
            "failed_actions": [],
            "prohibited_actions": [],
            "agent_action_trace": [],
            "tool_call_count": 0,
            "max_tool_calls": max_tool_calls,
            "remaining_tool_calls": max_tool_calls,
            "max_evidence_cycles": self.policy_supervisor.max_evidence_cycles,
            "retry_counts": {},
            "timeouts": {},
            "invalidations": [],
            "superseded_results": [],
            "current_authoritative_results": {},
            "material_change_requires_airo_review": False,
            "decision_authority": "AI Risk Oversight (AIRO)",
            "questionnaire_version": QUESTIONNAIRE_VERSION,
            "rule_version": RULESET_VERSION,
            "workflow_version": WORKFLOW_VERSION,
            "prompt_version": PROMPT_VERSION,
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
        pending_gate = snapshot.interrupts[0].value if snapshot.interrupts else None
        state["current_gate"] = pending_gate.get("gate_id") if pending_gate else None
        if pending_gate:
            state["status"] = {
                "evidence_request": "AWAITING_INFORMATION",
                "input_confirmation": "AWAITING_INPUT_CONFIRMATION",
                "exception_resolution": "AWAITING_EXCEPTION_DECISION",
                "final_triage": "AWAITING_FINAL_DECISION",
                "publication": "READY_TO_PUBLISH",
            }.get(pending_gate.get("gate_id"), state.get("status", "AWAITING_HUMAN"))
        self.repository.save(case_id, state, pending_gate)
        self.repository.add_audit(
            case_id,
            "system",
            "AIRO Case Coordinator",
            action,
            {
                "status": state.get("status"),
                "pending_gate": pending_gate.get("gate_id") if pending_gate else None,
                "next_nodes": list(snapshot.next),
                "llm_runtime": state.get("llm_runtime", {}),
                "autonomy_assignment": state.get("autonomy_assignment", {}),
                "latest_action": state.get("current_action_proposal", {}),
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
                state["status"] = "ERROR"
                state["error"] = (
                    "Workflow execution failed closed. Review protected service telemetry."
                )
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
            self.graph.invoke(Command(resume=decision.model_dump()), self._config(case_id))
            return self._save_snapshot(case_id, "GRAPH_RESUMED_OR_COMPLETED")

    def get_case(self, case_id: str) -> dict[str, Any]:
        case = self.repository.get(case_id)
        if not case:
            raise KeyError(case_id)
        case["audit"] = self.repository.audit(case_id)
        return case

    def list_cases(self) -> list[dict[str, Any]]:
        return self.repository.list()

    def health(self) -> tuple[bool, str]:
        return self.llm.health()
