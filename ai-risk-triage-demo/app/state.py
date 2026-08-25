from __future__ import annotations

from typing import Any, TypedDict


class TriageState(TypedDict, total=False):
    # Identity and lifecycle
    case_id: str
    thread_id: str
    case_state_version: int
    lifecycle_status: str
    domain_phase: str
    # Compatibility projection for existing API/UI clients. Policy and graph
    # transitions use lifecycle_status/domain_phase as authoritative fields.
    status: str
    error: str
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
    candidate_facts: list[dict[str, Any]]

    # Evidence processing
    evidence_extraction: dict[str, Any]
    confirmed_facts: list[dict[str, Any]]
    evidence_claims: list[dict[str, Any]]
    mandatory_evidence_gaps: list[dict[str, Any]]
    evidence_conflicts: list[dict[str, Any]]
    llm_advisory_observations: list[dict[str, Any]]
    advisory_observations: list[dict[str, Any]]
    missing_information: list[str]
    inconsistencies: list[str]
    confirmed_exceptions: list[dict[str, Any]]
    open_issues: list[dict[str, Any]]
    evidence_request: list[str]

    # Agentic coordination
    task_plan: list[dict[str, Any]]
    open_objectives: list[dict[str, Any]]
    completed_objectives: list[dict[str, Any]]
    completed_nodes: list[str]
    recommended_next_action: dict[str, Any]
    action_plan: list[dict[str, Any]]
    pending_actions: list[str]
    completed_actions: list[str]
    failed_actions: list[str]
    prohibited_actions: list[str]
    current_action_proposal: dict[str, Any]
    policy_assessment: dict[str, Any]
    supervisor_decision: dict[str, Any]
    action_validation: dict[str, Any]
    current_action_authorisation: dict[str, Any]
    action_authorisations: list[dict[str, Any]]
    reassessment: dict[str, Any]
    router_invoked: bool
    deterministic_fallback_requested: bool
    rework_actions: list[str]
    current_tool_invocation: dict[str, Any]
    latest_tool_result: dict[str, Any]
    tool_results: list[dict[str, Any]]
    latest_verification: dict[str, Any]
    verification_results: list[dict[str, Any]]
    agent_action_trace: list[dict[str, Any]]
    tool_call_count: int
    max_tool_calls: int
    remaining_tool_calls: int
    max_evidence_cycles: int
    total_loop_count: int
    max_total_loops: int
    remaining_total_loops: int
    execution_budgets: dict[str, Any]
    retry_counts: dict[str, int]
    timeouts: dict[str, float]

    # Decision engines
    materiality_result: dict[str, Any]
    lod2_result: dict[str, Any]
    materiality_tool_record: dict[str, Any]
    lod2_tool_record: dict[str, Any]
    proposed_outcome: dict[str, Any]
    readiness_result: dict[str, Any]

    # Challenge and human governance
    exceptions: list[str]
    follow_up_questions: list[str]
    challenge_summary: str
    human_decisions: list[dict[str, Any]]
    autonomy_log: list[dict[str, Any]]
    current_gate: str | None
    active_governance_loop: str | None
    decision_authority: str
    processed_decision_ids: list[str]

    # Durable asynchronous coordination and safe exception handling
    expected_external_events: list[dict[str, Any]]
    active_external_event: dict[str, Any] | None
    processed_external_events: list[dict[str, Any]]
    control_exception: dict[str, Any] | None
    control_exception_history: list[dict[str, Any]]

    # Final output
    final_outcome: dict[str, Any]
    review_pack: dict[str, Any]
    publication_draft: dict[str, Any]
    publication_status: str
    invalidations: list[dict[str, Any]]
    superseded_results: list[dict[str, Any]]
    current_authoritative_results: dict[str, Any]
    stale_outputs: list[str]
    dependency_metadata: dict[str, list[str]]
    material_change_requires_airo_review: bool
    completion_evaluation: dict[str, Any]
    transition_history: list[dict[str, Any]]

    # Version and runtime evidence
    questionnaire_version: str
    rule_version: str
    workflow_version: str
    prompt_version: str
    policy_version: str
    tool_contract_version: str
    model_version: str
    version_manifest: dict[str, str]
    llm_runtime: dict[str, Any]
