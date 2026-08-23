from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_gate_panel_has_action_specific_guidance_and_fields():
    html = (ROOT / "app" / "static" / "index.html").read_text(encoding="utf-8")
    script = (ROOT / "app" / "static" / "app.js").read_text(encoding="utf-8")

    for element_id in (
        "gate-reason",
        "gate-action-help",
        "additional-evidence-row",
        "answer-updates-row",
        "override-band-row",
        "confirmed-teams-row",
    ):
        assert f'id="{element_id}"' in html

    assert "function updateDecisionForm" in script
    assert 'gate.gate_id === "evidence_request" && action === "add_evidence"' in script
    assert 'gate.gate_id === "final_triage" && action === "override"' in script
    assert '$("decision-action").onchange' in script


def test_coordinator_panel_uses_current_gate_and_issue_statuses():
    script = (ROOT / "app" / "static" / "app.js").read_text(encoding="utf-8")

    assert "gate ? (gate.allowed_actions || [])" in script
    assert 'item.status !== "open"' in script
    assert "AIRO-accepted residual issues" in script
    assert "Latest tool verification (history)" in script
    assert "Last recorded AIRO decision" in script
    assert "now waiting at ${nextGate.title}" in script


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


def test_workflow_distinguishes_human_decisions_policy_skips_and_non_applicable_gates():
    script = (ROOT / "app" / "static" / "app.js").read_text(encoding="utf-8")

    assert "AIRO decision recorded" in script
    assert "Skipped by deterministic policy" in script
    assert "Evidence complete — Gate not triggered" in script
    assert "const skipped = done && evaluation?.required === false" in script


def test_mock_health_banner_does_not_claim_the_configured_ollama_model_is_running():
    script = (ROOT / "app" / "static" / "app.js").read_text(encoding="utf-8")

    assert 'health.llm_mode === "mock"' in script
    assert "deterministic demonstration runtime" in script
