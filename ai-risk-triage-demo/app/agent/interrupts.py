from __future__ import annotations

from typing import Any

from app.engines.autonomy import GateEvaluation
from app.schemas import HumanInputRequirement
from app.versions import GATE_VERSION

QUESTIONNAIRE_LABELS = {
    "approved_pattern": "Approved pattern",
    "customer_facing": "Customer-facing use",
    "customer_decisioning": "Customer decisioning",
    "personal_data": "Personal data",
    "sensitive_data": "Sensitive data",
    "external_model_or_supplier": "External model or supplier",
    "autonomous_actions": "Autonomous actions",
    "critical_process_dependency": "Critical-process dependency",
    "human_review_of_outputs": "Human review of outputs",
}


class AIROInterruptController:
    """Builds consistent, evidence-linked governance interrupt contracts."""

    gate_version = GATE_VERSION

    @staticmethod
    def _issue_field(issue: str) -> tuple[str | None, bool | None]:
        lower = issue.lower()
        if "personal data" in lower or any(term in lower for term in ("names", "email")):
            return "personal_data", True
        if "sensitive data" in lower:
            return "sensitive_data", True
        if "supplier" in lower or "external model" in lower:
            return "external_model_or_supplier", True
        if "autonomous" in lower:
            return "autonomous_actions", True
        if "human review" in lower and "fully automated" in lower:
            return "human_review_of_outputs", False
        return None, None

    @staticmethod
    def _matching_citations(issue: str, facts: list[dict[str, Any]]) -> list[dict[str, Any]]:
        terms = {
            word.strip(".,:;()") for word in issue.lower().split() if len(word.strip(".,:;()")) >= 5
        }
        matches = [
            fact for fact in facts if terms.intersection(str(fact.get("claim", "")).lower().split())
        ]
        selected = matches or facts[:2]
        return [
            {
                "claim": fact.get("claim"),
                "source": fact.get("source", "submitted_evidence"),
                "line_refs": fact.get("line_refs", []),
            }
            for fact in selected[:3]
        ]

    @staticmethod
    def _questionnaire_review_items(questionnaire: dict[str, Any]) -> list[str]:
        return [
            f"{label}: {'Yes' if questionnaire.get(field) else 'No'}"
            for field, label in QUESTIONNAIRE_LABELS.items()
        ]

    @classmethod
    def _required_inputs(
        cls,
        state: dict[str, Any],
        evaluation: GateEvaluation,
        context: dict[str, Any],
    ) -> list[dict[str, Any]]:
        gate_id = evaluation.gate_id
        questionnaire = state.get("questionnaire", {})
        facts = state.get("evidence_extraction", {}).get("facts", [])
        requirements: list[HumanInputRequirement] = []

        if gate_id == "evidence_request":
            missing = list(context.get("missing_information", []))
            conflicts = list(context.get("inconsistencies", []))
            questions = list(context.get("draft_questions", []))
            for index, issue in enumerate([*missing, *conflicts]):
                is_conflict = index >= len(missing)
                field, suggested = cls._issue_field(issue)
                question = questions[index] if index < len(questions) else issue
                artifacts = [question]
                if field == "personal_data":
                    artifacts.append("Approved privacy classification or assessment")
                requirements.append(
                    HumanInputRequirement(
                        requirement_id=f"evidence-{index + 1}",
                        kind=("evidence_conflict" if is_conflict else "mandatory_evidence_gap"),
                        title="Resolve evidence conflict" if is_conflict else "Provide evidence",
                        description=issue,
                        field=field,
                        current_value=questionnaire.get(field) if field else "Not provided",
                        evidence_supported_value=suggested if is_conflict else None,
                        suggested_value=suggested,
                        required_response=question,
                        required_artifacts=artifacts,
                        citations=cls._matching_citations(issue, facts),
                        accepted_resolutions=[
                            "add_evidence",
                            "proceed_with_gap",
                            "cancel_case",
                        ],
                    )
                )
            if not requirements:
                verification_issues = [
                    item
                    for item in state.get("open_issues", [])
                    if item.get("status") == "open"
                    and item.get("category") in {"verification", "security"}
                ]
                for index, issue in enumerate(verification_issues):
                    requirements.append(
                        HumanInputRequirement(
                            requirement_id=f"verification-{index + 1}",
                            kind="verification_failure",
                            title="Resolve verification failure",
                            description=issue.get("summary", "A governed result was not verified."),
                            required_response=(
                                "Provide corrected evidence or explicitly accept the "
                                "unresolved gap."
                            ),
                            review_items=[issue.get("category", "verification")],
                            accepted_resolutions=[
                                "add_evidence",
                                "proceed_with_gap",
                                "cancel_case",
                            ],
                        )
                    )
        elif gate_id == "input_confirmation":
            accepted = context.get("airo_accepted_evidence_issues", [])
            requirements.append(
                HumanInputRequirement(
                    requirement_id="material-input-confirmation",
                    kind="fact_confirmation",
                    title="Confirm the material input facts",
                    description=(
                        "These structured questionnaire facts will become the authoritative "
                        "inputs to the deterministic materiality and 2LoD engines."
                    ),
                    required_response=(
                        "Confirm the facts, edit an incorrect answer, return for more evidence, "
                        "or cancel the Case."
                    ),
                    current_value=(
                        f"Questionnaire version {state.get('questionnaire_version', 1)}"
                    ),
                    review_items=[
                        *cls._questionnaire_review_items(questionnaire),
                        *[f"Accepted residual issue: {item.get('summary')}" for item in accepted],
                    ],
                    accepted_resolutions=[
                        "confirm",
                        "edit_answers",
                        "return_for_evidence",
                        "cancel_case",
                    ],
                )
            )
        elif gate_id == "exception_resolution":
            exceptions = list(context.get("exceptions", []))
            follow_ups = list(context.get("follow_up_questions", []))
            items = exceptions or [
                context.get("challenge_summary") or "Review the challenge result."
            ]
            for index, item in enumerate(items):
                requirements.append(
                    HumanInputRequirement(
                        requirement_id=f"exception-{index + 1}",
                        kind="exception_judgement",
                        title="Interpret the recorded exception",
                        description=item,
                        required_response=(
                            "Record whether the Case may proceed, needs corrected facts or "
                            "additional evidence, or must be cancelled."
                        ),
                        review_items=follow_ups,
                        accepted_resolutions=[
                            "proceed",
                            "edit_answers",
                            "return_for_evidence",
                            "cancel_case",
                        ],
                    )
                )
        elif gate_id == "final_triage":
            proposed = context.get("proposed_outcome", {})
            requirements.extend(
                [
                    HumanInputRequirement(
                        requirement_id="final-materiality",
                        kind="final_decision",
                        title="Decide the final materiality band",
                        description="Review the deterministic materiality proposal and rationale.",
                        current_value=proposed.get("materiality_band", "Not proposed"),
                        required_response=(
                            "Confirm the proposal or record an accountable override."
                        ),
                        review_items=[
                            str(item.get("rationale", item))
                            for item in context.get("materiality", {}).get("factors", [])
                        ],
                        accepted_resolutions=["confirm", "override", "return_for_review"],
                    ),
                    HumanInputRequirement(
                        requirement_id="final-lod2",
                        kind="final_decision",
                        title="Decide second-line engagement",
                        description=("Review the independent deterministic 2LoD trigger proposal."),
                        current_value=proposed.get("triggered_2lod_teams", []),
                        required_response=(
                            "Confirm the proposed teams or record an accountable override."
                        ),
                        review_items=[
                            str(item.get("rationale", item))
                            for item in context.get("lod2", {}).get("triggers", [])
                        ],
                        accepted_resolutions=["confirm", "override", "return_for_review"],
                    ),
                ]
            )
        elif gate_id == "publication":
            draft = context.get("publication_draft", {})
            requirements.append(
                HumanInputRequirement(
                    requirement_id="publication-record",
                    kind="publication_approval",
                    title="Approve the controlled local publication",
                    description=(
                        "Verify that the draft reflects the current AIRO decision and remains "
                        "a local demonstration record."
                    ),
                    current_value=(
                        draft.get("title") or draft.get("target") or "Local demo publication draft"
                    ),
                    required_response=(
                        "Approve, save the draft, amend a material fact, or cancel publication."
                    ),
                    review_items=[
                        "No production Confluence, email or SharePoint write is enabled.",
                        "Final outcome: "
                        + str(
                            context.get("current_final_outcome", {}).get("status", "Not recorded")
                        ),
                    ],
                    accepted_resolutions=[
                        "approve",
                        "save_draft",
                        "amend_material_fact",
                        "cancel_case",
                    ],
                )
            )
        elif gate_id == "control_exception_review":
            exception = context.get("control_exception", {})
            requirements.append(
                HumanInputRequirement(
                    requirement_id="control-recovery",
                    kind="control_recovery",
                    title="Choose a safe recovery or terminal action",
                    description=exception.get("reason", "Automated continuation is unavailable."),
                    current_value=exception.get("code", "CONTROL_EXCEPTION"),
                    required_response=(
                        "Select only an allowed recovery and record the accountable rationale."
                    ),
                    review_items=[
                        f"Failed action: {exception.get('failed_action') or 'Not recorded'}",
                        *[
                            f"{key.replace('_', ' ')}: {value}"
                            for key, value in exception.get("budget_state", {}).items()
                        ],
                    ],
                    accepted_resolutions=list(exception.get("allowed_recovery_actions", [])),
                )
            )

        return [item.model_dump(mode="json") for item in requirements]

    @staticmethod
    def _recommended_action(evaluation: GateEvaluation, context: dict[str, Any]) -> str | None:
        if evaluation.gate_id == "evidence_request":
            return "add_evidence"
        if evaluation.gate_id == "input_confirmation" and not (
            context.get("remaining_gaps") or context.get("remaining_conflicts")
        ):
            return "confirm"
        return None

    @staticmethod
    def _action_impacts(
        evaluation: GateEvaluation,
        allowed_actions: list[str],
        effects: dict[str, str],
        rationale_required: dict[str, bool],
    ) -> dict[str, dict[str, Any]]:
        next_steps = {
            "evidence_request": {
                "add_evidence": (
                    "Re-run affected evidence checks; continue to Gate 2 only when ready."
                ),
                "proceed_with_gap": ("Continue to Gate 2 with a recorded residual risk condition."),
                "cancel_case": "Close without a risk approval.",
            },
            "input_confirmation": {
                "confirm": "Run readiness, materiality and independent 2LoD engines.",
                "edit_answers": "Return to selective evidence preparation.",
                "return_for_evidence": "Create a new Gate 1 evidence request.",
                "cancel_case": "Close without a risk approval.",
            },
            "exception_resolution": {
                "proceed": "Generate the review pack and continue to final AIRO triage.",
                "edit_answers": "Invalidate affected results and selectively replan.",
                "return_for_evidence": "Create a new Gate 1 evidence request.",
                "cancel_case": "Close without a risk approval.",
            },
            "final_triage": {
                "confirm": (
                    "Record the final AIRO outcome and prepare the local publication draft."
                ),
                "override": ("Record the override, then prepare the local publication draft."),
                "return_for_review": "Return to Gate 3 without a final approval.",
                "cancel_case": "Close without a risk approval.",
            },
            "publication": {
                "approve": (
                    "Publish the idempotent local demonstration record and evaluate completion."
                ),
                "save_draft": "Remain at Gate 5 with no publication approval.",
                "amend_material_fact": (
                    "Invalidate affected decisions/results and selectively replan."
                ),
                "cancel_case": "Close without publishing.",
            },
            "control_exception_review": {
                "retry": "Retry the failed objective within remaining budgets.",
                "deterministic_fallback": (
                    "Resume with the supervisor-prioritised deterministic fallback."
                ),
                "wait_external": "Create a durable external-event wait.",
                "cancel": "Cancel without a risk decision.",
                "fail_safe": "End workflow execution as failed safe.",
            },
        }
        required_fields = {
            "add_evidence": ["additional_evidence_or_questionnaire_update"],
            "edit_answers": ["questionnaire_update"],
            "amend_material_fact": ["additional_evidence_or_questionnaire_update"],
            "override": ["materiality_or_2lod_override"],
        }
        caution_actions = {
            "proceed_with_gap",
            "return_for_evidence",
            "return_for_review",
            "amend_material_fact",
            "override",
            "cancel_case",
            "cancel",
            "fail_safe",
        }
        gate_steps = next_steps.get(evaluation.gate_id, {})
        return {
            action: {
                "effect": effects[action],
                "rationale_required": rationale_required[action],
                "required_fields": required_fields.get(action, []),
                "will_change": (
                    ["Questionnaire/evidence version", "Only dependency-affected outputs"]
                    if action in {"add_evidence", "edit_answers", "amend_material_fact"}
                    else ["Human decision and audit history"]
                ),
                "will_rerun": (
                    ["Policy-selected evidence checks and dependent deterministic engines"]
                    if action in {"add_evidence", "edit_answers", "amend_material_fact"}
                    else []
                ),
                "will_remain_current": ["Unrelated verified results when dependency rules permit"],
                "next_step": gate_steps.get(action, "Apply the governed transition."),
                "tone": "caution" if action in caution_actions else "primary",
            }
            for action in allowed_actions
        }

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
        rationale_required = {
            action: action
            in {
                "proceed_with_gap",
                "proceed",
                "return_for_evidence",
                "return_for_review",
                "amend_material_fact",
                "override",
                "cancel_case",
                "cancel",
                "fail_safe",
            }
            for action in allowed_actions
        }
        required_inputs = self._required_inputs(state, evaluation, context)
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
            "rationale_required": rationale_required,
            "required_inputs": required_inputs,
            "blocking_item_count": sum(
                1 for item in required_inputs if item.get("blocking", False)
            ),
            "recommended_action": self._recommended_action(evaluation, context),
            "action_impacts": self._action_impacts(
                evaluation,
                allowed_actions,
                effects,
                rationale_required,
            ),
            "decision_authority": "AI Risk Oversight (AIRO)",
            "context": context,
            "autonomy": evaluation.to_dict(),
            "governance_message": (
                "The Coordinator is paused. AIRO must record the accountable decision."
            ),
        }
