from __future__ import annotations

from typing import Any, TypedDict


class TriageState(TypedDict, total=False):
    # Identity and lifecycle
    case_id: str
    thread_id: str
    status: str
    autonomy_profile: str
    autonomy_assignment: dict[str, Any]
    demo_scenario_id: str | None
    demo_controls: dict[str, Any]
    sampling_key: str | None
    case_objective: dict[str, Any]
    completion_criteria: list[str]
    created_at: str
    updated_at: str

    # Inputs
    questionnaire: dict[str, Any]
    evidence_text: str
    evidence_cycle: int
    submitted_facts: list[dict[str, Any]]

    # Evidence processing
    evidence_extraction: dict[str, Any]
    confirmed_facts: list[dict[str, Any]]
    evidence_claims: list[dict[str, Any]]
    mandatory_evidence_gaps: list[dict[str, Any]]
    advisory_observations: list[dict[str, Any]]
    missing_information: list[str]
    inconsistencies: list[str]
    confirmed_exceptions: list[dict[str, Any]]
    open_issues: list[dict[str, Any]]
    evidence_request: list[str]

    # Agentic coordination
    task_plan: list[dict[str, Any]]
    completed_nodes: list[str]
    recommended_next_action: dict[str, Any]
    action_plan: list[dict[str, Any]]
    pending_actions: list[str]
    completed_actions: list[str]
    failed_actions: list[str]
    prohibited_actions: list[str]
    current_action_proposal: dict[str, Any]
    policy_assessment: dict[str, Any]
    action_validation: dict[str, Any]
    reassessment: dict[str, Any]
    router_invoked: bool
    current_tool_invocation: dict[str, Any]
    latest_tool_result: dict[str, Any]
    latest_verification: dict[str, Any]
    agent_action_trace: list[dict[str, Any]]
    tool_call_count: int
    max_tool_calls: int
    remaining_tool_calls: int
    max_evidence_cycles: int
    retry_counts: dict[str, int]
    timeouts: dict[str, float]

    # Decision engines
    materiality_result: dict[str, Any]
    lod2_result: dict[str, Any]
    proposed_outcome: dict[str, Any]

    # Challenge and human governance
    exceptions: list[str]
    follow_up_questions: list[str]
    challenge_summary: str
    human_decisions: list[dict[str, Any]]
    autonomy_log: list[dict[str, Any]]
    current_gate: str | None
    decision_authority: str

    # Final output
    final_outcome: dict[str, Any]
    review_pack: dict[str, Any]
    publication_draft: dict[str, Any]
    publication_status: str
    invalidations: list[dict[str, Any]]
    superseded_results: list[dict[str, Any]]
    current_authoritative_results: dict[str, Any]
    material_change_requires_airo_review: bool

    # Version and runtime evidence
    questionnaire_version: str
    rule_version: str
    workflow_version: str
    prompt_version: str
    llm_runtime: dict[str, Any]
