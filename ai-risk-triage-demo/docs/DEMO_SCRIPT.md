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

## What remains under AIRO control

At every journey, finish by confirming that the LLM cannot set materiality, 2LoD engagement,
the autonomy profile, a Gate bypass or final approval. A skipped Gate is a versioned policy
decision; a non-applicable Gate is not described as an AI action. Formal external writes are
not implemented—the publication adapter creates only an idempotent local demo record.

See [SAMPLE_COVERAGE.md](SAMPLE_COVERAGE.md) for every sample, expected control and Gate.
