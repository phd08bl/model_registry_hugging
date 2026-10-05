Below is the updated **MRO FDE 8-Stage Operating Process**. I would treat this as the target standard for the FDE Workbench.

The core pattern remains:

> **Structured Data / Cards → Activities → Checklist → Evidence → Decision / Gate → Generated Artefact**

But I would add three important concepts around it:

> **Portfolio Priority → Discovery Waves → Child FDE Cases**

This avoids forcing SLT to prioritise dozens of detailed use cases before discovery, while also avoiding one enormous “Improve Independent Validation Efficiency” programme that never becomes actionable.

---

# MRO FDE Operating Model

The hierarchy should be:

```text
Leadership Priority / Process Family
        │
        │  e.g. Improve Independent Validation Efficiency
        │
        ├── Initial Discovery Wave
        │       AI Validation
        │
        ├── Future Discovery Wave
        │       Pricing Model Validation
        │
        └── Future Discovery Wave
                Economic Model Validation

Within each Discovery Wave
        │
        ↓
End-to-End Process
        ↓
Sub-processes
        ↓
Pain Points
        ↓
Evidence
        ↓
Improvement Opportunities
        ↓
Selected Child FDE Cases
        ↓
Stage 4–8 delivery lifecycle
```

The key distinction is:

**SLT prioritises outcomes and waves. FDE discovers the detailed opportunities.**

---

# The Eight-Stage MRO FDE Process

| Stage | Purpose / Key Question | Structured Data / Cards | Main Activities | Stage Checklist | Evidence | Decision / Gate | Generated Artefact | Main Participants |
|---|---|---|---|---|---|---|---|---|
| **1. Problem / Opportunity Intake** | **Is there a meaningful MRO process problem or improvement outcome worth considering?** | **Problem Card:** broad problem/outcome; process family; affected teams/users; why it matters; why now; problem raiser; likely Process Owner; known existing initiatives | Capture request; separate problem from proposed technology; identify process family; check obvious duplication; identify likely Process Owner; determine whether request is a narrow issue or broad process improvement theme | Problem understandable; process family identified; likely owner identified; affected users broadly known; within MRO scope; no obvious duplicate | Request/email/chat; audit finding; example case; existing backlog item; leadership request; operational issue | **Gate 1 — Worth assessing?** Proceed / Merge / Clarify / Stop | **Problem Brief** | Problem Raiser; FDE/Tech & Tooling; likely Process Owner |
| **2. Priority, Ownership & Discovery Scope** | **Does MRO want to prioritise this outcome, who owns it, and where should FDE start?** | **Priority & Ownership Card:** Process Owner; Leadership Sponsor; overall expected outcome; strategic priority; Process Family; Process Variants/teams; **Initial Discovery Wave**; future candidate waves; FDE Owner | Process Owner validates broad problem; define desired outcome; perform lightweight cross-wave scan if process spans multiple teams; identify likely process variants; SLT selects priority and first discovery wave; assign FDE | Process Owner confirmed; overall outcome agreed; SLT priority confirmed; initial discovery wave selected; scope boundary sufficiently clear; FDE assigned | Process Owner confirmation; SLT/steering decision; lightweight cross-wave information; existing strategy/priorities | **Gate 2 — Approved for detailed FDE Discovery?** Approve Wave 1 / Hold / Redirect / Stop | **Priority & Discovery Scope Decision** | Process Owner; SLT/Leadership; Tech & Tooling Lead; FDE Lead |
| **3. FDE Discovery & Process Decomposition** | **How does this process variant actually work, where are the material problems, and which opportunities should be taken forward?** | **Process Card; Process Decomposition Card; Pain Point Cards; Evidence Register; Improvement Opportunity Cards; Common-vs-Variant Assessment; Baseline; Constraints; Existing Initiatives** | Map end-to-end process; decompose into meaningful sub-processes; interview real users; review recent cases; identify systems/data/controls; identify pain points and root causes; establish baseline where useful; identify improvement opportunities; distinguish common vs team-specific capabilities; identify existing tools; recommend child cases; recommend next discovery wave | Current process sufficiently understood; subprocesses sufficiently decomposed; users consulted; material pain points evidenced; root causes understood; baseline captured where useful; constraints identified; existing initiatives mapped; opportunities identified; common/reusable patterns considered; Process Owner validates findings | Interviews; process documentation; actual cases; screenshots; process metrics; time/volume data; controls; existing PoCs/tools; user feedback | **Gate 3 — Do we understand the problem well enough to act?** Proceed / More discovery / Re-scope / Stop. Also decide which opportunities become **Child FDE Cases** | **FDE Discovery Pack + Process/Opportunity Map** | FDE leads; Process Owner validates; users/SMEs provide evidence; Tech/Data SMEs support |
| **4. Options, Delivery Route & Target Solution** | **What is the simplest appropriate solution for the selected opportunity?** | **Option Cards; Delivery Route Card; Target Solution Card; Initial Requirements; Acceptance Criteria; Dependency Card** | Generate realistic options; consider process change/no-tech option; compare prompt/Copilot/workflow/agent/custom build/existing platform; determine Copilot vs Cortex + Harness where relevant; assess feasibility, risk, reuse and support; agree scope/out-of-scope; define success criteria | Multiple reasonable options considered; simplest viable option assessed; build-vs-reuse considered; common MRO capabilities considered; architecture route justified; dependencies identified; target solution agreed; acceptance criteria defined | Discovery evidence; platform capability information; technical feasibility analysis; architecture advice; reusable component catalogue; option assessment | **Gate 4 — Is there an agreed solution worth proving?** PoC / Vertical Slice / Direct Delivery / Rework / Stop | **Options & Solution Recommendation** | FDE; Process Owner; Tech & Tooling; Engineer; Architecture/Platform SMEs as needed |
| **5. Experiment, PoC & Vertical Slice** | **Does the core capability work, and where necessary does one realistic end-to-end workflow work?** | **Experiment Card; Hypothesis; Baseline; Metrics; PoC Configuration; Vertical Slice Card; Test Cases; Results; Limitations; User Feedback** | Define hypotheses and success thresholds before testing; build minimum PoC; test core capability; assess against baseline; if appropriate build vertical slice covering one real user journey; test integrations, controls, HITL, evidence/logging; capture failures and limitations | Hypothesis defined; success criteria defined before test; representative cases used; results retained; baseline comparison performed where relevant; PoC conclusion clear; vertical slice completed where required; user feedback captured; material limitations understood | Test outputs; evaluation results; logs; example inputs/outputs; screenshots/demo; user feedback; failure cases; vertical-slice traces | **Gate 5A — Core capability viable?** Proceed / Iterate / Stop. **Gate 5B — End-to-end slice viable?** Proceed / Conditions / Return to Stage 4 / Stop | **PoC & Vertical Slice Results** | FDE; Engineer/Developer; representative users; Process Owner; evaluation SMEs |
| **6. Evaluation, Controls & Production Readiness** | **Can this proven solution be safely and appropriately productionised and operated in MRO?** | **Evaluation Card; Risk/Control Profile; Production Readiness Requirements; Human Oversight; Data/Access Profile; Operational Support Model; Residual Risk; Approval Record** | Determine applicable governance; classify solution; convert PoC/vertical-slice gaps into production requirements; assess AI/model/data/security/operational risks as applicable; confirm access and human oversight; establish logging/monitoring/support; remediate gaps; obtain approvals | Relevant risks assessed; applicable controls defined; PoC gaps addressed in production requirements; access/data requirements addressed; human oversight adequate; auditability/logging defined; support/monitoring model defined; required approvals identified/obtained | PoC/vertical slice evidence; architecture review; security/data assessments; AI/model-risk evidence; control testing; approval records | **Gate 6 — Ready for production implementation / controlled rollout?** Approve / Approve with conditions / Remediate / Not approve | **Evaluation & Production Readiness Pack** | Process Owner; FDE; Tech & Tooling; Delivery Owner; relevant Risk/Security/Data/Architecture SMEs |
| **7. Production Delivery, Testing, Rollout & Handover** | **Can the solution be implemented reliably, accepted by users and transferred into BAU?** | **Delivery & Handover Card; Jira/Epic links; Release Scope; Production Requirements; UAT; Support Owner; Maintenance Owner; Monitoring; Training; Rollback/Fallback** | Productionise proven solution; use Jira for detailed build/sprints; complete integrations; perform functional/system testing; repeat vertical-slice journey as end-to-end regression; perform UAT; prepare communications/training; deploy; establish monitoring/support; hand over | Production build complete; production requirements satisfied; functional testing complete; end-to-end regression passed; UAT passed; documentation available; users prepared; support and maintenance owners confirmed; monitoring/fallback ready; Process Owner accepts handover | Jira/release evidence; system test results; regression tests; UAT evidence; release record; operational documentation; training/comms; monitoring configuration | **Gate 7 — Accepted into BAU?** Accept / Limited Rollout / Remediate / Roll Back | **Release & Handover Pack** | Delivery Owner; Engineers; Tech & Tooling; Process Owner; users; Platform/Operations teams |
| **8. Adoption, Benefits, Learning & Reuse** | **Did the change improve the process, what did MRO learn, and what should be reused or scaled?** | **Benefits Card; Adoption Card; Reuse Card; Lessons Learned; Reusable Asset Record; Residual Issues; Next Improvement Opportunity** | Measure adoption; compare actual outcome against baseline/target; obtain user feedback; assess residual pain points; identify reusable prompts/services/components/agent skills/control patterns; decide whether to improve, scale, reuse or retire; feed lessons into later waves | Adoption reviewed; outcome measured where practical; baseline vs actual compared; user feedback captured; residual issues understood; reusable assets assessed; lessons captured; BAU ownership confirmed | Usage data; before/after metrics; user feedback; incidents/support data; Process Owner assessment; reusable artefacts | **Gate 8 — Final outcome?** Benefits realised / Partial benefits / Improve / Scale / Reuse / Retire | **Benefits, Learning & Reuse Review** | Process Owner; FDE/Tech & Tooling; users; Leadership for material initiatives |

---

# Stage 1–3 need to support broad process priorities

The major design change is that Stage 1 should **not require the Process Owner to present a neatly decomposed problem**.

For example, this is completely valid:

> **Improve Independent Validation Efficiency**

At Stage 1 this can remain a broad improvement outcome.

Stage 2 might identify:

```text
Process Family
Independent Validation

Variants
AI Validation
Pricing Model Validation
Economic Model Validation
Other validation teams
```

A lightweight scan may establish:

```text
AI Validation      — high apparent opportunity / ready for discovery
Pricing Validation — high potential / medium readiness
Economic Validation — potential opportunity / less understood
```

SLT can then decide:

> **Overall Priority: Improve Independent Validation Efficiency**  
> **Wave 1: AI Validation**

The detailed decomposition happens during **Stage 3**, not before.

---

# Stage 3 should explicitly include Process Decomposition

This deserves to become a standard FDE activity rather than something done informally.

The **Process Decomposition Card** could contain:

| Field | Example |
|---|---|
| Process Family | Independent Validation |
| Process Variant | AI Independent Validation |
| Process Boundary | Validation initiation → final approval |
| Process Owner | AI IV Lead |
| Major Sub-processes | Planning, evidence collection, document review, code review, testing, challenge, reporting, approval |
| Users / Roles | Validator, reviewer, approver |
| Systems | Relevant MRO systems/tools |
| Inputs | Model artefacts, documentation, data, code |
| Outputs | Validation evidence/report/findings |
| Major Pain Points | Linked Pain Point Cards |
| Existing Tools | Linked existing initiatives |
| Improvement Opportunities | Linked Opportunity Cards |
| Common Capability? | Yes / Partially / No |
| Candidate Child Case? | Yes / No |

This creates the bridge between a **Leadership-level priority** and something Tech & Tooling can actually deliver.

---

# When should an Improvement Opportunity become a Child FDE Case?

Do **not** create a child case for every pain point.

Create a separate Child FDE Case only when at least one of these materially differs:

| Split criterion | Example |
|---|---|
| **Distinct outcome** | Code review efficiency vs report drafting efficiency |
| **Distinct accountable owner** | Validation process owner vs central evidence platform owner |
| **Distinct solution path** | Copilot prompt vs reusable Python service |
| **Distinct experiment** | Separate hypothesis/test design required |
| **Distinct delivery lifecycle** | One can deliver in weeks; another requires platform integration |
| **Materially different risk/control profile** | Simple summarisation vs autonomous agent accessing MRO systems |

Otherwise keep related opportunities inside one case.

That prevents case proliferation.

---

# Rolling-Wave Discovery

The portfolio should **not** operate as:

```text
AI Discovery
↓
Pricing Discovery
↓
Economic Discovery
↓
Only then start building
```

Instead:

```text
SLT Priority
Improve Independent Validation Efficiency
          ↓
Light Cross-Wave Scan
          ↓
Select Wave 1 — AI Validation
          ↓
Detailed Discovery
          ↓
Opportunities / Child Cases
          ↓
Stage 4 → Stage 5 → Stage 6 → Stage 7
                   │
                   │ meanwhile
                   ↓
          Wave 2 Discovery
```

This means Wave 1 can start delivering value while later waves continue discovery.

Wave 1 evidence also improves Wave 2 discovery.

---

# Common vs Variant capability should become a standard FDE question

This is especially important in MRO.

During every discovery FDE should ask:

> **Is this problem/process genuinely specific to this team, or is there a wider MRO pattern?**

For example:

| Capability | AI Validation | Pricing Validation | Likely Pattern |
|---|---|---|---|
| Evidence retrieval | Required | Required | **Common MRO capability** |
| Document review | Required | Required | Common framework + domain rules |
| Code review | Required | Required | Shared service + specialised rules |
| Quantitative testing | AI-specific methods | Pricing-specific methods | Shared framework, specialised tools |
| AI evaluation | Required | Not generally required | AI-specific |
| Report drafting | Required | Required | **Common MRO capability** |

This is how FDE should progressively create reusable MRO capabilities rather than many disconnected tools.

---

# Stage 4 should explicitly decide the technology route

Another improvement I would standardise is the **Delivery Route Card**.

The decision should move from lowest to highest complexity:

```text
Process change
      ↓
Template / Standard
      ↓
Copilot Prompt / Chat
      ↓
Workflow Automation
      ↓
Copilot Agent
      ↓
Copilot + MRO Backend Service
      ↓
Cortex + MRO Agent Harness
      ↓
Custom Application / Platform Capability
```

The FDE should not assume that every problem requires an agent.

The Stage 4 decision should explicitly consider:

- user-led vs autonomous workflow;
- state requirements;
- specialist tools;
- integrations;
- evidence/auditability;
- human approval;
- methodology control;
- reusability;
- scale;
- support requirements.

This makes the architecture decision part of the **evidence-based FDE process**.

---

# Stage 5 should explicitly distinguish PoC and Vertical Slice

I would formally standardise:

> **PoC proves the capability.  
> Vertical Slice proves the workflow.  
> Production testing proves the product.**

### PoC

Example question:

> Can an LLM identify relevant code-review issues with acceptable quality?

### Vertical Slice

Example:

```text
Validator
↓
Provides real input
↓
Authentication / permissions
↓
Retrieval / data processing
↓
AI / workflow
↓
Human review
↓
Evidence capture
↓
Output / report
```

The vertical slice should be **narrow but end-to-end**.

It does not need to contain every production feature.

And it should only be mandatory where integration/workflow/control risk justifies it.

---

# Requirements should mature through the lifecycle

I would avoid trying to define all requirements during Stage 3.

A cleaner progression is:

| Stage | Requirement type |
|---|---|
| Stage 3 | **Process requirements** — what must remain true in the business process |
| Stage 4 | **Solution requirements** — what the solution must do |
| Stage 5 | **Acceptance criteria** — what must be demonstrated |
| Stage 6 | **Control / production-readiness requirements** |
| Stage 7 | **Operational requirements** — support, monitoring, resilience, ownership |

For example:

```text
Stage 3:
Validator remains accountable for final judgement.

Stage 4:
Tool must present findings for validator review.

Stage 5:
Validator can accept/reject findings and results are retained.

Stage 6:
All decisions must have user identity, timestamp and version trace.

Stage 7:
Logs retained in approved environment and support process documented.
```

This avoids premature requirements engineering.

---

# Roles should change through the stages

The Workbench should reflect that ownership changes.

| Role | Main responsibility |
|---|---|
| **SLT / Leadership** | Priority, wave sequencing, major investment/scope decisions |
| **Process Owner** | Business problem, outcome, validation of discovery, acceptance, benefits |
| **FDE** | Orchestration, discovery, decomposition, evidence, recommendation, stage progression |
| **Tech & Tooling / Engineer** | Feasibility, solution design, PoC, vertical slice, engineering |
| **Delivery Owner** | Production implementation, testing, rollout, support handover |
| **Risk / Governance SMEs** | Specialist assessments and approvals |
| **Users** | Real process knowledge, testing, feedback and UAT |

One principle should be explicit:

> **The FDE operates the Workbench. The Process Owner should not be turned into the Workbench administrator.**

FDE captures and structures; Process Owners and SMEs validate and decide.

---

# Additional considerations I would add

Beyond the two principles you provided, I would add these to the MRO standard.

| Consideration | Recommended rule |
|---|---|
| **1. Parent vs Child Cases** | Leadership priorities may remain parent cases; only create child cases where outcome/ownership/solution/delivery is materially distinct |
| **2. Rolling waves** | Do not complete all discovery waves before delivery starts |
| **3. Wave sequencing can change** | SLT should be able to change Wave 2/3 based on evidence learned from Wave 1 |
| **4. Common-before-local design** | Before building a team-specific tool, check whether the underlying capability should be reusable across MRO |
| **5. Build-vs-reuse check** | Every Stage 4 assessment should check existing Copilot, MRO tools, platform services and reusable components before new development |
| **6. Risk-proportionate process** | A prompt template should move through stages much faster than a high-autonomy agent |
| **7. Stop is a valid FDE outcome** | Discovery or experiment may conclude that automation is not worthwhile |
| **8. Existing initiatives should not restart** | Map existing work to the current stage and reuse previous research/PoCs/tests/evidence |
| **9. Evidence should support claims** | Evidence should be linked to pain points, requirements, experiment results and decisions rather than stored as unstructured attachments |
| **10. Stage Gate ≠ checklist completion** | Gate asks whether there is enough evidence to make the next decision |
| **11. Jira remains delivery tooling** | Workbench owns problem/evidence/decision/outcome; Jira owns detailed delivery work |
| **12. Benefits should roll up** | Child-case benefits should aggregate back to the parent Leadership Priority |
| **13. Reuse is an explicit outcome** | Every delivered solution should be assessed for reusable services, prompts, agent skills, evaluation methods, connectors and control patterns |
| **14. Portfolio capacity matters** | Do not open many discovery waves if FDE/Tech & Tooling cannot carry the resulting solutions into Stage 4–7 |
| **15. Re-discovery trigger** | Major scope/process/technology changes should allow a case to return to Stage 3/4 rather than forcing linear progression |

---

# The overall MRO FDE flow

Putting everything together:

```text
PROCESS OWNER / LEADERSHIP
identifies broad problem or outcome
        │
        ▼
1. PROBLEM INTAKE
Capture the problem
        │
        ▼
2. PRIORITY & DISCOVERY SCOPE
SLT prioritises outcome
Select Wave 1
        │
        ▼
3. FDE DISCOVERY
Map process variant
Decompose sub-processes
Find evidence
Find pain points
Identify common vs variant capabilities
Identify opportunities
        │
        ├── No worthwhile opportunity → STOP
        │
        ├── Existing solution → REUSE
        │
        └── Distinct opportunity → CHILD FDE CASE
                                    │
                                    ▼
4. OPTIONS & TARGET SOLUTION
Process / Copilot / Workflow / Agent /
Harness / Existing Platform / Custom
        │
        ▼
5. POC + VERTICAL SLICE
Capability works?
Workflow works?
        │
        ▼
6. EVALUATION & PRODUCTION READINESS
Can it be safely productionised?
        │
        ▼
7. PRODUCTION DELIVERY & HANDOVER
Build → Test → Regression → UAT → Rollout
        │
        ▼
8. BENEFITS & REUSE
Did it improve the process?
What should MRO reuse?
        │
        ├── Improve existing solution
        ├── Create reusable capability
        ├── Scale to another team
        └── Feed evidence into NEXT DISCOVERY WAVE
```

This final loop is important:

> **Stage 8 of Wave 1 can directly improve Stage 3 of Wave 2.**

So the MRO FDE process becomes a learning system rather than eight isolated governance stages.

---

## Recommended final definition

I would describe the whole model as:

> **The MRO FDE process is a rolling, evidence-led process that converts Leadership-prioritised process outcomes into actionable improvement opportunities, proves the simplest appropriate solutions, delivers them under proportionate controls, measures their benefits, and progressively builds reusable MRO capabilities.**
>
> **Leadership prioritises outcomes and discovery waves; Process Owners own the business process and outcomes; FDE leads discovery and decomposition; Tech & Tooling proves and delivers solutions; and evidence from each wave informs the next.**

That is now a much stronger model than simply **“8-stage project lifecycle”**. It gives you a clear operating model for **portfolio prioritisation, discovery, delivery and reuse** without making the process unnecessarily heavy.