# Human-Governed Agent Design

**Implementation status:** current local demo, tested in mock mode. All materiality, 2LoD,
pattern, profile, sampling and autonomy rules are illustrative. Real external writes,
enterprise identity and production policy are not implemented.

## Responsible-AI classification

This is **Code Agency**: software maintains Case State, selects from bounded permitted work,
invokes capabilities, evaluates results, replans, waits and resumes. It is not autonomous
risk authority. Its agency is constrained by deterministic policy and interruptible human
governance.

One Coordinator is used because evidence, policy, risk proposals, human decisions,
invalidation and publication all belong to one accountable Case. Multiple independent agents
would duplicate state and make authority/replay boundaries harder to prove.

## Agent objective

Every Case receives versioned objective `case-objective-1.0`: prepare a complete, cited and
policy-compliant triage package; keep proposals and evidence current; escalate meaningful
judgement; obtain required AIRO decisions; and finish only after deterministic completion
criteria pass.

The Coordinator is agentic because it observes the full state, receives a structured
supervisor decision, selects or requests one permitted action, invokes a tool, verifies the
result, updates only authorized fields, reassesses, selectively replans and can durably pause
for human authority or an external event.

## Authority boundary

| Component | May do | May not do |
|---|---|---|
| Policy Supervisor | Assign/downgrade profiles; set allowlists/mandatory action; enforce versions, budgets, waits and completion | Delegate policy authority to a model |
| LLM recommender | Recommend one allowlisted evidence action; extract cited candidate facts; produce labelled advisory challenge observations | Execute tools; confirm facts; change rules/profile; select materiality/2LoD; bypass a Gate; approve |
| Action Authorizer | Reject or authorize the proposed capability immediately before execution | Waive a failed check |
| Tool Registry | Validate contract, permission, profile, input, version and idempotency; invoke registered local capabilities | Invoke unknown or unrestricted actions |
| Result Verifier | Check identity/version/confidence/citations/authority and classify status | Turn unverified output into a fact |
| Deterministic engines | Produce versioned illustrative materiality and independent 2LoD proposals | Produce the final AIRO decision |
| AIRO | Confirm facts, accept/resolve exceptions, override proposals with rationale, authorize recovery and approve local publication | Resume with stale/mismatched/replayed authority context |

Submitted evidence is untrusted data. Prompt-like text inside it cannot change the system
prompt, policy, protected rules, permissions, Governance Loops or decisions.

## Action selection and permission

The supervisor returns the complete `SupervisorDecision`: allowed/prohibited actions,
allowed tools, mandatory action, LLM permission, current Governance Loop/external event,
readiness, four budgets, profile, completion candidacy and Control Exception rationale.

If one foundation action is mandatory, deterministic selection is used and the LLM is not
called. Otherwise the LLM can choose one action only from the supplied allowlist. Its
Pydantic proposal contains action, tool, reason, required inputs, confidence and whether
human review is recommended. The Action Authorizer then performs immediate checks; the LLM
never calls a tool directly.

## Tools, results and evidence classes

Contracts declare authority class, schemas, data permissions, read-only/external boundary,
allowed profiles, timeout/retry policy, verifier and owner. Tool invocations bind Case State
and rule versions plus an idempotency key. Result status is one of `VERIFIED`,
`VERIFIED_WITH_LIMITATIONS`, `ADVISORY_ONLY`, `REJECTED` or `EXECUTION_FAILED`.

State distinguishes candidate facts, AIRO-confirmed facts, deterministic evidence gaps,
evidence conflicts, LLM/tool advisory observations and AIRO-confirmed exceptions. The review
pack and UI preserve those labels. Candidate/advisory content never silently becomes a
confirmed material fact.

## Governance Loops and fail-safe behavior

The implemented loops are Evidence Resolution, Material Fact Confirmation, Exception
Interpretation, Final Triage Decision, Publication Approval and Control Exception Review.
They are trigger-based. A clean Case does not create an empty exception loop.

Human decisions are bound to decision ID, authority, Case, Gate/loop, Case State version and
rule version. External waits use a separate typed event contract with source, correlation,
schema, version, timeout and idempotent replay. Wrong or unknown context fails closed.

At each Human Gate, deterministic code produces a structured reviewer task: the blocking
items, exact response or artifact required, supporting citations, allowed resolutions and the
effect of each decision. The UI may recommend an allowed action only when that recommendation
is explicitly derived from this policy contract. It never exposes hidden chain-of-thought and
never converts an LLM observation into a confirmed fact or final risk decision.

Unauthorized proposals, exhausted budgets, invalid state, event timeout, tool/verification
failure or a blocked completion guard create a structured Control Exception. No further tool
execution occurs until AIRO authorizes a permitted recovery or terminal action. Failed-safe
workflow closure is distinct from a risk rejection.

## Deterministic controls

Profile assignment, permission policy, readiness, action authorization, materiality, 2LoD,
Gate triggering, invalidation and completion remain deterministic. Calibration is diagnostic
and never changes those rules. Straight-through operation is local-demo-only.

For implementation topology see [ARCHITECTURE.md](ARCHITECTURE.md). For safe extension steps
see [TEAM_DEVELOPMENT_GUIDE.md](TEAM_DEVELOPMENT_GUIDE.md).
