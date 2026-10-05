# MRO Forward Deployed Engineering (FDE) Operating Guidelines

## 1. Purpose and Positioning

This document defines the standard operating process for MRO Forward Deployed Engineering (FDE). It is intended for Process Owners, MRO Leadership / SLT, FDE Leads, AI Tech & Tooling, the wider MRO Tech & Tooling workstream, delivery teams and relevant SMEs.

The model is deliberately designed so that:

- **Stage 1 is quick and light for Process Owners.** It should capture only enough information to describe the process problem and desired outcome for prioritisation.
- **Stage 2 is for Leadership / SLT prioritisation.** SLT decides whether the outcome is important enough to investigate, who owns it and where FDE should start.
- **Stage 3 is the formal FDE Discovery process.** FDE leads process decomposition, evidence gathering, pain-point analysis and opportunity identification.
- **Stages 4–8 are an enhanced and standardised version of the current MRO Tech & Tooling workstream.** They formalise work that already happens today: solution assessment, research, PoCs, vertical slices, evaluation, productionisation, testing, rollout and benefits review.
- **Existing work should not be discarded or restarted.** Existing research, PoCs, test results, delivery artefacts and decisions should be mapped to the relevant stage and reused as evidence.
- **Use proportionality.** Light cases should remain light; more complex, higher-impact or agentic solutions should use more of the toolkit.

The core operating discipline is:

> **Use Cards to structure the questions, Activities to guide the work, Evidence to verify conclusions, Checklists to challenge readiness, Gates to make decisions, and Generated Artefacts to communicate the record. Use proportionality to determine how much of each is required.**

---

# 2. End-to-End Operating Model

> **Problem → Priority → Discover → Choose → Prove → Assess → Deliver → Measure**

| Stage | Primary purpose | Primary owner |
|---|---|---|
| **1. Candidate Process Problem & Outcome** | Capture a lightweight candidate problem and desired outcome | Process Owner / Sponsor, supported by FDE |
| **2. Leadership Priority, Ownership & Discovery Mobilisation** | Prioritise the outcome and select the first discovery scope / wave | MRO Leadership / SLT |
| **3. FDE Discovery & Process Decomposition** | Understand the real process, evidence, pain points and opportunities | FDE Lead |
| **4. Options, Delivery Route & Target Solution** | Select the simplest appropriate intervention and define what must be proved | FDE + Tech & Tooling + Process Owner |
| **5. Experiment, PoC & Vertical Slice** | Test the riskiest assumptions with the smallest credible experiment | FDE + Engineering + Users |
| **6. Evaluation, Controls & Production Readiness** | Evaluate what was proved and define what production must contain | FDE + Process Owner + Delivery / Governance SMEs |
| **7. Production Delivery, Testing, Controlled Rollout & Handover** | Productionise, test, release and transfer into BAU | Delivery Owner + Tech & Tooling + Process Owner |
| **8. Adoption, Benefits, Learning & Reuse** | Confirm adoption, outcome, benefits, reuse and next steps | Process Owner + FDE / Tech & Tooling |

---

# 3. Roles and Responsibilities

## Process Owner

The Process Owner owns the **business process and business outcome**, not the Workbench administration.

The Process Owner should:
- raise or sponsor candidate process problems;
- confirm the problem is real;
- confirm the intended process outcome;
- validate Discovery findings;
- make relevant users and SMEs available;
- accept the business fit of the selected intervention;
- support experiment/UAT where relevant;
- accept the implemented process into BAU;
- own or accept the benefits conclusion.

The Process Owner should **not** be expected to populate every Card or maintain every FDE artefact.

## MRO Leadership / SLT

Leadership should:
- prioritise business/process outcomes rather than individual technology ideas;
- select the first Discovery Wave where a priority spans multiple teams/process variants;
- confirm sponsorship and Process Owner accountability;
- allocate or approve discovery capacity;
- review material scaling, reuse and investment decisions;
- avoid prematurely approving a specific technology solution before Discovery.

## FDE Lead

The FDE Lead acts as the **orchestrator and structured problem-solving lead**.

The FDE Lead should:
- operate the FDE Workbench;
- structure candidate problems;
- prepare material for prioritisation;
- lead process decomposition and Discovery;
- gather and link evidence;
- facilitate option assessment;
- define bounded experiments;
- coordinate stage gates;
- maintain traceability across stages;
- ensure learning and reusable patterns feed later cases/waves.

## AI Tech & Tooling / MRO Tech & Tooling

The workstream should:
- assess technical feasibility;
- identify existing/reusable MRO capabilities;
- build PoCs and vertical slices;
- support architecture and delivery-route decisions;
- develop production solutions;
- perform technical testing and support release;
- build reusable components where justified.

Stages 4–8 should be treated as a **standardised extension of the current Tech & Tooling operating model**, not a replacement for it.

## Methodology Owners / SMEs

They should:
- clarify required methodology, professional judgement and controls;
- help define representative cases and evaluation criteria;
- challenge whether the solution preserves required process standards.

## Delivery / Product / Service Owners

They should:
- accept delivery capacity;
- own production implementation;
- ensure supportability;
- maintain the production service after handover.

---

# 4. Broad Priorities, Process Variants and Discovery Waves

Leadership may prioritise a broad outcome such as:

> **Improve Independent Validation Efficiency**

This does not imply every validation team has the same process.

A Process Family may contain different Process Variants:
- AI Validation
- Pricing Model Validation
- Economic Model Validation
- other validation teams

Recommended pattern:

```text
Leadership Priority / Process Family
        ↓
Light cross-wave scan where needed
        ↓
SLT selects Initial Discovery Wave
        ↓
Detailed FDE Discovery for that variant
        ↓
Improvement Opportunities
        ↓
Selected Child FDE Cases
        ↓
Stages 4–8
```

Detailed Discovery for all waves does **not** need to be completed before delivery starts. Use a rolling-wave model:

```text
Wave 1 Discovery → Stages 4–8
                         ↓
                  Wave 2 Discovery can start
```

Evidence from earlier waves should make later waves faster and more focused.

---

# 5. Parent and Child FDE Cases

A broad Leadership Priority can remain a **Parent Case**.

Do not create a Child Case for every pain point.

Create a separate Child FDE Case only where an opportunity has a materially distinct:
- business outcome;
- accountable owner;
- solution route;
- experiment;
- delivery lifecycle;
- risk/control profile.

Otherwise keep related opportunities under the same case.

---

# 6. Standard Stage Pattern

Every stage uses the same operating pattern:

1. **Structured Data / Cards** — the structured facts, decisions and records required for the stage.
2. **Activities** — what the responsible people actually need to do.
3. **Checklist** — minimum readiness conditions before the stage closes.
4. **Evidence** — evidence supporting conclusions, not just attachments.
5. **Decision / Gate** — accountable decision about whether/how to proceed.
6. **Generated Artefact** — readable summary generated from the structured record.

The Cards are the primary record. Generated documents are views of that record.

---

# Stage 1 — Candidate Process Problem & Outcome

## Purpose / Key Question

> **Is there a sufficiently clear MRO process problem or improvement outcome to put forward for prioritisation?**

Stage 1 is deliberately **quick and light**. It is not detailed Discovery and does not approve a tool, PoC or delivery capacity.

## Main Participants

- Process Owner / Sponsor / Function Lead / IVT Head / appropriate senior colleague
- FDE Intake Lead
- potential Process Owner if not yet confirmed
- SMEs/users only where a small clarification is required

## Structured Data / Cards

### Card 1A — Candidate Problem Card

| Question | Response |
|---|---|
| What process or workflow needs improvement? | |
| What triggers or starts the process? | |
| What marks successful completion? | |
| What is the current problem or limitation? | |
| Give one recent example. | |
| Who experiences the problem? | |
| Which teams/process variants are affected? | |
| What is the approximate frequency, volume or scale? | |
| What is the main efficiency, quality, risk, control or delivery impact? | |
| What outcome should improve? | |
| How would we recognise improvement? | |
| Who is the proposed Process Owner? | |
| Which users/SMEs could support Discovery? | |
| Is the process local or potentially common across MRO? | |
| Are there existing tools, PoCs, backlog items or initiatives? | |
| What evidence/examples are currently available? | |

### Card 1B — FDE Intake Assessment

| Assessment | Response |
|---|---|
| Process Family | |
| Candidate scope | Local / Team-specific / Broad Process Family / Cross-MRO |
| Requested solution mentioned by sponsor | Optional; not treated as agreed solution |
| Underlying problem sufficiently clear? | Yes / Partly / No |
| Related existing initiative/tool? | |
| Possible duplicate? | No / Partial / Yes |
| Potentially common MRO capability? | Yes / Possibly / Unclear / No |
| Likely routing | FDE / Existing Programme / BAU Process Change / Platform / Other |
| Key information gap before prioritisation | |
| FDE recommendation | Ready / Clarify / Combine / Route Elsewhere / Stop |

## Main Activities

1. Candidate raises the problem.
2. Complete a short written intake or 15–20 minute conversation.
3. FDE separates the **problem/outcome** from a requested technology.
4. Identify broad process boundary only; do not decompose subprocesses.
5. Identify affected users/teams and indicative scale.
6. Identify likely Process Owner and users/SMEs.
7. Check known backlog, tools and initiatives.
8. Consider local vs potentially wider-MRO relevance.
9. FDE produces Candidate Brief and recommendation.

## Stage Checklist

- [ ] Candidate describes a process problem/outcome rather than only requesting a tool.
- [ ] Broad process/workflow is understandable.
- [ ] At least one recent example is available where practical.
- [ ] Affected users/teams are identified.
- [ ] Desired outcome is understandable.
- [ ] Initial scale/frequency/materiality is known where available.
- [ ] Proposed Process Owner identified.
- [ ] Relevant users/SMEs could support Discovery.
- [ ] Existing work/duplicates checked.
- [ ] Local vs potentially wider-MRO relevance considered.
- [ ] Enough information exists for Leadership comparison.

## Evidence

Minimum evidence only:
- recent case/example;
- request/email/Teams message;
- process document;
- indicative volume/data;
- audit/control issue;
- existing backlog/tool/PoC;
- user feedback.

No full evidence pack or validated baseline is required.

## Gate 1 — Ready for Prioritisation?

FDE Intake Lead decides:
- Ready for Stage 2
- Clarify
- Combine with Existing Candidate
- Route Elsewhere
- Stop

This does **not** mean Leadership has prioritised the case or delivery capacity is committed.

## Generated Artefact — Candidate Brief

- Process / Process Family
- Candidate Problem
- Recent Evidence / Example
- Affected Users / Teams
- Indicative Scale / Materiality
- Desired Outcome
- How Improvement Could Be Recognised
- Proposed Process Owner
- Local / Potentially Common Across MRO
- Existing Related Work
- Key Information Gaps
- FDE Recommendation

## Stage 1 Boundary

Stage 1 does **not** require:
- detailed process mapping;
- subprocess decomposition;
- root-cause analysis;
- detailed baseline;
- requirements;
- technology selection;
- Copilot vs Cortex decision;
- PoC;
- delivery estimate;
- confirmed Child Cases.

> **Stage 1 principle: Capture the problem well enough to prioritise it; do not try to discover or solve it yet.**

---

# Stage 2 — Leadership Priority, Ownership & Discovery Mobilisation

## Purpose / Key Question

> **Does MRO want to prioritise this business outcome, who is accountable for it, and where should FDE Discovery start?**

Stage 2 approves **Discovery**, not technology delivery.

## Main Participants

- MRO Leadership / SLT
- Process Owner
- Leadership Sponsor / IVT Head
- FDE Lead
- Tech & Tooling Lead
- users/SMEs are usually nominated, not deeply involved

## Structured Data / Cards

### Card 2A — Leadership Priority & Outcome

| Question | Response |
|---|---|
| What business/process outcome are we trying to improve? | |
| Why does this matter to MRO? | |
| Which Leadership/MRO priority does it support? | |
| What efficiency, quality, risk, control or delivery issue does it address? | |
| What happens if no action is taken? | |
| Is the issue local, cross-IVT or potentially MRO-wide? | |
| Is there enough evidence to justify Discovery? | |
| Who is the Leadership Sponsor? | |
| Who is the accountable Process Owner? | |
| Does this overlap with existing work? | |
| What decision is Leadership being asked to make? | |

### Leadership Prioritisation Assessment

Use H/M/L or concise narrative.

| Factor | Assessment | Rationale |
|---|---|---|
| Strategic alignment | H/M/L | |
| Risk/control/quality value | H/M/L | |
| Scale/user impact | H/M/L | |
| Potential efficiency benefit | H/M/L | |
| Potential cross-MRO reuse | H/M/L | |
| Urgency | H/M/L | |
| Evidence of current problem | H/M/L | |
| Process Owner readiness | H/M/L | |
| SME/user availability | H/M/L | |
| Interaction with existing capacity | H/M/L | |

### Card 2B — Discovery Mobilisation & Wave Scope

| Question | Response |
|---|---|
| Process Family | |
| Known Process Variants / teams | |
| Cross-wave scan required? | Yes / No |
| Initial Discovery Wave | |
| Why start with this wave? | |
| Discovery question | |
| In scope | |
| Out of scope | |
| Users / SMEs | |
| FDE Lead | |
| Indicative capacity / timebox | |
| Target date for findings | |
| Related initiatives / dependencies | |
| Future candidate waves | |
| Leadership conditions | |

## Light Cross-Wave Scan

Use only where a broad priority spans materially different teams/process variants.

| Process Variant | Indicative Pain/Opportunity | Strategic Relevance | Existing Work | Discovery Readiness | Notes |
|---|---|---|---|---|---|

This is **not** Stage 3 Discovery. Its only purpose is to help SLT select the first wave.

## Main Activities

1. FDE prepares concise Leadership pack.
2. Process Owner validates broad problem/outcome.
3. Leadership compares candidates.
4. Leadership prioritises / holds / combines / redirects / declines.
5. Where needed, perform a light cross-wave scan.
6. SLT selects Initial Discovery Wave.
7. Confirm Sponsor and Process Owner.
8. Assign FDE Lead and Discovery capacity.
9. Nominate users/SMEs.
10. Define Discovery question and target findings date.

## Stage Checklist

- [ ] Leadership understands the desired outcome.
- [ ] Strategic relevance is sufficiently understood.
- [ ] Sponsor identified where required.
- [ ] Process Owner confirmed and accepts accountability.
- [ ] Existing/overlapping work considered.
- [ ] Leadership understands approval is for Discovery, not Build.
- [ ] Main process variants understood at high level where relevant.
- [ ] Initial Discovery Wave selected where needed.
- [ ] Discovery question is clear.
- [ ] Users/SMEs can participate.
- [ ] FDE capacity/timebox allocated.
- [ ] Target findings date agreed.
- [ ] Leadership conditions recorded.

## Evidence

- Stage 1 Candidate Brief
- FDE Intake Assessment
- Process Owner confirmation
- strategic/priority statements
- indicative impact evidence
- cross-wave scan if used
- existing work/capacity information

No detailed process map or full business case is required.

## Gate 2 — Approved for Detailed FDE Discovery?

Leadership decides:
- Prioritise & Mobilise Wave 1
- Hold
- Combine
- Route Elsewhere
- Decline

For a broad priority, Gate 2 identifies the first Discovery Wave but does not commit MRO to future waves or to a build.

## Generated Artefact — Leadership Priority & Discovery Mobilisation Record

- Candidate / Priority
- Desired Outcome
- Decision / Relative Priority
- Leadership Sponsor
- Process Owner
- Process Family
- Initial Discovery Wave
- Reason for Wave Selection
- Discovery Question
- FDE Lead
- Users / SMEs
- Capacity / Timebox
- Target Findings Date
- Future Candidate Waves
- Conditions / Dependencies
- Decision Maker / Date

> **Stage 2 principle: Prioritise the outcome, establish accountability, choose the first Discovery scope and mobilise enough capacity to learn — without prematurely approving what to build.**

---

# Stage 3 — FDE Discovery & Process Decomposition

## Purpose / Key Question

> **How does the selected process variant actually work, where are the material problems, what evidence supports them, and which improvement opportunities are worth taking forward?**

Stage 3 converts broad Leadership priority into evidence-based process understanding and actionable opportunities.

## Main Participants

- FDE Lead
- Process Owner
- Methodology Owner
- actual users / SMEs
- team leads / handoff owners
- Tech/Data/Platform/Security SMEs where required

## Structured Data / Cards

### Card 3A — Process & Controls

Capture:
- process purpose;
- start trigger;
- genuine completion;
- in/out-of-scope boundary;
- inputs/outputs;
- main steps;
- methodology/judgement;
- controls;
- exceptions;
- measures.

### Card 3B — Ownership & Handoffs

| Step/Subprocess | Responsible Role | Input Provider | Output Recipient | Decision/Approval | Typical Wait | Escalation/Failure Owner |
|---|---|---|---|---|---|---|

### Card 3C — User Tasks & Real Cases

Walk through at least one representative recent case.

| Task Step | Input | User Action | Tool/System | Human Judgement | Active Time | Waiting/Rework | Pain Point | Required Control |
|---|---|---|---|---|---|---|---|---|

### Card 3D — Systems, Data & Evidence

| Source/System | Purpose | Owner | Authoritative? | Access | Interface | Quality/Traceability Issue | Restriction | Production Consideration |
|---|---|---|---|---|---|---|---|---|

### Card 3E — Pain Points, Baseline & Root Causes

For each material pain point capture:
- process location;
- affected users;
- frequency/scale;
- impact;
- evidence;
- likely root cause;
- symptom vs root cause;
- workaround;
- baseline;
- desired improvement.

### Card 3F — Process Decomposition & Common-vs-Variant Assessment

| Subprocess | Purpose | Owner | Key Pain Points | Materiality | Existing Initiative | Opportunity? |
|---|---|---|---|---|---|---|

Reuse classification:
- Local
- Potentially Common
- Clearly Common
- Unknown

### Card 3G — Current-State Consensus & Opportunity Map

Record:
- process boundary;
- subprocesses;
- genuine process variants;
- handoffs;
- controls/judgement;
- data/evidence;
- delays/rework;
- baseline;
- exceptions;
- uncertainty;
- Process Owner confirmation.

### Improvement Opportunity Card

| Field | Content |
|---|---|
| Opportunity | |
| Pain Point Addressed | |
| Supporting Evidence | |
| Process Step | |
| Affected Users | |
| Desired Outcome | |
| Indicative Value | H/M/L + rationale |
| Constraints | |
| Existing Related Work | |
| Reuse Potential | Local / Potentially Common / Common / Unknown |
| Child Case Required? | Yes / No / TBD |
| Recommended Next Action | |

## Main Activities

1. Confirm Stage 2 Discovery boundary/question.
2. Map end-to-end process.
3. Decompose into meaningful subprocesses.
4. Walk through recent real cases.
5. Identify roles, handoffs, waiting, rework, judgement and controls.
6. Map systems, evidence, data, access and restrictions.
7. Capture baseline where useful.
8. Identify pain points and root causes.
9. Map existing tools/PoCs/initiatives.
10. Convert evidence into improvement opportunities without prematurely selecting technology.
11. Assess common vs variant capability.
12. Playback current state and resolve material disagreement.
13. Recommend opportunities for Stage 4.
14. Recommend Child Cases only where materially distinct.
15. Recommend next Discovery Wave where relevant.

## Stage Checklist

- [ ] Start/completion and boundary understood.
- [ ] End-to-end process and material subprocesses mapped.
- [ ] Dependencies understood.
- [ ] Relevant process variants recorded.
- [ ] At least one representative recent case reviewed.
- [ ] Actual user work, tools, handoffs, waiting and rework examined.
- [ ] Human judgement/methodology understood.
- [ ] Controls and escalation boundaries understood.
- [ ] Important exceptions/failures recorded.
- [ ] Authoritative data/evidence sources identified.
- [ ] Data quality/traceability/access/restrictions considered.
- [ ] Pain points linked to evidence.
- [ ] Root causes sufficiently understood.
- [ ] Baseline/scale captured where useful.
- [ ] Existing tools/PoCs mapped.
- [ ] Improvement opportunities identified without fixing technology too early.
- [ ] Reuse/common-vs-variant potential assessed.
- [ ] Process Owner validates current state.
- [ ] Enough evidence exists for option design.

## Evidence Register

| Evidence ID | Source | Evidence | Supports | Process Step | Owner/Date |
|---|---|---|---|---|---|

## Gate 3 — Is the Process Sufficiently Understood to Act?

Per opportunity:
- Proceed to Stage 4
- Continue Targeted Discovery
- Merge with Existing Initiative
- Remain within Parent Case
- Create Child FDE Case
- Defer
- Stop

Leadership retains authority to prioritise later waves.

## Generated Artefact — FDE Discovery Pack

1. Discovery Scope
2. Current-State Process
3. Ownership & Handoffs
4. Controls & Judgement
5. Systems, Data & Evidence
6. Baseline
7. Pain Points & Root Causes
8. Existing Initiatives
9. Improvement Opportunities
10. Common-vs-Variant Assessment
11. Recommended Child Cases
12. FDE Recommendation
13. Next-Wave Recommendation

> **Stage 3 principle: Discover the process before designing the solution.**

---

# Stage 4 — Options, Delivery Route & Target Solution

## Purpose / Key Question

> **What is the simplest appropriate intervention that can achieve the confirmed outcome while preserving required controls, ownership and supportability?**

Stage 4 is the first deliberate solution-design stage and should align closely with the current MRO Tech & Tooling workstream.

## Main Participants

- FDE Lead
- Process Owner
- Methodology Owner
- Tech & Tooling / Engineer
- Architecture / Platform / Data SMEs where relevant
- potential Delivery Owner
- Operations/Support where material

## Structured Data / Cards

### Card 4A — Intervention & Route Assessment

Consider proportionately:
- Process Change
- Guidance / Template
- Existing Capability
- Copilot / Controlled Prompt
- Workflow Automation
- Analytical Tool / Service
- Copilot Agent
- Copilot Front End + Controlled MRO Backend
- Cortex + MRO Agent Harness
- Combined / Custom Solution

### Options Assessment

| Option | How It Works | Outcome Coverage | Control Fit | Data/Integration | Reuse | Delivery Effort | Running Effort | Evidence Gap | Recommendation |
|---|---|---|---|---|---|---|---|---|---|

### Card 4B — Ownership & Operating Model

Separate:
- business outcome;
- process;
- methodology;
- AI/model governance if applicable;
- data;
- product/service;
- code/configuration;
- platform;
- support;
- change authority;
- benefits.

### Card 4C — Target Solution & Experiment Readiness

Capture:
- opportunity addressed;
- target users/outcome;
- selected route;
- solution summary;
- scope/out-of-scope;
- capabilities;
- process changes;
- human judgement/approval;
- controls;
- systems/data/integrations;
- reusable components;
- dependencies;
- initial requirements;
- acceptance criteria;
- evidence gaps;
- PoC required?;
- vertical slice required?;
- what Stage 5 must prove.

## Delivery Route Principle

> **Process Change → Guidance/Template → Existing Capability → Copilot/Prompt → Workflow Automation → Analytical Tool/Service → Copilot Agent → Controlled MRO Backend / Cortex + Harness → Custom Application**

Additional complexity must be justified by requirements that simpler options cannot meet.

## Main Activities

1. Restate Stage 3 problem/outcome/constraints.
2. Consider process simplification first.
3. Check existing/reusable capabilities.
4. Generate proportionate options.
5. Compare outcome, controls, integration, ownership, effort, support and reuse.
6. Determine whether needs are user-led, deterministic, analytical or agentic.
7. Select preferred route.
8. Define target solution at enough detail to test.
9. Define acceptance criteria.
10. Convert uncertainty into explicit Stage 5 questions.
11. Confirm engineering/delivery capacity before implying commitment.

## Stage Checklist

- [ ] Intervention addresses evidenced opportunity.
- [ ] Process change considered before technology.
- [ ] Existing capabilities assessed.
- [ ] Lower-complexity options considered.
- [ ] Agentic architecture justified only where required.
- [ ] Build-vs-reuse considered.
- [ ] Common MRO capability potential considered.
- [ ] Controls/human judgement preserved.
- [ ] Data/access/integration appear feasible enough to test.
- [ ] Ownership credible.
- [ ] Support implications considered.
- [ ] Scope/out-of-scope clear.
- [ ] Initial requirements sufficient.
- [ ] Acceptance criteria defined before testing.
- [ ] Evidence gaps explicit.
- [ ] PoC/vertical slice need determined.
- [ ] No production commitment implied prematurely.

## Gate 4 — Is There an Agreed Intervention Worth Proving?

- Proceed to PoC
- Proceed to Vertical Slice
- PoC then Vertical Slice
- Direct Low-Risk Delivery
- Adopt Existing Capability
- Process/Guidance Change
- Obtain Additional Evidence
- Return to Stage 3
- Defer
- Stop

Gate 4 approves **what should be proved next**, not production deployment.

## Generated Artefact — Options & Route Decision Record

Includes:
- Opportunity
- Desired Outcome
- Recommended Intervention
- Delivery Route
- Alternatives
- Rationale
- Key Evidence
- Controls/Human Judgement
- Reuse
- Target Solution
- Dependencies
- Ownership
- Evidence Gaps
- Acceptance Criteria
- PoC / Vertical Slice requirement
- What Stage 5 must prove
- Process Owner / Delivery Owner conditions
- Decision / Date

> **Stage 4 principle: Choose the simplest intervention that can achieve the evidenced outcome; reuse before build; introduce agentic complexity only when justified.**

---

# Stage 5 — Experiment, PoC & Vertical Slice

## Purpose / Key Question

> **Does the proposed solution work well enough to justify production-readiness assessment, and have the material Stage 4 uncertainties been tested?**

PoC and Vertical Slice are **experiment types**, not mandatory sequential steps for every case.

This stage standardises and strengthens PoC/testing activities already performed by MRO Tech & Tooling.

## Experiment Types

| Type | Use When | Main Question |
|---|---|---|
| Capability PoC | Core capability uncertain | Can the core capability work? |
| Vertical Slice | Workflow/integration/control uncertain | Can one realistic end-to-end path work? |
| User Trial | User/process fit uncertain | Can users successfully use it? |
| PoC + Vertical Slice | Both capability and workflow uncertain | Can it work, and can it work in the process? |
| Light Validation | Simple/proven change | Does it behave as expected before delivery? |

## Structured Data / Cards

### Card 5A — Experiment Charter

Capture:
- Stage 4 evidence gap;
- hypothesis;
- riskiest assumptions;
- experiment type;
- baseline;
- representative cases;
- success measures;
- minimum thresholds;
- controls/human gates;
- authorised data/environment;
- configuration/version;
- outputs/evidence;
- limitations/out-of-scope;
- owners/reviewers;
- target completion/decision point.

### Card 5B — Test Cases & Evidence

| Test Case | Scenario/Input | Expected | Success Criterion | Actual | Evidence | Human Correction | Failure/Issue | Result |
|---|---|---|---|---|---|---|---|---|

### Card 5C — Vertical Slice Definition

Only where required:
- user/role;
- trigger;
- input;
- access;
- evidence/data;
- workflow;
- capability;
- integrations;
- human decision;
- controls;
- trace;
- output;
- failure/fallback;
- excluded scope.

### Card 5D — Experiment Action / Issue Log

Use only for experiment-critical actions. Do not recreate Jira.

### Card 5E — Results, Limitations & Recommendation

Capture:
- question answered?;
- hypothesis supported?;
- baseline comparison;
- criteria met?;
- capability result;
- vertical-slice result;
- user feedback;
- failures;
- human intervention;
- control issues;
- limitations;
- untested assumptions;
- production-readiness gaps;
- recommendation.

## Main Activities

1. Start from “What Stage 5 must prove”.
2. Identify riskiest material assumptions.
3. Select minimum experiment type.
4. Define success before testing.
5. Confirm representative cases/data/environment.
6. Build/configure only what is needed.
7. Run tests and realistic user tasks.
8. Run narrow end-to-end vertical slice where required.
9. Capture failures and corrections.
10. Compare with baseline/threshold.
11. Record limitations/unproven assumptions.
12. Make evidence-based recommendation.

## Stage Checklist

- [ ] Experiment addresses Stage 4 evidence gap.
- [ ] Specific question/hypothesis defined.
- [ ] Riskiest assumptions identified.
- [ ] Scope bounded.
- [ ] Representative cases available.
- [ ] Data/environment authorised.
- [ ] Baseline defined where useful.
- [ ] Success criteria set before testing.
- [ ] Evaluation method agreed.
- [ ] Configuration/version recorded.
- [ ] Human reviewers named.
- [ ] Relevant controls/HITL represented.
- [ ] No unauthorised production actions.
- [ ] Failures/escalation captured.
- [ ] Results retained.
- [ ] User feedback captured where relevant.
- [ ] Limitations/unproven assumptions recorded.

## Gates

### Gate 5A — Core Capability Viable?
- Proceed
- Proceed with Conditions
- Iterate Bounded Experiment
- Return to Stage 4
- Stop

### Gate 5B — End-to-End Workflow Viable?
Where required:
- Proceed
- Proceed with Conditions
- Iterate
- Return to Stage 4
- Stop

## Generated Artefact — Experiment, PoC & Vertical Slice Results Pack

- experiment question/hypothesis;
- type/scope;
- baseline/success criteria;
- test cases;
- configuration;
- results;
- failures/human corrections;
- user feedback;
- controls/workflow findings;
- limitations;
- untested assumptions;
- production-readiness gaps;
- Gate decision;
- FDE / Process Owner recommendation.

> **Stage 5 principle: Test the riskiest material uncertainty with the smallest credible experiment.**
>
> **PoC proves the capability; Vertical Slice proves the workflow; Stage 7 production testing proves the product.**

---

# Stage 6 — Evaluation, Controls & Production Readiness

## Purpose / Key Question

> **What did Stage 5 actually prove, and can the proposed solution now be safely and appropriately productionised and operated in MRO?**

Stage 6 is the bridge from evidence to production requirements.

## Main Participants

- FDE Lead
- Process Owner
- Methodology Owner
- Engineer/Developer
- Delivery Owner
- Users/SMEs
- Risk/Data/Security/Architecture/AI Governance SMEs where applicable
- independent challenger where proportionate

## Structured Data / Cards

### Card 6A — Results & Acceptance Evaluation

| Criterion | Baseline | Target | Actual | Evidence | Result |
|---|---:|---:|---:|---|---|

Assess only relevant dimensions:
- outcome effectiveness;
- quality;
- control quality;
- user effort;
- correction effort;
- reliability;
- traceability;
- user acceptance;
- operational feasibility.

### Card 6B — Production Readiness & Control Requirements

| Readiness Area | Current Gap | Production Requirement | Owner | Required Before |
|---|---|---|---|---|

Potential areas:
- process controls;
- human approval;
- methodology/version control;
- data/access;
- security;
- traceability;
- logging/audit;
- model/prompt/configuration versioning;
- integrations;
- failure/fallback;
- monitoring;
- resilience;
- support;
- change management;
- training.

### Card 6C — Ownership, Support & Operating Model

Confirm credible ownership of:
- business outcome;
- process;
- methodology;
- product/service;
- data;
- code/configuration;
- platform;
- deployment;
- monitoring/support;
- incident management;
- change approval;
- benefits.

### Card 6D — Gate Decision & Conditions

Capture:
- Stage 5 conclusion;
- business outcome demonstrated?;
- acceptance result;
- value still justified?;
- production scope;
- controls;
- conditions;
- governance;
- independent challenge;
- residual risks;
- owner decisions;
- FDE recommendation;
- final gate decision.

## Main Activities

1. Evaluate Stage 5 against pre-agreed criteria.
2. Include failures/corrections/exceptions.
3. Confirm what is proven/unproven.
4. Reassess expected value.
5. Determine applicable governance proportionately.
6. Convert experiment gaps into production requirements.
7. Confirm controls, HITL, access, logging, monitoring and failure handling.
8. Confirm ownership/support.
9. Identify residual risks/conditions.
10. Obtain independent challenge where proportionate.
11. Decide whether to proceed to production implementation.

## Stage Checklist

- [ ] Stage 5 assessed against agreed criteria.
- [ ] Failures/corrections retained.
- [ ] Limitations/unproven assumptions explicit.
- [ ] Value remains proportionate.
- [ ] Applicable governance identified.
- [ ] Stage 5 gaps converted to production requirements.
- [ ] Human oversight/escalation defined.
- [ ] Data/access/security sufficiently defined.
- [ ] Logging/auditability defined.
- [ ] Monitoring/fallback/recovery defined.
- [ ] Ownership/support credible.
- [ ] Residual risks/conditions recorded.
- [ ] Independent challenge completed where appropriate.
- [ ] Production scope sufficiently clear.

## Gate 6 — Ready for Production Implementation / Controlled Rollout?

- Approve
- Approve with Conditions
- Remediate and Re-review
- Return to Stage 5
- Return to Stage 4
- Return to Stage 3
- Stop / Defer

Gate 6 authorises the **production path**, not BAU acceptance.

## Generated Artefact — Evaluation & Production Readiness Pack

- Experiment summary
- Results against criteria
- Business outcome assessment
- Failures/corrections
- User/SME assessment
- Limitations/unproven assumptions
- Production readiness requirements
- Controls/HITL
- Data/access/security/auditability
- Ownership/support
- residual risks
- independent challenge
- conditions
- Gate 6 decision
- Stage 7 high-level scope

> **Stage 6 principle: Stage 5 tells us what happened; Stage 6 decides what that evidence means and what production must contain.**

---

# Stage 7 — Production Delivery, Testing, Controlled Rollout & Handover

## Purpose / Key Question

> **Can the Stage 6-approved solution be implemented reliably, demonstrated to meet production requirements, released safely and transferred into sustainable BAU ownership?**

This stage most closely resembles the current MRO Tech & Tooling delivery lifecycle. The standard adds traceability and clearer handover; it does not require the workstream to be rebuilt.

## Main Participants

- Delivery Owner
- Technical Lead / Engineers
- Tech & Tooling / FDE
- Process Owner
- Methodology Owner
- users
- Platform/Infrastructure/Operations
- governance SMEs where Stage 6 requires them

## Structured Data / Cards

### Card 7A — Delivery Charter & Production Scope

Capture:
- approved scope/outcome/users;
- Process Owner;
- Benefits Owner;
- Methodology Owner;
- Product/Service Owner;
- Delivery Owner;
- Technical Lead;
- Stage 6 conditions;
- production controls;
- dependencies;
- Jira references;
- testing;
- rollout;
- fallback;
- monitoring;
- support;
- training.

### Card 7B — Production Requirements & Traceability

| Requirement ID | Production Requirement | Source | Jira/Delivery Ref | Test Evidence | Status | Owner |
|---|---|---|---|---|---|---|

Each material Stage 6 requirement should link to implementation and evidence.

### Card 7C — Production Testing & UAT

Test proportionately:
- functional/system;
- integrations;
- data/output;
- E2E/regression;
- Stage 5 vertical-slice journey;
- process variants;
- human gates;
- access/permissions;
- evidence lineage;
- logging;
- exceptions/failure;
- fallback;
- performance/reliability;
- monitoring;
- UAT.

### Card 7D — Controlled Rollout & Release

| Rollout Phase | Users/Scope | Review Point | Measures | Stop/Rollback Conditions | Approval to Expand |
|---|---|---|---|---|---|

Do not mandate arbitrary 10%/50%/100% rollout.

### Card 7E — Operational Handover & BAU Acceptance

Confirm:
- production version;
- release approval;
- UAT;
- methodology/configuration;
- access;
- monitoring;
- incidents;
- support;
- maintenance/change owner;
- fallback;
- limitations;
- training;
- runbook;
- post-release review;
- benefits owner;
- operational handover.

## Definition of Ready

- [ ] Scope/outcome clear.
- [ ] Stage 6 conditions understood.
- [ ] Acceptance criteria testable.
- [ ] Data/access/infrastructure ready or planned.
- [ ] Architecture/delivery route agreed.
- [ ] Dependencies understood.
- [ ] Controls/HITL specified.
- [ ] Ownership clear.
- [ ] Delivery Owner accepts capacity.

## Main Activities

1. Translate Stage 6 scope/conditions into delivery work.
2. Use Jira for engineering detail.
3. Implement production-grade controls/integrations/access/logging/monitoring.
4. Maintain requirement traceability.
5. Perform functional/system tests.
6. Re-run key vertical-slice journey as production regression.
7. Test exceptions/failures/access/human gates/fallback.
8. Conduct UAT.
9. Prepare communications/training.
10. Controlled rollout where proportionate.
11. Monitor and apply stop/rollback conditions.
12. Complete operational handover.
13. Obtain BAU acceptance.

## Definition of Done

### Delivery
- [ ] Approved functionality delivered.
- [ ] Stage 6 requirements implemented.
- [ ] Integrations complete.
- [ ] Critical dependencies resolved.

### Testing
- [ ] Acceptance criteria satisfied.
- [ ] Controls operate as designed.
- [ ] E2E/regression complete where relevant.
- [ ] UAT accepted.
- [ ] Material failures/exceptions tested.

### Release
- [ ] Release approval recorded.
- [ ] Monitoring/support active.
- [ ] Fallback/rollback available where required.
- [ ] Guidance/training available.
- [ ] Known limitations communicated.

### Ownership / BAU
- [ ] Process Owner accepts implementation.
- [ ] Methodology Owner accepts relevant configuration.
- [ ] Product/service ownership confirmed.
- [ ] Operational ownership transferred.
- [ ] Change authority understood.
- [ ] No critical dependency remains on a temporary/PoC-only contributor or environment.

### Stage 8 Readiness
- [ ] Benefits Owner confirmed.
- [ ] Original baseline retained.
- [ ] Post-release measures defined.
- [ ] Benefits review point agreed.

## Gate 7 — Accepted into BAU?

- Accept into BAU
- Accept with Monitored Conditions
- Continue Limited Rollout
- Remediate Before Expansion
- Roll Back / Withdraw
- Return to Stage 6
- Return to Stage 5 if a fundamental assumption fails

## Generated Artefact — Release, Rollout & Handover Pack

1. Approved Scope
2. Delivered Solution
3. Production Requirement Traceability
4. Functional/System Testing
5. E2E/Regression
6. UAT
7. Controls/Access/Evidence
8. Production Version/Configuration
9. Rollout Results
10. Known Limitations
11. Monitoring/Support/Incident Model
12. Rollback/Fallback
13. Training/Guidance
14. Operational Ownership
15. BAU Acceptance
16. Stage 8 Measurement Plan

## Jira vs FDE Workbench

**Jira owns:**
- Epics;
- Stories;
- Sprints;
- engineering tasks;
- bugs;
- assignments;
- detailed milestones.

**FDE Workbench owns:**
- approved scope;
- Stage 6 requirements/conditions;
- evidence traceability;
- high-level delivery status;
- test/UAT evidence;
- release decision;
- rollout evidence;
- ownership;
- BAU acceptance;
- original problem/outcome linkage.

> **Stage 7 principle: Productionise the proven solution, not the PoC. Test the production product, then transfer sustainable ownership into BAU.**

---

# Stage 8 — Adoption, Benefits, Learning & Reuse

## Purpose / Key Question

> **Is the released change being used as intended, has it delivered the original process outcome, what has MRO learned, and what should now be continued, improved, reused, scaled or retired?**

## Main Participants

- Process Owner
- BAU Product/Service Owner
- FDE / Tech & Tooling
- representative users
- Support/Operations
- Methodology Owner
- Leadership/SLT for material scaling/next-wave decisions

## Structured Data / Cards

### Card 8A — Adoption & Operational Health

Capture:
- target vs actual users;
- expected vs actual usage;
- workarounds;
- effort moved/reduced;
- correction/review burden;
- support issues;
- incidents;
- monitoring;
- methodology/process changes;
- training need;
- ongoing operating burden.

### Card 8B — Benefits & Outcome Review

| Measure | Original Baseline | Target/Direction | Current Result | Evidence | Assessment |
|---|---:|---:|---:|---|---|

Possible measures:
- adoption;
- completion time;
- active user effort;
- waiting/handoffs;
- rework;
- quality/error;
- correction effort;
- control effectiveness;
- satisfaction;
- support effort/cost;
- incidents/exceptions.

Benefit classification:
- Benefits Realised
- Benefits Partially Realised
- Too Early to Assess
- Benefits Not Demonstrated
- Negative / Unintended Outcome

### Card 8C — Reuse & Scaling Assessment

Classification:
- Case-specific
- Candidate for Reuse
- Reusable Pattern
- Reusable Component
- Shared MRO Service

A reusable asset should have:
- owner;
- supported use cases;
- limitations;
- maturity;
- repository/location;
- documentation;
- test evidence;
- dependencies;
- change/version process.

### Card 8D — Lessons, Residual Issues & Next Opportunities

Capture:
- process learning;
- user behaviour;
- technology learning;
- methodology/control learning;
- data/evidence learning;
- operating-model learning;
- residual pain points;
- new opportunities;
- relevance to future waves.

### Card 8E — Closure Decision

Capture:
- outcome achieved?;
- benefits classification;
- benefits accepted by;
- Process Owner / BAU owner;
- Continue / Improve / Scale / Reuse / Retire;
- remaining actions;
- residual risks;
- reusable assets;
- follow-on cases/backlog;
- next-wave implication;
- next BAU review date;
- FDE case status.

## Main Activities

1. Allow enough real use.
2. Measure adoption and actual usage behaviour.
3. Review operational health/support/incidents.
4. Compare actual outcome with original baseline/target.
5. Assess net effort, including corrections/support/displaced work.
6. Reassess quality/control outcomes.
7. Capture Process Owner/user assessment.
8. Identify residual issues.
9. Assess case-specific vs reusable assets.
10. Assign ownership for reusable assets.
11. Feed learning into later FDE waves.
12. Decide continue/improve/scale/reuse/retire.
13. Formally close or continue benefits monitoring.

## Review Timing

Use proportionality.

Possible default:
- **Early Operational Review** — several weeks after rollout.
- **Benefits Review** — around 2–3 months after meaningful adoption, or after enough representative cases have occurred.

For low-volume processes, use evidence volume rather than a fixed calendar date.

## Stage Checklist

### Adoption / Operations
- [ ] Adoption measured.
- [ ] Usage behaviour reviewed.
- [ ] Workarounds/displaced effort considered.
- [ ] Support burden/incidents understood.
- [ ] Human correction/review effort assessed.

### Benefits
- [ ] Results compared with original baseline where meaningful.
- [ ] Original desired outcome revisited.
- [ ] Quality/control reassessed.
- [ ] Benefit not inferred merely from deployment.
- [ ] Process Owner accepts benefit conclusion.

### Reuse / Learning
- [ ] Reusable elements assessed.
- [ ] Candidate reusable assets documented.
- [ ] Reusable assets have owners or remain only candidates.
- [ ] Documentation/testing needs identified.
- [ ] Related cases/waves linked.
- [ ] Future-wave learning captured.

### Closure
- [ ] Residual issues recorded.
- [ ] Outstanding improvements routed.
- [ ] Continue/Improve/Scale/Reuse/Retire decision recorded.
- [ ] BAU ownership remains clear.
- [ ] Next review identified where needed.
- [ ] FDE closure status recorded.

## Gate 8 — What Should Happen Next?

- Close — Benefits Realised
- Close — Partial Benefits Accepted
- Continue Benefits Monitoring
- Improve through BAU Backlog
- Return to FDE Stage 4/5
- Scale
- Reuse
- Start / Inform Next Discovery Wave
- Retire

Material scaling and future-wave decisions should return to Leadership/Steering where appropriate.

## Generated Artefact — Benefits, Learning & Reuse Review

1. Original Problem & Outcome
2. Delivered Change
3. Adoption & Operational Health
4. Baseline vs Actual Benefits
5. Quality / Controls / Human Review
6. Support / Incidents / Operating Burden
7. User & Process Owner Assessment
8. Residual Issues
9. Reusable Assets / Patterns
10. Lessons Learned
11. Implications for Other Cases / Waves
12. Follow-on Actions
13. Gate 8 Decision
14. Closure / BAU Ownership

> **Stage 8 principle: Deployment is not a benefit. Measure real use, real outcome, net effort and reusable learning.**

---

# 7. Existing MRO Tech & Tooling Work — Transition Guidance

The eight-stage model should **not require current initiatives to restart**.

For every existing initiative, perform a lightweight **FDE Alignment Check**:

| Question | Alignment |
|---|---|
| What process problem does the initiative solve? | Stage 1 |
| Who is the Process Owner? | Stage 2 |
| What expected outcome has been agreed? | Stage 2 |
| What Discovery evidence already exists? | Stage 3 |
| Which opportunity/solution route was selected? | Stage 4 |
| What PoC / vertical-slice evidence already exists? | Stage 5 |
| What readiness/control work already exists? | Stage 6 |
| What delivery/testing/rollout evidence already exists? | Stage 7 |
| What adoption/benefits evidence exists? | Stage 8 |
| Does it still align with current Leadership priority? | Portfolio check |

Rules:

1. **Do not rerun completed research.**
2. **Do not repeat PoCs simply to fit the new lifecycle.**
3. **Reuse valid testing and delivery evidence.**
4. **Fill only material gaps.**
5. **Map each initiative to the stage it is genuinely in.**
6. **If problem/outcome/owner is unclear, backfill those fields lightly rather than restarting the project.**

This means the existing MRO Tech & Tooling workstream remains recognisable. Stages 4–8 mainly add a more consistent structure, evidence trail, gating model, production traceability and benefits loop.

---

# 8. Proportionate Use of the FDE Toolkit

| Route | Expected Use |
|---|---|
| **Light** | Candidate/priority record; only relevant Discovery/Route fields; simple testing/acceptance; short handover and benefits conclusion |
| **Standard** | Relevant Cards across all stages; structured Discovery; options; bounded experiment; evaluation; delivery evidence; benefits review |
| **Enhanced** | Full evidence trail; architecture/data/control assessment; methodology/version controls; independent challenge; vertical slice; detailed testing; controlled rollout; richer monitoring |

> **Light / Standard / Enhanced determines depth, not whether the eight-stage logic exists.**

Even a Light case should still answer:

> **Problem → Priority → Understand → Choose → Prove → Assess → Deliver → Measure**

---

# 9. Recommended Workbench Information Structure

```text
MRO FDE Portfolio
│
├── Candidate Backlog
│
├── Leadership Priorities
│   └── Process Families / Discovery Waves
│
├── Active FDE Cases
│   └── FDE-XXX
│       ├── Case Record
│       ├── Cards / Structured Data
│       ├── Evidence Register
│       ├── Decision / Gate History
│       ├── Generated Artefacts
│       ├── Jira / Delivery Links
│       └── Benefits / Closure
│
├── Reusable Patterns & Capabilities
│
└── Closed Cases
```

Confluence can support the interim documentation model, but the longer-term FDE Workbench should become the structured system of record.

---

# 10. Recommended Lifecycle Statuses

```text
Candidate
→ Prioritised
→ Discovery
→ Route Assessment
→ Experiment
→ Evaluation
→ Delivery
→ Controlled Rollout
→ Benefits Review
→ Closed
```

Jira should be linked once detailed delivery work is justified; a Jira Epic is not required for every Stage 1 candidate.

---

# 11. End-to-End Operating Principles

1. **Problem before technology.**
2. **Leadership prioritises outcomes; FDE discovers detailed opportunities.**
3. **FDE leads process decomposition; Process Owners validate business reality.**
4. **Do not assume all teams share the same process.**
5. **Use rolling Discovery Waves rather than researching every team before delivering anything.**
6. **Create Child Cases only where lifecycle/ownership/outcome is materially distinct.**
7. **Reuse before build.**
8. **Choose the lowest-complexity solution that meets the need.**
9. **Agentic complexity must be justified by agentic requirements.**
10. **Every material uncertainty should become an explicit experiment question.**
11. **PoC proves capability; Vertical Slice proves workflow; production testing proves the product.**
12. **Failures are evidence.**
13. **Governance should be proportionate to actual risk and complexity.**
14. **Stage Gates are decisions, not checklist-completion exercises.**
15. **Jira remains the detailed delivery-management tool.**
16. **Existing MRO Tech & Tooling work should be mapped and reused, not restarted.**
17. **Deployment is not a benefit.**
18. **Benefits and reusable learning should feed future Discovery Waves.**
19. **FDE should not become permanent BAU support.**
20. **The process should be structured enough to be evidence-led, but light enough to remain useful.**

---

# 12. One-Line Definition

> **The MRO FDE process is a rolling, evidence-led operating model that turns Leadership-prioritised process outcomes into understood problems, proportionate solutions, tested improvements, controlled delivery and measurable benefits — while progressively building reusable MRO capabilities.**
