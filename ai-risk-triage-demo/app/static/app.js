const state = { cases: [], samples: {}, current: null, activeTab: "overview", calibration: null };
const WORK_QUEUE_LIMIT = 5;
const GATE_LABELS = {
  evidence_request: "Gate 1 — Evidence request",
  input_confirmation: "Gate 2 — Input confirmation",
  exception_resolution: "Gate 3 — Challenge and exception review",
  final_triage: "Gate 4 — Final triage",
  publication: "Gate 5 — Publication",
};

const CATEGORY_ORDER = [
  "core_workflow",
  "progressive_automation",
  "advanced_controls",
];
const PROFILE_CLASSES = {
  human_governed: "profile-human",
  conditional_review: "profile-conditional",
  exception_based: "profile-exception",
  straight_through: "profile-straight-through",
  straight_through_demo: "profile-straight-through",
};

const $ = (id) => document.getElementById(id);
const escapeHtml = (value) => String(value ?? "").replace(/[&<>'"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"}[c]));
const pretty = (value) => JSON.stringify(value ?? {}, null, 2);

async function api(path, options = {}) {
  const response = await fetch(path, { headers: {"Content-Type": "application/json"}, ...options });
  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`;
    try { detail = (await response.json()).detail || detail; } catch (_) {}
    throw new Error(detail);
  }
  return response.json();
}

function toast(message, error = false) {
  const el = $("toast");
  el.textContent = message;
  el.className = `toast${error ? " error" : ""}`;
  setTimeout(() => el.classList.add("hidden"), 4200);
}

async function loadHealth() {
  try {
    const health = await api("/api/health");
    $("health-dot").classList.add(health.status === "ok" ? "ok" : "bad");
    const runtimeDetail = health.llm_mode === "mock"
      ? "deterministic demonstration runtime"
      : health.ollama_model;
    $("health-label").textContent = `${health.llm_mode.toUpperCase()} · ${runtimeDetail}`;
    $("health-message").textContent = health.message;
  } catch (error) {
    $("health-dot").classList.add("bad");
    $("health-label").textContent = "Runtime unavailable";
    $("health-message").textContent = error.message;
  }
}

async function loadSamples() {
  state.samples = await api("/api/samples");
  const container = $("sample-buttons");
  container.innerHTML = "";
  CATEGORY_ORDER.forEach(category => {
    const entries = Object.entries(state.samples).filter(([, sample]) => sample.category === category);
    if (!entries.length) return;

    const group = document.createElement("section");
    group.className = "sample-profile-group";
    const heading = document.createElement("div");
    heading.className = "sample-profile-heading";
    heading.innerHTML = `
      <h4>${escapeHtml(entries[0][1].category_name)}</h4>
      <p>${category === "advanced_controls" ? "Protected technical fixtures that demonstrate fail-closed controls." : "Select a scenario to inspect its real state and action trace."}</p>`;
    group.appendChild(heading);

    const cards = document.createElement("div");
    cards.className = "sample-profile-cards";
    entries.forEach(([key, sample]) => {
      const profile = sample.expected_assigned_profile;
      const button = document.createElement("button");
      button.className = "sample-button";
      button.innerHTML = `
        <strong class="sample-card-title">${escapeHtml(sample.title)}</strong>
        <span class="profile-badge ${PROFILE_CLASSES[profile]}">${escapeHtml(profile.replaceAll("_", " "))}</span>
        <span class="sample-journey">${escapeHtml(sample.short_description)}</span>
        <small><b>Features:</b> ${escapeHtml(sample.learning_objectives.join(" · "))}</small>
        <small><b>Likely AIRO attention:</b> ${escapeHtml(sample.likely_airo_attention)}</small>`;
      button.onclick = async () => {
        try {
          const created = await api(`/api/samples/${key}`, {method: "POST"});
          await loadCases(created.case_id);
          toast("Demonstration case created. Start the Coordinator when ready.");
        } catch (error) { toast(error.message, true); }
      };
      cards.appendChild(button);
    });
    group.appendChild(cards);
    container.appendChild(group);
  });
}

function sampleMetadataForCase(caseState) {
  return state.samples[caseState?.demo_scenario_id] || null;
}

async function loadCases(selectId = null) {
  state.cases = await api("/api/cases");
  renderCaseList();
  const target = selectId || state.current?.case_id;
  if (target) await selectCase(target);
}

function renderCaseList() {
  const container = $("case-list");
  if (!state.cases.length) {
    container.innerHTML = '<p class="muted">No cases yet.</p>';
    $("queue-summary").textContent = "No Cases. Create a demonstration or custom Case below.";
    return;
  }
  const recentCases = state.cases.slice(0, WORK_QUEUE_LIMIT);
  const selectedIsOlder = Boolean(
    state.current && !recentCases.some(item => item.case_id === state.current.case_id)
  );
  const selectedSummary = selectedIsOlder
    ? {
        case_id: state.current.case_id,
        title: state.current.title,
        status: state.current.status,
        autonomy_profile: state.current.autonomy_profile,
        pending_gate: state.current.pending_gate,
        updated_at: state.current.updated_at,
        historical_pin: true,
      }
    : null;
  const visibleCases = selectedSummary
    ? [selectedSummary, ...recentCases.slice(0, WORK_QUEUE_LIMIT - 1)]
    : recentCases;
  const awaitingCount = state.cases.filter(item => item.pending_gate).length;
  const draftCount = state.cases.filter(item => item.status === "DRAFT").length;
  $("queue-summary").textContent = `${awaitingCount} awaiting AIRO · ${draftCount} not started · ${state.cases.length} total`;
  container.innerHTML = visibleCases.map(item => {
    const gateLabel = item.pending_gate
      ? GATE_LABELS[item.pending_gate.gate_id] || item.pending_gate.title || item.pending_gate.gate_id
      : null;
    const action = gateLabel
      ? `Resume at ${gateLabel}`
      : item.status === "DRAFT"
        ? "Open and start Coordinator"
        : item.status === "CLOSED"
          ? "View completed Case and audit"
          : item.status === "CANCELLED"
            ? "View cancelled Case and audit"
            : item.status === "ERROR"
              ? "Review failed-closed Case"
              : "Open saved Case";
    const cardClass = gateLabel ? "needs-action" : item.status === "DRAFT" ? "ready" : "read-only";
    const updated = item.updated_at
      ? new Date(item.updated_at).toLocaleString([], {dateStyle: "medium", timeStyle: "short"})
      : "Unknown";
    return `
      <button class="case-item ${cardClass} ${state.current?.case_id === item.case_id ? "active" : ""}" data-case-id="${escapeHtml(item.case_id)}" aria-current="${state.current?.case_id === item.case_id ? "true" : "false"}">
        <span class="case-item-topline"><strong>${escapeHtml(item.title)}</strong>${item.historical_pin ? '<span class="historical-pin">Opened by ID</span>' : ""}</span>
        <small>${escapeHtml(item.case_id)} · ${escapeHtml(item.autonomy_profile.replaceAll("_", " "))}</small>
        <span class="mini-status">${escapeHtml(gateLabel || item.status.replaceAll("_", " "))}</span>
        <span class="queue-action">${escapeHtml(action)}</span>
        <small class="queue-updated">Updated ${escapeHtml(updated)}</small>
      </button>`;
  }).join("") + (state.cases.length > WORK_QUEUE_LIMIT
    ? `<p class="queue-limit-note">Showing ${selectedIsOlder ? "the selected historical Case and four recent Cases" : `the ${WORK_QUEUE_LIMIT} most recently updated Cases`}. Use exact Case ID to open an older record.</p>`
    : "");
  container.querySelectorAll(".case-item").forEach(button => {
    button.onclick = async () => {
      await selectCase(button.dataset.caseId);
      $("case-view").scrollIntoView({behavior: "smooth", block: "start"});
    };
  });
}

async function selectCase(caseId) {
  try {
    state.current = await api(`/api/cases/${caseId}`);
    $("empty-state").classList.add("hidden");
    $("case-view").classList.remove("hidden");
    renderCaseList();
    renderCurrentCase();
    return true;
  } catch (error) { toast(error.message, true); }
  return false;
}

async function openCaseById(event) {
  event.preventDefault();
  const caseId = $("case-lookup").value.trim().toUpperCase();
  if (!caseId) {
    toast("Enter a Case ID such as AIRO-1234ABCD.", true);
    return;
  }
  const opened = await selectCase(caseId);
  if (!opened) return;
  $("case-lookup").value = "";
  const pending = state.current.pending_gate;
  toast(pending
    ? `Case restored. Review and resume ${GATE_LABELS[pending.gate_id] || pending.title}.`
    : `Case restored with status ${state.current.status.replaceAll("_", " ")}.`);
  $("case-view").scrollIntoView({behavior: "smooth", block: "start"});
}

function renderCurrentCase() {
  const current = state.current;
  const s = current.state;
  const q = s.questionnaire || {};
  const sample = sampleMetadataForCase(s);
  const profileClass = PROFILE_CLASSES[current.autonomy_profile] || "profile-human";
  const profileName = current.autonomy_profile.replaceAll("_", " ");
  const latestAutonomy = (s.autonomy_log || []).at(-1);
  const actualGate = current.pending_gate
    ? `${current.pending_gate.title} (${current.pending_gate.gate_id})`
    : current.status === "DRAFT"
      ? "Not started"
      : current.status === "CLOSED"
        ? "No pending gate — case closed"
        : current.status === "CANCELLED"
          ? "No pending gate — case cancelled"
          : current.status === "ERROR"
            ? "No pending gate — case failed closed"
        : "No pending Human Gate";
  const gateExplanation = current.pending_gate?.reason || current.pending_gate?.autonomy?.rationale
    || (current.status === "DRAFT"
      ? "The StateGraph will determine the first gate after Start Coordinator is selected."
      : latestAutonomy?.rationale || "The current StateGraph route has no pending Human Gate.");
  const assignment = s.autonomy_assignment || {};
  $("case-id").textContent = current.case_id;
  $("case-title").textContent = q.use_case_name || current.title;
  $("case-purpose").textContent = q.purpose || "";
  $("autonomy-badge").textContent = profileName;
  $("autonomy-badge").className = `badge profile-badge ${profileClass}`;
  $("status-badge").textContent = current.status.replaceAll("_", " ");
  $("case-automation-context").innerHTML = `
    ${current.pending_gate ? `<div class="resume-context"><span>Durable resume point</span><strong>${escapeHtml(GATE_LABELS[current.pending_gate.gate_id] || current.pending_gate.title)}</strong><small>The saved Case and LangGraph checkpoint were restored. Review the Gate context and submit an AIRO decision to continue; opening the Case did not execute an action.</small></div>` : ""}
    <div><span>System-assigned profile</span><strong>${escapeHtml(profileName)}</strong><small>${escapeHtml(assignment.rationale || sample?.profile_summary || "Deterministic policy controls permissions and gate progression.")}</small></div>
    <div><span>Approved maximum / governed pattern</span><strong>${escapeHtml((assignment.approved_maximum_profile || "human_governed").replaceAll("_", " "))}</strong><small>${escapeHtml(assignment.governed_pattern_id || "No governed pattern — unmatched normal case")}</small></div>
    <div><span>Illustrative policy version</span><strong>${escapeHtml(assignment.policy_version || "Not assigned")}</strong><small>Evidence issues, deviations or elevated risk can downgrade permissions; the LLM cannot upgrade them.</small></div>
    <div><span>Actual current gate</span><strong>${escapeHtml(actualGate)}</strong></div>
    <div><span>Why this route</span><strong>${escapeHtml(gateExplanation)}</strong></div>
    ${sample ? `<div class="demo-steps"><span>Demonstration steps</span><ol>${sample.interactive_steps.map(step => `<li>${escapeHtml(step)}</li>`).join("")}</ol><small>Expected metadata explains the lesson; runtime state remains authoritative.</small></div>` : ""}`;
  $("start-btn").classList.toggle("hidden", current.status !== "DRAFT");
  $("continue-btn").classList.toggle("hidden", !current.pending_gate);
  $("continue-btn").textContent = current.pending_gate
    ? `Continue at ${GATE_LABELS[current.pending_gate.gate_id] || current.pending_gate.title}`
    : "Continue at current Gate";
  renderWorkflow(s, current.pending_gate);
  renderCoordinator(s, current.pending_gate);
  renderGate(current.pending_gate);
  renderTab();
}

function renderWorkflow(s, gate) {
  const completed = new Set(s.completed_nodes || []);
  const definitions = [
    ["Intake", ["normalise_intake"], null],
    ["Evidence / Gate 1 if required", ["observe_case"], "evidence_request"],
    ["Input confirmation / Gate 2", ["input_gate"], "input_confirmation"],
    ["Risk engines", ["decision_engines"], null],
    ["Exceptions / Gate 3 if required", ["challenge_assessment"], "exception_resolution"],
    ["Final triage / Gate 4", ["review_pack"], "final_triage"],
    ["Publication / Gate 5 if required", ["publish"], "publication"],
  ];
  const gateMap = {evidence_request:1, input_confirmation:2, exception_resolution:4, final_triage:5, publication:6};
  const gateEvaluations = new Map();
  (s.autonomy_log || []).forEach(item => gateEvaluations.set(item.gate_id, item));
  const currentIndex = gate ? gateMap[gate.gate_id] : (s.status === "CLOSED" ? 6 : 0);
  $("workflow-steps").innerHTML = definitions.map(([label, nodes, gateId], index) => {
    // When the graph loops back, downstream node markers are historical rather
    // than evidence that those stages are still current.
    const done = gate
      ? index < currentIndex
      : nodes.some(node => completed.has(node)) || (s.status === "CLOSED" && index < 7);
    const evaluation = gateId ? gateEvaluations.get(gateId) : null;
    const skipped = done && evaluation?.required === false;
    const cls = skipped ? "skipped" : done ? "done" : (index === currentIndex ? "current" : "");
    const completedLabel = evaluation
      ? evaluation.required === false
        ? "Skipped by deterministic policy"
        : "AIRO decision recorded"
      : gateId === "evidence_request"
        ? "Evidence complete — Gate not triggered"
        : label === "Risk engines"
          ? "Deterministic results current"
          : "Completed";
    const stateLabel = done
      ? completedLabel
      : index === currentIndex
        ? (gate ? `Awaiting ${gate.gate_id.replaceAll("_", " ")}` : s.status === "DRAFT" ? "Ready to start" : "Current")
        : s.status === "CANCELLED" ? "Not reached — case cancelled" : "Pending / not current";
    return `<div class="step ${cls}"><strong>${index + 1}. ${label}</strong><small>${escapeHtml(stateLabel)}</small></div>`;
  }).join("");
}

function renderCoordinator(s, gate) {
  const materiality = s.materiality_result?.proposed_materiality_band || "Not calculated";
  const teams = s.lod2_result?.teams || [];
  const acceptedExceptionSet = new Set((s.confirmed_exceptions || []).filter(item => item.status === "accepted").map(item => item.summary));
  const unresolvedExceptions = (s.exceptions || []).filter(item => !acceptedExceptionSet.has(item));
  const currentGapSet = new Set(s.missing_information || []);
  const currentConflictSet = new Set(s.inconsistencies || []);
  const issueIsCurrent = item => {
    if (item.status !== "open") return false;
    if (item.category === "mandatory_evidence_gap") return currentGapSet.has(item.summary);
    if (item.category === "inconsistency") return currentConflictSet.has(item.summary);
    return true;
  };
  const acceptedEvidenceIssues = (s.open_issues || []).filter(item =>
    item.status === "accepted"
    && ["mandatory_evidence_gap", "inconsistency", "verification"].includes(item.category)
    && (item.category === "verification" || currentGapSet.has(item.summary) || currentConflictSet.has(item.summary))
  );
  const acceptedEvidenceSet = new Set(acceptedEvidenceIssues.map(item => item.summary));
  const openControlIssues = (s.open_issues || []).filter(item => !item.advisory && issueIsCurrent(item)).map(item => item.summary);
  const gaps = [...new Set([
    ...(s.missing_information || []).filter(item => !acceptedEvidenceSet.has(item)),
    ...(s.inconsistencies || []).filter(item => !acceptedEvidenceSet.has(item)),
    ...unresolvedExceptions,
    ...openControlIssues,
  ])];
  const terminalAction = s.status === "CLOSED"
    ? "Case completed"
    : s.status === "CANCELLED"
      ? "Case cancelled — no approval recorded"
      : s.status === "ERROR"
        ? "Case failed closed — inspect the audit history"
        : null;
  const next = gate ? `Waiting for AIRO at ${gate.title}` : (terminalAction || s.recommended_next_action?.action || "Continue workflow");
  const latestTrace = (s.agent_action_trace || []).at(-1);
  const latestDecision = (s.human_decisions || []).at(-1);
  const deterministicIssues = (s.open_issues || []).filter(item => !item.advisory && issueIsCurrent(item));
  const advisoryIssues = [
    ...(s.advisory_observations || []).map(item => item.observation || item),
    ...(s.open_issues || []).filter(item => item.advisory).map(item => item.summary),
  ];
  const permitted = gate ? (gate.allowed_actions || []) : (s.policy_assessment?.permitted_actions || []);
  const remainingLoops = Math.max(0, (s.max_evidence_cycles ?? 0) - (s.evidence_cycle ?? 0));
  const invalidated = s.invalidations || [];
  const traceRows = (s.agent_action_trace || []).slice(-5).map(item => `
    <tr><td>${escapeHtml(item.selection_source)}</td><td>${escapeHtml(item.proposal?.selected_action)}</td><td>${escapeHtml(item.invocation?.tool_id || "No tool")}</td><td>${escapeHtml(item.verification?.disposition || "Pending")}</td><td>${escapeHtml(item.remaining_tool_calls)}</td></tr>`).join("");
  $("coordinator-summary").innerHTML = `
    <div class="summary-grid">
      <div class="summary-tile"><span>Current state</span><strong>${escapeHtml(s.status || "DRAFT")}</strong></div>
      <div class="summary-tile"><span>Recommended next action</span><strong>${escapeHtml(next)}</strong></div>
      <div class="summary-tile"><span>Proposed materiality</span><strong>${escapeHtml(materiality)}</strong></div>
      <div class="summary-tile"><span>Proposed 2LoD teams</span><strong>${teams.length ? escapeHtml(teams.join(", ")) : "Not calculated"}</strong></div>
      <div class="summary-tile"><span>Evidence cycles</span><strong>${s.evidence_cycle || 0}</strong></div>
      <div class="summary-tile"><span>LLM runtime</span><strong>${escapeHtml(s.llm_runtime?.selected_runtime || s.llm_runtime?.runtime || "Not called")}</strong></div>
      <div class="summary-tile"><span>Current objective</span><strong>${escapeHtml(s.case_objective?.statement || "Not assigned")}</strong></div>
      <div class="summary-tile"><span>Latest evidence tool (history)</span><strong>${escapeHtml(latestTrace?.invocation?.tool_id || "Not called")}</strong><small>${escapeHtml(latestTrace?.proposal?.reason || "")}</small></div>
      <div class="summary-tile"><span>Latest tool verification (history)</span><strong>${escapeHtml(latestTrace?.verification?.disposition || "Not available")}</strong><small>${escapeHtml((latestTrace?.verification?.issues || []).join(" · "))}</small></div>
      <div class="summary-tile"><span>Unused evidence-work budget</span><strong>${s.remaining_tool_calls ?? s.max_tool_calls ?? "Not set"} tool calls · ${remainingLoops} evidence loops</strong><small>Capacity remaining under the bounded policy; not an outstanding task.</small></div>
      <div class="summary-tile"><span>${gate ? "Current AIRO Gate actions" : "Current Coordinator actions"}</span><strong>${permitted.length ? escapeHtml(permitted.join(", ")) : "None — reassessing or complete"}</strong></div>
      <div class="summary-tile"><span>Last recorded AIRO decision</span><strong>${escapeHtml(latestDecision?.action?.replaceAll("_", " ") || "None yet")}</strong><small>${escapeHtml(latestDecision?.rationale || "")}</small></div>
    </div>
    ${gaps.length ? `<div class="attention"><strong>Items requiring attention</strong><ul>${gaps.slice(0,8).map(x => `<li>${escapeHtml(x)}</li>`).join("")}</ul></div>` : '<div class="attention"><strong>No unresolved evidence or challenge items are currently recorded.</strong></div>'}
    <div class="explanation-grid">
      <div><h4>Deterministic issues</h4>${deterministicIssues.length ? `<ul>${deterministicIssues.map(x => `<li>${escapeHtml(x.summary)}</li>`).join("")}</ul>` : "<p>None recorded.</p>"}</div>
      <div><h4>AIRO-accepted residual issues</h4>${acceptedEvidenceIssues.length ? `<ul>${acceptedEvidenceIssues.map(x => `<li>${escapeHtml(x.summary)} <small>(accepted by ${escapeHtml(x.owner || "AIRO")}; still a risk condition)</small></li>`).join("")}</ul>` : "<p>None current.</p>"}</div>
      <div><h4>LLM/tool advisory observations</h4>${advisoryIssues.length ? `<ul>${advisoryIssues.map(x => `<li>${escapeHtml(x)}</li>`).join("")}</ul>` : "<p>None recorded.</p>"}</div>
      <div><h4>Replanning audit history</h4><p>${invalidated.length} invalidation record(s); ${(s.superseded_results || []).length} preserved previous result(s). Historical records do not indicate a current issue.</p></div>
      <div><h4>Current AIRO Gate</h4><p>${escapeHtml(gate ? `${gate.gate_id}: ${gate.decision_required || gate.summary}. ${gate.reason}` : "No Gate pending")}</p></div>
    </div>
    <div class="trace-summary"><h4>Concise action trace</h4>${traceRows ? `<table><thead><tr><th>Selected by</th><th>Action</th><th>Tool</th><th>Verification</th><th>Budget left</th></tr></thead><tbody>${traceRows}</tbody></table>` : "<p>No action recorded yet.</p>"}</div>
  `;
}

function renderGate(gate) {
  const panel = $("gate-panel");
  if (!gate) { panel.classList.add("hidden"); return; }
  const displayContext = {...(gate.context || {})};
  if (displayContext.evidence_summary && !displayContext.advisory_evidence_summary) {
    displayContext.advisory_evidence_summary = displayContext.evidence_summary;
    displayContext.advisory_summary_notice = "LLM-prepared summary — AIRO confirmation required. The current remaining_gaps and remaining_conflicts fields control deterministic routing.";
    delete displayContext.evidence_summary;
  }
  displayContext.available_actions = Object.entries(gate.action_effects || {}).map(([action, effect]) => ({action, effect, rationale_required: Boolean(gate.rationale_required?.[action])}));
  panel.classList.remove("hidden");
  $("gate-title").textContent = gate.title;
  $("gate-summary").textContent = gate.summary;
  $("gate-reason").textContent = `Why AIRO is needed: ${gate.reason}`;
  $("gate-context").innerHTML = `<pre>${escapeHtml(pretty(displayContext))}</pre>`;
  $("decision-action").innerHTML = (gate.allowed_actions || []).map(action => `<option value="${escapeHtml(action)}">${escapeHtml(action.replaceAll("_", " "))}</option>`).join("");
  $("decision-rationale").value = "";
  $("additional-evidence").value = "";
  $("answer-updates").value = "";
  $("override-band").value = "";
  $("confirmed-teams").value = "";
  updateDecisionForm(gate);
}

function updateDecisionForm(gate = state.current?.pending_gate) {
  if (!gate) return;
  const action = $("decision-action").value;
  const showEvidence = gate.gate_id === "evidence_request" && action === "add_evidence";
  const showAnswers = showEvidence || action === "edit_answers";
  const showOverride = gate.gate_id === "final_triage" && action === "override";
  $("additional-evidence-row").classList.toggle("hidden", !showEvidence);
  $("answer-updates-row").classList.toggle("hidden", !showAnswers);
  $("override-band-row").classList.toggle("hidden", !showOverride);
  $("confirmed-teams-row").classList.toggle("hidden", !showOverride);
  const rationaleRequired = Boolean(gate.rationale_required?.[action]);
  $("decision-rationale").required = rationaleRequired;
  $("decision-rationale").placeholder = rationaleRequired
    ? "Required: explain the accountable AIRO decision"
    : "Optional decision note";
  const effect = gate.action_effects?.[action] || "The Coordinator will apply this governed transition.";
  $("gate-action-help").textContent = `${effect}${rationaleRequired ? " A rationale is required." : ""}`;
}

function section(title, value) {
  return `<div class="data-section"><h4>${escapeHtml(title)}</h4><pre class="json">${escapeHtml(pretty(value))}</pre></div>`;
}

function labelledList(title, label, values, className = "") {
  return `<div class="explanation-box ${className}"><h4>${escapeHtml(title)}</h4><span class="finding-label">${escapeHtml(label)}</span>${values.length ? `<ul>${values.map(value => `<li>${escapeHtml(typeof value === "string" ? value : value.summary || value.observation || value.claim)}</li>`).join("")}</ul>` : "<p>None recorded.</p>"}</div>`;
}

function renderTab() {
  document.querySelectorAll(".tab").forEach(button => button.classList.toggle("active", button.dataset.tab === state.activeTab));
  const s = state.current.state;
  let html = "";
  if (state.activeTab === "overview") {
    html = section("Agent objective", s.case_objective || {}) + section("Proposed outcome", s.proposed_outcome || {}) + section("Final outcome", s.final_outcome || {}) + section("Autonomy decisions", s.autonomy_log || []) + section("Agent action trace", s.agent_action_trace || []);
  } else if (state.activeTab === "evidence") {
    const confirmed = s.confirmed_facts || [];
    const claims = s.evidence_claims || [];
    const currentGaps = new Set(s.missing_information || []);
    const currentConflicts = new Set(s.inconsistencies || []);
    const currentIssues = (s.open_issues || []).filter(item => item.status === "open");
    const acceptedIssues = (s.open_issues || []).filter(item =>
      item.status === "accepted"
      && (item.category === "verification" || currentGaps.has(item.summary) || currentConflicts.has(item.summary))
    );
    const deterministic = currentIssues.filter(item =>
      !item.advisory && ["mandatory_evidence_gap", "inconsistency"].includes(item.category)
    );
    const advisory = s.advisory_observations || [];
    const confirmedExceptions = s.confirmed_exceptions || [];
    const rejected = currentIssues.filter(item => item.category === "verification" || item.category === "security");
    html = `<div class="finding-grid">${labelledList("AIRO-confirmed facts", "AIRO-confirmed input", confirmed)}${labelledList("Current deterministic evidence issues", "Deterministic issue — action required", deterministic, "deterministic")}${labelledList("AIRO-accepted residual issues", "Accepted for continued review — not resolved", acceptedIssues)}${labelledList("Evidence claims", "Source-linked claim", claims)}${labelledList("Advisory observations", "LLM/tool advisory — AIRO confirmation required", advisory, "advisory")}${labelledList("Confirmed exceptions", "AIRO-confirmed exception", confirmedExceptions)}${labelledList("Rejected or unverified", "Unverified/rejected result", rejected, "rejected")}</div>` + section("Questionnaire", s.questionnaire || {}) + section("Technical evidence state", {evidence_extraction:s.evidence_extraction || {}, open_issues:s.open_issues || [], evidence_request:s.evidence_request || []}) + section("Invalidated and superseded results", {invalidations:s.invalidations || [], superseded_results:s.superseded_results || []});
  } else if (state.activeTab === "assessment") {
    html = '<p class="warning">The scoring shown is illustrative and is not approved PwC or MRO methodology.</p>' + section("Materiality engine", s.materiality_result || {});
  } else if (state.activeTab === "lod2") {
    html = '<p class="warning">2LoD triggers are answer-based and independent of the final materiality score.</p>' + section("2LoD trigger engine", s.lod2_result || {});
  } else if (state.activeTab === "pack") {
    html = section("AIRO review pack", s.review_pack || {}) + section("Publication draft", s.publication_draft || {});
  } else if (state.activeTab === "calibration") {
    html = `
      <p class="warning">Calibration is an offline rule-governance activity. It does not change a live case or update thresholds automatically.</p>
      <div class="calibration-actions">
        <button id="sensitivity-btn" class="primary">Run case sensitivity</button>
        <button id="backtest-btn" class="secondary">Run demo historical backtest</button>
      </div>
      <div id="calibration-results">${state.calibration ? section("Calibration result", state.calibration) : '<p class="muted">Choose an analysis to inspect how the deterministic rules behave.</p>'}</div>`;
  } else if (state.activeTab === "history") {
    html = (state.current.audit || []).map(event => `<div class="audit-item"><span>${escapeHtml(event.occurred_at)}</span><strong>${escapeHtml(event.action)}</strong><span>${escapeHtml(event.actor)}<br><small>${escapeHtml(pretty(event.details))}</small></span></div>`).join("") || '<p>No audit events.</p>';
  }
  $("tab-content").innerHTML = html;
  if (state.activeTab === "calibration") {
    $("sensitivity-btn").onclick = runSensitivity;
    $("backtest-btn").onclick = runBacktest;
  }
}

async function runSensitivity() {
  try {
    state.calibration = await api("/api/calibration/sensitivity", {method:"POST", body:JSON.stringify({questionnaire:state.current.state.questionnaire})});
    renderTab();
  } catch (error) { toast(error.message, true); }
}

async function runBacktest() {
  try {
    state.calibration = await api("/api/calibration/demo-backtest");
    renderTab();
  } catch (error) { toast(error.message, true); }
}

async function startCurrent() {
  try {
    $("start-btn").disabled = true;
    state.current = await api(`/api/cases/${state.current.case_id}/start`, {method:"POST"});
    renderCurrentCase();
    await loadCases(state.current.case_id);
    toast("Coordinator started and paused or completed safely.");
  } catch (error) { toast(error.message, true); }
  finally { $("start-btn").disabled = false; }
}

async function submitDecision(event) {
  event.preventDefault();
  const previousGate = state.current?.pending_gate;
  let answerUpdates = {};
  try {
    if ($("answer-updates").value.trim()) answerUpdates = JSON.parse($("answer-updates").value);
  } catch (_) { toast("Questionnaire updates must be valid JSON.", true); return; }
  const teamsText = $("confirmed-teams").value.trim();
  const payload = {
    action: $("decision-action").value,
    rationale: $("decision-rationale").value,
    additional_evidence: $("additional-evidence").value,
    answer_updates: answerUpdates,
    override_band: $("override-band").value || null,
    confirmed_teams: teamsText ? teamsText.split(",").map(x => x.trim()).filter(Boolean) : null,
    reviewer: $("reviewer").value || "AIRO demo reviewer",
  };
  try {
    const button = event.target.querySelector("button[type=submit]");
    button.disabled = true;
    state.current = await api(`/api/cases/${state.current.case_id}/resume`, {method:"POST", body:JSON.stringify(payload)});
    renderCurrentCase();
    await loadCases(state.current.case_id);
    const nextGate = state.current.pending_gate;
    toast(nextGate
      ? `${previousGate?.title || "AIRO Gate"} recorded; now waiting at ${nextGate.title}.`
      : `${previousGate?.title || "AIRO decision"} recorded; case status is ${state.current.status.replaceAll("_", " ")}.`);
  } catch (error) { toast(error.message, true); }
  finally { event.target.querySelector("button[type=submit]").disabled = false; }
}

async function createCustomCase(event) {
  event.preventDefault();
  const data = new FormData(event.target);
  const bools = ["approved_pattern","customer_facing","customer_decisioning","personal_data","sensitive_data","external_model_or_supplier","autonomous_actions","critical_process_dependency","human_review_of_outputs"];
  const questionnaire = {
    use_case_name:data.get("use_case_name"), purpose:data.get("purpose"), business_owner:data.get("business_owner"), users:"Internal or declared users", financial_impact:data.get("financial_impact")
  };
  bools.forEach(key => questionnaire[key] = data.has(key));
  try {
    const created = await api("/api/cases", {method:"POST", body:JSON.stringify({questionnaire, evidence_text:data.get("evidence_text")})});
    await loadCases(created.case_id);
    toast("Custom case created.");
  } catch (error) { toast(error.message, true); }
}

document.addEventListener("DOMContentLoaded", async () => {
  $("refresh-btn").onclick = () => loadCases();
  $("start-btn").onclick = startCurrent;
  $("continue-btn").onclick = () => $("gate-panel").scrollIntoView({behavior: "smooth", block: "start"});
  $("decision-form").onsubmit = submitDecision;
  $("decision-action").onchange = () => updateDecisionForm();
  $("case-lookup-form").onsubmit = openCaseById;
  $("custom-case-form").onsubmit = createCustomCase;
  document.querySelectorAll(".tab").forEach(button => button.onclick = () => { state.activeTab = button.dataset.tab; renderTab(); });
  await Promise.all([loadHealth(), loadSamples(), loadCases()]);
});
