# Team development guide

This guide explains how to extend the current AIRO Case Coordinator without weakening its
governance boundary. All current rules and patterns are illustrative demo policy.

## Change principles

1. Keep one Coordinator and one authoritative Case state.
2. Put repeatable risk or permission decisions in deterministic, testable code—not prompts.
3. Let the LLM recommend evidence work only from supplied allowlists.
4. Invoke tools only through typed, versioned registry contracts.
5. Verify every result before it changes authoritative state.
6. Reserve material judgement, overrides and formal approval to AIRO Gates.
7. Fail unknown states, profiles, actions, tools and permissions closed.
8. Record versions and preserve prior results when dependencies change.
9. Label unapproved materiality, 2LoD, pattern and autonomy rules as illustrative.
10. Do not describe a future adapter or enterprise control as implemented.

Before encoding a real rule, identify its accountable owner, approval, effective date,
version, evidence requirements, exception handling, testing and rollback decision.

## Add a tool

Use this only for a capability the Coordinator actually invokes.

1. Add a narrow `ToolIdentifier` in `app/schemas.py`.
2. Add or reuse a Pydantic input/output model in `app/agent/tools.py`; forbid unexpected
   fields where the boundary requires it.
3. Add a `ToolContract` with purpose/version, authority class, schemas, data permissions,
   read-only/external boundary, timeout/retries, idempotency, result verifier, owner,
   profiles and implementation status.
4. Register one handler in `ToolRegistry._handlers`.
5. If the LLM router may select it, also follow **Add a router action** below.
6. Add deterministic verifier checks and explicit semantic limitations.
7. Add tests for unknown ID, version, schema, permission, timeout/retry, idempotency,
   sanitized failure and result verification.
8. Update `docs/ARCHITECTURE.md` and relevant sample documentation.

Do not add placeholder contracts for unimplemented future integrations. Describe them as
future considerations until an active, governed call path exists.

## Add a router action

1. Add an evidence-preparation-only `ActionType` in `app/schemas.py`. Decision actions such
   as approval, materiality selection, Gate bypass or profile change are prohibited.
2. Map it to exactly one active `ToolIdentifier` in `ACTION_TO_TOOL`.
3. Define its trusted input keys in `ACTION_INPUTS`; never execute model-authored payloads.
4. Add deterministic readiness/prerequisite logic to `plan_evidence_actions()` and/or
   `PolicySupervisor._planned_actions()`.
5. Ensure the policy provides both allowlists and the immediate `ActionAuthoriser` validates
   action/tool match, inputs, data permission, versions, budgets, confidence, profile and
   authority before execution.
6. Define how successful, advisory, rejected and failed results update Case state.
7. Include budget and loop termination behavior.
8. Test deterministic single-action selection, multi-action LLM selection, mismatched tool,
   non-allowlisted action, low confidence, provider failure and exhausted budget.

The graph and provider adapters must not gain provider-specific action branches.

## Add a governed pattern

1. Obtain an accountable, versioned policy decision outside the LLM.
2. Add exactly one pattern ID and maximum profile to `DEMO_PATTERN_MAXIMUMS`.
3. Add a matching typed `DemonstrationCase` in `app/samples.py`.
4. Keep expected metadata descriptive; the graph must independently produce the result.
5. Use `DemonstrationControls` only for a protected repeatable lesson such as stable
   sampling, low confidence, invalid tool proposal or reduced budget.
6. Test assignment, downgrade, eligibility, sampling, all expected Gates and completion.
7. Update `docs/DEMO_SCRIPT.md` and `docs/SAMPLE_COVERAGE.md`.

The policy registry and sample catalogue must have identical IDs. Never add a profile field
to the normal `CreateCaseRequest` or infer a profile from a user-editable title.

## Change a deterministic rule

Materiality, 2LoD and autonomy rules are separate control surfaces.

1. Confirm the rule owner, approval status and whether the change is demo-only or approved.
2. Change the smallest pure function in `app/engines/` or deterministic policy condition.
3. Increment the relevant constant in `app/versions.py`.
4. Add boundary tests, dealbreaker/minimum-route tests and overlapping-trigger tests.
5. Re-run every active sample; update an expected outcome only when the new approved rule
   genuinely changes it.
6. Run backtesting and sensitivity against suitable labelled cases.
7. Review false-low effects first and record the accountable change decision.
8. Update every document that explains the rule, version or journey.

Calibration output is evidence for human rule owners. It must never rewrite rules, versions
or thresholds automatically.

## Add a Gate

1. Define the reserved human decision and accountable authority.
2. Add a deterministic Gate requirement in the autonomy policy; unknown profiles must still
   require review.
3. Build the payload through `AIROInterruptController`, including typed `required_inputs`,
   evidence/citations, rule rationale, allowed decisions, `action_impacts`, required fields,
   selective reruns and rationale requirements. Every Gate must tell a reviewer exactly what
   is blocked and what a valid response requires.
4. Add the `interrupt()` node and explicit `Command` transitions in `app/graph.py`.
5. Keep all side effects outside the interrupting node because it restarts on resume.
6. Add status/current-Gate mapping in `CaseCoordinator._save_snapshot()`.
7. Update the UI guided inputs and impact preview without exposing irrelevant fields; retain
   structured JSON only as an advanced fallback when a simpler control is possible.
8. Test every required-input kind and decision-impact contract plus valid/invalid actions,
   required rationale, empty required submissions, restart/resume, cancel/return loops,
   profile requirements and fail-closed behavior.
9. Update both Mermaid diagrams and every sample affected by the Gate.

Prefer a named Governance Loop with a precise triggering condition. Do not add a fixed human
stop merely to preserve numbering; a clean routine Case must not pause at an empty exception
review.

## Add an external event

1. Define event type, expected source, schema version, due time, timeout action and Case State
   version in `ExternalEventExpectation`.
2. Create the expectation deterministically and route to the event-wait node; a machine wait
   is not a Human Gate.
3. Validate event-ID replay, Case ID, correlation, source, type, schema, Case State version
   and any artifact hash at the Coordinator boundary.
4. Treat the artifact as untrusted evidence, append rather than overwrite it, and invoke
   dependency-aware invalidation and selective rework.
5. Make timeout create a structured Control Exception.
6. Test valid resume, each mismatch, duplicate replay, timeout and restart.

## Change readiness, recovery or completion

- Keep readiness and completion as pure deterministic functions with explicit criteria.
- Never run materiality/2LoD on unconfirmed or stale required inputs.
- Create a structured `ControlException` when no safe transition exists; an execution failure
  is not a risk rejection.
- Expose only recovery actions supported by remaining budgets.
- Completion requires closed objectives/actions, no blockers/open Control Exception, current
  risk proposals/review pack, a final decision and reconciled local publication.
- Add regression tests for each new blocker and recovery transition.

## Update Case state

1. Add the key and type to `TriageState`.
2. Identify the sole node/service that owns each write and all readers in API/UI/tests/docs.
3. Decide whether the value is submitted, advisory, confirmed, authoritative, audit history
   or local output; do not blur those categories.
4. Add initialization in `CaseCoordinator` when a safe explicit default is required.
5. Add dependency handling to `invalidation_update()` if the value can become stale.
6. Ensure old values are archived rather than overwritten when governance evidence matters.
7. Update review-pack/version output only if the field belongs there.
8. Add creation, update, persistence, restart and UI-display tests as applicable.

Compatibility fields may remain only while an active caller uses them. Record their purpose
and remove them once repository-wide searches show no runtime, test, UI or documentation
dependency.

## Change or add an LLM provider

Follow the [LLM provider guide](LLM_PROVIDER_GUIDE.md). In summary:

1. Add narrow settings and use `SecretStr` for credentials.
2. Implement `StructuredLLMClient` or the full `LLMClient` contract.
3. Reuse `app/llm/prompts.py` and existing Pydantic result models.
4. Translate only expected provider failures to sanitized `LLMRuntimeError`.
5. Register one explicit provider builder; unknown modes must fail at startup.
6. Add fake-client tests with no key or network dependency.
7. Confirm provider metadata contains no secret, prompt, evidence or internal error body.

Changing transport never changes LLM authority.

## Update dependencies or packaging

1. Prove the dependency is imported or required by an active runtime/package path.
2. Put runtime libraries in `project.dependencies` and test/development tools in the `dev`
   extra.
3. Avoid adding a dependency for a small standard-library task.
4. Update the declared minimum only with compatibility evidence.
5. Install from `pyproject.toml` in a new temporary environment.
6. Run `pip check`, tests and quality checks.
7. Build a wheel and verify `app/static/index.html`, CSS and JavaScript are included.
8. Update Windows commands and provider instructions if startup changes.

Do not choose or add a software licence without the organisation's legal decision.

## Create a sample

1. Choose one learning objective not already demonstrated adequately.
2. Use synthetic, non-sensitive questionnaire/evidence text.
3. Add a governed pattern entry and typed `DemonstrationCase` with matching ID.
4. State what the sample demonstrates, its expected path, dynamic actions, tools,
   verification, exceptions, Governance Loops, final result and exact user steps.
5. Record both the policy-assigned effective profile and approved maximum. Label any protected
   teaching control explicitly; it must not act as a profile override.
6. Use a unique `featured_case_number`/`featured_case_name` only when the sample belongs to
   the required eight-Case feature set.
7. Confirm expected metadata cannot force graph behavior.
8. Add it to parameterized policy, risk and full mock-journey tests.
9. Update `SAMPLE_COVERAGE.md`, `DEMO_SCRIPT.md`, README counts and UI contract tests.

## Add tests

Prefer assertions on contracts and behavior over exact explanatory prose. For behavior
changes, test the failure path before or with the fix.

The minimum suite for governed changes includes:

- valid and invalid schema input;
- deterministic rule boundaries;
- policy allow/deny and unknown-state behavior;
- action/tool matching and no invocation after rejection;
- verifier accepted/advisory/escalated outcomes;
- prompt-injection and citation failure;
- evidence loop and selective invalidation;
- every affected Gate, interrupt and resume;
- budget/recursion termination; and
- mock operation without a live provider.

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m compileall -q app tests
.\.venv\Scripts\python.exe -m pip check
```

No type checker is currently configured; do not claim or add one solely for a routine change.

## Preserve governance controls during review

Before handover, confirm:

- normal users cannot select or upgrade profiles;
- the LLM cannot determine materiality, 2LoD, Gate bypass, rules or approval;
- every executed tool is registered, typed, allowlisted and verified;
- evidence is treated as untrusted and citations are checked;
- material changes invalidate dependent approvals/results;
- AIRO decisions and autonomy evaluations are auditable;
- publication remains a local demonstration with no enterprise credentials;
- all rules and patterns remain visibly illustrative; and
- mock mode is reproducible without Ollama or hosted network access.

For production, separately establish SSO/RBAC, separation of duties, approved evidence
storage, model gateway, security controls, monitoring, recovery, policy ownership, evaluation
tolerances and external-integration governance.
