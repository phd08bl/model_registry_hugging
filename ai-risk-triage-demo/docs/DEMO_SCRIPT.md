# Demonstration script

All profiles, patterns, sampling keys and expected outcomes are illustrative demo policy,
not approved PwC or MRO methodology. Expected sample metadata explains a lesson and is
never read by the StateGraph to force a runtime result.

## Recommended 10–15 minute journey

### 1. Establish the boundary (1 minute)

Open the home page in mock mode. Point to the governance banner and the three sample groups.
Explain that there is one stateful Case Coordinator. The deterministic supervisor assigns
permissions; a bounded router can recommend evidence actions; the registry invokes only
approved tools; the verifier labels limitations; deterministic engines propose risk; AIRO
owns judgement. Expand **Create custom case** to show that there is no profile selector.
Confirm that the runtime banner reads **MOCK · deterministic demonstration runtime**. The
workflow strip distinguishes **AIRO decision recorded**, **Skipped by deterministic policy**
and **Gate not triggered**; these labels come from current Case state and the autonomy log.

### 2. Router, verifier and evidence Gate (4 minutes)

Create **Human Governed — Policy RAG Evidence Conflict**, then select **Start Coordinator**.

What should happen:

1. Extraction and consistency objectives are supervised and routed.
2. The RAG and supplier checkers run as advisory tools.
3. Tool versions, selection reasons and verification dispositions appear in the concise
   trace.
4. The questionnaire/evidence personal-data conflict creates mandatory Gate 1.

At Gate 1 choose `add_evidence`. Paste:

```text
Privacy assessment confirms that employee names and corporate email addresses are authorised
for access filtering. Supplier due diligence, contract, assurance and model-change
responsibilities are approved and documented.
```

Use this questionnaire update:

```json
{"personal_data": true}
```

Resume. Open **Inputs & Evidence** and point out the invalidation history, superseded
evidence result and targeted evidence rerun. Continue with `confirm`, `proceed`, `confirm`
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

### 3. Progressive permissions (3 minutes)

Create **Conditional Review — Approved Internal Translation Helper**. Start it and show that
clean read-only preparation occurs automatically, while final triage remains an AIRO Gate.

Create **Exception Based — Deterministically Sampled for Review**. Confirm Gate 2. Gate 4 is
required because the protected stable sampling key selected the case—not because risk was
elevated. Compare with **Exception Based — Eligible Approved Pattern**, whose final-triage
Gate is policy-skipped and whose skip rationale/version is retained.

Create **Straight Through Demo — Eligible Internal Summary**. Confirm Gate 2. The eligible
case completes later permitted decisions and a local-only publication record. Emphasise that
this is a local demonstration policy, not a production route. Contrast it with **Straight
Through Attempt — Ineligible Autonomous Customer Case**: its approved maximum is visible,
but elevated declarations deterministically downgrade the effective profile to
`human_governed` before the LLM runs.

### 4. Fail-closed advanced control (2 minutes)

Create **Advanced — Invalid Tool Proposal**. Start it. The protected mock proposes the
materiality engine for an evidence-extraction action. Show:

- proposal disposition `rejected`;
- no invocation and no result;
- tool-call count still zero;
- Gate 1 escalation and rejection rationale in the action trace.

Optionally compare **Advanced — Low-Confidence Router Result** or **Advanced —
Action-Budget Exhaustion**. Both stop deterministically without an infinite loop.

### 5. Prompt injection or selective replanning (2–4 minutes)

For a security close, start **Advanced — Prompt-Injection Evidence**. The embedded “ignore
previous instructions” text stays untrusted; an intentionally invalid citation is rejected;
the security issue is displayed; no approval, rule or Gate changes.

For a dependency close, start **Advanced — Selective Replanning and Invalidation**. Confirm
Gate 2. At Gate 3 select `edit_answers` and enter:

```json
{"personal_data": true}
```

Explain in the rationale that attendee identifiers are now in scope. The Coordinator archives
the earlier materiality, 2LoD and dependent results, reruns relevant evidence actions and both
engines because their inputs changed, regenerates dependent output, and returns to AIRO.

## Active sample run cards

The expected actions below describe observable router/tool trace entries. Foundational
consistency and citation checks may also run because deterministic policy requires them. For
standard Gates, use a short AIRO rationale even when the form does not require one.

### `human_evidence_conflict`

- **Learning objective:** bounded evidence routing, citation verification, Gate 1 and
  selective replanning.
- **Starting condition:** a policy-RAG questionnaire says no personal data while evidence
  mentions employee names/email and lacks privacy/supplier assurance.
- **Assigned profile:** `human_governed`.
- **Expected router/tools:** extraction, RAG and supplier actions through
  `evidence_extractor`, `rag_evidence_checker` and `supplier_evidence_checker`.
- **Verification:** accepted deterministic checks plus advisory semantic results.
- **Expected Gates:** evidence request → input confirmation → exception resolution → final
  triage → publication.
- **Exact user actions:** start; at Gate 1 choose `add_evidence`, paste the privacy/supplier
  text from the main journey and set `{"personal_data": true}`; then choose `confirm`,
  `proceed`, `confirm`, `approve`.
- **Expected outcome/key point:** `CLOSED` with a local publication record; the corrected
  answer invalidates evidence-dependent work and the two engines remain human-governed.

### `human_full_review`

- **Learning objective:** default human governance and AIRO ownership for a clean new case.
- **Starting condition:** a low-risk internal meeting summary is not an approved pattern.
- **Assigned profile:** `human_governed`.
- **Expected router/tool:** `extract_submitted_evidence` / `evidence_extractor`.
- **Verification:** accepted extraction with advisory semantic limitation.
- **Expected Gates:** input confirmation → exception resolution → final triage → publication.
- **Exact user actions:** start, then `confirm`, `proceed`, `confirm`, `approve`.
- **Expected outcome/key point:** `CLOSED`; low apparent risk does not grant autonomy.

### `agentic_ai_autonomy`

- **Learning objective:** assess another agentic system without creating a multi-agent
  coordinator.
- **Starting condition:** an internal agent can plan and propose tool actions.
- **Assigned profile:** `human_governed`.
- **Expected router/tool:** `check_agentic_ai_autonomy` /
  `agentic_ai_autonomy_checker` (with foundational evidence actions).
- **Verification:** advisory findings about action limits, approval, stop and rollback.
- **Expected Gates:** input confirmation → exception resolution → final triage → publication.
- **Exact user actions:** start, inspect autonomy observations, then `confirm`, `proceed`,
  `confirm`, `approve`.
- **Expected outcome/key point:** `CLOSED`; advisory LLM/tool analysis cannot set autonomy or
  final risk.

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

### `straight_through_ineligible`

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
- **Expected Gate:** evidence request.
- **Exact user actions:** start and stop at Gate 1 to inspect proposal, zero tool calls and
  rejection rationale.
- **Expected outcome/key point:** `AWAITING_INFORMATION`; low confidence fails closed and no
  infinite loop occurs.

### `invalid_tool_proposal`

- **Learning objective:** the action/tool allowlist blocks risk-engine misuse.
- **Starting condition:** protected mock proposes `materiality_engine` for evidence
  extraction.
- **Assigned profile:** `human_governed`.
- **Expected router/tools:** invalid proposal only; no invocation/result.
- **Verification:** `rejected`, with policy mismatch and `tool_not_invoked=true`.
- **Expected Gate:** evidence request.
- **Exact user actions:** start and inspect the last trace; do not submit a Gate decision for
  the teaching stop.
- **Expected outcome/key point:** `AWAITING_INFORMATION`; the LLM cannot cross the
  deterministic risk-decision boundary.

### `prompt_injection_evidence`

- **Learning objective:** submitted instructions remain data and invalid citations escalate.
- **Starting condition:** evidence contains an “ignore previous instructions” phrase and a
  protected invalid citation marker.
- **Assigned profile:** `human_governed`.
- **Expected router/tool:** extraction / `evidence_extractor`.
- **Verification:** `escalate`; citation check fails and a security issue is retained.
- **Expected Gate:** evidence request.
- **Exact user actions:** start and inspect the untrusted evidence, citation failure and
  security issue; stop at Gate 1.
- **Expected outcome/key point:** `AWAITING_INFORMATION`; no instruction changes rules,
  Gates, approval or outcome.

### `selective_replanning`

- **Learning objective:** dependency-aware invalidation distinguishes current from
  superseded results.
- **Starting condition:** a clean internal summary reaches deterministic proposals before a
  material input correction.
- **Assigned profile:** `human_governed`.
- **Expected router/tool:** extraction / `evidence_extractor`, then targeted rerouting after
  the edit.
- **Verification:** accepted/advisory results before and after replanning.
- **Expected Gates:** input confirmation → exception resolution → final triage → publication,
  with renewed review after change.
- **Exact user actions:** start; `confirm` Gate 2; at Gate 3 choose `edit_answers` with
  `{"personal_data": true}` and rationale that attendee identifiers are in scope; inspect
  invalidations, then complete the renewed displayed Gates.
- **Expected outcome/key point:** dependent materiality/2LoD/review outputs are archived and
  rerun; unrelated history is preserved.

### `action_budget_exhaustion`

- **Learning objective:** a hard action budget prevents unbounded tool loops.
- **Starting condition:** protected fixture permits only one tool call while more objectives
  remain.
- **Assigned profile:** `human_governed`.
- **Expected router/tool:** one extraction / `evidence_extractor`, followed by deterministic
  `escalate_to_airo` with no tool.
- **Verification:** extraction accepted/advisory; escalation recorded as `escalate`.
- **Expected Gate:** evidence request.
- **Exact user actions:** start and inspect call count `1`, remaining budget `0` and the final
  no-tool trace; stop at Gate 1.
- **Expected outcome/key point:** `AWAITING_INFORMATION`; the bounded loop terminates safely.

## What remains under AIRO control

At every journey, finish by confirming that the LLM cannot set materiality, 2LoD engagement,
the autonomy profile, a Gate bypass or final approval. A skipped Gate is a versioned policy
decision; a non-applicable Gate is not described as an AI action. Formal external writes are
not implemented—the publication adapter creates only an idempotent local demo record.

See [SAMPLE_COVERAGE.md](SAMPLE_COVERAGE.md) for every sample, expected control and Gate.
