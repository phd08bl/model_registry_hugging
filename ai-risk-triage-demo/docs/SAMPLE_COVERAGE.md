# Demonstration-case coverage

## Review-first gap analysis

This matrix records the post-refactor state inspected before sample changes.

| Agent feature | Existing sample coverage | Gap found | Implemented sample/change |
|---|---|---|---|
| Single Coordinator and deterministic engines | All original workflows used one graph | Boundary was not explained on each card | All cards and case views explain supervisor/router/tool/verifier/AIRO roles |
| System-assigned profiles | Governed fixtures existed; normal input had no profile | Expected metadata still used a legacy profile name; sampling used random case IDs | Typed governed fixtures, `straight_through_demo`, protected stable sampling keys |
| Bounded router and allowlist | Normal extraction/check routes | No low-confidence or invalid-tool journey | Low-confidence and invalid-tool advanced cases with no invocation on rejection |
| Result verification | Normal semantic limitations were traced | No invalid citation or injection sample | Prompt-injection sample with invalid citation, security issue and escalation |
| Selective replanning | Unit-level invalidation and an early evidence loop | No post-engine interactive proof | Selective-replanning case edits a risk input after engines and preserves superseded results |
| Progressive Automation | Four profiles broadly represented | Random sampling and outdated Gate descriptions | Eligible, sampled, exception, straight-through and downgraded cases use actual policy |
| Budget/failure controls | Supervisor unit tests | Escalation proposal could reach verifier without a tool result and lacked trace | Action-budget case plus explicit rejected/escalated no-tool trace node |
| Evidence checker depth | RAG/agentic/supplier tools existed | One keyword could mask all missing controls | Separate advisory observations for grounding/citations, action/rollback and supplier duties |
| Prompt-injection detection | Verifier had a heuristic | Exact “ignore previous instructions” phrase did not match | Optional-qualifier pattern fixed and regression-tested |
| UI explanation | Objective/profile/tool/budget and raw JSON existed | Samples grouped only by profile; distinctions relied on JSON | Three learning groups, expected lesson, AIRO attention, typed findings and concise trace |

## Final sample coverage matrix

Expected fields document and test a fixture; they never force graph output. “Policy-skipped”
means a recorded deterministic decision. A Gate absent because its triggering event did not
occur is not described as skipped by the AI.

| Sample | Effective profile | Router/tool feature | Verification feature | Expected Gates | Key learning |
|---|---|---|---|---|---|
| Policy RAG Evidence Conflict | human governed | LLM chooses among extraction, RAG and supplier checks | Citations plus advisory semantic limits | G1, G2, G3, G4, G5 | A conflict forces evidence review and a corrected answer replans |
| New Internal Meeting Summary | human governed | Extraction and deterministic consistency | Source-linked extraction is advisory | G2, G3, G4, G5 | New low-risk appearance does not grant autonomy |
| Agentic-AI Autonomy Controls | human governed | Agentic autonomy checker | Action-control findings remain advisory | G2, G3, G4, G5 | The Coordinator assesses another agent without becoming many agents |
| Approved Internal Translation Helper | conditional review | Automatic read-only preparation | Verified/advisory tool trace | G4, G5 | Clean preparation Gates are policy-skipped; final triage is human |
| Pattern Deviation Requires Review | conditional review | Evidence preparation plus challenge | Deviation remains an explicit issue | G3, G4, G5 | An approved maximum does not erase a case deviation |
| Eligible Approved Pattern | exception based | Automatic preparation | Verified results and skip records | G2, G5 | Non-sampled eligible case skips permitted later review |
| Deterministically Sampled for Review | exception based | Same eligible preparation | Stable sampling reason | G2, G4, G5 | Sampling, not higher risk, can require final review |
| Exception Requires Review | exception based | Preparation plus challenge | Exception separated from advisory observations | G2, G3, G4, G5 | Exceptions override streamlined processing |
| Eligible Internal Summary | straight-through demo | Approved read-only tools and local adapter | Versioned, idempotent local result | G2 | Maximum demo permissions remain tightly bounded |
| Ineligible Autonomous Customer Case | human governed (downgraded) | Agentic and supplier checks | Advisory findings plus deterministic engines | G2, G3, G4, G5 | Elevated declarations prevent straight-through authority |
| Low-Confidence Router Result | human governed | Protected mock returns 0.20 confidence | Proposal rejected; no invocation | G1 | Confidence policy fails closed |
| Invalid Tool Proposal | human governed | Router proposes deterministic engine as evidence tool | Allowlist rejection; no invocation | G1 | Router cannot cross the risk-decision boundary |
| Prompt-Injection Evidence | human governed | Extraction preserves untrusted text | Missing citation plus security observation | G1 | Document instructions never become system authority |
| Selective Replanning and Invalidation | human governed | Targeted rerouting after answer edit | Current/superseded distinction | G2, G3, then renewed review | Dependencies, not a blind reset, determine reruns |
| Action-Budget Exhaustion | human governed | One permitted tool call, then deterministic escalation | Explicit no-tool escalation trace | G1 | Bounded loops cannot recurse indefinitely |

## Capability coverage assertions

`tests/test_samples.py` validates every fixture’s policy assignment, documented deterministic
risk expectation, rejection paths, injection handling, budget stop and selective
invalidation. `tests/test_progressive_automation.py` covers all four effective profiles,
stable sampling and Gate-skip behaviour. Registry, verifier, router and policy contract tests
remain in `tests/test_agent_governance.py`.

The exact wording produced by Ollama is intentionally not asserted. Mock mode uses protected
scenario controls stored outside normal creation input. Ollama mode uses the same Pydantic
proposal/result boundaries, but semantic wording may vary.
