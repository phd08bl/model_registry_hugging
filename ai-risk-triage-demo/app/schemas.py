from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator

from app.versions import CASE_OBJECTIVE_VERSION

MaterialityBand = Literal["negligible", "minor", "moderate", "material", "severe"]
AutonomyProfile = Literal[
    "human_governed",
    "conditional_review",
    "exception_based",
    "straight_through",
    "straight_through_demo",
]


class LifecycleStatus(StrEnum):
    """Authoritative operational lifecycle, separate from risk-domain progress."""

    NEW = "NEW"
    OPEN = "OPEN"
    WORKING = "WORKING"
    AWAITING_HUMAN = "AWAITING_HUMAN"
    AWAITING_EXTERNAL_EVENT = "AWAITING_EXTERNAL_EVENT"
    CONTROL_EXCEPTION = "CONTROL_EXCEPTION"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    FAILED_SAFE = "FAILED_SAFE"


class DomainPhase(StrEnum):
    """Risk-triage domain phase; never overloaded with lifecycle state."""

    INTAKE = "INTAKE"
    EVIDENCE_REVIEW = "EVIDENCE_REVIEW"
    INPUT_CONFIRMATION = "INPUT_CONFIRMATION"
    ASSESSMENT = "ASSESSMENT"
    CHALLENGE = "CHALLENGE"
    FINAL_DECISION = "FINAL_DECISION"
    PUBLICATION = "PUBLICATION"


class GovernanceLoop(StrEnum):
    EVIDENCE_RESOLUTION = "EVIDENCE_RESOLUTION"
    MATERIAL_FACT_CONFIRMATION = "MATERIAL_FACT_CONFIRMATION"
    EXCEPTION_INTERPRETATION = "EXCEPTION_INTERPRETATION"
    FINAL_TRIAGE_DECISION = "FINAL_TRIAGE_DECISION"
    PUBLICATION_APPROVAL = "PUBLICATION_APPROVAL"
    CONTROL_EXCEPTION_REVIEW = "CONTROL_EXCEPTION_REVIEW"


class AuthorityClass(StrEnum):
    READ_ONLY = "READ_ONLY"
    ADVISORY_PROCESSING = "ADVISORY_PROCESSING"
    REVERSIBLE_PREPARATION = "REVERSIBLE_PREPARATION"
    PROTECTED_DECISION_SUPPORT = "PROTECTED_DECISION_SUPPORT"
    EXTERNAL_DRAFT = "EXTERNAL_DRAFT"
    CONSEQUENTIAL_EXTERNAL_ACTION = "CONSEQUENTIAL_EXTERNAL_ACTION"


class VerificationStatus(StrEnum):
    VERIFIED = "VERIFIED"
    VERIFIED_WITH_LIMITATIONS = "VERIFIED_WITH_LIMITATIONS"
    ADVISORY_ONLY = "ADVISORY_ONLY"
    REJECTED = "REJECTED"
    EXECUTION_FAILED = "EXECUTION_FAILED"


CASE_OBJECTIVE_STATEMENT = (
    "Prepare a complete, transparent and evidence-linked risk-triage proposal for AIRO "
    "review, without making or changing the final AIRO risk decision."
)
CASE_COMPLETION_CRITERIA = (
    "Submitted and AIRO-confirmed facts are distinguishable and evidence-linked.",
    "Mandatory evidence gaps, inconsistencies and exceptions are resolved or accepted by AIRO.",
    "Approved deterministic materiality and 2LoD engines have produced versioned proposals.",
    "Tool and LLM outputs have verification records and limitations.",
    "Every mandatory AIRO Gate has an accountable decision.",
    "The review pack contains only current authoritative results and preserves superseded history.",
)


class Questionnaire(BaseModel):
    model_config = {"extra": "forbid"}

    use_case_name: str = Field(min_length=3)
    purpose: str = Field(min_length=10)
    business_owner: str = Field(min_length=2)
    users: str = "Internal colleagues"
    approved_pattern: bool = False
    customer_facing: bool = False
    customer_decisioning: bool = False
    personal_data: bool = False
    sensitive_data: bool = False
    external_model_or_supplier: bool = False
    autonomous_actions: bool = False
    critical_process_dependency: bool = False
    human_review_of_outputs: bool = True
    financial_impact: Literal["low", "medium", "high"] = "low"

    @model_validator(mode="after")
    def sensitive_data_requires_personal_data(self) -> Questionnaire:
        if self.sensitive_data:
            self.personal_data = True
        return self


class CreateCaseRequest(BaseModel):
    model_config = {"extra": "forbid"}

    questionnaire: Questionnaire
    evidence_text: str = ""


class DemoCaseFixture(CreateCaseRequest):
    """Governed fixture metadata kept out of the normal case-creation contract."""

    demo_pattern_id: str
    autonomy_profile: AutonomyProfile


class DemonstrationControls(BaseModel):
    """Protected mock/demo controls unavailable through normal case creation."""

    model_config = {"extra": "forbid"}

    router_mode: Literal["normal", "low_confidence", "non_allowlisted_tool"] = "normal"
    tool_result_mode: Literal["normal", "malformed_output"] = "normal"
    sampling_key: str | None = None
    max_tool_calls: int | None = Field(default=None, ge=1, le=20)


class DemonstrationCase(BaseModel):
    """Typed explanatory metadata kept separate from authoritative case state."""

    model_config = {"extra": "forbid"}

    sample_id: str = Field(pattern=r"^[a-z0-9_]+$")
    title: str
    short_description: str
    category: Literal[
        "featured_cases",
        "progressive_automation",
        "advanced_controls",
    ]
    featured_case_number: int | None = Field(default=None, ge=1, le=8)
    featured_case_name: str | None = None
    learning_objectives: list[str] = Field(min_length=1)
    initial_submission: CreateCaseRequest
    governed_pattern_id: str
    expected_assigned_profile: AutonomyProfile
    expected_approved_maximum_profile: AutonomyProfile
    expected_profile_rationale_contains: list[str] = Field(default_factory=list)
    expected_router_actions: list[ActionType] = Field(default_factory=list)
    expected_tools: list[ToolIdentifier] = Field(default_factory=list)
    expected_verification_statuses: list[
        Literal["accepted", "advisory", "retry", "escalate", "rejected"]
    ] = Field(default_factory=list)
    expected_gates: list[str] = Field(default_factory=list)
    expected_governance_loops: list[GovernanceLoop] = Field(default_factory=list)
    expected_external_event_type: str | None = None
    expected_exceptions: list[str] = Field(default_factory=list)
    expected_path: list[str] = Field(default_factory=list)
    expected_materiality_band: MaterialityBand | None = None
    expected_2lod_teams: list[str] = Field(default_factory=list)
    expected_final_status: str | None = None
    likely_airo_attention: str
    interactive_steps: list[str] = Field(min_length=1)
    demo_controls: DemonstrationControls = Field(default_factory=DemonstrationControls)

    @model_validator(mode="after")
    def identifiers_and_title_match(self) -> DemonstrationCase:
        if self.sample_id != self.governed_pattern_id:
            raise ValueError("Sample and governed-pattern identifiers must match.")
        if self.title != self.initial_submission.questionnaire.use_case_name:
            raise ValueError("Demonstration title must match the submitted use-case name.")
        if (self.featured_case_number is None) != (self.featured_case_name is None):
            raise ValueError("Featured Case number and name must be supplied together.")
        if self.featured_case_number is not None and self.category != "featured_cases":
            raise ValueError("Numbered featured Cases must use the featured_cases category.")
        return self

    @property
    def questionnaire(self) -> Questionnaire:
        return self.initial_submission.questionnaire

    @property
    def evidence_text(self) -> str:
        return self.initial_submission.evidence_text

    @property
    def demo_pattern_id(self) -> str:
        return self.governed_pattern_id

    @property
    def autonomy_profile(self) -> AutonomyProfile:
        """Compatibility alias for existing callers; this is expected metadata only."""

        return self.expected_approved_maximum_profile


class CaseObjective(BaseModel):
    """Immutable mission boundary for every Coordinator case."""

    model_config = {"frozen": True}

    statement: str
    completion_criteria: tuple[str, ...]
    version: str = CASE_OBJECTIVE_VERSION


class ActionType(StrEnum):
    EXTRACT_SUBMITTED_EVIDENCE = "extract_submitted_evidence"
    CHECK_QUESTIONNAIRE_EVIDENCE_CONSISTENCY = "check_questionnaire_evidence_consistency"
    CHECK_RAG_EVIDENCE = "check_rag_evidence"
    CHECK_AGENTIC_AI_AUTONOMY = "check_agentic_ai_autonomy"
    CHECK_SUPPLIER_EVIDENCE = "check_supplier_evidence"
    VERIFY_CITATIONS = "verify_citations"
    RUN_MATERIALITY_ENGINE = "run_materiality_engine"
    RUN_2LOD_ENGINE = "run_2lod_engine"
    CHALLENGE_ASSESSMENT = "challenge_assessment"
    GENERATE_REVIEW_PACK = "generate_review_pack"
    ESCALATE_TO_AIRO = "escalate_to_airo"


class ToolIdentifier(StrEnum):
    EVIDENCE_EXTRACTOR = "evidence_extractor"
    EVIDENCE_CONSISTENCY_CHECKER = "evidence_consistency_checker"
    RAG_EVIDENCE_CHECKER = "rag_evidence_checker"
    AGENTIC_AUTONOMY_CHECKER = "agentic_ai_autonomy_checker"
    SUPPLIER_EVIDENCE_CHECKER = "supplier_evidence_checker"
    CHALLENGE_ASSESSOR = "challenge_assessor"
    CITATION_VERIFIER = "citation_verifier"
    MATERIALITY_ENGINE = "materiality_engine"
    LOD2_TRIGGER_ENGINE = "lod2_trigger_engine"
    REVIEW_PACK_GENERATOR = "review_pack_generator"


class ActionProposal(BaseModel):
    model_config = {"extra": "forbid"}

    selected_action: ActionType
    selected_tool: ToolIdentifier | None = None
    reason: str = Field(min_length=1, max_length=2000)
    inputs_required: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    human_review_recommended: bool = False
    human_review_required: bool = False

    @model_validator(mode="after")
    def align_human_review_flags(self) -> ActionProposal:
        """Retain the old field while exposing the target recommendation contract."""

        if self.human_review_required or self.human_review_recommended:
            self.human_review_required = True
            self.human_review_recommended = True
        return self


class ExecutionBudgets(BaseModel):
    model_config = {"extra": "forbid"}

    maximum_tool_calls: int = Field(ge=0)
    remaining_tool_calls: int = Field(ge=0)
    maximum_retries: int = Field(ge=0)
    remaining_retries: int = Field(ge=0)
    maximum_evidence_cycles: int = Field(ge=0)
    remaining_evidence_cycles: int = Field(ge=0)
    maximum_total_loops: int = Field(ge=1)
    remaining_total_loops: int = Field(ge=0)


class SupervisorDecision(BaseModel):
    """Deterministic whole-Case policy decision; never populated by an LLM."""

    model_config = {"extra": "forbid"}

    policy_version: str
    allowed_actions: list[ActionType] = Field(default_factory=list)
    prohibited_actions: list[str] = Field(default_factory=list)
    allowed_tools: list[ToolIdentifier] = Field(default_factory=list)
    mandatory_action: ActionType | None = None
    llm_recommender_permitted: bool = False
    human_decision_required: bool = False
    active_governance_loop: GovernanceLoop | None = None
    governance_reason: str | None = None
    external_event_required: bool = False
    expected_event_type: str | None = None
    ready_for_deterministic_engines: bool = False
    external_write_permitted: bool = False
    remaining_tool_calls: int = Field(ge=0)
    remaining_retries: int = Field(ge=0)
    remaining_evidence_cycles: int = Field(ge=0)
    remaining_total_loops: int = Field(ge=0)
    effective_automation_profile: AutonomyProfile
    completion_candidate: bool = False
    control_exception: bool = False
    control_exception_reason: str | None = None
    rationale: str


class ActionAuthorisation(BaseModel):
    model_config = {"extra": "forbid"}

    authorisation_id: str
    action: str
    tool: ToolIdentifier | None = None
    decision: Literal["AUTHORISED", "REJECTED", "HUMAN_AUTHORITY_REQUIRED"]
    reason: str
    checks: dict[str, bool] = Field(default_factory=dict)
    policy_version: str
    case_state_version: int = Field(ge=1)
    rule_version: str
    timestamp: str


class ToolContract(BaseModel):
    model_config = {"extra": "forbid"}

    tool_id: ToolIdentifier
    version: str
    purpose: str
    input_schema: str
    output_schema: str
    permission: Literal["read_only", "advisory", "verification", "deterministic", "write"]
    risk_classification: Literal["low", "medium", "high"]
    timeout_seconds: float = Field(gt=0)
    max_retries: int = Field(ge=0, le=3)
    idempotency_required: bool
    human_approval_required: bool
    allowed_profiles: set[AutonomyProfile]
    implementation_status: Literal["implemented", "mocked", "future_adapter"]
    authority_class: AuthorityClass
    data_permissions: list[str] = Field(default_factory=list)
    read_only: bool
    result_verifier: str
    owner: str


class ToolInvocation(BaseModel):
    model_config = {"extra": "forbid"}

    invocation_id: str
    case_id: str
    action: (
        ActionType
        | Literal[
            "run_materiality_engine",
            "run_2lod_engine",
            "generate_review_pack",
            "challenge_assessment",
        ]
    )
    tool_id: ToolIdentifier
    tool_version: str
    case_state_version: int = Field(default=1, ge=1)
    rule_version: str = "unknown"
    inputs: dict[str, Any]
    input_references: list[str] = Field(default_factory=list)
    idempotency_key: str
    state_fingerprint: str = ""
    approved_by: str | None = None


class ToolResult(BaseModel):
    model_config = {"extra": "forbid"}
    invocation_id: str
    case_id: str
    tool_id: ToolIdentifier
    tool_version: str
    case_state_version: int = Field(default=1, ge=1)
    rule_version: str = "unknown"
    state_fingerprint: str = ""
    status: Literal["succeeded", "failed", "prohibited"]
    output: dict[str, Any] = Field(default_factory=dict)
    source_references: list[str] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    advisory: bool = False
    error: str | None = None
    retry_count: int = Field(default=0, ge=0)
    duration_ms: float = Field(default=0, ge=0)
    timed_out: bool = False
    idempotent_replay: bool = False


class VerificationResult(BaseModel):
    verified: bool
    disposition: Literal["accepted", "advisory", "retry", "escalate", "rejected"]
    status: VerificationStatus | None = None
    checks: dict[str, bool] = Field(default_factory=dict)
    limitations: list[str] = Field(default_factory=list)
    issues: list[str] = Field(default_factory=list)
    label: str | None = None

    @model_validator(mode="after")
    def derive_status(self) -> VerificationResult:
        if self.status is not None:
            return self
        if self.disposition == "accepted":
            self.status = VerificationStatus.VERIFIED
        elif self.disposition == "advisory":
            self.status = (
                VerificationStatus.VERIFIED_WITH_LIMITATIONS
                if self.verified
                else VerificationStatus.ADVISORY_ONLY
            )
        elif self.disposition == "retry":
            self.status = VerificationStatus.EXECUTION_FAILED
        else:
            self.status = VerificationStatus.REJECTED
        return self


class OpenIssue(BaseModel):
    issue_id: str
    category: Literal[
        "mandatory_evidence_gap",
        "advisory_observation",
        "inconsistency",
        "confirmed_exception",
        "security",
        "verification",
    ]
    summary: str
    status: Literal["open", "resolved", "accepted"] = "open"
    owner: str = "AIRO"
    source_references: list[str] = Field(default_factory=list)
    advisory: bool = False


class AgentActionTrace(BaseModel):
    trace_id: str
    occurred_at: str
    proposal: ActionProposal
    invocation: ToolInvocation | None = None
    result: ToolResult | None = None
    verification: VerificationResult | None = None
    policy_version: str
    autonomy_profile: AutonomyProfile
    remaining_tool_calls: int
    rationale: str
    selection_source: Literal["llm_router", "deterministic_policy", "fallback"]
    observed_state: dict[str, Any] = Field(default_factory=dict)
    supervisor_decision: dict[str, Any] = Field(default_factory=dict)
    authorisation: ActionAuthorisation | None = None
    state_changes: list[str] = Field(default_factory=list)
    invalidated_outputs: list[str] = Field(default_factory=list)
    transition_decision: str | None = None
    stategraph_node: str
    tool_contract: ToolContract | None = None
    state_diff: dict[str, dict[str, Any]] = Field(default_factory=dict)
    next_transition: str


class StateInvalidation(BaseModel):
    invalidation_id: str
    invalidated_result: str
    previous_version: str | None = None
    reason: str
    triggering_change: str
    affected_dependencies: list[str] = Field(default_factory=list)
    replacement_required: bool = True
    replacement_result: str | None = None
    material_change: bool = False
    previous_approval_remains_effective: bool = True
    invalidated_at: str


class ReadinessResult(BaseModel):
    model_config = {"extra": "forbid"}

    ready_for_engines: bool
    blocking_gaps: list[str] = Field(default_factory=list)
    blocking_conflicts: list[str] = Field(default_factory=list)
    facts_requiring_confirmation: list[str] = Field(default_factory=list)
    permitted_next_actions: list[str] = Field(default_factory=list)
    rationale: str
    questionnaire_version_current: bool = True
    rule_version_current: bool = True
    stale_dependencies: list[str] = Field(default_factory=list)


class ExternalEventExpectation(BaseModel):
    model_config = {"extra": "forbid"}

    event_type: str
    case_id: str
    correlation_id: str
    expected_source: str
    schema_version: str
    due_at: str
    timeout_action: str
    case_state_version: int = Field(ge=1)
    status: Literal["WAITING", "RECEIVED", "TIMED_OUT", "CANCELLED"] = "WAITING"


class ExternalEventSubmission(BaseModel):
    model_config = {"extra": "forbid"}

    event_id: str = Field(default_factory=lambda: f"EVT-{uuid4().hex[:12].upper()}")
    event_type: str
    case_id: str
    correlation_id: str
    source: str
    schema_version: str = "demo-external-event-1.0"
    case_state_version: int = Field(ge=1)
    artifact_text: str = Field(default="", max_length=30000)
    artifact_hash: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    occurred_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())

    @model_validator(mode="after")
    def evidence_event_requires_content(self) -> ExternalEventSubmission:
        if (
            self.event_type
            in {
                "stakeholder_evidence_received",
                "external_response_received",
            }
            and not self.artifact_text.strip()
        ):
            raise ValueError("Evidence-response events require artifact text.")
        return self


class ControlException(BaseModel):
    model_config = {"extra": "forbid"}

    exception_id: str
    code: str
    reason: str
    failed_action: str | None = None
    failed_tool: str | None = None
    recoverable: bool
    retry_count: int = Field(ge=0)
    budget_state: dict[str, int] = Field(default_factory=dict)
    allowed_recovery_actions: list[str] = Field(default_factory=list)
    timestamp: str
    status: Literal["OPEN", "RECOVERED", "CANCELLED", "FAILED_SAFE"] = "OPEN"


class ControlRecoveryRequest(BaseModel):
    model_config = {"extra": "forbid"}

    recovery_id: str = Field(default_factory=lambda: f"REC-{uuid4().hex[:12].upper()}")
    action: Literal[
        "retry",
        "deterministic_fallback",
        "wait_external",
        "cancel",
        "fail_safe",
    ]
    rationale: str = Field(min_length=3, max_length=4000)
    reviewer: str = Field(min_length=2, max_length=200)
    case_state_version: int = Field(ge=1)


class CompletionEvaluation(BaseModel):
    model_config = {"extra": "forbid"}

    complete: bool
    criteria: dict[str, bool]
    blockers: list[str] = Field(default_factory=list)
    evaluated_at: str
    policy_version: str


class AutonomyAssignment(BaseModel):
    effective_profile: AutonomyProfile
    approved_maximum_profile: AutonomyProfile
    rationale: str
    policy_version: str
    governed_pattern_id: str | None = None
    eligible: bool
    downgraded: bool = False


class HumanInputRequirement(BaseModel):
    """One explicit reviewer task in a Human Governance interrupt."""

    model_config = {"extra": "forbid"}

    requirement_id: str
    kind: Literal[
        "mandatory_evidence_gap",
        "evidence_conflict",
        "verification_failure",
        "fact_confirmation",
        "exception_judgement",
        "final_decision",
        "publication_approval",
        "control_recovery",
    ]
    title: str
    description: str
    required_response: str
    blocking: bool = True
    field: str | None = None
    current_value: Any = None
    evidence_supported_value: Any = None
    suggested_value: Any = None
    required_artifacts: list[str] = Field(default_factory=list)
    review_items: list[str] = Field(default_factory=list)
    citations: list[dict[str, Any]] = Field(default_factory=list)
    accepted_resolutions: list[str] = Field(default_factory=list)


class HumanDecision(BaseModel):
    model_config = {"extra": "forbid"}

    decision_id: str = Field(default_factory=lambda: f"DEC-{uuid4().hex[:12].upper()}")
    action: str
    rationale: str = Field(default="", max_length=4000)
    additional_evidence: str = Field(default="", max_length=30000)
    answer_updates: dict[str, Any] = Field(default_factory=dict)
    override_band: MaterialityBand | None = None
    confirmed_teams: list[str] | None = None
    reviewer: str = "AIRO demo reviewer"
    reviewer_role: str = "AIRO reviewer"
    decision_authority: str = "AI Risk Oversight (AIRO)"
    case_id: str | None = None
    gate_id: str | None = None
    governance_loop: GovernanceLoop | None = None
    case_state_version: int | None = Field(default=None, ge=1)
    rule_version: str | None = None
    decided_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())

    @model_validator(mode="after")
    def reviewer_identity_is_present(self) -> HumanDecision:
        if not self.reviewer.strip() or not self.reviewer_role.strip():
            raise ValueError("Reviewer identity and role are required.")
        return self


class EvidenceItem(BaseModel):
    claim: str
    source: str = "submitted_evidence"
    line_refs: list[int] = Field(default_factory=list)
    confidence: float = Field(default=0.7, ge=0.0, le=1.0)


class EvidenceExtraction(BaseModel):
    summary: str
    facts: list[EvidenceItem] = Field(default_factory=list)
    potential_missing_information: list[str] = Field(default_factory=list)
    potential_inconsistencies: list[str] = Field(default_factory=list)
    risk_signals: list[str] = Field(default_factory=list)


class ChallengeResult(BaseModel):
    exceptions: list[str] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list)
    challenge_summary: str = "No additional LLM challenge was identified."


class HealthResponse(BaseModel):
    status: str
    llm_mode: str
    provider: str
    model: str
    available: bool
    selected_runtime: str
    fallback_enabled: bool
    message: str


class HistoricalAssessment(BaseModel):
    case_reference: str
    questionnaire: Questionnaire
    expert_materiality_band: MaterialityBand


class BacktestRequest(BaseModel):
    cases: list[HistoricalAssessment] = Field(min_length=1)


class SensitivityRequest(BaseModel):
    questionnaire: Questionnaire
