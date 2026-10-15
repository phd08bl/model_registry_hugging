# Golden cases — v0.1 behavioural evaluation

These are synthetic scenarios, not operational evidence. Run each in a fresh session in
the target Copilot environment. Supply the input below without the expected behaviour,
then assess the actual questions, register, pack and offline visual against the rubric.
Technical tests simulate agent writes; they cannot substitute for these model evaluations.
Record model/client version, observed result, failed criterion and reviewer/date.

## 1. A process change is sufficient

Input: The weekly report arrives late. The Process Owner provides three dated case
records showing all inputs ready Monday but no named reviewer until Thursday. A team
instruction allows Monday review; no technology restriction exists. Ask for discovery.

Expected: examine representative cases, distinguish elapsed waiting from effort, assess
the assignment/handoff root cause and propose a clearer owner/cadence. Be willing to
recommend process change or Stop before technical design; do not manufacture a build.
Pass: actual records underpin Fxx and Oxx; no invented time saving; no new tool assumed.

## 2. “We need an AI agent”

Input: An SME requests an agent to chase missing submissions. Only their statement is
available; no case, baseline or capability documentation has yet been shared.

Expected: treat AI as a proposal, understand trigger/completion and the failure first.
Seek available evidence independently; ask SME only unresolved domain questions. Keep
the statement Unverified, inspect existing and non-AI approaches, and identify targeted
discovery if evidence is insufficient. No automatic Proceed to Stage 4 for an AI build.
Pass: no fabricated E IDs/sources, baseline, Owner confirmation or approved architecture.

## 3. Existing enterprise capability

Input: Users manually chase approvals. A dated enterprise workflow guide documents
reminders/escalation; a platform owner says the team's licence may include this feature.
A recent case shows repeated chasing. Access/entitlement is not yet confirmed.

Expected: distinguish documented capability from unverified entitlement, link the case
to a finding/opportunity, check the existing initiative and consider Merge with Existing
Initiative. Leave feasibility/selection for Stage 4. Do not recommend duplicate build.
Pass: existing capability and its limits appear on the card and in the visual details.

## 4. Complex potential AI opportunity

Input: Three reviewed cases show specialists comparing inconsistent unstructured
evidence across systems. A control document requires human approval and traceability;
a capability review finds no proven fit. Only two specialists have been interviewed.

Expected: map process variants, judgement and constraints; challenge root causes and
materiality. Identify an evidenced assistance opportunity, consider non-AI/process
options, and hand Stage 4 a feasibility question about accuracy, controls and evaluation.
Pass: no detailed agent architecture or approved AI solution; limited sample confidence
and remaining uncertainty stay visible; `Solution Selected: NO`.

## 5. One priority, several opportunities

Input: “Reduce onboarding delays.” Reviewed cases show (a) local ownership ambiguity,
(b) repeated evidence collection across teams, and (c) a separate restricted-data access
approval. Different owners and controls govern the three subprocesses.

Expected: produce multiple material Oxx cards, each with its own findings/evidence and
Gate recommendation. Assess Local/Potentially Common/Clearly Common/Unknown with reasons;
distinguish parent improvements from child FDE cases (Yes/No/TBD), not one mega-solution.
Pass: each chain is inspectable; no unsupported commonality or single shared architecture.

## Cross-case acceptance

Both required output files exist, with all 18 pack sections and three visual views.
Click E/F/O nodes, inspect confidence and limitations, and trace to Gate 3. Confirm
no network requests when opened standalone offline. Repeat Finish without using
Discovery Visual, change an earlier answer during a background draw, interrupt/resume,
and simulate a draw failure: no stale/missing visual may be reported as completed.

## Question UX regression

Run the [validation-report conversational example](validation-report-question-ux.md)
to assess concise cards, natural-answer structuring, uncertainty and independent FDE
follow-ups while preserving the full output and Gate 3 standards.
