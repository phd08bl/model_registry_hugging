const state = { cases: [], samples: {}, current: null, activeTab: "overview", calibration: null, lastEvent: null, sampleQuery: "", sampleProfile: "all" };
const WORK_QUEUE_LIMIT = 5;
const GATE_LABELS = {
  control_exception_review: "Control Exception review",
  evidence_request: "Gate 1 — Evidence request",
  input_confirmation: "Gate 2 — Input confirmation",
  exception_resolution: "Gate 3 — Challenge and exception review",
  final_triage: "Gate 4 — Final triage",
  publication: "Gate 5 — Publication",
};

const CATEGORY_ORDER = [
  "featured_cases",
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
const QUESTIONNAIRE_BOOLEAN_FIELDS = {
  approved_pattern: "Approved pattern",
  customer_facing: "Customer-facing use",
  customer_decisioning: "Customer decisioning",
  personal_data: "Personal data",
  sensitive_data: "Sensitive data",
  external_model_or_supplier: "External model or supplier",
  autonomous_actions: "Autonomous actions",
  critical_process_dependency: "Critical-process dependency",
  human_review_of_outputs: "Human review of outputs",
};

const $ = (id) => document.getElementById(id);
const escapeHtml = (value) => String(value ?? "").replace(/[&<>'"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"}[c]));
const pretty = (value) => JSON.stringify(value ?? {}, null, 2);
const traceBadge = (tag) => `<span class="trace-badge trace-${tag.toLowerCase()}">[${tag}]</span>`;

function activeTeachingControls(controls = {}) {
  return Object.fromEntries(Object.entries(controls).filter(([, value]) =>
    value !== null && value !== "normal"
  ));
}

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
    $("health-label").textContent = `${health.provider.toUpperCase()} · ${health.model}`;
    $("health-message").textContent = health.message;
  } catch (error) {
    $("health-dot").classList.add("bad");
    $("health-label").textContent = "Runtime unavailable";
    $("health-message").textContent = error.message;
  }
}

async function loadSamples() {
  state.samples = await api("/api/samples");
  renderSampleCatalogue();
}

function sampleSearchText(sample) {
  return [
    sample.title,
    sample.short_description,
    sample.likely_airo_attention,
    sample.featured_case_name,
    sample.expected_assigned_profile,
    ...(sample.learning_objectives || []),
    ...(sample.expected_router_actions || []),
    ...(sample.expected_tools || []),
    ...(sample.expected_governance_loops || []),
  ].join(" ").toLowerCase();
}

function sampleDetailRow(label, value, technical = false) {
  const content = Array.isArray(value) ? value : [value];
  const items = content.filter(Boolean);
  const rendered = items.length
    ? items.map(item => technical ? `<code>${escapeHtml(item)}</code>` : escapeHtml(item)).join(technical ? " " : " · ")
    : "None expected";
  return `<div><dt>${escapeHtml(label)}</dt><dd>${rendered}</dd></div>`;
}

async function createSampleCase(key, button) {
  const originalLabel = button.textContent;
  button.disabled = true;
  button.textContent = "Creating case…";
  try {
    const created = await api(`/api/samples/${key}`, {method: "POST"});
    await loadCases(created.case_id);
    toast("Demonstration case created. Start the Coordinator when ready.");
  } catch (error) {
    toast(error.message, true);
  } finally {
    button.disabled = false;
    button.textContent = originalLabel;
  }
}

function renderSampleCatalogue() {
  const container = $("sample-buttons");
  container.innerHTML = "";
  const query = state.sampleQuery.trim().toLowerCase();
  const allEntries = Object.entries(state.samples);
  const filteredEntries = allEntries.filter(([, sample]) =>
    (!query || sampleSearchText(sample).includes(query))
    && (state.sampleProfile === "all" || sample.expected_assigned_profile === state.sampleProfile)
  );
  $("sample-count").textContent = `${filteredEntries.length} of ${allEntries.length} demonstrations shown`;

  CATEGORY_ORDER.forEach(category => {
    const entries = filteredEntries
      .filter(([, sample]) => sample.category === category)
      .sort(([, left], [, right]) => {
        if (category === "featured_cases") {
          return (left.featured_case_number || 99) - (right.featured_case_number || 99);
        }
        return left.title.localeCompare(right.title);
      });
    if (!entries.length) return;

    const group = document.createElement("details");
    group.className = "sample-category-group";
    group.open = category === "featured_cases" || Boolean(query) || state.sampleProfile !== "all";
    const heading = document.createElement("summary");
    heading.className = "sample-profile-heading";
    heading.innerHTML = `
      <span><strong>${escapeHtml(entries[0][1].category_name)}</strong><small>${category === "featured_cases" ? "Required end-to-end journeys covering the Coordinator's major features." : category === "advanced_controls" ? "Additional protected fixtures demonstrating fail-closed controls." : "Policy-assigned examples across the four automation profiles."}</small></span>
      <b>${entries.length}</b>`;
    group.appendChild(heading);

    const cards = document.createElement("div");
    cards.className = "sample-profile-cards";
    entries.forEach(([key, sample]) => {
      const profile = sample.expected_assigned_profile;
      const card = document.createElement("article");
      card.className = `sample-card ${PROFILE_CLASSES[profile] || "profile-human"}`;
      const activeControls = activeTeachingControls(sample.teaching_controls || {});
      const teachingControlSummary = Object.keys(activeControls).length
        ? `${Object.entries(activeControls).map(([name, value]) => `${titleWords(name)}: ${titleWords(value)}`).join("; ")}. ${sample.teaching_controls_notice}`
        : `None active. ${sample.teaching_controls_notice}`;
      card.innerHTML = `
        ${sample.featured_case_number ? `<span class="featured-case-badge">Case ${sample.featured_case_number} · Required coverage</span>` : ""}
        <div class="sample-card-heading"><strong class="sample-card-title">${escapeHtml(sample.title)}</strong><span class="profile-badge ${PROFILE_CLASSES[profile]}">Policy assigned · ${escapeHtml(titleWords(profile))}</span></div>
        <p class="sample-journey">${escapeHtml(sample.short_description)}</p>
        <p class="sample-focus"><b>AIRO focus:</b> ${escapeHtml(sample.likely_airo_attention)}</p>
        <div class="sample-card-meta"><span>${(sample.learning_objectives || []).length} teaching feature${(sample.learning_objectives || []).length === 1 ? "" : "s"}</span><span>Expected: ${escapeHtml(titleWords(sample.expected_final_status || "See runtime"))}</span></div>
        <details class="sample-card-details"><summary>Expected journey and teaching details</summary><dl>
          ${sampleDetailRow("What feature this sample demonstrates", sample.learning_objectives)}
          ${sampleDetailRow("Profile assignment", `Effective ${titleWords(sample.expected_assigned_profile)}; approved maximum ${titleWords(sample.expected_approved_maximum_profile)}`)}
          ${sampleDetailRow("Teaching controls (not a profile override)", teachingControlSummary)}
          ${sampleDetailRow("Expected path", (sample.expected_path || []).join(" → "))}
          ${sampleDetailRow("Expected dynamic actions", sample.expected_router_actions, true)}
          ${sampleDetailRow("Expected tools", sample.expected_tools, true)}
          ${sampleDetailRow("Expected exceptions", sample.expected_exceptions)}
          ${sampleDetailRow("Expected Governance Loops", sample.expected_governance_loops)}
          ${sampleDetailRow("Expected final result", titleWords(sample.expected_final_status || "See runtime"))}
        </dl></details>
        <button type="button" class="primary sample-create-button">Create and open case</button>`;
      const createButton = card.querySelector(".sample-create-button");
      createButton.onclick = () => createSampleCase(key, createButton);
      cards.appendChild(card);
    });
    group.appendChild(cards);
    container.appendChild(group);
  });

  if (!filteredEntries.length) {
    container.innerHTML = '<div class="sample-empty"><strong>No demonstrations match.</strong><p>Change the search or automation-profile filter.</p></div>';
  }
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
  const teachingControls = activeTeachingControls(sample?.teaching_controls || s.demo_controls || {});
  $("case-id").textContent = current.case_id;
  $("case-title").textContent = q.use_case_name || current.title;
  $("case-purpose").textContent = q.purpose || "";
  $("autonomy-badge").textContent = profileName;
  $("autonomy-badge").className = `badge profile-badge ${profileClass}`;
  $("status-badge").textContent = current.status.replaceAll("_", " ");
  $("case-automation-context").innerHTML = `
    ${current.pending_gate ? `<div class="resume-context"><span>Durable resume point</span><strong>${escapeHtml(GATE_LABELS[current.pending_gate.gate_id] || current.pending_gate.title)}</strong><small>The saved Case and LangGraph checkpoint were restored. Review the Gate context and submit an AIRO decision to continue; opening the Case did not execute an action.</small></div>` : ""}
    <div><span>System-assigned profile</span><strong>${escapeHtml(profileName)}</strong><small>${escapeHtml(humaniseAssignmentReason(assignment, sample?.profile_summary))}</small></div>
    <div><span>Approved maximum / governed pattern</span><strong>${escapeHtml(titleWords(assignment.approved_maximum_profile || "human_governed"))}</strong><small>${escapeHtml(assignment.governed_pattern_id ? titleWords(assignment.governed_pattern_id) : "No governed pattern — unmatched normal case")}</small></div>
    <div><span>Illustrative policy version</span><strong>${escapeHtml(assignment.policy_version || "Not assigned")}</strong><small>Evidence issues, deviations or elevated risk can downgrade permissions; the LLM cannot upgrade them.</small></div>
    <div><span>Protected teaching controls (not a profile override)</span><strong>${escapeHtml(Object.keys(teachingControls).length ? pretty(teachingControls) : "None")}</strong><small>These fixture-only controls demonstrate failure and sampling paths. The policy-assigned profile above remains authoritative.</small></div>
    <div><span>Actual current gate</span><strong>${escapeHtml(actualGate)}</strong></div>
    <div><span>Why this route</span><strong>${escapeHtml(gateExplanation)}</strong></div>
    ${sample ? `<div class="demo-steps"><span>Demonstration expectations</span><strong>${escapeHtml(sample.short_description)}</strong><small><b>Expected path:</b> ${escapeHtml(sample.expected_path.join(" → "))}</small><small><b>Dynamic actions:</b> ${escapeHtml(sample.expected_router_actions.join(", ") || "None")}</small><small><b>Tools:</b> ${escapeHtml(sample.expected_tools.join(", ") || "No execution expected")}</small><small><b>Exceptions:</b> ${escapeHtml(sample.expected_exceptions.join(" · ") || "None expected")}</small><small><b>Governance Loops:</b> ${escapeHtml(sample.expected_governance_loops.join(", ") || "None expected")}</small><small><b>Expected final result:</b> ${escapeHtml(sample.expected_final_status || "See runtime")}</small><ol>${sample.interactive_steps.map(step => `<li>${escapeHtml(step)}</li>`).join("")}</ol><small>Teaching expectations are explanatory metadata; authoritative runtime Case State decides the actual route.</small></div>` : ""}`;
  $("start-btn").classList.toggle("hidden", current.status !== "DRAFT");
  $("continue-btn").classList.toggle("hidden", !current.pending_gate);
  $("continue-btn").textContent = current.pending_gate
    ? `Continue at ${GATE_LABELS[current.pending_gate.gate_id] || current.pending_gate.title}`
    : "Continue at current Gate";
  renderCaseJourney(s, current.pending_gate);
  renderCoordinator(s, current.pending_gate);
  renderGate(current.pending_gate);
  renderExternalEvent(current.pending_event || s.active_external_event);
  renderTab();
}

function renderCaseJourney(s, gate) {
  const completed = new Set(s.completed_nodes || []);
  const stale = new Set(s.stale_outputs || []);
  const lifecycle = s.lifecycle_status || "NEW";
  const phase = s.domain_phase || "INTAKE";
  const phases = [
    {key:"intake", label:"Intake", phase:"INTAKE", nodes:["normalise_intake"]},
    {key:"evidence", label:"Evidence preparation", phase:"EVIDENCE_REVIEW", nodes:["observe_case", "evidence_gate"], gateId:"evidence_request", staleFields:["evidence_extraction", "confirmed_facts"]},
    {key:"confirmation", label:"Input confirmation", phase:"INPUT_CONFIRMATION", nodes:["input_gate"], gateId:"input_confirmation", staleFields:["confirmed_facts"]},
    {key:"assessment", label:"Assessment and 2LoD", phase:"ASSESSMENT", nodes:["decision_engines"], staleFields:["materiality_result", "lod2_result"]},
    {key:"challenge", label:"Exception review", phase:"CHALLENGE", nodes:["challenge_assessment", "exception_gate"], gateId:"exception_resolution"},
    {key:"decision", label:"Final AIRO decision", phase:"FINAL_DECISION", nodes:["review_pack", "final_gate"], gateId:"final_triage", staleFields:["review_pack", "final_outcome"]},
    {key:"publication", label:"Publication", phase:"PUBLICATION", nodes:["publication_gate", "publish"], gateId:"publication", staleFields:["publication_draft"]},
  ];
  const phaseIndex = new Map(phases.map((item, index) => [item.phase, index]));
  const gateIndex = new Map(phases.filter(item => item.gateId).map((item, index) => [item.gateId, phases.indexOf(item)]));
  const currentIndex = gateIndex.get(gate?.gate_id) ?? phaseIndex.get(phase) ?? 0;
  const gateEvaluations = new Map();
  (s.autonomy_log || []).forEach(item => gateEvaluations.set(item.gate_id, item));
  const gateDecisions = new Set((s.human_decisions || []).map(item => item.gate_id));
  const hasReplanning = Boolean((s.invalidations || []).length);
  const activeEvent = s.active_external_event?.status === "WAITING" ? s.active_external_event : null;

  const phaseName = phases[currentIndex]?.label || phase.replaceAll("_", " ");
  let controlTone = "working";
  let controlTitle = `Coordinator working in ${phaseName}`;
  let controlReason = coordinatorCurrentAction(s, gate).reason;
  let waitingOn = "AIRO Case Coordinator";
  let nextTransition = (s.supervisor_decision?.allowed_actions || []).map(titleWords).join(", ") || "Deterministic reassessment";
  if (s.control_exception?.status === "OPEN" || lifecycle === "CONTROL_EXCEPTION") {
    controlTone = "exception";
    controlTitle = `Control Exception: ${s.control_exception?.code || "review required"}`;
    controlReason = s.control_exception?.reason || "The workflow stopped because no safe transition was available.";
    waitingOn = "AIRO Control Exception reviewer";
    nextTransition = (gate?.allowed_actions || s.control_exception?.allowed_recovery_actions || []).map(titleWords).join(", ") || "Fail-safe review";
  } else if (activeEvent || lifecycle === "AWAITING_EXTERNAL_EVENT") {
    controlTone = "event";
    controlTitle = `Waiting for external event: ${titleWords(activeEvent?.event_type || "response")}`;
    controlReason = activeEvent ? `Only a validated response from ${activeEvent.expected_source} with the expected correlation ID can resume this Case.` : "A correlated external response is required.";
    waitingOn = activeEvent?.expected_source || "Expected external source";
    nextTransition = "Validate event, update evidence, then selectively replan";
  } else if (gate || lifecycle === "AWAITING_HUMAN") {
    controlTone = "human";
    controlTitle = `AIRO decision required: ${gate?.decision_required || gate?.title || phaseName}`;
    controlReason = gate?.reason || "A protected human judgement is required before the Coordinator can continue.";
    waitingOn = "AIRO reviewer";
    nextTransition = (gate?.allowed_actions || []).map(titleWords).join(", ") || "Submit an authorised Gate decision";
  } else if (lifecycle === "COMPLETED" || s.status === "CLOSED") {
    controlTone = "complete";
    controlTitle = "Case completed";
    controlReason = "The deterministic completion guard passed and publication was reconciled.";
    waitingOn = "No outstanding actor";
    nextTransition = "None — Case is read-only";
  } else if (lifecycle === "CANCELLED" || s.status === "CANCELLED") {
    controlTone = "cancelled";
    controlTitle = "Case cancelled";
    controlReason = "Processing stopped without recording an approval.";
    waitingOn = "No outstanding actor";
    nextTransition = "None — Case is read-only";
  } else if (lifecycle === "FAILED_SAFE" || s.status === "ERROR") {
    controlTone = "exception";
    controlTitle = "Case failed safe";
    controlReason = "No further automated transition is permitted; inspect the protected audit record.";
    waitingOn = "AIRO and technical support";
    nextTransition = "Controlled investigation only";
  } else if (lifecycle === "NEW" || s.status === "DRAFT") {
    controlTone = "ready";
    controlTitle = "Ready to start the Coordinator";
    controlReason = "Starting invokes the governed StateGraph; opening the Case alone never executes an action.";
    waitingOn = "Case operator";
    nextTransition = "Start Coordinator";
  }

  $("current-control-state").className = `current-control-state control-${controlTone}`;
  $("current-control-state").innerHTML = `
    <div class="control-state-heading"><span class="control-status">${escapeHtml(titleWords(lifecycle))}</span><strong>${escapeHtml(controlTitle)}</strong><p>${escapeHtml(controlReason)}</p></div>
    <div class="control-state-facts">
      <div class="control-state-fact"><span>Domain phase</span><strong>${escapeHtml(phaseName)}</strong></div>
      <div class="control-state-fact"><span>Governance Loop</span><strong>${escapeHtml(s.active_governance_loop ? titleWords(s.active_governance_loop) : "None active")}</strong></div>
      <div class="control-state-fact"><span>Waiting on</span><strong>${escapeHtml(waitingOn)}</strong></div>
      <div class="control-state-fact"><span>Next permitted transition</span><strong>${escapeHtml(nextTransition)}</strong></div>
    </div>`;

  $("workflow-steps").innerHTML = phases.map((item, index) => {
    const evaluation = item.gateId ? gateEvaluations.get(item.gateId) : null;
    const explicitDone = item.nodes.some(node => completed.has(node));
    const done = lifecycle === "COMPLETED" || s.status === "CLOSED" || explicitDone || index < currentIndex;
    const isStale = (item.staleFields || []).some(field => stale.has(field));
    const isCurrent = index === currentIndex && !["COMPLETED", "CANCELLED"].includes(lifecycle);
    const noExceptionLoop = item.key === "challenge" && evaluation?.required === false && !(s.exceptions || []).length && !(s.confirmed_exceptions || []).length;
    let status = "pending";
    let icon = "○";
    let statusLabel = lifecycle === "CANCELLED" ? "Not reached — Case cancelled" : "Pending — not current";
    if (isCurrent) {
      const historicalHigh = Math.max(...[...completed].map(node => phases.findIndex(stage => stage.nodes.includes(node))), currentIndex);
      status = controlTone === "human" || controlTone === "event"
        ? "waiting"
        : controlTone === "exception"
          ? "exception"
          : hasReplanning && currentIndex < historicalHigh
            ? "reopened"
            : "current";
      icon = status === "reopened" ? "↻" : status === "exception" ? "!" : status === "waiting" ? "◷" : "●";
      if (controlTone === "human") statusLabel = "Waiting for AIRO";
      else if (controlTone === "event") statusLabel = "Waiting for external event";
      else if (controlTone === "exception") statusLabel = "Paused by Control Exception";
      else if (controlTone === "ready") statusLabel = "Ready to start";
      else statusLabel = status === "reopened" ? "Reopened after a governed change" : "Current phase";
    } else if (isStale) {
      status = "stale";
      icon = "!";
      statusLabel = "Stale — replacement required";
    } else if (noExceptionLoop) {
      status = "skipped";
      icon = "−";
      statusLabel = "Not required — no exception loop";
    } else if (done) {
      status = "complete";
      icon = "✓";
      statusLabel = item.key === "assessment" ? "Deterministic results current" : "Completed";
    }

    let governanceLabel = "No Human Gate in this phase";
    if (item.gateId) {
      if (gate?.gate_id === item.gateId) governanceLabel = "AIRO Gate is active";
      else if (gateDecisions.has(item.gateId)) governanceLabel = "AIRO decision recorded";
      else if (evaluation?.required === false) governanceLabel = "Gate skipped by deterministic policy";
      else if (done && item.gateId === "evidence_request") governanceLabel = "Gate not triggered";
      else if (done) governanceLabel = "Gate completed or not applicable";
      else governanceLabel = "Gate evaluated only if required";
    }
    const invalidation = (s.invalidations || []).findLast?.(record => (item.staleFields || []).includes(record.invalidated_result));
    return `<article class="journey-stage stage-${status}" role="listitem" aria-current="${isCurrent ? "step" : "false"}">
      <div class="journey-stage-top"><span class="journey-icon" aria-hidden="true">${icon}</span><strong>${escapeHtml(item.label)}</strong></div>
      <span class="journey-status">${escapeHtml(statusLabel)}</span>
      <small>${escapeHtml(governanceLabel)}</small>
      ${invalidation ? `<small class="journey-invalidation ${isCurrent ? "current-invalidation" : ""}"><b>${isCurrent ? "Why reopened:" : "Why stale:"}</b> ${escapeHtml(invalidation.reason || invalidation.triggering_change)}</small>` : ""}
    </article>`;
  }).join("");
}

function selectionMethodLabel(source, supervisor = {}) {
  const labels = {
    deterministic_policy: "Deterministic",
    llm_router: "Bounded LLM recommendation",
    fallback: "Deterministic fallback",
  };
  if (labels[source]) return labels[source];
  if (supervisor.mandatory_action) return "Deterministic";
  if (supervisor.llm_recommender_permitted) return "Bounded LLM recommendation";
  return "Deterministic transition";
}

function coordinatorCurrentAction(s, gate) {
  if (gate) return {
    action: `Await AIRO decision: ${gate.decision_required || gate.title}`,
    reason: gate.reason || "A protected Governance Gate reserves this judgement to AIRO.",
  };
  if (s.active_external_event?.status === "WAITING") return {
    action: `Wait for ${s.active_external_event.event_type}`,
    reason: `A validated event from ${s.active_external_event.expected_source} is required before the same Case can resume.`,
  };
  if (s.control_exception?.status === "OPEN") return {
    action: "Hold in Control Exception",
    reason: s.control_exception.reason,
  };
  if (s.status === "CLOSED") return {action:"Case completed", reason:"All governed completion checks passed."};
  if (s.status === "CANCELLED") return {action:"Case cancelled", reason:"No approval was recorded."};
  if (s.status === "ERROR") return {action:"Fail closed", reason:"Inspect the protected audit record."};
  if (s.current_action_proposal?.selected_action) return {
    action: s.current_action_proposal.selected_action,
    reason: s.current_action_proposal.reason || "Selected within the current policy boundary.",
  };
  return {
    action: s.recommended_next_action?.action || "Reassess authoritative Case State",
    reason: s.recommended_next_action?.reason || "No tool action is currently in flight.",
  };
}

function completionCriteriaView(s) {
  const configured = s.completion_criteria || [];
  const evaluation = s.completion_evaluation || {};
  const checks = Object.entries(evaluation.criteria || {});
  const configuredRows = configured.map(criterion => `<li><span>${escapeHtml(criterion)}</span><b>${evaluation.complete ? "MET" : checks.length ? "EVALUATED BELOW" : "PENDING"}</b></li>`).join("");
  const checkRows = checks.map(([name, met]) => `<li><span>${escapeHtml(name.replaceAll("_", " "))}</span><b class="${met ? "criterion-met" : "criterion-blocked"}">${met ? "PASS" : "BLOCKED"}</b></li>`).join("");
  return `<details class="completion-panel"><summary>Completion criteria and deterministic checks</summary>
    <h4>Configured completion criteria</h4>
    ${configuredRows ? `<ul class="criteria-list">${configuredRows}</ul>` : "<p>No governed completion criteria are configured.</p>"}
    <h4>Latest deterministic completion checks</h4>
    ${checkRows ? `<ul class="criteria-list">${checkRows}</ul>` : "<p>Checks run before closure; no evaluation has run yet.</p>"}
  </details>`;
}

function renderCoordinator(s, gate) {
  const stale = new Set(s.stale_outputs || []);
  const materiality = stale.has("materiality_result") ? "STALE — replacement required" : s.materiality_result?.proposed_materiality_band || "Not calculated";
  const teams = stale.has("lod2_result") ? [] : s.lod2_result?.teams || [];
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
  const supervisor = s.supervisor_decision || {};
  const supervisorAllowed = supervisor.allowed_actions || s.policy_assessment?.permitted_actions || [];
  const gateAllowed = gate?.allowed_actions || [];
  const remainingLoops = Math.max(0, (s.max_evidence_cycles ?? 0) - (s.evidence_cycle ?? 0));
  const invalidated = s.invalidations || [];
  const currentAction = coordinatorCurrentAction(s, gate);
  const currentAuthorisation = s.current_action_authorisation || {};
  const latestProposal = latestTrace?.proposal || {};
  const selectionMethod = latestTrace
    ? selectionMethodLabel(latestTrace.selection_source, supervisor)
    : "Not selected";
  const currentOpenObjective = (s.open_objectives || [])[0];
  const completion = s.completion_evaluation || {};
  const completionChecks = Object.values(completion.criteria || {});
  const completionProgress = completionChecks.length
    ? `${completionChecks.filter(Boolean).length} of ${completionChecks.length} criteria met`
    : `0 of ${(s.completion_criteria || []).length} criteria evaluated`;
  const workspaceHeading = gate
    ? `Paused at ${GATE_LABELS[gate.gate_id] || gate.title}`
    : currentAction.action;
  const workspaceReason = gate
    ? "Select an allowed decision in the Human Governance panel to resume this Case."
    : currentAction.reason;
  const traceRows = (s.agent_action_trace || []).slice(-5).map(item => `
    <tr><td>${escapeHtml(item.selection_source)}</td><td>${escapeHtml(item.proposal?.selected_action)}</td><td>${escapeHtml(item.invocation?.tool_id || "No tool")}</td><td>${escapeHtml(item.verification?.disposition || "Pending")}</td><td>${escapeHtml(item.remaining_tool_calls)}</td></tr>`).join("");
  $("coordinator-summary").innerHTML = `
    <div class="workspace-focus"><span>Current control point</span><strong>${escapeHtml(workspaceHeading)}</strong><p>${escapeHtml(workspaceReason)}</p></div>
    <div class="summary-grid priority-summary">
      <div class="summary-tile"><span>Lifecycle / domain phase</span><strong>${escapeHtml(titleWords(s.lifecycle_status || "NEW"))} / ${escapeHtml(titleWords(s.domain_phase || "INTAKE"))}</strong><small>Case State v${escapeHtml(s.case_state_version || 1)}</small></div>
      <div class="summary-tile"><span>Proposed materiality</span><strong>${escapeHtml(titleWords(materiality))}</strong></div>
      <div class="summary-tile"><span>Proposed 2LoD teams</span><strong>${teams.length ? escapeHtml(teams.join(", ")) : "Not calculated"}</strong></div>
      <div class="summary-tile"><span>Current open objective</span><strong>${escapeHtml(currentOpenObjective?.action ? titleWords(currentOpenObjective.action) : "None")}</strong><small>${escapeHtml(currentOpenObjective?.reason || "")}</small></div>
      <div class="summary-tile"><span>Active Governance Loop</span><strong>${escapeHtml(s.active_governance_loop ? titleWords(s.active_governance_loop) : "None")}</strong></div>
      ${gate ? `<div class="summary-tile"><span>Current AIRO Gate allowed decisions</span><strong>${gateAllowed.length ? escapeHtml(gateAllowed.map(titleWords).join(", ")) : "None recorded"}</strong></div>` : ""}
      <div class="summary-tile"><span>Completion progress</span><strong>${completion.complete ? "Complete" : escapeHtml(completionProgress)}</strong><small>${escapeHtml((completion.blockers || []).join(" / ") || "Evaluation runs before closure.")}</small></div>
    </div>
    <details class="workspace-details"><summary>Coordinator controls, budgets and recent history</summary><div class="summary-grid">
      <div class="summary-tile"><span>Compatibility state label</span><strong>${escapeHtml(titleWords(s.status || "DRAFT"))}</strong></div>
      <div class="summary-tile"><span>Recommended next action</span><strong>${escapeHtml(next)}</strong></div>
      <div class="summary-tile"><span>Case objective</span><strong>${escapeHtml(s.case_objective?.statement || "Not assigned")}</strong></div>
      <div class="summary-tile"><span>Unresolved objectives</span><strong>${escapeHtml((s.open_objectives || []).map(item => item.action).join(", ") || "None")}</strong></div>
      <div class="summary-tile"><span>Most recent selected action / method</span><strong>${escapeHtml(latestProposal.selected_action ? titleWords(latestProposal.selected_action) : "No action selected")} / ${escapeHtml(selectionMethod)}</strong><small>${escapeHtml(latestProposal.reason || latestTrace?.rationale || "No historical selection rationale recorded.")}</small></div>
      <div class="summary-tile"><span>Current in-flight authorisation</span><strong>${escapeHtml(currentAuthorisation.decision || "No tool action in flight")}</strong><small>${escapeHtml(currentAuthorisation.reason || "Completed authorisations remain in the action timeline.")}</small></div>
      <div class="summary-tile"><span>Latest evidence tool</span><strong>${escapeHtml(latestTrace?.invocation?.tool_id || "Not called")}</strong><small>Historical action</small></div>
      <div class="summary-tile"><span>Latest verification</span><strong>${escapeHtml(latestTrace?.verification?.disposition || "Not available")}</strong><small>${escapeHtml((latestTrace?.verification?.issues || []).join(" · "))}</small></div>
      <div class="summary-tile"><span>Tool / retry / loop budget</span><strong>${s.remaining_tool_calls ?? s.max_tool_calls ?? "Not set"} tools · ${supervisor.remaining_retries ?? "—"} retries</strong><small>${supervisor.remaining_total_loops ?? "—"} Coordinator loops remain.</small></div>
      <div class="summary-tile"><span>Evidence loops</span><strong>${s.evidence_cycle || 0} used · ${remainingLoops} remaining</strong></div>
      <div class="summary-tile"><span>LLM runtime</span><strong>${escapeHtml(s.llm_runtime?.selected_runtime || s.llm_runtime?.runtime || "Not called")}</strong></div>
      <div class="summary-tile"><span>Policy Supervisor allowed actions</span><strong>${supervisorAllowed.length ? escapeHtml(supervisorAllowed.map(titleWords).join(", ")) : "None - paused, reassessing, or complete"}</strong></div>
      <div class="summary-tile"><span>Prohibited actions</span><strong>${escapeHtml((supervisor.prohibited_actions || []).map(titleWords).join(", ") || "None recorded")}</strong></div>
      <div class="summary-tile"><span>Last AIRO decision</span><strong>${escapeHtml(latestDecision?.action ? titleWords(latestDecision.action) : "None yet")}</strong><small>${escapeHtml(latestDecision?.rationale || "")}</small></div>
    </div></details>
    ${completionCriteriaView(s)}
    ${s.active_external_event ? `<div class="attention"><strong>Awaiting external event</strong><p>${escapeHtml(s.active_external_event.event_type)} from ${escapeHtml(s.active_external_event.expected_source)}; correlation ${escapeHtml(s.active_external_event.correlation_id)}.</p></div>` : ""}
    ${s.control_exception ? `<div class="attention rejected"><strong>Control Exception: ${escapeHtml(s.control_exception.code)}</strong><p>${escapeHtml(s.control_exception.reason)}</p></div>` : ""}
    ${s.completion_evaluation && Object.keys(s.completion_evaluation).length ? `<div class="attention"><strong>Completion guard</strong><p>${s.completion_evaluation.complete ? "All deterministic completion criteria passed." : escapeHtml((s.completion_evaluation.blockers || []).join(" / ") || "The completion guard has not passed; expand the criteria checks for details.")}</p></div>` : ""}
    <div class="issue-routing"><div><strong>Evidence and issue records remain separated.</strong><p>Six governed panels distinguish gaps, conflicts, advisory observations, exceptions, confirmed facts and candidate facts.</p></div><button id="open-evidence-view" type="button" class="secondary compact-button">Open Evidence register</button></div>
    ${invalidated.length || (s.superseded_results || []).length ? `<div class="explanation-grid"><div><h4>Replanning audit history</h4><p>${invalidated.length} invalidation record(s); ${(s.superseded_results || []).length} preserved previous result(s). Historical records do not indicate a current issue.</p></div></div>` : ""}
    <details class="trace-summary"><summary>Recent action trace</summary>${traceRows ? `<table><thead><tr><th>Selected by</th><th>Action</th><th>Tool</th><th>Verification</th><th>Budget left</th></tr></thead><tbody>${traceRows}</tbody></table>` : "<p>No action recorded yet.</p>"}</details>
  `;
  $("open-evidence-view").onclick = () => openCaseTab("evidence");
}

function requirementValue(value) {
  if (value === null || value === undefined || value === "") return "Not recorded";
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (Array.isArray(value)) return value.length ? value.join(", ") : "None";
  if (typeof value === "object") return pretty(value);
  return String(value);
}

function renderHumanRequirement(requirement, index) {
  const comparisons = requirement.field ? `
    <div class="requirement-comparison">
      <div><span>Questionnaire field</span><strong>${escapeHtml(titleWords(requirement.field))}</strong></div>
      <div><span>Current answer</span><strong>${escapeHtml(requirementValue(requirement.current_value))}</strong></div>
      <div><span>Evidence indicates</span><strong>${escapeHtml(requirementValue(requirement.evidence_supported_value))}</strong></div>
    </div>` : requirement.current_value !== null && requirement.current_value !== undefined ? `
    <div class="requirement-current"><span>Current proposal or state</span><strong>${escapeHtml(requirementValue(requirement.current_value))}</strong></div>` : "";
  const citations = (requirement.citations || []).map(item => `
    <li><strong>${escapeHtml(item.claim || "Supporting evidence")}</strong><small>${escapeHtml(item.source || "submitted_evidence")}${item.line_refs?.length ? ` Â· lines ${escapeHtml(item.line_refs.join(", "))}` : ""}</small></li>`).join("");
  return `<article class="human-requirement ${requirement.blocking ? "blocking" : ""}">
    <div class="requirement-heading"><span class="requirement-number">${index + 1}</span><div><strong>${escapeHtml(requirement.title)}</strong><small>${escapeHtml(titleWords(requirement.kind))}${requirement.blocking ? " Â· blocks progress" : ""}</small></div></div>
    <p>${escapeHtml(requirement.description)}</p>
    ${comparisons}
    <div class="required-response"><span>What you need to do</span><strong>${escapeHtml(requirement.required_response)}</strong></div>
    ${(requirement.required_artifacts || []).length ? `<div class="requirement-list"><span>Provide or identify</span>${readableList(requirement.required_artifacts)}</div>` : ""}
    ${(requirement.review_items || []).length ? `<details class="requirement-more"><summary>Review ${(requirement.review_items || []).length} supporting item${requirement.review_items.length === 1 ? "" : "s"}</summary>${readableList(requirement.review_items)}</details>` : ""}
    ${citations ? `<details class="requirement-more"><summary>View linked evidence and citations</summary><ul class="requirement-citations">${citations}</ul></details>` : ""}
  </article>`;
}

function renderDecisionOptions(gate, selectedAction) {
  const options = (gate.allowed_actions || []).map(action => {
    const impact = gate.action_impacts?.[action] || {};
    const recommended = action === gate.recommended_action;
    return `<label class="decision-option ${impact.tone === "caution" ? "caution" : ""}">
      <input type="radio" name="gate-decision" value="${escapeHtml(action)}" ${action === selectedAction ? "checked" : ""} />
      <span><strong>${escapeHtml(titleWords(action))}${recommended ? '<b class="recommended-badge">Recommended</b>' : ""}</strong><small>${escapeHtml(impact.effect || gate.action_effects?.[action] || "Apply the governed transition.")}</small><em>${impact.rationale_required ? "Rationale required" : "Rationale optional"}</em></span>
    </label>`;
  }).join("");
  $("decision-options").innerHTML = options;
  document.querySelectorAll('input[name="gate-decision"]').forEach(input => {
    input.onchange = () => {
      $("decision-action").value = input.value;
      updateDecisionForm(gate);
    };
  });
}

function currentAnswerUpdates() {
  try {
    return $("answer-updates").value.trim() ? JSON.parse($("answer-updates").value) : {};
  } catch (_) {
    return {};
  }
}

function renderGuidedAnswerControls(gate, action) {
  const relevantFields = [...new Set((gate.required_inputs || []).map(item => item.field).filter(Boolean))];
  const useAllFields = ["edit_answers", "amend_material_fact"].includes(action);
  const fields = useAllFields ? Object.keys(QUESTIONNAIRE_BOOLEAN_FIELDS) : relevantFields;
  const updates = currentAnswerUpdates();
  const questionnaire = state.current?.state?.questionnaire || {};
  $("guided-answer-controls").innerHTML = fields.map(field => `
    <label>${escapeHtml(QUESTIONNAIRE_BOOLEAN_FIELDS[field] || titleWords(field))}<small>Current: ${questionnaire[field] ? "Yes" : "No"}</small>
      <select data-answer-field="${escapeHtml(field)}">
        <option value="">No change</option>
        <option value="true" ${updates[field] === true ? "selected" : ""}>Change to Yes</option>
        <option value="false" ${updates[field] === false ? "selected" : ""}>Change to No</option>
      </select>
    </label>`).join("");
  document.querySelectorAll("[data-answer-field]").forEach(select => {
    select.onchange = () => {
      const next = currentAnswerUpdates();
      if (!select.value) delete next[select.dataset.answerField];
      else next[select.dataset.answerField] = select.value === "true";
      $("answer-updates").value = Object.keys(next).length ? JSON.stringify(next, null, 2) : "";
      $("answer-updates").setCustomValidity("");
      showDecisionFormError("");
    };
  });
  return fields.length > 0;
}

function renderDecisionImpact(gate, action) {
  const impact = gate.action_impacts?.[action] || {};
  const row = (label, values) => (values || []).length
    ? `<div><span>${escapeHtml(label)}</span><strong>${escapeHtml(values.join(" Â· "))}</strong></div>`
    : "";
  $("decision-impact-preview").innerHTML = `
    <summary><span>Expected next step</span><strong>${escapeHtml(impact.next_step || "Apply the governed transition.")}</strong></summary>
    <div class="decision-impact-detail"><h5>What this decision will do</h5>
    ${row("Will change", impact.will_change)}
    ${row("Will rerun", impact.will_rerun)}
    ${row("Will remain current", impact.will_remain_current)}
    </div>`;
}

function renderGate(gate) {
  const panel = $("gate-panel");
  if (!gate) { panel.classList.add("hidden"); $("gate-support").innerHTML = ""; return; }
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
  const allowed = (gate.allowed_actions || []).map(action => ({
    action,
    effect: gate.action_effects?.[action] || "Apply the governed transition.",
    rationale_required: Boolean(gate.rationale_required?.[action]),
  }));
  const decisionHistory = (state.current?.state?.human_decisions || []).filter(item =>
    item.gate_id === gate.gate_id
  );
  const evidenceItems = [
    ...(gate.supporting_facts || []).map(item => typeof item === "string" ? item : item.summary || item.claim || pretty(item)),
    ...(gate.evidence || []).map(item => typeof item === "string" ? item : item.summary || item.claim || pretty(item)),
    ...(gate.citations || []).map(item => typeof item === "string" ? item : item.source_reference || item.source || pretty(item)),
  ];
  const evidencePreview = evidenceItems.slice(0, 5);
  const remainingEvidenceCount = Math.max(0, evidenceItems.length - evidencePreview.length);
  const requirements = (gate.required_inputs || []).length ? gate.required_inputs : [{
    requirement_id: "legacy-gate-task",
    kind: "fact_confirmation",
    title: "Review and record the required decision",
    description: gate.decision_required || gate.summary,
    required_response: gate.reason,
    blocking: true,
  }];
  const blockingCount = gate.blocking_item_count ?? requirements.filter(item => item.blocking).length;
  $("gate-context").innerHTML = `
    <div class="gate-decision-focus"><span>Your task</span><strong>${blockingCount} blocking item${blockingCount === 1 ? "" : "s"} require${blockingCount === 1 ? "s" : ""} an AIRO decision</strong><p>${escapeHtml(gate.decision_required || gate.summary)}</p></div>
    <div class="human-requirements">${requirements.map(renderHumanRequirement).join("")}</div>`;
  $("gate-support").innerHTML = `
    <details class="decision-support"><summary>Review decision support, evidence and allowed effects</summary>
    <div class="gate-context-grid">
      <div><b>Relevant deterministic rule</b>${readableRecord(gate.relevant_deterministic_rule || gate.autonomy || {}, "No rule context recorded")}</div>
      <div><b>Evidence and citations</b>${readableList(evidencePreview, "No supporting citation recorded")}${remainingEvidenceCount ? `<details class="evidence-more"><summary>Show ${remainingEvidenceCount} more evidence item${remainingEvidenceCount === 1 ? "" : "s"}</summary>${readableList(evidenceItems.slice(5))}</details>` : ""}</div>
      <div><b>Coordinator recommendation</b>${readableRecord(gate.coordinator_recommendation || {}, "No recommendation recorded")}</div>
      <div><b>Uncertainty and verification</b>${readableRecord(gate.uncertainty_and_verification || {}, "No uncertainty recorded")}</div>
    </div>
    <section class="allowed-decision-section"><h4>Allowed decisions and effects</h4><div class="allowed-decision-grid">${allowed.map(item => `<div><strong>${escapeHtml(titleWords(item.action))}</strong><p>${escapeHtml(item.effect)}</p><small>${item.rationale_required ? "Rationale required" : "Rationale optional"}</small></div>`).join("")}</div></section>
    <section class="decision-history-summary"><h4>Previous decisions at this Gate</h4>${decisionHistory.length ? decisionHistory.map(item => `<div><strong>${escapeHtml(titleWords(item.action))}</strong><span>${escapeHtml(item.reviewer || "AIRO reviewer")}</span><p>${escapeHtml(item.rationale || "No rationale recorded")}</p></div>`).join("") : '<p class="muted">No previous decision at this Gate.</p>'}</section>
    <details class="technical-record"><summary>Additional structured Gate context</summary><pre class="json">${escapeHtml(pretty(displayContext))}</pre></details></details>`;
  $("decision-action").innerHTML = (gate.allowed_actions || []).map(action => `<option value="${escapeHtml(action)}">${escapeHtml(titleWords(action))}</option>`).join("");
  const initialAction = (gate.allowed_actions || []).includes(gate.recommended_action)
    ? gate.recommended_action
    : (gate.allowed_actions || [])[0];
  $("decision-action").value = initialAction || "";
  renderDecisionOptions(gate, initialAction);
  $("decision-rationale").value = "";
  $("additional-evidence").value = "";
  $("answer-updates").value = "";
  $("override-band").value = "";
  $("confirmed-teams").value = "";
  updateDecisionForm(gate);
}

function renderExternalEvent(expectation) {
  const panel = $("event-panel");
  const lastEventForCase = state.lastEvent?.case_id === state.current?.case_id ? state.lastEvent : null;
  if (!expectation && !lastEventForCase) { panel.classList.add("hidden"); return; }
  panel.classList.remove("hidden");
  const replayOnly = !expectation && Boolean(lastEventForCase);
  $("event-contract").innerHTML = `<pre>${escapeHtml(pretty(expectation || {last_accepted_event: lastEventForCase, status: "COMPLETED - replay available for idempotency demonstration"}))}</pre>`;
  $("event-source").value = expectation?.expected_source || lastEventForCase?.source || "business_owner";
  $("event-source").disabled = replayOnly;
  $("event-artifact").disabled = replayOnly;
  $("event-form").querySelector('button[type="submit"]').disabled = replayOnly;
  $("external-response-btn").disabled = replayOnly;
  $("invalid-event-btn").disabled = replayOnly;
  $("timeout-event-btn").disabled = replayOnly;
  $("duplicate-event-btn").disabled = !lastEventForCase;
}

function updateDecisionForm(gate = state.current?.pending_gate) {
  if (!gate) return;
  showDecisionFormError("");
  const action = $("decision-action").value;
  const materialAmendment = action === "amend_material_fact";
  const showEvidence = (gate.gate_id === "evidence_request" && action === "add_evidence") || materialAmendment;
  const showAnswers = showEvidence || action === "edit_answers" || materialAmendment;
  const showOverride = gate.gate_id === "final_triage" && action === "override";
  $("additional-evidence-row").classList.toggle("hidden", !showEvidence);
  $("answer-updates-row").classList.toggle("hidden", !showAnswers);
  const hasGuidedAnswers = showAnswers && renderGuidedAnswerControls(gate, action);
  $("guided-answer-row").classList.toggle("hidden", !hasGuidedAnswers);
  $("answer-updates-row").open = showAnswers && !hasGuidedAnswers;
  $("override-band-row").classList.toggle("hidden", !showOverride);
  $("confirmed-teams-row").classList.toggle("hidden", !showOverride);
  const rationaleRequired = Boolean(gate.rationale_required?.[action]);
  $("decision-rationale").required = rationaleRequired;
  $("decision-rationale").placeholder = rationaleRequired
    ? "Required: explain the accountable AIRO decision"
    : "Optional decision note";
  const effect = gate.action_effects?.[action] || "The Coordinator will apply this governed transition.";
  const requiredFields = gate.action_impacts?.[action]?.required_fields || [];
  $("gate-action-help").textContent = `${effect}${requiredFields.length ? ` Required input: ${requiredFields.map(titleWords).join(" or ")}.` : ""}${rationaleRequired ? " A rationale is required." : ""}`;
  document.querySelectorAll(".decision-option").forEach(option => {
    option.classList.toggle("selected", option.querySelector("input")?.value === action);
  });
  renderDecisionImpact(gate, action);
}

function section(title, value) {
  return `<details class="data-section technical-record"><summary>${escapeHtml(title)}</summary><pre class="json">${escapeHtml(pretty(value))}</pre></details>`;
}

function words(value) {
  return String(value ?? "").replaceAll("_", " ");
}

function titleWords(value) {
  return words(value).toLowerCase().replace(/\b\w/g, character => character.toUpperCase());
}

function humaniseAssignmentReason(assignment = {}, fallback = "") {
  if (!Object.keys(assignment).length) return fallback || "Deterministic policy controls permissions and Gate progression.";
  const effective = titleWords(assignment.effective_profile || "human_governed");
  const maximum = titleWords(assignment.approved_maximum_profile || "human_governed");
  const pattern = assignment.governed_pattern_id ? titleWords(assignment.governed_pattern_id) : null;
  if (assignment.downgraded) {
    return `The illustrative deterministic policy reduced the approved maximum ${maximum} to ${effective} because elevated declared risk requires stronger human control.${pattern ? ` Matched governed demo pattern: ${pattern}.` : ""}`;
  }
  return `The illustrative deterministic policy assigned ${effective}.${pattern ? ` Matched governed demo pattern: ${pattern}.` : " No governed demo pattern matched; normal Cases use Human Governed."}`;
}

function signal(value, yesLabel = "Yes", noLabel = "No") {
  return `<span class="signal ${value ? "signal-yes" : "signal-no"}">${escapeHtml(value ? yesLabel : noLabel)}</span>`;
}

function readableList(values, empty = "None recorded") {
  if (!values?.length) return `<p class="muted">${escapeHtml(empty)}.</p>`;
  return `<ul class="readable-list">${values.map(value => {
    const text = typeof value === "string"
      ? value
      : value.summary || value.rationale || value.claim || value.team || value.action || pretty(value);
    return `<li>${escapeHtml(text)}</li>`;
  }).join("")}</ul>`;
}

function readableRecord(value, empty = "Not recorded") {
  if (!value || (typeof value === "object" && !Object.keys(value).length)) return `<p class="muted">${escapeHtml(empty)}.</p>`;
  if (typeof value !== "object") return `<p>${escapeHtml(value)}</p>`;
  const entries = Object.entries(value).filter(([, item]) => ["string", "number", "boolean"].includes(typeof item));
  if (!entries.length) return `<p class="muted">Structured detail is available below.</p>`;
  return `<dl class="readable-record">${entries.slice(0, 8).map(([key, item]) => {
    const humaniseValue = typeof item === "string" && /(action|status|mode|phase|profile|gate_id|governance_loop)$/.test(key);
    return `<div><dt>${escapeHtml(words(key))}</dt><dd>${typeof item === "boolean" ? signal(item) : escapeHtml(humaniseValue ? titleWords(item) : item)}</dd></div>`;
  }).join("")}</dl>`;
}

function renderQuestionnaireOverview(s) {
  const q = s.questionnaire || {};
  const assignment = s.autonomy_assignment || {};
  const objective = s.case_objective || {};
  const riskSignals = [
    ["Customer-facing", q.customer_facing],
    ["Customer decisioning", q.customer_decisioning],
    ["Personal data", q.personal_data],
    ["Sensitive data", q.sensitive_data],
    ["External supplier or model", q.external_model_or_supplier],
    ["Autonomous actions", q.autonomous_actions],
    ["Critical-process dependency", q.critical_process_dependency],
    ["Human review of outputs", q.human_review_of_outputs],
  ];
  return `<div class="view-intro"><h4>Questionnaire and governed assignment</h4><p>This view explains the submitted use case and the deterministic profile assignment. It does not control workflow progression.</p></div>
    <div class="domain-summary-grid">
      <section class="domain-card"><h4>Use-case overview</h4><dl class="readable-record">
        <div><dt>Name</dt><dd>${escapeHtml(q.use_case_name || "Not supplied")}</dd></div>
        <div><dt>Purpose</dt><dd>${escapeHtml(q.purpose || "Not supplied")}</dd></div>
        <div><dt>Business owner</dt><dd>${escapeHtml(q.business_owner || "Not supplied")}</dd></div>
        <div><dt>Users</dt><dd>${escapeHtml(q.users || "Not supplied")}</dd></div>
        <div><dt>Financial impact</dt><dd><span class="signal signal-neutral">${escapeHtml(words(q.financial_impact || "low"))}</span></dd></div>
      </dl></section>
      <section class="domain-card"><h4>System-assigned automation</h4><dl class="readable-record">
        <div><dt>Effective profile</dt><dd>${escapeHtml(titleWords(assignment.effective_profile || s.autonomy_profile || "human_governed"))}</dd></div>
        <div><dt>Approved maximum</dt><dd>${escapeHtml(titleWords(assignment.approved_maximum_profile || "human_governed"))}</dd></div>
        <div><dt>Governed pattern</dt><dd>${escapeHtml(assignment.governed_pattern_id ? titleWords(assignment.governed_pattern_id) : "No matched pattern")}</dd></div>
        <div><dt>Assignment reason</dt><dd>${escapeHtml(humaniseAssignmentReason(assignment))}</dd></div>
      </dl></section>
    </div>
    <section class="domain-card"><h4>Declared risk and control signals</h4><div class="signal-grid">${riskSignals.map(([label, value]) => `<div><span>${escapeHtml(label)}</span>${signal(Boolean(value))}</div>`).join("")}</div></section>
    <section class="domain-card objective-card"><h4>Governed Case objective</h4><p>${escapeHtml(objective.statement || "No objective assigned")}</p><h5>Completion criteria</h5>${readableList(objective.completion_criteria || s.completion_criteria || [], "No criteria configured")}</section>
    <div class="technical-disclosures">${section("Questionnaire technical record", q)}${section("Assignment technical record", assignment)}${section("Objective technical record", objective)}</div>`;
}

function resultSummary(key, value) {
  if (key === "materiality_result") {
    const activeDrivers = (value.score_details || []).filter(item => item.active);
    return `<div class="result-hero"><span>Proposed materiality</span><strong>${escapeHtml(words(value.proposed_materiality_band || "Not calculated"))}</strong><small>Raw illustrative score: ${escapeHtml(value.raw_score ?? "—")} · ${escapeHtml(value.proposed_validation_requirement || "No validation proposal")}</small></div>
      <div class="domain-summary-grid"><section class="domain-card"><h4>Active drivers</h4>${readableList(activeDrivers, "No active scoring drivers")}</section><section class="domain-card"><h4>Rule effects</h4>${readableList([...(value.minimum_route_rules || []), ...(value.uplift_reasons || []), ...(value.dealbreakers || [])], "No uplift or minimum-route rule applied")}</section></div>`;
  }
  if (key === "lod2_result") {
    return `<div class="result-hero"><span>Proposed second-line engagement</span><strong>${escapeHtml((value.teams || []).join(", ") || "No team triggered")}</strong><small>Independent answer-based illustrative trigger engine</small></div>
      <section class="domain-card"><h4>Trigger reasons</h4>${readableList(value.triggers || [], "No deterministic trigger fired")}</section>`;
  }
  if (key === "review_pack") {
    return `<div class="result-hero"><span>AIRO review pack</span><strong>${escapeHtml(value.title || "Prepared review pack")}</strong><small>${escapeHtml(value.governance_statement || "AIRO retains final authority.")}</small></div>
      <div class="summary-counts"><span><b>${(value.mandatory_evidence_gaps || []).length}</b> mandatory gaps</span><span><b>${(value.inconsistencies || []).length}</b> conflicts</span><span><b>${(value.open_issues || []).length}</b> recorded issues</span><span><b>${(value.human_decisions || []).length}</b> AIRO decisions</span></div>`;
  }
  if (key === "publication_draft") {
    return `<div class="result-hero"><span>Controlled local publication draft</span><strong>${escapeHtml(value.title || value.status || "Draft prepared")}</strong><small>No production Confluence, email or SharePoint write is enabled.</small></div>${readableRecord(value)}`;
  }
  return readableRecord(value);
}

function labelledList(title, label, values, className = "") {
  const items = values || [];
  const renderItems = subset => `<ul>${subset.map(value => `<li>${escapeHtml(typeof value === "string" ? value : value.summary || value.observation || value.claim)}</li>`).join("")}</ul>`;
  const preview = items.slice(0, 3);
  const remaining = items.slice(3);
  return `<div class="explanation-box ${className}"><h4><span>${escapeHtml(title)}</span><b class="finding-count">${items.length}</b></h4><span class="finding-label">${escapeHtml(label)}</span>${items.length ? renderItems(preview) : "<p>None recorded.</p>"}${remaining.length ? `<details class="finding-more"><summary>Show ${remaining.length} more</summary>${renderItems(remaining)}</details>` : ""}</div>`;
}

function openCaseTab(tabName, scrollToView = true) {
  state.activeTab = tabName;
  renderTab();
  if (scrollToView) {
    requestAnimationFrame(() => document.querySelector(".tabs")?.scrollIntoView({behavior: "smooth", block: "start"}));
  }
}

function handleTabKeydown(event) {
  if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
  const tabs = [...document.querySelectorAll(".tab")];
  const currentIndex = tabs.indexOf(event.currentTarget);
  const nextIndex = event.key === "Home"
    ? 0
    : event.key === "End"
      ? tabs.length - 1
      : (currentIndex + (event.key === "ArrowRight" ? 1 : -1) + tabs.length) % tabs.length;
  event.preventDefault();
  tabs[nextIndex].focus();
  openCaseTab(tabs[nextIndex].dataset.tab, false);
}

function governedResultSection(title, key, value, s) {
  const stale = new Set(s.stale_outputs || []);
  const invalidation = [...(s.invalidations || [])].reverse().find(item => item.invalidated_result === key);
  const superseded = (s.superseded_results || []).filter(item => item.result_type === key);
  const isStale = stale.has(key);
  const current = !isStale && value && Object.keys(value).length;
  const replacementStatus = current
    ? "CURRENT REPLACEMENT AVAILABLE"
    : invalidation?.replacement_required
      ? "REPLACEMENT PENDING"
      : "NOT YET GENERATED";
  return `<div class="data-section governed-result ${isStale ? "stale-result" : "current-result"}">
    <h4>${escapeHtml(title)} <span class="result-status">${escapeHtml(isStale ? "STALE / SUPERSEDED" : current ? "CURRENT" : "NOT CURRENT")}</span></h4>
    ${invalidation ? `<div class="warning"><b>Invalidation reason:</b> ${escapeHtml(invalidation.reason)}<br><b>Trigger:</b> ${escapeHtml(invalidation.triggering_change)}<br><b>Replacement status:</b> ${escapeHtml(replacementStatus)}</div>` : `<p class="muted">Replacement status: ${escapeHtml(replacementStatus)}</p>`}
    ${current ? `${resultSummary(key, value)}${section("Technical result record", value)}` : "<p>No authoritative current result is displayed.</p>"}
    ${superseded.length ? `<details><summary>${superseded.length} preserved superseded result(s)</summary><pre class="json">${escapeHtml(pretty(superseded))}</pre></details>` : ""}
  </div>`;
}

function renderActionCycle(item, index, total) {
  const selectedTag = item.selection_source === "llm_router" ? "LLM" : "DET";
  const stages = [
    ["STATE", "Observed State", item.observed_state || {}],
    ["DET", "Policy Decision", item.supervisor_decision || {}],
    [selectedTag, "Selected Action", {proposal:item.proposal || {}, selection_method:item.selection_source, rationale:item.rationale}],
    ["DET", "Authorisation", item.authorisation || {decision:"NOT AUTHORISED"}],
    ["TOOL", "Tool Execution", {stategraph_node:item.stategraph_node, tool_contract:item.tool_contract, invocation:item.invocation, output:item.result}],
    ["VERIFY", "Verification", item.verification || {}],
    ["STATE", "State Changes", {changed_fields:item.state_changes || [], state_diff:item.state_diff || {}}],
    ["STATE", "Invalidated Outputs", item.invalidated_outputs || []],
    ["DET", "Transition Decision", {decision:item.transition_decision, next_transition:item.next_transition}],
  ];
  return `<details class="trace-cycle" ${index === total - 1 ? "open" : ""}>
    <summary>Cycle ${index + 1}: ${escapeHtml(item.proposal?.selected_action || "governed transition")} · ${escapeHtml(item.verification?.disposition || "pending")}</summary>
    <div class="trace-stages">${stages.map(([tag, title, value]) => `<section><h5>${traceBadge(tag)} ${escapeHtml(title)}</h5><pre>${escapeHtml(pretty(value))}</pre></section>`).join("")}</div>
  </details>`;
}

function renderSupportingCycle(tag, title, record, index, total) {
  const stagesByTag = {
    HITL: [
      ["STATE", "Observed Governance State", {gate_id:record.gate_id, case_state_version:record.case_state_version}],
      ["HITL", "Human Decision", record],
      ["STATE", "Decision Effects", {action:record.action, invalidated_outputs:record.invalidated_outputs || [], rationale:record.rationale}],
    ],
    EVENT: [
      ["EVENT", "External Event Contract", {event_id:record.event_id, event_type:record.event_type, correlation_id:record.correlation_id, source:record.source, schema_version:record.schema_version}],
      ["VERIFY", "Event Verification", {status:record.status, received_at:record.received_at}],
      ["STATE", "Event State Changes", record],
    ],
    STATE: [
      ["STATE", "StateGraph Node", {node:record.node, occurred_at:record.occurred_at}],
      ["DET", "Transition Decision", {decision:record.decision, reason:record.reason}],
      ["STATE", "State Changes", record.state_changes || []],
    ],
    END: [
      ["END", "Completion Decision", record],
      ["DET", "Completion Policy", {policy_version:record.policy_version, blockers:record.blockers || []}],
    ],
  };
  const stages = stagesByTag[tag] || [[tag, title, record]];
  return `<details class="trace-cycle supporting-cycle" ${index === total - 1 ? "open" : ""}>
    <summary>${traceBadge(tag)} ${escapeHtml(title)} ${index + 1}</summary>
    <div class="trace-stages">${stages.map(([stageTag, stageTitle, value]) => `<section><h5>${traceBadge(stageTag)} ${escapeHtml(stageTitle)}</h5><pre>${escapeHtml(pretty(value))}</pre></section>`).join("")}</div>
  </details>`;
}

function renderTab() {
  document.querySelectorAll(".tab").forEach(button => {
    const active = button.dataset.tab === state.activeTab;
    button.classList.toggle("active", active);
    button.setAttribute("aria-selected", String(active));
    button.tabIndex = active ? 0 : -1;
  });
  const s = state.current.state;
  let html = "";
  if (state.activeTab === "overview") {
    html = renderQuestionnaireOverview(s);
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
    const advisory = s.advisory_observations || [];
    const confirmedExceptions = s.confirmed_exceptions || [];
    const rejected = currentIssues.filter(item => item.category === "verification" || item.category === "security");
    const mandatoryGaps = (s.mandatory_evidence_gaps || []).length ? s.mandatory_evidence_gaps : (s.missing_information || []);
    html = `<div class="view-intro"><h4>Evidence and issue register</h4><p>Current authoritative findings remain separated by governance meaning. Expand only the longer panels you need to review.</p></div><div class="finding-grid evidence-six-panels">
      ${labelledList("Mandatory evidence gaps", "Deterministic gap — action required", mandatoryGaps, "deterministic")}
      ${labelledList("Evidence conflicts", "Conflict — resolution required", s.evidence_conflicts || [], "deterministic")}
      ${labelledList("LLM advisory observations", "Advisory — AIRO confirmation required", s.llm_advisory_observations || advisory, "advisory")}
      ${labelledList("Confirmed exceptions", "AIRO-confirmed exception", confirmedExceptions)}
      ${labelledList("Confirmed facts", "AIRO-confirmed input", confirmed)}
      ${labelledList("Candidate facts awaiting confirmation", "LLM/tool candidate — not confirmed", s.candidate_facts || claims, "advisory")}
    </div>
    <div class="finding-grid">${labelledList("AIRO-accepted residual issues", "Accepted for continued review — not resolved", acceptedIssues)}${labelledList("Rejected or unverified", "Unverified/rejected result", rejected, "rejected")}</div>`
      + section("Questionnaire", s.questionnaire || {})
      + section("Technical evidence state", {evidence_extraction:s.evidence_extraction || {}, evidence_claims:claims, open_issues:s.open_issues || [], evidence_request:s.evidence_request || []})
      + section("Invalidation history", s.invalidations || []);
  } else if (state.activeTab === "assessment") {
    html = '<p class="warning">The scoring shown is illustrative and is not approved PwC or MRO methodology.</p>' + governedResultSection("Materiality engine", "materiality_result", s.materiality_result || {}, s);
  } else if (state.activeTab === "lod2") {
    html = '<p class="warning">2LoD triggers are answer-based and independent of the final materiality score.</p>' + governedResultSection("2LoD trigger engine", "lod2_result", s.lod2_result || {}, s);
  } else if (state.activeTab === "pack") {
    html = governedResultSection("AIRO review pack", "review_pack", s.review_pack || {}, s) + governedResultSection("Publication draft", "publication_draft", s.publication_draft || {}, s);
  } else if (state.activeTab === "calibration") {
    html = `
      <p class="warning">Calibration is an offline rule-governance activity. It does not change a live case or update thresholds automatically.</p>
      <div class="calibration-actions">
        <button id="sensitivity-btn" class="primary">Run case sensitivity</button>
        <button id="backtest-btn" class="secondary">Run demo historical backtest</button>
      </div>
      <div id="calibration-results">${state.calibration ? section("Calibration result", state.calibration) : '<p class="muted">Choose an analysis to inspect how the deterministic rules behave.</p>'}</div>`;
  } else if (state.activeTab === "history") {
    html = section("Human decisions", s.human_decisions || []) + section("Action authorisations", s.action_authorisations || []) + section("External events", s.processed_external_events || []) + section("Control Exception history", s.control_exception_history || []) + section("Invalidation history", s.invalidations || []) + ((state.current.audit || []).map(event => `<div class="audit-item"><span>${escapeHtml(event.occurred_at)}</span><strong>${escapeHtml(event.action)}</strong><span>${escapeHtml(event.actor)}<br><small>${escapeHtml(pretty(event.details))}</small></span></div>`).join("") || '<p>No audit events.</p>');
  } else if (state.activeTab === "trace") {
    const cycles = s.agent_action_trace || [];
    const supportingRecords = [
      ["HITL", "Human decision", s.human_decisions || []],
      ["EVENT", "External event", s.processed_external_events || []],
      ["STATE", "StateGraph transition", s.transition_history || []],
      ["END", "Completion", s.completion_evaluation ? [s.completion_evaluation] : []],
    ];
    html = '<p class="warning">Structured control records and concise decision rationales only. Hidden model reasoning and chain-of-thought are never displayed.</p>'
      + `<h4>Connected Coordinator cycles</h4>${cycles.length ? cycles.map((item, index) => renderActionCycle(item, index, cycles.length)).join("") : "<p>No action cycle recorded yet.</p>"}`
      + `<div class="trace-support"><h4>Governance, event, transition and completion cycles</h4>${supportingRecords.map(([tag, title, records]) => records.length
        ? records.map((record, index) => renderSupportingCycle(tag, title, record, index, records.length)).join("")
        : `<p>${traceBadge(tag)} No ${escapeHtml(title.toLowerCase())} record yet.</p>`).join("")}</div>`;
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

function showDecisionFormError(message, target = null) {
  const error = $("decision-form-error");
  error.textContent = message;
  error.classList.toggle("hidden", !message);
  if (message && target) target.focus();
}

async function submitDecision(event) {
  event.preventDefault();
  const previousGate = state.current?.pending_gate;
  const answerUpdatesField = $("answer-updates");
  const action = $("decision-action").value;
  showDecisionFormError("");
  let answerUpdates = {};
  try {
    if (answerUpdatesField.value.trim()) answerUpdates = JSON.parse(answerUpdatesField.value);
    answerUpdatesField.setCustomValidity("");
  } catch (_) {
    answerUpdatesField.setCustomValidity("Enter a valid JSON object, for example {\"personal_data\": true}.");
    answerUpdatesField.reportValidity();
    answerUpdatesField.focus();
    toast("Questionnaire updates must be valid JSON.", true);
    return;
  }
  const teamsText = $("confirmed-teams").value.trim();
  if (["add_evidence", "amend_material_fact"].includes(action)
      && !$("additional-evidence").value.trim() && !Object.keys(answerUpdates).length) {
    showDecisionFormError(
      "Provide additional evidence or change at least one questionnaire answer before submitting.",
      document.querySelector("[data-answer-field]") || $("additional-evidence"),
    );
    return;
  }
  if (action === "edit_answers" && !Object.keys(answerUpdates).length) {
    showDecisionFormError(
      "Change at least one questionnaire answer before submitting Edit Answers.",
      document.querySelector("[data-answer-field]") || answerUpdatesField,
    );
    return;
  }
  if (action === "override" && !$("override-band").value && !teamsText) {
    showDecisionFormError(
      "Change the materiality band and/or provide the confirmed 2LoD teams.",
      $("override-band"),
    );
    return;
  }
  const payload = {
    action,
    rationale: $("decision-rationale").value,
    additional_evidence: $("additional-evidence").value,
    answer_updates: answerUpdates,
    override_band: $("override-band").value || null,
    confirmed_teams: teamsText ? teamsText.split(",").map(x => x.trim()).filter(Boolean) : null,
    reviewer: $("reviewer").value || "AIRO demo reviewer",
    case_id: state.current.case_id,
    gate_id: previousGate?.gate_id,
    governance_loop: previousGate?.governance_loop || null,
    case_state_version: state.current.state.case_state_version,
    rule_version: state.current.state.rule_version,
  };
  const button = event.target.querySelector("button[type=submit]");
  const originalButtonLabel = button.textContent;
  try {
    button.disabled = true;
    button.textContent = "Submitting decisionâ€¦";
    if (previousGate?.gate_id === "control_exception_review") {
      const recovery = {
        action: payload.action,
        rationale: payload.rationale || "AIRO authorised the selected governed recovery.",
        reviewer: payload.reviewer,
        case_state_version: payload.case_state_version,
      };
      state.current = await api(`/api/cases/${state.current.case_id}/recover`, {method:"POST", body:JSON.stringify(recovery)});
    } else {
      state.current = await api(`/api/cases/${state.current.case_id}/resume`, {method:"POST", body:JSON.stringify(payload)});
    }
    renderCurrentCase();
    await loadCases(state.current.case_id);
    const nextGate = state.current.pending_gate;
    toast(nextGate
      ? `${previousGate?.title || "AIRO Gate"} recorded; now waiting at ${nextGate.title}.`
      : `${previousGate?.title || "AIRO decision"} recorded; case status is ${state.current.status.replaceAll("_", " ")}.`);
  } catch (error) { toast(error.message, true); }
  finally {
    button.disabled = false;
    button.textContent = originalButtonLabel;
  }
}

async function submitExternalEvent(kind = "valid", replay = false) {
  const expectation = state.current?.pending_event || state.current?.state?.active_external_event;
  if (!expectation && !replay) { toast("This Case is not awaiting an external event.", true); return; }
  let payload = replay ? state.lastEvent : {
    event_id: `EVT-${crypto.randomUUID().replaceAll("-", "").slice(0, 12).toUpperCase()}`,
    event_type: kind === "timeout" ? "timeout" : kind === "external" ? "external_response_received" : expectation.event_type,
    case_id: state.current.case_id,
    correlation_id: kind === "invalid" ? `${expectation.correlation_id}-INVALID` : expectation.correlation_id,
    source: $("event-source").value,
    schema_version: expectation.schema_version,
    case_state_version: state.current.state.case_state_version,
    artifact_text: kind === "timeout" ? "" : $("event-artifact").value,
  };
  try {
    const result = await api(`/api/cases/${state.current.case_id}/events`, {method:"POST", body:JSON.stringify(payload)});
    if (!replay) state.lastEvent = payload;
    state.current = result;
    renderCurrentCase();
    await loadCases(state.current.case_id);
    toast(result.event_submission?.status === "IDEMPOTENT_REPLAY" ? "Duplicate event was accepted idempotently without reprocessing." : "External event validated and the Coordinator resumed.");
  } catch (error) { toast(error.message, true); }
}

async function handleExternalEventSubmit(event) {
  event.preventDefault();
  await submitExternalEvent("valid");
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
  $("continue-btn").onclick = () => {
    $("decision-form").scrollIntoView({behavior: "smooth", block: "start"});
    window.setTimeout(() => document.querySelector('input[name="gate-decision"]:checked')?.focus(), 350);
  };
  $("decision-form").onsubmit = submitDecision;
  $("event-form").onsubmit = handleExternalEventSubmit;
  $("invalid-event-btn").onclick = () => submitExternalEvent("invalid");
  $("external-response-btn").onclick = () => submitExternalEvent("external");
  $("timeout-event-btn").onclick = () => submitExternalEvent("timeout");
  $("duplicate-event-btn").onclick = () => submitExternalEvent("valid", true);
  $("decision-action").onchange = () => updateDecisionForm();
  $("answer-updates").oninput = event => {
    event.target.setCustomValidity("");
    showDecisionFormError("");
  };
  $("additional-evidence").oninput = () => showDecisionFormError("");
  $("override-band").onchange = () => showDecisionFormError("");
  $("confirmed-teams").oninput = () => showDecisionFormError("");
  $("case-lookup-form").onsubmit = openCaseById;
  $("custom-case-form").onsubmit = createCustomCase;
  $("sample-search").oninput = event => {
    state.sampleQuery = event.target.value;
    renderSampleCatalogue();
  };
  $("sample-profile-filter").onchange = event => {
    state.sampleProfile = event.target.value;
    renderSampleCatalogue();
  };
  document.querySelectorAll(".tab").forEach(button => {
    button.onclick = () => openCaseTab(button.dataset.tab, false);
    button.onkeydown = handleTabKeydown;
  });
  await Promise.all([loadHealth(), loadSamples(), loadCases()]);
});
