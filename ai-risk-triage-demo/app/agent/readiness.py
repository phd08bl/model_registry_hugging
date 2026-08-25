from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from app.schemas import Questionnaire, ReadinessResult
from app.versions import QUESTIONNAIRE_VERSION, RULESET_VERSION


class ReadinessPolicy:
    """Deterministically prevents risk engines using incomplete or stale inputs."""

    @staticmethod
    def _open_issue_summaries(state: dict[str, Any], category: str) -> list[str]:
        return [
            str(issue.get("summary"))
            for issue in state.get("open_issues", [])
            if issue.get("category") == category and issue.get("status") == "open"
        ]

    def evaluate(self, state: dict[str, Any]) -> ReadinessResult:
        try:
            Questionnaire.model_validate(state.get("questionnaire", {}))
            questionnaire_valid = True
        except (ValidationError, TypeError):
            questionnaire_valid = False

        blocking_gaps = self._open_issue_summaries(state, "mandatory_evidence_gap")
        blocking_conflicts = self._open_issue_summaries(state, "inconsistency")
        if not state.get("open_issues"):
            blocking_gaps = list(state.get("missing_information", []))
            blocking_conflicts = list(state.get("inconsistencies", []))

        profile = state.get("autonomy_profile", "human_governed")
        questionnaire = state.get("questionnaire", {})
        material_confirmation_required = bool(
            profile == "human_governed"
            or questionnaire.get("sensitive_data")
            or questionnaire.get("customer_decisioning")
            or questionnaire.get("autonomous_actions")
            or questionnaire.get("critical_process_dependency")
            or blocking_conflicts
        )
        facts_requiring_confirmation = []
        if material_confirmation_required and not state.get("confirmed_facts"):
            facts_requiring_confirmation.append(
                "Material questionnaire and evidence facts require AIRO confirmation."
            )

        questionnaire_current = state.get("questionnaire_version") == QUESTIONNAIRE_VERSION
        rules_current = state.get("rule_version") == RULESET_VERSION
        stale_dependencies = sorted(
            set(state.get("stale_outputs", [])) & {"questionnaire", "confirmed_facts"}
        )
        ready = all(
            (
                questionnaire_valid,
                not blocking_gaps,
                not blocking_conflicts,
                not facts_requiring_confirmation,
                questionnaire_current,
                rules_current,
                not stale_dependencies,
            )
        )
        permitted = ["run_deterministic_engines"] if ready else []
        if blocking_gaps or blocking_conflicts:
            permitted.append("resolve_evidence")
        if facts_requiring_confirmation:
            permitted.append("request_material_fact_confirmation")
        if not questionnaire_current or not rules_current or stale_dependencies:
            permitted.append("enter_control_exception")
        return ReadinessResult(
            ready_for_engines=ready,
            blocking_gaps=blocking_gaps,
            blocking_conflicts=blocking_conflicts,
            facts_requiring_confirmation=facts_requiring_confirmation,
            permitted_next_actions=permitted,
            rationale=(
                "All current, confirmed inputs required by both deterministic engines are ready."
                if ready
                else "One or more deterministic readiness conditions block the risk engines."
            ),
            questionnaire_version_current=questionnaire_current,
            rule_version_current=rules_current,
            stale_dependencies=stale_dependencies,
        )
