from __future__ import annotations

from typing import Any


def build_review_pack(state: dict[str, Any]) -> dict[str, Any]:
    questionnaire = state.get("questionnaire", {})
    materiality = state.get("materiality_result", {})
    lod2 = state.get("lod2_result", {})
    return {
        "title": f"AIRO Risk Triage Review Pack — {questionnaire.get('use_case_name', state['case_id'])}",
        "case_id": state["case_id"],
        "case_objective": state.get("case_objective", {}),
        "completion_criteria": state.get("completion_criteria", []),
        "use_case_overview": {
            "purpose": questionnaire.get("purpose"),
            "business_owner": questionnaire.get("business_owner"),
            "users": questionnaire.get("users"),
            "approved_pattern": questionnaire.get("approved_pattern"),
        },
        "proposed_materiality": materiality,
        "proposed_2lod_engagement": lod2,
        "evidence_summary": state.get("evidence_extraction", {}),
        "mandatory_evidence_gaps": state.get("mandatory_evidence_gaps", []),
        "advisory_observations": state.get("advisory_observations", []),
        "inconsistencies": state.get("inconsistencies", []),
        "open_issues": state.get("open_issues", []),
        "exceptions": state.get("exceptions", []),
        "follow_up_questions": state.get("follow_up_questions", []),
        "human_decisions": state.get("human_decisions", []),
        "final_outcome": state.get("final_outcome", {}),
        "autonomy_assignment": state.get("autonomy_assignment", {}),
        "agent_action_trace": state.get("agent_action_trace", []),
        "invalidations": state.get("invalidations", []),
        "superseded_results": state.get("superseded_results", []),
        "versions": {
            "questionnaire": state.get("questionnaire_version"),
            "materiality_rules": materiality.get("rule_version"),
            "2lod_rules": lod2.get("rule_version"),
            "workflow": state.get("workflow_version"),
            "prompt": state.get("prompt_version"),
            "llm": state.get("llm_runtime", {}),
        },
        "governance_statement": (
            "The Coordinator prepared this proposal. AIRO retains responsibility for review, "
            "challenge, amendment, override and the final triage outcome."
        ),
    }
