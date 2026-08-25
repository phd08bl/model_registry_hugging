# Demonstration script

All profiles, patterns, sampling keys and expected outcomes are illustrative demo policy,
not approved PwC or MRO methodology. Expected sample metadata explains a lesson and is
never read by the StateGraph to force a runtime result.

## Recommended 10–15 minute journey

### 1. Establish the boundary (1 minute)

Open the home page in mock mode. Point to the governance banner and the searchable,
profile-filtered demonstration catalogue. Its three category groups are expandable; **Eight
major feature Cases** opens first so the required coverage is immediately visible. Expand **Expected journey and
teaching details** only when comparing paths, actions, tools, exceptions or Governance Loops,
then use the explicit **Create and open case** action. Creating a Case does not start the
Coordinator.
Explain that there is one stateful Case Coordinator. The deterministic supervisor assigns
permissions; a bounded router can recommend evidence actions; the registry invokes only
approved tools; the verifier labels limitations; deterministic engines propose risk; AIRO
owns judgement. Expand **Create custom case** to show that there is no profile selector.
Confirm that the runtime banner reads **MOCK · deterministic demonstration runtime**. The
read-only **Case journey** distinguishes **AIRO decision recorded**, **Gate skipped by
deterministic policy**, **Gate not triggered**, waits, stale results and reopened work. Explain
that it is a projection of authoritative Case State, not the StateGraph itself and not a
workflow controller. Actual graph nodes remain in Technical Trace.

Use the primary **Coordinator Workspace** to distinguish the current Coordinator instruction
from the most recent completed action. At a Gate, the current instruction must say that AIRO
is awaited; the completed router/tool action remains explicitly labelled as history. Point out
that **Policy Supervisor allowed actions** and **Current AIRO Gate allowed decisions** are
separate controls. Expand the configured completion criteria, then open **Evidence** to show
the six non-merged finding panels and **Technical Trace** to show action, HITL, event,
StateGraph and end cycles. Do not interpret any structured trace as model chain-of-thought.

In the Case journey, point first to the current-control banner: lifecycle, domain phase,
Governance Loop, waiting party and next permitted transition. Then use the phase cards to
explain completed work and optional Gate outcomes. During the external-event and selective-
replanning demonstrations, confirm that the journey shows the wait or loop-back explicitly
and does not fall back to Intake. When invalidation reopens the active phase, its primary
status remains **Waiting for AIRO**, **Waiting for external event** or **Current phase**;
**Why reopened** carries the invalidation explanation. Only non-current affected phases use
the softer **Stale — replacement required** treatment.

Standard tabs now show domain summaries rather than opening with raw JSON. Use the labelled
technical-record expanders only when the audience needs contract detail, and reserve
**Technical Trace** for the engineering walkthrough. At a Human Gate, begin with **Decision
required now**, then expand **Review rule, evidence, recommendation and decision effects**
when that decision support is needed. The action form remains immediately visible so the
reviewer does not need to scroll past a long evidence record. Expand the remaining evidence
items or structured Gate context only for deeper review.

### 2. Standard and multiple-action control paths (3 minutes)

Create **Case 1 — Standard Low-Risk Internal Summary**. Start it and show routine evidence
preparation, later deterministic single-action selection, no Evidence Resolution loop, input
readiness, negligible materiality, an empty independent 2LoD proposal, final AIRO review and
controlled local publication.

Create **Case 2 — Multiple Permitted Evidence Actions**. In **Technical Trace**, expand an
LLM-selected action cycle and compare:

1. the deterministic supervisor's multiple allowed actions;
2. the single bounded LLM recommendation;
3. the deterministic `AUTHORISED` record and bound Tool Contract;
4. the tool result and verifier disposition;
5. the next `reassess_case` transition and subsequent action cycle.

This Case shows action recommendation, not risk judgement: the LLM cannot authorise the tool,
set materiality/2LoD or bypass an AIRO Gate.

### 3. Questionnaire conflict and Evidence Resolution (4 minutes)

Create **Case 3 — Questionnaire/Evidence Conflict**, then select **Start Coordinator**.

What should happen:

1. Extraction and consistency objectives are supervised and routed.
2. The RAG checker runs as an unrelated advisory tool.
3. Tool versions, selection reasons and verification dispositions appear in the concise
   trace.
4. The questionnaire/evidence personal-data conflict creates mandatory Gate 1.

At Gate 1, first point out that **Your task** names the personal-data conflict, compares the
current questionnaire value with the evidence-supported value, lists the source citations and
states exactly what must be supplied. Select the recommended **Add Evidence** decision card.
Paste:

```text
Privacy assessment classifies employee names and corporate email addresses as personal data
authorised for this internal purpose.
```

In the guided **Questionnaire corrections** control, change **Personal data** to **Yes**. The
advanced JSON fallback will show the equivalent update:

```json
{"personal_data": true}
```

Before resuming, use **What this decision will do** to show the expected invalidation,
selective reruns, preserved unrelated checks and next Gate. Resume. Open **Evidence** and point
out the invalidation history and targeted evidence rerun:
extraction, consistency and citations rerun because their inputs changed, while the unrelated
verified RAG check remains current. Continue with `confirm`, `proceed`, `confirm`
and `approve`, adding a short AIRO rationale each time. The materiality band and 2LoD teams
come from separate deterministic engines; none of those choices came from the router.

The expected live transition sequence is:

| After action | Current status | UI should show |
|---|---|---|
| Start Coordinator | `AWAITING_INFORMATION` | Gate 1; current deterministic gap/conflict; latest evidence-tool verification labelled as history |
| Gate 1 `add_evidence` with the text and JSON above | `AWAITING_INPUT_CONFIRMATION` | Gate 2; no current evidence conflict; the old finding only in invalidation/superseded audit history |
| Gate 2 `confirm` | `AWAITING_EXCEPTION_DECISION` | Gate 3; AIRO-confirmed input facts; deterministic proposal and any current exception |
| Gate 3 `proceed` with rationale | `AWAITING_FINAL_DECISION` | Gate 4; exception recorded as AIRO-accepted, not as an unresolved attention item |
| Gate 4 `confirm` | `READY_TO_PUBLISH` | Gate 5; `AIRO_CONFIRMED` final outcome and a local-only publication draft |
| Gate 5 `approve` | `CLOSED` | No pending Gate; local demo publication status and completed workflow |

If Gate 1 uses `proceed_with_gap`, the issue is displayed as an **AIRO-accepted residual
issue**. It is deliberately not called resolved, and it remains a risk condition for later
policy and exception routing. The Gate form shows only fields used by the selected action;
historical tool verification is not presented as the verification status of the current Gate.

### 4. Progressive permissions (3 minutes)

Create **Conditional Review — Approved Internal Translation Helper**. Start it and show that
clean read-only preparation occurs automatically, while final triage remains an AIRO Gate.

Create **Exception Based — Deterministically Sampled for Review**. Confirm Gate 2. Gate 4 is
required because the protected stable sampling key selected the case—not because risk was
elevated. Compare with **Exception Based — Eligible Approved Pattern**, whose final-triage
Gate is policy-skipped and whose skip rationale/version is retained.

Create **Straight Through Demo — Eligible Internal Summary**. Confirm Gate 2. The eligible
case completes later permitted decisions and a local-only publication record. Emphasise that
this is a local demonstration policy, not a production route. Contrast it with **Case 8 —
Elevated/High-Risk Protected Decisions**: its approved maximum is visible,
but elevated declarations deterministically downgrade the effective profile to
`human_governed` before the LLM runs.

### 5. Fail-closed advanced controls (3 minutes)

Create **Advanced — Invalid Tool Proposal**. Start it. The protected mock proposes the
materiality engine for an evidence-extraction action. Show:

- proposal disposition `rejected`;
- no invocation and no result;
- tool-call count still zero;
- a structured Control Exception, rejection rationale and zero unauthorized tool execution;
- the recovery actions that remain possible under the protected budget.

Optionally compare **Advanced — Low-Confidence Router Result** or **Advanced —
Action-Budget Exhaustion**. Both stop deterministically without an infinite loop.

Then start **Case 7 — Tool Verification Failure**. Unlike the invalid proposal, this tool is
authorised and executes, but its payload fails `output_schema_valid`. The Technical Trace
shows one bounded retry, a second rejection, no candidate/confirmed fact update and a Control
Exception. Use this contrast to explain why authorisation and result verification are separate
controls.

### 6. Prompt injection or selective replanning (2–4 minutes)

For a security close, start **Advanced — Prompt-Injection Evidence**. The embedded “ignore
previous instructions” text stays untrusted; an intentionally invalid citation is rejected;
the security issue is displayed; no approval, rule or Gate changes.

For a dependency close, start **Case 6 — Stale Outputs and Selective Replanning**. Confirm
Gate 2, proceed at Gate 3 and confirm the initial final result at Gate 4. At Gate 5 select
`amend_material_fact` and enter:

```json
{"personal_data": true}
```

Explain in the rationale that newly reviewed evidence confirms attendee identifiers are now in
scope. Before resolving the renewed evidence Gate, show that the prior AIRO decision,
materiality, 2LoD and review pack are visibly stale/superseded; the existing extraction remains
current; and only consistency/citation work was rerun. No stale result appears current.

## Active sample run cards

The expected actions below describe observable router/tool trace entries. Foundational
consistency and citation checks may also run because deterministic policy requires them. For
standard Gates, use a short AIRO rationale even when the form does not require one.

### Case 3 — `human_evidence_conflict`

- **Learning objective:** bounded evidence routing, citation verification, Gate 1 and
  selective replanning.
- **Starting condition:** a policy-RAG questionnaire says no personal data while cited
  evidence names employees and corporate email addresses.
- **Assigned profile:** `human_governed`.
- **Expected router/tools:** extraction and RAG actions through `evidence_extractor` and
  `rag_evidence_checker`, plus deterministic consistency and citation verification.
- **Verification:** accepted deterministic checks plus advisory semantic results.
- **Expected Gates:** evidence request → input confirmation → exception resolution → final
  triage → publication.
- **Exact user actions:** start; at Gate 1 choose `add_evidence`, paste the privacy
  classification text from the main journey and set `{"personal_data": true}`; then choose `confirm`,
  `proceed`, `confirm`, `approve`.
- **Expected outcome/key point:** `CLOSED` with a local publication record; the corrected
  answer invalidates evidence-dependent work and the two engines remain human-governed.

### Case 1 — `human_full_review`

- **Learning objective:** routine preparation, deterministic single-action selection, no
  evidence exception, readiness, deterministic engines, final review and local publication.
- **Starting condition:** a low-risk internal meeting summary matches the approved demo pattern.
- **Assigned profile:** `human_governed`.
- **Expected router/tool:** `extract_submitted_evidence` / `evidence_extractor`.
- **Verification:** accepted extraction with advisory semantic limitation.
- **Expected Governance Loops:** material-fact confirmation → final triage → publication;
  exception interpretation is not triggered because there is no current exception.
- **Exact user actions:** start, then `confirm`, `confirm`, `approve`.
- **Expected outcome/key point:** `CLOSED`; readiness passes, materiality is `negligible`, the
  independent 2LoD proposal is empty and low apparent risk still does not grant autonomy.

### Case 2 — `multiple_evidence_actions`

- **Learning objective:** distinguish bounded LLM action recommendation from deterministic
  authorisation, tool execution, verification and transition control.
- **Starting condition:** a complete policy-RAG case makes extraction, consistency, RAG,
  supplier and citation objectives available without creating a deterministic evidence gap.
- **Assigned profile:** `human_governed`; the illustrative policy assigns it, and no teaching
  control overrides the profile.
- **Expected router/tools:** the bounded recommender chooses one from multiple allowlisted
  actions; the Authoriser binds the registered evidence, RAG or supplier Tool Contract.
- **Verification:** every executed result is accepted or labelled advisory before State can
  change; the Coordinator then re-observes and continues the remaining plan.
- **Expected Governance Loops:** material-fact confirmation → final triage → publication.
- **Exact user actions:** start; expand an LLM-selected Technical Trace cycle; compare allowed
  actions, proposal, authorisation, tool/result and next transition; then `confirm`, `confirm`,
  `approve`.
- **Expected outcome/key point:** `CLOSED`; the LLM selects one evidence action but never
  authorises execution or makes the risk decision.

### Case 5 — `agentic_ai_autonomy`

- **Learning objective:** assess another agentic system without creating a multi-agent
  coordinator.
- **Starting condition:** a critical internal agent can execute maintenance actions, but
  evidence for prior approval, pause, kill switch and rollback controls is missing.
- **Assigned profile:** `human_governed`.
- **Expected router/tool:** `check_agentic_ai_autonomy` /
  `agentic_ai_autonomy_checker` (with foundational evidence actions).
- **Verification:** advisory observations identify the missing approval, stop and rollback
  evidence; deterministic materiality independently proposes `severe` and 2LoD triggers.
- **Expected Governance Loops:** material-fact confirmation → exception interpretation →
  final triage → publication.
- **Exact user actions:** start, inspect the separate autonomy observations, then `confirm`,
  `proceed` with rationale, `confirm`, `approve`.
- **Expected outcome/key point:** `CLOSED`; missing human-control evidence receives accountable
  interpretation, while advisory analysis still cannot set autonomy, 2LoD or final risk.

### `conditional_clean_final`

- **Learning objective:** clean preparation can skip while final accountability remains.
- **Starting condition:** an exact approved internal translation pattern.
- **Assigned profile:** `conditional_review`.
- **Expected router/tool:** extraction / `evidence_extractor`.
- **Verification:** accepted/advisory extraction trace.
- **Expected Gates:** final triage → publication.
- **Exact user actions:** start, `confirm` at final triage, then `approve` publication.
- **Expected outcome/key point:** `CLOSED`; Gate skips are deterministic policy records, not
  LLM decisions.

### `conditional_exception`

- **Learning objective:** a pattern deviation restores governed exception review.
- **Starting condition:** the translation helper is outside its approved pattern.
- **Assigned profile:** `conditional_review`.
- **Expected router/tool:** extraction / `evidence_extractor`.
- **Verification:** accepted extraction; rule-supported exception remains current.
- **Expected Gates:** exception resolution → final triage → publication.
- **Exact user actions:** start, `proceed` with deviation rationale, `confirm`, `approve`.
- **Expected outcome/key point:** `CLOSED`; a maximum profile never suppresses an exception.

### `exception_based_eligible`

- **Learning objective:** eligible, non-sampled exception-based processing with audited
  skips.
- **Starting condition:** mature approved low-risk pattern with complete evidence.
- **Assigned profile:** `exception_based`.
- **Expected router/tool:** extraction / `evidence_extractor`.
- **Verification:** accepted/advisory extraction trace.
- **Expected Gates:** input confirmation → publication.
- **Exact user actions:** start, `confirm` inputs, then `approve` publication.
- **Expected outcome/key point:** `CLOSED`; exception and final Gates are skipped only after
  deterministic eligibility/sampling evaluation.

### `exception_based_sampled`

- **Learning objective:** stable policy-owned sampling can require review without elevated
  risk.
- **Starting condition:** otherwise eligible pattern with a protected sampling key.
- **Assigned profile:** `exception_based`.
- **Expected router/tool:** extraction / `evidence_extractor`.
- **Verification:** accepted/advisory extraction trace.
- **Expected Gates:** input confirmation → final triage → publication.
- **Exact user actions:** start, `confirm` inputs, inspect the sampling rationale, `confirm`
  final triage, `approve` publication.
- **Expected outcome/key point:** `CLOSED`; sampling—not the LLM or higher risk—causes final
  review.

### `exception_based_triggered`

- **Learning objective:** exceptions take precedence over streamlined processing.
- **Starting condition:** an unapproved pattern under an exception-based maximum.
- **Assigned profile:** `exception_based`.
- **Expected router/tool:** extraction / `evidence_extractor`.
- **Verification:** accepted extraction with a current rule-supported exception.
- **Expected Gates:** input confirmation → exception resolution → final triage → publication.
- **Exact user actions:** start, `confirm`, `proceed` with rationale, `confirm`, `approve`.
- **Expected outcome/key point:** `CLOSED`; exception routing cannot be bypassed by profile.

### `straight_through_eligible`

- **Learning objective:** maximum demo autonomy remains bounded and local.
- **Starting condition:** explicitly governed, eligible low-risk internal summary.
- **Assigned profile:** `straight_through_demo`.
- **Expected router/tool:** extraction / `evidence_extractor`.
- **Verification:** accepted/advisory evidence trace.
- **Expected Gates:** input confirmation only.
- **Exact user actions:** start and choose `confirm` at input confirmation.
- **Expected outcome/key point:** `CLOSED` with `AUTO_CONFIRMED_WITHIN_DEMO_POLICY` and
  `PUBLISHED_LOCAL_DEMO`; no enterprise write occurs.

### Case 8 — `straight_through_ineligible`

- **Learning objective:** elevated declarations deterministically downgrade permissions.
- **Starting condition:** autonomous customer decisioning in a critical process using
  sensitive data and a supplier.
- **Assigned profile:** `human_governed`; approved maximum remains
  `straight_through_demo` for explanation.
- **Expected router/tools:** agentic-autonomy and supplier checks through their approved
  tools.
- **Verification:** accepted deterministic outputs plus advisory semantic findings.
- **Expected Gates:** input confirmation → exception resolution → final triage → publication.
- **Exact user actions:** start, inspect the pre-LLM downgrade, then `confirm`, `proceed`,
  `confirm`, `approve`.
- **Expected outcome/key point:** `CLOSED`; severe/elevated input never receives
  straight-through authority.

### `low_confidence_router`

- **Learning objective:** confidence policy rejects a model proposal before execution.
- **Starting condition:** protected mock router returns confidence `0.20` with several
  available evidence actions.
- **Assigned profile:** `human_governed`.
- **Expected router/tools:** router proposal only; no tool invocation.
- **Verification:** `rejected`, with `tool_not_invoked=true`.
- **Expected Governance Loop:** Control Exception review.
- **Exact user actions:** start and stop at Control Exception review to inspect proposal, zero tool calls and
  rejection rationale.
- **Expected outcome/key point:** `CONTROL_EXCEPTION`; low confidence fails closed and no
  infinite loop occurs.

### `invalid_tool_proposal`

- **Learning objective:** the action/tool allowlist blocks risk-engine misuse.
- **Starting condition:** protected mock proposes `materiality_engine` for evidence
  extraction.
- **Assigned profile:** `human_governed`.
- **Expected router/tools:** invalid proposal only; no invocation/result.
- **Verification:** `rejected`, with policy mismatch and `tool_not_invoked=true`.
- **Expected Governance Loop:** Control Exception review.
- **Exact user actions:** start and inspect the last trace; do not submit a Gate decision for
  the teaching stop.
- **Expected outcome/key point:** `CONTROL_EXCEPTION`; the LLM cannot cross the
  deterministic risk-decision boundary.

### Case 7 — `malformed_tool_result`

- **Learning objective:** a successful call is not trusted until its output contract passes.
- **Starting condition:** the protected fixture replaces the extraction payload with an
  unsupported `facts` shape after execution.
- **Assigned profile:** `human_governed`; the teaching control does not override the profile.
- **Expected router/tool:** extraction / `evidence_extractor`, attempted twice under its
  one-retry Tool Contract.
- **Verification:** first result is `retry`; second is `escalate`; `output_schema_valid=false`.
- **Expected exceptions/Governance Loop:** verification failure → Control Exception review.
- **Exact user actions:** start; inspect tool-call count `2`, retry count `1`, both verifier
  records and the empty candidate/confirmed-fact panels; stop at the teaching exception.
- **Expected outcome/key point:** `CONTROL_EXCEPTION`; malformed output never updates facts,
  and the bounded retry cannot become an infinite loop.

### `prompt_injection_evidence`

- **Learning objective:** submitted instructions remain data and invalid citations escalate.
- **Starting condition:** evidence contains an “ignore previous instructions” phrase and a
  protected invalid citation marker.
- **Assigned profile:** `human_governed`.
- **Expected router/tool:** extraction / `evidence_extractor`.
- **Verification:** `escalate`; citation check fails and a security issue is retained.
- **Expected Governance Loop:** Control Exception review.
- **Exact user actions:** start and inspect the untrusted evidence, citation failure and
  security issue; stop at Control Exception review.
- **Expected outcome/key point:** `CONTROL_EXCEPTION`; no instruction changes rules,
  Gates, approval or outcome.

### Case 6 — `selective_replanning`

- **Learning objective:** dependency-aware invalidation distinguishes current from
  superseded results.
- **Starting condition:** a clean internal summary reaches Gate 5 after an initial final AIRO
  decision and review-pack preparation.
- **Assigned profile:** `human_governed`.
- **Expected router/tool:** initial foundational checks; after the amendment only consistency
  and citation checks rerun, while the unaffected extraction result remains current.
- **Verification:** accepted/advisory results before and after replanning.
- **Expected Gates:** input confirmation → exception resolution → final triage → publication,
  then renewed evidence and AIRO review after the Gate 5 amendment.
- **Exact user actions:** start; `confirm` Gate 2; `proceed` at Gate 3; `confirm` Gate 4. At
  Gate 5 choose `amend_material_fact`, enter `{"personal_data": true}` and explain that newly
  reviewed attendee-identifier evidence changed the fact. Inspect the Evidence, Assessment,
  Second-Line Engagement, Review Pack and History views before resolving the renewed Gates.
- **Expected outcome/key point:** the prior final AIRO decision and dependent engine/review
  outputs are visibly stale and preserved as superseded; extraction is not rerun, and no
  stale result is displayed as current.

### `action_budget_exhaustion`

- **Learning objective:** a hard action budget prevents unbounded tool loops.
- **Starting condition:** protected fixture permits only one tool call while more objectives
  remain.
- **Assigned profile:** `human_governed`.
- **Expected router/tool:** one extraction / `evidence_extractor`, followed by a deterministic
  supervisor stop before any second tool.
- **Verification:** extraction accepted/advisory; budget exception records the blocked work.
- **Expected Governance Loop:** Control Exception review.
- **Exact user actions:** start and inspect call count `1`, remaining budget `0` and the
  structured exception; stop at Control Exception review.
- **Expected outcome/key point:** `CONTROL_EXCEPTION`; the bounded loop terminates safely.

### Case 4 — `missing_supplier_evidence`

- **Learning objective:** durable External Event Wait, strict correlation/version validation,
  idempotent replay and selective evidence rework.
- **Starting condition:** an unapproved hosted foundation-model use case declares a supplier
  dependency but the required assurance artifact has not arrived.
- **Expected assigned profile:** `human_governed`.
- **Expected router/tools:** extraction, consistency/citation checks and supplier evidence
  check; all calls remain inside the registered capability boundary.
- **Expected wait:** `AWAITING_EXTERNAL_EVENT` with a displayed event contract; this is not a
  Human Gate.
- **Exact user actions:** start; inspect the event contract; first use **Try invalid
  correlation** and observe rejection; then submit the supplied evidence artifact. Optionally
  use **Replay last event** to demonstrate idempotency or create a new Case and **Simulate
  timeout** to reach Control Exception review.
- **Expected resume path:** selective evidence checks rerun, then material-fact confirmation,
  exception interpretation, final triage and local publication Governance Loops.
- **Expected outcome/key point:** the Coordinator never polls or fabricates evidence and
  cannot resume from the wrong source/correlation/schema/Case State version.

## What remains under AIRO control

At every journey, finish by confirming that the LLM cannot set materiality, 2LoD engagement,
the autonomy profile, a Gate bypass or final approval. A skipped Gate is a versioned policy
decision; a non-applicable Gate is not described as an AI action. Formal external writes are
not implemented—the publication adapter creates only an idempotent local demo record.

See [SAMPLE_COVERAGE.md](SAMPLE_COVERAGE.md) for every sample, expected control and Gate.
