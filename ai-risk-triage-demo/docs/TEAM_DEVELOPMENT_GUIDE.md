# Team development guide

## 1. Agree governance before changing code

Create an accountable decision register covering:

- questionnaire owner and version;
- materiality rule owner, thresholds, dealbreakers and minimum routes;
- 2LoD trigger owners and required evidence;
- decisions reserved to AIRO or specialist teams;
- autonomy eligibility, exclusions, sampling and rollback authority;
- LLM-permitted tasks, prohibited tasks and approved models;
- publication authority and target-system owners.

Do not encode workshop assumptions as policy. Keep unapproved rules labelled as demo or
draft configuration.

## 2. Stabilise deterministic engines first

Move real rules from Python into reviewed, signed and effective-dated configuration only
after the rulebook is agreed. Validate configuration at startup. Record the exact version in
every case and review pack. Add golden tests for boundaries, dealbreakers and overlapping
2LoD triggers.

## 3. Build an evidence contract

For each answer define:

- authoritative source types;
- minimum evidence and acceptable freshness;
- extraction schema and confidence treatment;
- deterministic consistency checks;
- who may confirm or amend the structured fact.

LLM output is proposed evidence metadata, not a confirmed fact. Low confidence or material
conflicts should route to AIRO.

## 4. Treat orchestration as a state machine

Each node should have one purpose and explicit inputs/outputs. Keep external side effects out
of interrupting nodes because a resumed LangGraph node restarts. Make integration calls
idempotent and record external references. Unknown states and policies must fail to a human
gate.

For a new evidence capability, change all four explicit control layers: add a typed action,
add a versioned registry contract and handler, allow it in the deterministic supervisor only
when its prerequisites hold, and add verifier tests. Do not let an adapter call another tool
or write case state directly.

For a new Progressive Automation pattern, register a governed pattern ID and maximum profile,
then add a demonstration fixture and downgrade/Gate/sampling tests. Never expose the profile
as a normal case-creator choice and never let an LLM promote a case or population.

For a new demonstration, add one typed `DemonstrationCase` in `app/samples.py`. Keep its
expected metadata descriptive: runtime policy, engines and tools must independently produce
the tested result. Use a protected fixture identifier or `DemonstrationControls` only for a
repeatable technical lesson such as sampling, low confidence or budget exhaustion; never
match a complete title and never add the controls to `CreateCaseRequest`. Update
`docs/SAMPLE_COVERAGE.md` and add a parameterised transition test that asserts typed actions,
statuses and Gates rather than explanatory wording.

When a desired demonstration takes a different route, inspect the actual supervisor and
deterministic rules first. Correct the fixture if its expectation is wrong. Correct core code
only for a real governance defect, and add a regression test; do not weaken a Gate or change a
risk rule to make a card look convenient.

## 5. Validate the autonomy ladder

Recommended rollout:

1. **Shadow:** run proposals beside the current manual process.
2. **Human governed:** AIRO confirms every material point and decision.
3. **Conditional:** automate preparation, retain mandatory decisions.
4. **Exception based:** apply only to approved low-risk populations with sampling.
5. **Straight through:** consider only after approved evidence, limits and rollback.

Promotion criteria should include false-low rate, override rate, evidence completeness,
process time, incident rate and sampling results. Set a kill switch that returns the population
to human-governed mode.

## 6. Calibration and monitoring

Use expert-labelled historical cases before launch. Analyse:

- exact-band agreement and distance from expert assessment;
- false-low outcomes by risk factor and use-case pattern;
- false-high outcomes and avoidable escalations;
- threshold sensitivity and question influence;
- dealbreaker and minimum-route coverage;
- 2LoD trigger precision/recall where labels exist;
- human overrides, recurring exceptions and evidence defects.

The Calibration tab and API demonstrate this separation. A calibration service produces
diagnostics; rule owners decide changes through controlled approval. Never allow online model
learning to rewrite materiality or routing rules.

## 7. Production backlog

Suggested workstreams:

| Workstream | Initial deliverable |
|---|---|
| Product/governance | Decision register, RACI, scope and success measures |
| Risk methodology | Versioned questionnaire and deterministic rule configuration |
| Evidence | File ingestion, provenance, redaction and evidence-quality policy |
| Orchestration | Production checkpointer, queues, retries and recovery tests |
| Human experience | Accessible review workspace, rationale standards and SLA views |
| Integrations | Governed Confluence/SharePoint adapters after approval gates |
| Assurance | Threat model, privacy assessment, model evaluation and control testing |
| Intelligence | Override/exception taxonomy, calibration dashboards and trend monitoring |

## 8. Definition of done for a production release

- The same input and rule version produce reproducible deterministic results.
- Every material output has source evidence or an explicit gap.
- Every skipped gate has a recorded deterministic policy explanation.
- Reserved decisions cannot be bypassed through API or UI.
- The system can restore and resume interrupted cases after restart.
- External writes are approved, idempotent and auditable.
- False-low and high-risk scenario tests meet approved tolerance.
- Operations can monitor, suspend and return automation to a safer profile.
