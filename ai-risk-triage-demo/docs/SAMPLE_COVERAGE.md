# Demonstration-case coverage

**Status:** current 18-case catalogue. Eight numbered Cases provide the required major-feature
journeys; six dedicated Progressive Automation Cases, together with the featured human and
downgraded journeys, cover all four policy-assigned profiles; four additional control Cases
demonstrate bounded failure paths.

All profiles, patterns, sampling keys, materiality rules, 2LoD triggers and expected outcomes
are illustrative demo policy. Expected metadata documents and tests the lesson; the StateGraph
never reads it to force a runtime result.

## Eight major feature Cases

| # | Sample key and purpose | Runtime evidence | Expected control path | Expected result |
|---|---|---|---|---|
| 1 | `human_full_review` — standard low-risk Case | Routine extraction; later deterministic single-action selections; no evidence exception; readiness; negligible materiality; empty independent 2LoD proposal | Input confirmation → engines → final AIRO review → controlled local publication | `AIRO_CONFIRMED`, then `PUBLISHED_LOCAL_DEMO` |
| 2 | `multiple_evidence_actions` — multiple permitted evidence actions | Supervisor exposes several actions; bounded LLM recommends one; deterministic Authoriser binds the Tool Contract; verifier records accepted/advisory disposition; Coordinator re-observes and continues | Evidence action loop → input confirmation → final AIRO review → local publication | `AIRO_CONFIRMED` |
| 3 | `human_evidence_conflict` — questionnaire/evidence conflict | Questionnaire says no personal data; cited evidence names employee identifiers; deterministic consistency conflict; citation verification; AIRO amendment; extraction/consistency/citation rerun while unrelated RAG verification remains current | Evidence Resolution → input confirmation → exception interpretation where applicable → final review → publication | `AIRO_CONFIRMED` |
| 4 | `missing_supplier_evidence` — missing supplier evidence | External foundation model; missing contract/due-diligence assurance; durable correlated stakeholder wait; same-Case event resume; supplier check rerun; invalid correlation, timeout and duplicate-event controls | External Event Wait → selective evidence rework → input/exception/final/publication Gates | `AIRO_CONFIRMED` |
| 5 | `agentic_ai_autonomy` — autonomy exception | Autonomous and critical-process declarations; agentic control checker; missing approval/pause/kill-switch/rollback evidence; severe deterministic materiality; independent 2LoD triggers | Input confirmation → Exception Interpretation → final AIRO review → publication | `AIRO_CONFIRMED` |
| 6 | `selective_replanning` — stale outputs and selective replanning | Initial engines and final AIRO decision; one material-fact amendment; dependent proposals/review pack/decision become stale; extraction preserved; dependency-selected reruns only | Initial G2/G3/G4/G5 → amendment → renewed evidence and AIRO review | `AIRO_RECONFIRMATION_REQUIRED_AFTER_INVALIDATION` |
| 7 | `malformed_tool_result` — tool verification failure | Authorised tool returns a protected malformed payload; output-schema rejection; no candidate/confirmed fact update; one bounded retry; unresolved failure | Tool execution → verifier retry → verifier escalation → Control Exception review | `CONTROL_EXCEPTION` |
| 8 | `straight_through_ineligible` — elevated/high-risk Case | Straight-Through Demo approved maximum; elevated declarations deterministically downgrade effective profile to Human Governed; severe proposal; mandatory second-line teams and protected Gates | Downgrade → evidence checks → G2/G3/G4/G5 | `AIRO_CONFIRMED`; no Router/profile bypass |

## Progressive Automation examples

| Sample | Policy-assigned effective profile | Teaching point | Expected Gates/result |
|---|---|---|---|
| `human_full_review` | `human_governed` | Low apparent risk never removes AIRO authority | G2, G4, G5; AIRO-confirmed local publication |
| `conditional_clean_final` | `conditional_review` | Clean read-only preparation may skip preparation Gates; final triage remains human | G4, G5 |
| `conditional_exception` | `conditional_review` | An unapproved-pattern exception restores exception review | G3, G4, G5 |
| `exception_based_eligible` | `exception_based` | Eligible, non-sampled Case records deterministic Gate skips | G2, G5; demo-policy auto-confirmation |
| `exception_based_sampled` | `exception_based` | Stable protected sampling—not risk or the LLM—requires final review | G2, G4, G5 |
| `exception_based_triggered` | `exception_based` | A confirmed exception overrides streamlined processing | G2, G3, G4, G5 |
| `straight_through_eligible` | `straight_through_demo` | Explicitly eligible low-risk fixture can complete later local-only decisions | G2; local demo publication only |
| `straight_through_ineligible` | `human_governed` (approved maximum `straight_through_demo`) | Elevated risk forces a pre-LLM policy downgrade | G2, G3, G4, G5 |

There is no user-selectable or fixture-controlled profile override. The deterministic
illustrative policy assigns both approved maximum and effective profile. Protected teaching
controls such as a stable sampling key, malformed output, low confidence or a one-call budget
change only the demonstrated route/result condition; they never change the assigned profile.
The catalogue and Case header label this distinction explicitly.

## Additional bounded-control Cases

| Sample | Control demonstrated | Expected result |
|---|---|---|
| `low_confidence_router` | Below-threshold recommendation; no invocation | Control Exception |
| `invalid_tool_proposal` | Non-allowlisted tool proposal rejected before execution | Control Exception |
| `prompt_injection_evidence` | Untrusted document instruction and invalid citation remain data, not authority | Control Exception |
| `action_budget_exhaustion` | One-call protected budget proves deterministic loop termination | Control Exception |

## Required metadata and verification

Every catalogue item supplies:

- expected path;
- expected dynamic actions;
- expected tools;
- expected verification statuses;
- expected exceptions;
- expected Governance Loops and Gates;
- expected final result;
- learning objectives explaining what the sample demonstrates;
- exact interactive steps;
- expected policy-assigned profile and approved maximum;
- protected teaching controls, explicitly labelled as not being a profile override.

`tests/test_featured_cases.py` validates the numbered Case mapping and the runtime behavior of
Cases 1, 2, 3 and 8. Existing sample, external-event, verifier, replanning and Progressive
Automation tests validate Cases 4–7, every fixture’s deterministic risk expectations, all four
effective profiles, stable sampling, Gate skips, retry/budget limits and protected decisions.

The exact wording produced by a live LLM is intentionally not asserted. Mock mode uses
protected deterministic teaching behavior; every live-provider mode uses the same typed
proposal, Authoriser, Tool Contract and Result Verifier boundaries.
