from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_gate_panel_has_action_specific_guidance_and_fields():
    html = (ROOT / "app" / "static" / "index.html").read_text(encoding="utf-8")
    script = (ROOT / "app" / "static" / "app.js").read_text(encoding="utf-8")

    for element_id in (
        "gate-reason",
        "decision-form-title",
        "gate-action-help",
        "additional-evidence-row",
        "answer-updates-row",
        "override-band-row",
        "confirmed-teams-row",
        "external-response-btn",
        "gate-support",
    ):
        assert f'id="{element_id}"' in html

    assert html.index('id="decision-form"') < html.index('id="gate-support"')
    assert "Only fields relevant to the selected decision are shown" in html
    assert "Advanced: questionnaire updates as JSON" in html
    assert "Guided corrections above update this JSON automatically" in html
    assert 'id="reviewer" value="AIRO demo reviewer" required' in html
    assert "function updateDecisionForm" in script
    assert "function renderHumanRequirement" in script
    assert "function renderDecisionOptions" in script
    assert "function renderGuidedAnswerControls" in script
    assert "function renderDecisionImpact" in script
    assert "function showDecisionFormError" in script
    assert 'id="decision-options"' in html
    assert 'id="guided-answer-controls"' in html
    assert 'id="decision-impact-preview"' in html
    assert 'id="decision-form-error"' in html
    assert 'gate.gate_id === "evidence_request" && action === "add_evidence"' in script
    assert 'gate.gate_id === "final_triage" && action === "override"' in script
    assert 'action === "amend_material_fact"' in script
    assert '$("decision-action").onchange' in script
    assert "gate.required_inputs" in script
    assert "gate.action_impacts" in script
    assert "gate.recommended_action" in script


def test_coordinator_panel_uses_current_gate_and_issue_statuses():
    script = (ROOT / "app" / "static" / "app.js").read_text(encoding="utf-8")

    assert "const supervisorAllowed = supervisor.allowed_actions" in script
    assert "const gateAllowed = gate?.allowed_actions || []" in script
    assert "Current AIRO Gate allowed decisions" in script
    assert "Items requiring attention" not in script
    assert "Evidence and issue records remain separated" in script
    assert "Latest verification" in script
    assert "Historical action" in script
    assert "Last AIRO decision" in script
    assert "now waiting at ${nextGate.title}" in script


def test_workspace_distinguishes_current_action_history_and_completion_contract():
    script = (ROOT / "app" / "static" / "app.js").read_text(encoding="utf-8")

    assert "function coordinatorCurrentAction" in script
    assert "s.current_action_proposal?.selected_action" in script
    assert "s.current_action_proposal || latestTrace" not in script
    assert "Most recent selected action / method" in script
    assert 'llm_router: "Bounded LLM recommendation"' in script
    assert 'deterministic_policy: "Deterministic"' in script
    assert 'fallback: "Deterministic fallback"' in script
    assert "function completionCriteriaView" in script
    assert "Configured completion criteria" in script
    assert "s.completion_criteria || []" in script


def test_default_views_prioritise_readable_summaries_over_raw_records():
    script = (ROOT / "app" / "static" / "app.js").read_text(encoding="utf-8")
    styles = (ROOT / "app" / "static" / "styles.css").read_text(encoding="utf-8")

    assert "function renderQuestionnaireOverview" in script
    assert "Questionnaire and governed assignment" in script
    assert "Declared risk and control signals" in script
    assert "function resultSummary" in script
    assert "Proposed materiality" in script
    assert "Proposed second-line engagement" in script
    assert 'class="data-section technical-record"' in script
    assert 'class="gate-decision-focus"' in script
    assert 'class="decision-support"' in script
    assert '$("gate-support").innerHTML' in script
    assert "Review decision support, evidence and allowed effects" in script
    assert "const evidencePreview = evidenceItems.slice(0, 5)" in script
    assert "remainingEvidenceCount" in script
    assert "Allowed decisions and effects" in script
    assert "Additional structured Gate context" in script
    assert ".domain-summary-grid" in styles
    assert ".allowed-decision-grid" in styles
    assert ".decision-support" in styles
    assert ".technical-record" in styles
    assert "max-height: min(780px, calc(100vh - 24px))" not in styles
    assert "scrollbar-gutter: stable" not in styles
    assert ".decision-impact-preview > summary" in styles
    assert '$("decision-form").scrollIntoView' in script
    assert 'input[name="gate-decision"]:checked' in script
    assert ".decision-submit-row" in styles
    assert ".human-requirement" in styles
    assert ".decision-option.selected" in styles
    assert ".guided-answer-controls" in styles
    assert ".decision-impact-preview" in styles
    assert ".form-error" in styles


def test_work_queue_is_bounded_searchable_and_resume_oriented():
    html = (ROOT / "app" / "static" / "index.html").read_text(encoding="utf-8")
    script = (ROOT / "app" / "static" / "app.js").read_text(encoding="utf-8")

    for element_id in (
        "queue-summary",
        "case-lookup-form",
        "case-lookup",
        "continue-btn",
    ):
        assert f'id="{element_id}"' in html

    assert "const WORK_QUEUE_LIMIT = 5" in script
    assert "state.cases.slice(0, WORK_QUEUE_LIMIT)" in script
    assert "recentCases.slice(0, WORK_QUEUE_LIMIT - 1)" in script
    assert "Resume at ${gateLabel}" in script
    assert "A Gate decision is never submitted automatically" in html
    assert "function openCaseById" in script
    assert "Durable resume point" in script


def test_case_creation_catalogue_is_compact_searchable_and_complete():
    html = (ROOT / "app" / "static" / "index.html").read_text(encoding="utf-8")
    script = (ROOT / "app" / "static" / "app.js").read_text(encoding="utf-8")
    styles = (ROOT / "app" / "static" / "styles.css").read_text(encoding="utf-8")
    api = (ROOT / "app" / "main.py").read_text(encoding="utf-8")

    for element_id in ("sample-search", "sample-profile-filter", "sample-count"):
        assert f'id="{element_id}"' in html
    assert "Creating a Case does not start the Coordinator" in html
    assert "function renderSampleCatalogue" in script
    assert "function sampleSearchText" in script
    assert "function createSampleCase" in script
    assert '"featured_cases"' in script
    assert "sample.featured_case_number" in script
    assert "left.featured_case_number || 99" in script
    assert "Required coverage" in script
    assert "Policy assigned ·" in script
    assert "Teaching controls (not a profile override)" in script
    assert '"featured_case_number": sample.featured_case_number' in api
    assert '"featured_case_name": sample.featured_case_name' in api
    assert "they do not override the policy-assigned profile" in api
    assert 'class="sample-card-details"' in script
    assert "Expected journey and teaching details" in script
    for label in (
        "What feature this sample demonstrates",
        "Expected path",
        "Expected dynamic actions",
        "Expected tools",
        "Expected exceptions",
        "Expected Governance Loops",
        "Expected final result",
    ):
        assert f'sampleDetailRow("{label}"' in script
    assert "Create and open case" in script
    assert "sample.expected_assigned_profile === state.sampleProfile" in script
    assert ".sample-category-group" in styles
    assert ".featured-case-badge" in styles
    assert ".sample-card-details" in styles
    assert ".sample-button {" not in styles


def test_case_journey_uses_authoritative_state_and_non_linear_control_statuses():
    script = (ROOT / "app" / "static" / "app.js").read_text(encoding="utf-8")
    html = (ROOT / "app" / "static" / "index.html").read_text(encoding="utf-8")
    styles = (ROOT / "app" / "static" / "styles.css").read_text(encoding="utf-8")

    assert "Authoritative Case State" in html
    assert 'id="case-journey-title">Case journey' in html
    assert 'id="current-control-state"' in html
    assert 'class="control-state-facts"' in script
    assert "Read-only progress view" in html
    assert "How to read this journey" in html
    assert "function renderCaseJourney" in script
    assert 'const phase = s.domain_phase || "INTAKE"' in script
    assert "phaseIndex.get(phase) ?? 0" in script
    assert 's.active_external_event?.status === "WAITING"' in script
    assert 'lifecycle === "CONTROL_EXCEPTION"' in script
    assert "Stale — replacement required" in script
    assert "Reopened after a governed change" in script
    assert "Waiting for external event" in script
    assert "Waiting for AIRO" in script
    assert "AIRO decision recorded" in script
    assert "Gate skipped by deterministic policy" in script
    assert "Gate not triggered" in script
    assert script.index("if (isCurrent)") < script.index("} else if (isStale)")
    assert 'isCurrent ? "Why reopened:" : "Why stale:"' in script
    assert ".journey-stage.stage-stale" in styles
    assert ".journey-stage.stage-reopened" in styles
    assert "#c8873c" in styles
    assert ".journey-stage.stage-exception" in styles
    assert ".control-event" in styles
    assert ".control-state-facts" in styles
    assert "function renderWorkflow" not in script
    assert "StateGraph</p><h3>Case progress" not in html


def test_normal_workspace_humanises_codes_and_hides_empty_completion_guard():
    script = (ROOT / "app" / "static" / "app.js").read_text(encoding="utf-8")

    assert "function titleWords" in script
    assert "titleWords(lifecycle)" in script
    assert "titleWords(s.active_governance_loop)" in script
    assert "titleWords(action)" in script
    assert "function humaniseAssignmentReason" in script
    assert "titleWords(assignment.governed_pattern_id)" in script
    assert "Current control point" in script
    assert "Paused at ${GATE_LABELS[gate.gate_id] || gate.title}" in script
    assert "0 of ${(s.completion_criteria || []).length} criteria evaluated" in script
    assert "Object.keys(s.completion_evaluation).length" in script


def test_health_banner_uses_provider_neutral_runtime_fields():
    script = (ROOT / "app" / "static" / "app.js").read_text(encoding="utf-8")
    html = (ROOT / "app" / "static" / "index.html").read_text(encoding="utf-8")

    assert "health.provider.toUpperCase()" in script
    assert "health.model" in script
    assert "health.ollama_model" not in script
    assert "the configured bounded LLM processes evidence" in html


def test_workspace_separates_findings_guards_stale_results_and_connects_cycles():
    script = (ROOT / "app" / "static" / "app.js").read_text(encoding="utf-8")
    html = (ROOT / "app" / "static" / "index.html").read_text(encoding="utf-8")
    styles = (ROOT / "app" / "static" / "styles.css").read_text(encoding="utf-8")

    assert "Coordinator Workspace" in html
    for panel in (
        "Mandatory evidence gaps",
        "Evidence conflicts",
        "LLM advisory observations",
        "Confirmed exceptions",
        "Confirmed facts",
        "Candidate facts awaiting confirmation",
    ):
        assert panel in script
    assert "Evidence and issue register" in script
    assert "const preview = items.slice(0, 3)" in script
    assert 'class="finding-count"' in script
    assert "Open Evidence register" in script
    assert 'openCaseTab("evidence")' in script
    assert ".finding-more" in styles
    assert 'role="tablist"' in html
    assert 'role="tabpanel"' in html
    assert 'aria-controls="tab-content"' in html
    assert 'button.setAttribute("aria-selected", String(active))' in script
    assert "function handleTabKeydown" in script
    assert "button.onkeydown = handleTabKeydown" in script
    assert "STALE / SUPERSEDED" in script
    assert "No authoritative current result is displayed" in script
    for stage in (
        "Observed State",
        "Policy Decision",
        "Selected Action",
        "Authorisation",
        "Tool Execution",
        "Verification",
        "State Changes",
        "Invalidated Outputs",
        "Transition Decision",
    ):
        assert stage in script
    for tag in ("STATE", "DET", "TOOL", "VERIFY", "HITL", "EVENT", "END"):
        assert f'traceBadge("{tag}")' in script or f'["{tag}",' in script
    assert '? "LLM" : "DET"' in script
    assert "function renderSupportingCycle" in script
    assert 'class="trace-cycle supporting-cycle"' in script
