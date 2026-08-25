# Release-Readiness and Exception-Driven Upgrade Report

**Release candidate:** `0.2.0`  
**Review date:** 25 August 2026  
**Audience:** AI Tech & Tooling and AI Risk Oversight

## 1. Baseline findings and tests

- The workspace was not a Git repository, so no `git status`, history or diff was available.
- Existing user files and the working virtual environment were preserved.
- The pre-upgrade system already had one StateGraph Coordinator, local Case/checkpoint
  persistence, deterministic materiality/2LoD, system-assigned profiles, bounded routing,
  tools/verification, AIRO Gates, invalidation, local publication, multiple LLM adapters and
  calibration diagnostics.
- Gaps were fixed downstream Gates, incomplete full-state supervision/authorization, no
  explicit lifecycle/domain split, readiness/completion guard, machine external-event wait,
  Control Exception lifecycle or comprehensive replay/version binding.
- Baseline on Python 3.13.9: 129 tests passed; Ruff lint/format, compileall and `pip check`
  passed. No type checker was configured.

The detailed pre-change evidence is in
[CURRENT_AGENT_DESIGN_REVIEW.md](CURRENT_AGENT_DESIGN_REVIEW.md).

## 2. Architecture consistency

The repository now consistently implements one Coordinator with a structured deterministic
`SupervisorDecision`, deterministic mandatory selection or one bounded LLM recommendation,
immediate `ActionAuthorisation`, typed tools/result history, lifecycle/domain phase,
readiness before independent materiality/2LoD proposals, trigger-based Governance Loops,
correlated External Event Wait, Control Exception recovery, selective invalidation and a
deterministic completion guard.

The LLM cannot set policy, profile, materiality, 2LoD, Governance Loops, authorization, final
decisions or publication authority. AIRO retains final authority.

## 3. Files retained, refactored and added

- All active application, test, configuration and static UI files were retained.
- Added `app/agent/authorizer.py`, `readiness.py`, `completion.py` and
  `tests/test_exception_driven_coordinator.py`.
- Refactored schemas, state, supervisor, graph, Coordinator, registry, verifier, invalidation,
  autonomy policy, database summaries, APIs, versions, samples and the static workspace.
- Retained the root reference design and two implementation-review documents as clearly
  labelled historical/pre-upgrade evidence, not current authority.
- No source files were merged or removed. Current explanations were reconciled into the
  README and authoritative documents for architecture, agent design, development and demos.

## 4. Removed/generated artifacts

No uncertain source, configuration, documentation or asset was removed. Only ignored,
regenerable artifacts were cleaned: bytecode/cache directories, Pytest/Ruff caches,
editable-install egg metadata and local Case/checkpoint databases. `data/.gitkeep` remains.
The ignored `.venv/` was deliberately preserved for the developer and must not be packaged.

## 5. Dependencies and packaging

- Package/application version is `0.2.0`; Python support remains `>=3.11`.
- Existing runtime dependencies were retained because imports and clean installation confirm
  active use; development dependencies remain in the `dev` extra.
- Static UI files are packaged/served correctly.
- Mock mode requires no Ollama, API key or provider network. Ollama is optional.
- No software licence is declared; the receiving organization must decide licensing.

## 6. Security and data review

- No real credentials, personal data, production URLs or connection strings were found;
  search matches are placeholders or sanitization tests.
- `.env` and databases are ignored; `.env.example` contains placeholders only.
- Evidence is untrusted. External events validate Case/correlation/source/type/schema/state
  version/integrity and duplicate IDs are idempotent.
- Real Confluence, email, SharePoint and task writes remain unimplemented; publication is
  local-demo-only. Unknown permission/state fails closed.

## 7. Markdown reviewed

Every Markdown file was inspected. Current terminology, modules, APIs, Windows commands,
samples, diagrams and provider settings were reconciled. All materiality, 2LoD, pattern,
profile and autonomy rules are labelled illustrative; straight-through is demo-only;
calibration never updates rules; future concepts are not claimed as implemented.

## 8. Defects corrected

- Removed meaningless exception interrupts for clean cases.
- Corrected invalidation/readiness dependency direction and stale-marker clearing.
- Reran the relevant supplier check after external evidence without exhausting unrelated
  journeys.
- Corrected tool-budget exception classification and hid impossible recovery actions.
- Bound human decisions/events to Case/rule/state versions and replay IDs.
- Made workflow failures `FAILED_SAFE` Control Exceptions, not risk rejections.
- Added UI/API support for event waits, recovery and structured histories.
- Corrected current-action semantics: completed/rejected proposals now remain in history while
  transient execution fields are cleared, and the supervisor is reevaluated for Gate/event
  pauses.
- Separated Policy Supervisor executable actions from AIRO Gate decisions, exposed the
  configured completion contract before closure, removed the merged workspace warning list,
  and made HITL/event/transition/end trace records expandable cycles.
- Replaced the misleading linear “StateGraph” progress bar with a read-only Case journey
  derived from lifecycle/domain state. It separates phases from Gates and displays human and
  external waits, Control Exceptions, policy skips, invalidation, stale outputs and reopened
  work without treating tabs as workflow controllers.
- Added cache-safe versioned frontend assets and `no-store` demo responses so old JavaScript
  cannot render against new HTML/CSS. Reworked the workspace, Gate, Questionnaire,
  Assessment, Second-Line and Review Pack views around readable decision summaries with
  structured records available through progressive disclosure.
- Replaced generic Human-Gate instructions with a typed reviewer-task contract. The UI now
  identifies each blocking item, compares current and evidence-supported values, provides
  citations and required artifacts, presents allowed decisions as cards, guides common
  questionnaire corrections and previews invalidation/selective-rerun effects before submit.
- Removed the Human Governance card's desktop-only nested scrollbar and viewport-height cap.
  Gate actions now use the normal document scroll, the Case-header continuation shortcut
  focuses the selected decision, and detailed decision impacts collapse beneath a concise
  expected-next-step summary.

## 9. Tests added or modified

The 162-test suite covers all profiles, system assignment, supervision, deterministic/LLM
selection, immediate authorization, tool/result contracts, citations, rejected proposals,
prompt injection, budgets, invalidation/replanning, interrupts/restart, readiness, engines,
review pack/publication, calibration, all 18 samples, mock/Ollama-unavailable behavior,
events/timeouts/replay, recovery, human authority replay/version and completion blockers.
It also covers malformed-output retry/exhaustion, post-final-decision invalidation, the external
response event alias and the connected UI trace/stale-result contract.
It additionally guards exact deterministic/bounded-LLM selection labels, current-versus-
historical action display, separate supervisor/Gate permissions, visible completion criteria,
non-merged evidence issue views and structured supporting trace cycles.
It now also guards the numbered Cases 1–8 contract, the dedicated multiple-permitted-action
journey, featured-case ordering and teaching metadata, selective conflict rework, protected
high-risk downgrades and verification-failure classification as a fail-closed journey.
Human-Gate regressions additionally verify precise Gate 1 conflict guidance, typed reviewer
tasks and decision impacts for every Gate type, and rejection of an empty Edit Answers action.

## 10. Final quality results

| Check | Result |
|---|---|
| Pytest | 162 passed |
| Ruff lint | passed |
| Ruff format check | passed |
| Compileall | passed |
| Pip dependency check | passed |
| Type checker | not configured |

## 11. Clean-environment verification

A new temporary Python 3.13.9 environment installed successfully with
`pip install -e ".[dev]"`, then passed the then-current 147 tests and `pip check`. After the
final catalogue, featured-Case, UI-alignment and Human-Gate guidance regressions were added,
the project environment passed all 162 tests. A real Uvicorn mock process
using isolated temporary databases returned health `ok`/`mock-llm`; `/`, CSS and JS returned
HTTP 200; 18 samples loaded; all eight featured Case numbers were present and ordered; and
the malformed-result sample applied one retry, updated no candidate facts and paused at
Control Exception review. The multi-action Case recorded an LLM recommendation from a
multi-action allowlist, deterministic authorisation, advisory verification and
`reassess_case`; the supplier Case entered External Event Wait; and the elevated Case was
downgraded to Human Governed. No pre-populated database or Ollama was required. The temporary
process and isolated databases were removed afterward.

The final live sweep started all 18 samples successfully. Every sample that paused at a Human
Gate exposed at least one blocking reviewer task and a one-to-one impact contract for every
allowed decision; the supplier sample correctly entered its separate external-event wait.
Case 3 exposed the exact `personal_data` false-to-true correction with citations, accepted the
guided-equivalent update and advanced to Gate 2. Gates 2â€“5 and Control Exception review each
exposed their specific task kind.

The in-app browser list was empty after the documented connection retry, so no visual
click-through was possible. UI contract tests and live HTTP static/API verification passed.

## 12. Remaining limitations and uncertain files

- Local demo and synthetic fixtures only; all risk/autonomy policy is illustrative.
- Offline tests do not evaluate live-provider semantic quality.
- Enterprise identity/RBAC/SoD, secure document storage, DLP, observability, production event
  infrastructure and real integrations are not implemented.
- The historical root reference design is deliberately retained because future governance
  owners may need it. It is not runtime authority.
- No Git metadata was available for final diff/change attribution.

## 13. Final deliverable tree

```text
app/
  agent/{authorizer,completion,interrupts,invalidation,policy,readiness,router,tools,verifier}.py
  engines/{autonomy,lod2,materiality}.py
  llm/{base,factory,mock,ollama,openai,prompts}.py
  services/{calibration,evidence,review_pack}.py
  static/{app.js,index.html,styles.css}
  config.py coordinator.py database.py graph.py main.py
  samples.py schemas.py state.py versions.py
data/.gitkeep
docs/{AGENT_DESIGN,AGENTIC_STATEGRAPH_AND_PROGRESSIVE_AUTOMATION,ARCHITECTURE}.md
docs/{CURRENT_AGENT_DESIGN_REVIEW,DEMO_SCRIPT,IMPLEMENTATION_REVIEW}.md
docs/{LLM_PROVIDER_GUIDE,RELEASE_READINESS_REPORT,SAMPLE_COVERAGE}.md
docs/TEAM_DEVELOPMENT_GUIDE.md
tests/conftest.py and 14 test modules
.env.example .gitignore Makefile pyproject.toml README.md
AIRO_Agentic_Case_Coordinator_Reference_Design.md
```

## 14. Exact Windows run commands

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
$env:LLM_MODE = "mock"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

If `py` is unavailable, use `python -m venv .venv` with a supported interpreter. Selecting a
VS Code interpreter does not change an open terminal; reopen it or activate with
`.\.venv\Scripts\Activate.ps1`.

Ollama mode:

```powershell
ollama serve
ollama pull llama3.2:3b
$env:LLM_MODE = "ollama"
$env:OLLAMA_MODEL = "llama3.2:3b"
$env:ALLOW_MOCK_FALLBACK = "true"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## 15. Recommended handover sequence

1. Read `README.md`, `ARCHITECTURE.md` and `AGENT_DESIGN.md`.
2. Install/run mock mode and execute README quality commands.
3. Demonstrate RAG conflict, clean routine, invalid proposal and missing-supplier event cases.
4. AIRO validates authority, illustrative-policy warnings, Loop triggers and recovery.
5. Tooling owners review provider/data and operational controls before hosted/production use.
6. Agree licence, rule owners, evaluation data, monitoring, approval and rollback.
