# Agent-design implementation review

Review date: 23 August 2026. Untouched baseline: **36 tests passed in 2.22 seconds**.

This table records the initial review findings before implementation. “Sufficient” means the
existing capability met the requested governance outcome and was deliberately retained.

| Target capability | Existing implementation | Sufficient? | Gap or design concern | Implemented change | Affected files |
|---|---|---:|---|---|---|
| One stateful Coordinator | One `CaseCoordinator` and one `StateGraph`; engines/services were capabilities, not agents | Yes | None; splitting into role-playing agents would weaken traceability | Retained and documented | `app/coordinator.py`, `app/graph.py`, docs |
| Deterministic materiality and 2LoD | Separate transparent Python engines with versions and tests | Yes | Invocation was not represented as an approved tool contract | Retained engines; invoked through the registry boundary | `app/engines/*`, `app/agent/tools.py`, `app/graph.py` |
| Durable AIRO Gates | LangGraph `interrupt()` and `Command(resume=...)` with SQLite checkpoints | Mostly | Payload shape was duplicated and lacked several decision-contract fields | Added shared interrupt controller; retained durable mechanics | `app/agent/interrupts.py`, `app/graph.py` |
| Immutable bounded objective | No explicit objective model in case state | No | Mission could only be inferred from documentation | Added frozen typed objective and completion criteria | `app/schemas.py`, `app/coordinator.py`, `app/state.py` |
| Deterministic policy supervisor | `AutonomyPolicyEngine` decided gate requirements | Partial | It did not control actions, tools, budgets, router access, external actions, or profile assignment | Added `PolicySupervisor` around the retained gate engine | `app/agent/policy.py`, `app/engines/autonomy.py` |
| System-assigned profiles | Creator supplied `autonomy_profile` directly | No | Normal creators could select stronger autonomy | Removed the field from normal API input; added governed demo fixtures and deterministic downgrades | `app/schemas.py`, `app/coordinator.py`, `app/samples.py`, UI |
| Typed action contracts | Evidence/challenge methods returned typed results, but no action/tool/trace contracts | No | No schema-level allowlist for LLM action selection | Added enums and Pydantic contracts with forbidden extra fields | `app/schemas.py` |
| Approved tool registry | Direct function and LLM calls | No | No single versioned permission/validation/idempotency boundary | Added one registry covering implemented, mocked and safe local adapters | `app/agent/tools.py` |
| Bounded LLM router | Fixed LLM extraction/challenge calls | Partial | No structured selection among several permitted evidence actions | Added allowlist-only router with direct single-action path and safe fallback | `app/agent/router.py`, `app/llm/*` |
| Explicit bounded loop | Linear extraction/check sequence with evidence re-entry | Partial | No observe/supervise/validate/execute/verify loop or action budget | Added named bounded-loop nodes; kept engines and Gates explicit | `app/graph.py`, `app/state.py` |
| Result verification | Pydantic validated provider response schemas | Partial | No deterministic identity/version/citation/authority/injection result checks | Added `ResultVerifier` and advisory limitations | `app/agent/verifier.py`, `app/graph.py` |
| Structured issue/state separation | Gaps, inconsistencies and exceptions had separate lists; advisory findings shared follow-up fields | Partial | Missing typed issues, actions, budgets, trace and authoritative/superseded results | Strengthened state with typed records while retaining compatibility fields | `app/state.py`, `app/schemas.py` |
| Selective invalidation | Answer/evidence changes reran broad evidence flow; stale results were not explicitly archived | No | Final and derived outputs could lack an explicit invalidation history | Added dependency-aware invalidation and superseded-result history | `app/agent/invalidation.py`, `app/graph.py` |
| Progressive automation as permission | Gate sequence changed deterministically by profile | Partial | Profile was user-selected and logs lacked full eligibility/risk/sampling context | System assignment, downgrade, permission checks and richer autonomy log | `app/agent/policy.py`, `app/graph.py` |
| Safe external actions | Publication was local only and warned about future adapters | Mostly | No executable contract proving approval and idempotency controls | Added approval-gated, idempotent local demonstration adapters; no real writes | `app/agent/tools.py` |
| LLM provider unavailable | Governed mock fallback existed and runtime was recorded | Yes | Router needed the same provider-neutral fallback path | Added shared prompts, provider registry, generic fallback and typed adapters | `app/llm/*` |
| Calibration | Backtest and sensitivity existed and never changed rules | Yes | None | Deliberately left unchanged | `app/services/calibration.py` |

## Architecture conflicts rejected

- Separate Evidence, Materiality, 2LoD, Challenge or Publication agents were not created.
- A generic ReAct loop was not introduced; it would obscure deterministic engines and AIRO
  decision gates.
- Real Confluence, email or task writes were not added.
- Existing illustrative scores, thresholds and 2LoD rules were not replaced or presented as
  PwC/MRO methodology.
- SQLite checkpointing, FastAPI, pluggable LLM/mock modes and human interrupt/resume semantics were
  retained.
