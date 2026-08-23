# Release-readiness report

Review date: 23 August 2026  
Audience: AI Tech & Tooling and AI Risk Oversight  
Scope: complete local repository delivery review after the LLM-provider refactor

## 1. Baseline findings

- The workspace is not a Git repository (`.git` is absent), so `git status` and a final
  `git diff` are not available. Existing files were reviewed in place and no reset/checkout
  operation was used.
- The active implementation already had one `CaseCoordinator`, one LangGraph `StateGraph`,
  one policy supervisor, one router, one registry and one verifier.
- The source tree contained a checked-in/local `.venv`, Python/test/Ruff caches, stale
  editable-install metadata and approximately 12.2 GB of local SQLite Case/checkpoint data.
- Four Python files failed the configured Ruff format check.
- Static HTML/CSS/JavaScript was served in editable mode but not declared as package data,
  so it was absent from generated source metadata.
- `jinja2`, `python-multipart` and `DEFAULT_AUTONOMY_PROFILE` were declared but unused.
- Three router actions, five registry tools, one API route and two old base fixtures had no
  active runtime/API/UI/sample call path.
- The detailed Progressive Automation document reversed the current
  `straight_through_demo` canonical name and `straight_through` compatibility alias.
- The root text scratchpad duplicated demo guidance and contained machine-specific absolute
  links.
- No real API key, password, token, certificate or production connection string was found.
  Matches were placeholders, test fakes, example URLs or localhost configuration.
- No software licence was declared.

## 2. Baseline quality results

Environment: Python 3.13.9.

| Check | Untouched baseline |
|---|---|
| `python -m pytest` | 122 passed in 21.31 seconds |
| `python -m ruff check .` | Passed |
| `python -m ruff format --check .` | Failed: 4 files would be reformatted |
| `python -m compileall -q app tests` | Passed |
| Type checking | Not run; no type checker is configured |

The older “36 tests” statement in `IMPLEMENTATION_REVIEW.md` is retained only as a labelled
historical refactor baseline.

## 3. Architecture consistency

The final architecture remains:

> One stateful AIRO Case Coordinator uses a deterministic policy supervisor to control a
> bounded LLM evidence/action router and approved tools. Results are verified, evidence
> changes selectively invalidate/replan work, and meaningful judgement is escalated through
> AIRO Gates. Separate deterministic engines produce materiality and 2LoD proposals; AIRO
> retains final decision authority.

The audit confirmed StateGraph orchestration, persistent Case/checkpoint state, system-owned
profiles, bounded routing, typed tool contracts, verification, deterministic engines,
`interrupt()` Gates, invalidation/supersession, audit records, local publication, mock/Ollama/
OpenAI modes, backtesting and sensitivity. No competing agent or legacy graph is retained.

## 4. Files retained

- All active application packages under `app/`.
- All 13 original test modules and the new release-contract test.
- All original ten Markdown documents after status/current-implementation reconciliation,
  plus this release-readiness report.
- `.env.example`, `.gitignore`, `Makefile`, `pyproject.toml` and `data/.gitkeep`.
- `AIRO_Agentic_Case_Coordinator_Reference_Design.md`, deliberately retained as an uncertain
  but valuable historical/future design source with a prominent non-authoritative boundary.

## 5. Files refactored or updated

- `app/versions.py` was added to centralize runtime, policy, Gate, tool and rule versions.
- `app/main.py`, `app/coordinator.py` and provider/tool error paths were changed to avoid
  exposing raw internal exception text.
- Unreachable action/tool contracts and unreferenced base fixtures were removed from active
  source definitions without changing the governed workflow.
- `pyproject.toml` now declares packaged static assets and only used runtime dependencies.
- `.gitignore`, `.env.example` and the optional POSIX `Makefile` were reconciled.
- Provider, architecture, team-development, demonstration and root handover documentation
  were updated to the current implementation.

## 6. Content merged

- Exact journeys and expected controls for all 15 active cases were consolidated into
  `docs/DEMO_SCRIPT.md`; `docs/SAMPLE_COVERAGE.md` remains the compact coverage matrix.
- Current architecture responsibilities were consolidated into `README.md`,
  `docs/ARCHITECTURE.md` and `docs/AGENT_DESIGN.md`.
- The useful intent of the root scratchpad was already present in the authoritative README,
  agent design and demo script, so no unique content was lost when it was removed.

## 7. Files removed and evidence

| Removed item | Evidence |
|---|---|
| `New Text Document.txt` | No imports, packaging, runtime, test or Markdown references; duplicated existing guidance and contained absolute machine paths |
| `.venv/` | Reproducible local environment declared by `pyproject.toml` |
| `.pytest_cache/`, `.ruff_cache/`, all `__pycache__/` and `*.pyc` | Generated test/lint/interpreter caches |
| `airo_agentic_risk_triage_demo.egg-info/` | Stale editable-install metadata regenerated by installation/build |
| `data/cases.db`, `data/checkpoints.db` and checkpoint sidecars | Local runtime Case/checkpoint data; application creates empty stores automatically |

No uncertain source, test, configuration, Markdown or demonstration asset was removed.

## 8. Generated artifacts cleaned

The delivery tree excludes virtual environments, caches, bytecode, package metadata, build
output and local databases. `.gitignore` now prevents their recommit, including database
WAL/SHM sidecars, Ruff/mypy/coverage output, egg-info, build, distribution and log files.

## 9. Dependencies

- Removed `jinja2`: no template engine is imported; the UI is returned with `FileResponse`.
- Removed `python-multipart`: there are no `Form`, `File` or `UploadFile` routes.
- Retained FastAPI/Uvicorn, LangGraph/checkpoint SQLite, Pydantic/settings, HTTPX and OpenAI
  because each has an active import/runtime path.
- Retained pytest and Ruff only in the `dev` extra.
- Static UI package-data patterns were added and verified in the built wheel.
- Package/application version remains `0.1.0`; Python support remains `>=3.11`.

## 10. Markdown review

Every Markdown file was inspected:

- `README.md` is now the Windows-first delivery entry point and status matrix.
- `ARCHITECTURE.md` matches current StateGraph nodes, modules and publication boundary.
- `AGENT_DESIGN.md` explains Responsible AI Code Agency and deterministic/human limits.
- `TEAM_DEVELOPMENT_GUIDE.md` contains explicit tool/action/pattern/rule/Gate/state/
  dependency/sample/test procedures.
- `DEMO_SCRIPT.md` contains a run card for every active sample.
- `AGENTIC_STATEGRAPH_AND_PROGRESSIVE_AUTOMATION.md` uses current supervisor and profile terms.
- `LLM_PROVIDER_GUIDE.md` distinguishes implemented adapters from example extension code.
- `IMPLEMENTATION_REVIEW.md` is labelled historical.
- `SAMPLE_COVERAGE.md` is labelled current illustrative coverage.
- The root reference design is explicitly historical/future and non-authoritative.

All local Markdown links resolve. Referenced LangGraph, Ollama and official OpenAI framework
pages responded during the review. Mermaid node/component names were compared with current
code.

## 11. Defects corrected

- Static web assets are included in package builds.
- Raw workflow, tool-validation and Ollama transport exception bodies are no longer stored or
  returned through normal user-visible metadata.
- Unused actions/tools, stale base fixtures, obsolete configuration and an unused API route
  were removed.
- Governed pattern registry and active sample IDs must now match exactly.
- Canonical/compatibility straight-through terminology is consistent.
- Runtime/rule/version strings are centralized.
- Ruff formatting drift is corrected.

## 12. Tests added or modified

- Added package-version/static-data/dependency, Markdown-link and ignore-contract tests.
- Added governed-pattern/sample-registry coherence coverage.
- Added sanitization tests for stored workflow errors, tool failures and Ollama errors.
- Updated tool-registry idempotency coverage after removal of uncalled future adapters.
- Corrected the legacy straight-through alias test name/direction.

Existing deterministic engine, all-profile, router, verifier, injection, budget, selective
replanning, interrupt/resume, review-pack, publication, calibration and all-sample journeys
remain covered.

## 13. Final quality results

| Check | Final workspace result | Fresh-environment result |
|---|---|---|
| `python -m pytest` | 129 passed in 21.56 seconds | 129 passed in 21.42 seconds |
| `python -m ruff check .` | Passed | Passed |
| `python -m ruff format --check .` | Passed | Passed |
| `python -m compileall -q app tests` | Passed | Passed |
| `python -m pip check` | No broken requirements | No broken requirements |
| Type checking | Not run—no type checker configured | Not applicable |

The final workspace run occurred immediately before artifact cleanup. Running Python tests
again would intentionally recreate bytecode/test caches, so the cleaned delivery tree was
verified with read-only filesystem and search checks afterward.

## 14. Clean-environment verification

Using Python 3.13.9 in a uniquely named temporary virtual environment:

1. `pip` was upgraded and `pip install -e ".[dev]"` succeeded from `pyproject.toml`.
2. All 129 tests and configured quality checks passed.
3. `pip check` found no broken dependencies.
4. A non-editable wheel built successfully; `index.html`, `styles.css` and `app.js` were
   present in the wheel.
5. Mock-mode `GET /api/health` returned available provider `mock-llm`.
6. `/`, JavaScript and CSS loaded successfully.
7. All 15 samples were listed; `human_full_review` was created and started to the expected
   input-confirmation Gate.
8. A real hidden Uvicorn process started on localhost and its health endpoint responded.
9. The Case/checkpoint paths started empty and were created automatically in the temporary
   runtime directory.
10. No Ollama process or API key was required; mock mode made no provider network call.

The first clean pytest attempt encountered an existing machine permission problem in
pytest's shared `Temp\pytest-of-liyao` directory: 61 tests ran and 68 setup operations failed
with the same `PermissionError`. Rerunning the already-installed environment with an isolated
per-run `--basetemp` and cache directory produced the clean 129-pass result above. The
temporary environment, runtime databases and wheel-check directories were then removed.

The Windows `py` launcher is not installed on this review machine, so clean verification used
the documented `python -m venv` fallback. The declared `>=3.11` package range and exact
`py -3.11` handover command remain correct for machines with the standard launcher.

## 15. Remaining limitations

- Local demonstration only; no SSO/RBAC, separation of duties, protected production evidence
  store, enterprise model gateway, DLP, monitoring, backup/recovery or production database.
- No real Confluence, SharePoint, email or task-system integration.
- Prompt-injection detection is heuristic and is not a complete content-security control.
- Live Ollama/OpenAI semantic behavior is not exercised by the offline automated suite.
- All rule/profile/pattern values are illustrative and require accountable approval.
- Calibration never changes rules automatically.
- No static type checker is configured.
- No software licence is declared; this remains an organisational/legal handover decision.
- This workspace lacks Git metadata, so commit history/status/diff could not be reviewed.

## 16. Uncertain files deliberately retained

`AIRO_Agentic_Case_Coordinator_Reference_Design.md` was retained because it may be important
source material for future team decisions. It is now prominently separated from implemented
scope. No other uncertain file remains.

## 17. Final repository tree

```text
.env.example
.gitignore
AIRO_Agentic_Case_Coordinator_Reference_Design.md
Makefile
README.md
pyproject.toml
app/
  __init__.py
  config.py
  coordinator.py
  database.py
  graph.py
  main.py
  samples.py
  schemas.py
  state.py
  versions.py
  agent/
    __init__.py
    interrupts.py
    invalidation.py
    policy.py
    router.py
    tools.py
    verifier.py
  engines/
    __init__.py
    autonomy.py
    lod2.py
    materiality.py
  llm/
    __init__.py
    base.py
    factory.py
    mock.py
    ollama.py
    openai.py
    prompts.py
  services/
    __init__.py
    calibration.py
    evidence.py
    review_pack.py
  static/
    app.js
    index.html
    styles.css
data/
  .gitkeep
docs/
  AGENT_DESIGN.md
  AGENTIC_STATEGRAPH_AND_PROGRESSIVE_AUTOMATION.md
  ARCHITECTURE.md
  DEMO_SCRIPT.md
  IMPLEMENTATION_REVIEW.md
  LLM_PROVIDER_GUIDE.md
  RELEASE_READINESS_REPORT.md
  SAMPLE_COVERAGE.md
  TEAM_DEVELOPMENT_GUIDE.md
tests/
  conftest.py
  test_agent_governance.py
  test_autonomy.py
  test_calibration.py
  test_llm_providers.py
  test_lod2.py
  test_materiality.py
  test_mock_gate_journeys.py
  test_progressive_automation.py
  test_release_contract.py
  test_samples.py
  test_ui_gate_contract.py
  test_work_queue_resume.py
  test_workflow.py
```

## 18. Exact Windows commands

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
$env:LLM_MODE = "mock"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

If `py` is unavailable, run `python -m venv .venv` with a supported installed interpreter.
Selecting a VS Code interpreter does not update an already-open terminal; reopen it, activate
`.\.venv\Scripts\Activate.ps1`, or continue using the direct executable commands above.

Ollama mode:

```powershell
ollama serve
ollama pull llama3.2:3b
$env:LLM_MODE = "ollama"
$env:OLLAMA_MODEL = "llama3.2:3b"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## 19. Recommended handover sequence

1. AI Tech & Tooling reads `README.md`, then `ARCHITECTURE.md` and `AGENT_DESIGN.md`.
2. Install in a new virtual environment and run every quality command from the README.
3. Start mock mode and run the recommended demo plus one fail-closed advanced case.
4. AIRO reviews the illustrative rule/profile/pattern warnings and the Gate authority model.
5. Provider owners review `LLM_PROVIDER_GUIDE.md` before enabling any live endpoint.
6. Agree licence, rule owners, approved methodology, data handling and production controls
   before treating this as more than a demonstration.
7. Preserve `human_governed` as the starting production posture and require evidence,
   monitoring, sampling, approval and rollback for any future autonomy increase.

## Completion report

Release-readiness work is complete. The delivery tree contains only source, tests,
configuration, documentation and the empty runtime-data placeholder. It has no local virtual
environment, cache, bytecode, build/egg-info output, local database, log, secret file or
machine-specific scratchpad. A new team member can install the declared project, start mock
mode without Ollama, use the packaged UI and samples, and trace the governance boundary from
README to current architecture and developer guidance.
