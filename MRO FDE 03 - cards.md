Yes. These eight cards are a strong practical toolkit for MRO FDE. They provide structured conversations with leadership, process owners, users, SMEs and platform teams, and they distinguish evidence from opinion and assumptions.

However, the original cards are framed around “AI transformation” and “customer projects.” For MRO, they should be reframed as **technology-neutral process discovery cards**. Otherwise, the interviews could lead participants towards AI before the process problem has been understood.

I suggest naming the adapted set:

> **MRO Tech & Tooling FDE Discovery Cards**

# 1. How the cards fit together

| Card | Primary participants | MRO FDE purpose | Main output |
|---|---|---|---|
| 1. Leadership Outcome | Sponsor, leadership, process owner | Confirm why the outcome matters | Priority, outcome and sponsorship |
| 2. Process and Controls | Process owner and SMEs | Understand how success is delivered | Process boundary and control requirements |
| 3. Ownership and Handoffs | Process owner, delivery leads | Identify coordination problems | Roles, hand-offs, waits and escalations |
| 4. User Tasks | Actual users and validators | Observe how work really happens | Tasks, pain points and human judgement |
| 5. Systems, Data and Access | Platform, data, security and SMEs | Assess the digital foundation | Systems, data, permissions and constraints |
| 6. Current-State Consensus | Cross-functional group | Reconcile different accounts | Agreed current-state workflow |
| 7. Intervention and Route | Process owner, FDE and architecture | Compare proportionate responses | Preferred option and delivery route |
| 8. Experiment and Actions | Process owner, FDE and delivery team | Define the next evidence-gathering step | Experiment charter and actions |

The sequence moves from **outcome → process → evidence → options → experiment**. It does not move directly from request to build.

# 2. Common notation for all cards

The original distinction between facts, views, assumptions and unknowns is useful. For MRO, use:

- **E — Evidence:** verified fact supported by data, documentation or observation.
- **V — View:** stakeholder opinion or experience.
- **A — Assumption:** working hypothesis that needs testing.
- **Q — Question:** unknown or unresolved point.

Each entry should also record:

- Source or evidence link.
- Person who provided it.
- Date.
- Whether another role must confirm it.
- Owner of any outstanding question.

This will allow the FDE Workbench to separate evidence from assertions and preserve a controlled discovery record.

# 3. MRO-adapted cards

## Card 1 — Leadership Outcome and Sponsorship

### Replaces

“Why are we undertaking AI transformation now?”

### MRO title

> **What MRO outcome needs to improve, and why now?**

### Participants

- Executive sponsor.
- Relevant leadership member.
- Common MRO process owner or IVT Head.
- FDE lead.

### Suggested duration

10–15 minutes.

### Questions

#### 1. What has triggered this priority?

- Regulatory or audit requirement?
- Control issue?
- Capacity or cycle-time pressure?
- Quality or consistency concern?
- Colleague experience?
- Strategic opportunity?
- Repeated requests from several IVTs?

Ask for a recent example and supporting evidence.

#### 2. If only one outcome could improve, what should it be?

Record:

- The outcome.
- Why it matters.
- Who benefits.
- What observable change is expected.
- What current measure or evidence shows the problem.

#### 3. Where should discovery begin, and what is outside scope?

Record:

- Process or sub-process.
- Teams or IVTs involved.
- Model types initially included.
- Explicit exclusions.
- Activities that should not be changed at this stage.

Do not preselect the technology.

#### 4. Who will sponsor and own the process?

Record:

- Executive sponsor.
- Common process owner.
- IVT/local owners.
- SMEs and users.
- Leadership decisions still required.
- Capacity available for discovery.

### Card summary

- Priority outcome.
- Supporting evidence.
- Non-negotiable requirements.
- Sponsor and process owner.
- Initial scope.
- Matters requiring confirmation.

### Stage gate

The steering forum confirms whether the case should enter FDE discovery.

---

## Card 2 — Process Outcome, Controls and Success

### Replaces

“Business and design card—how is a successful project completed?”

### MRO title

> **How is the process expected to deliver a good and controlled outcome?**

### Participants

- Process owner.
- Methodology/control owner.
- Senior SMEs.
- FDE lead.

### Questions

#### 1. Who uses the process and what must it deliver?

Record:

- Users and downstream stakeholders.
- Required output.
- Required evidence.
- Quality expectations.
- Internal and external obligations.

#### 2. What are the main steps from trigger to completion?

Create a short flow:

> Trigger → inputs → key activities → decisions → approvals → output → record

For each step, identify:

- Responsible role.
- Input and output.
- Decision or confirmation point.
- System or tool used.

#### 3. Which decisions must remain with qualified people?

Record:

- Professional judgements.
- Risk decisions.
- Findings and ratings.
- Approvals.
- Escalations.
- Challenge and override.
- Required separation of duties.

#### 4. Where does the process currently create rework or inconsistency?

Ask for specific examples of:

- Duplicate evidence requests.
- Repeated document preparation.
- Incorrect or incomplete outputs.
- Manual reconciliation.
- Different interpretations.
- Rejected or returned work.

### Card summary

- Process outcome.
- Mandatory deliverables.
- Control and judgement boundaries.
- Acceptance criteria.
- Most valuable areas for investigation.

---

## Card 3 — Ownership, Handoffs and Collaboration

### Replaces

“Project and collaboration card—where does the project get stuck?”

### MRO title

> **Where do ownership, handoffs and dependencies delay or weaken the process?**

### Participants

- Process owner.
- Team leads.
- Project or delivery coordinators.
- SMEs from upstream and downstream teams.

### Questions

#### 1. Who hands what to whom, and how is receipt confirmed?

Record:

- Upstream and downstream roles.
- Artefact or information transferred.
- Communication channel.
- Required acknowledgement.
- System of record.

#### 2. Where is work actively progressing and where is it waiting?

Separate:

- Active work time.
- Waiting time.
- Queue or approval delay.
- Missing evidence delay.
- System access delay.
- Rework.

Use measured data where available; otherwise mark it as an estimate.

#### 3. How are changes communicated and controlled?

Record a recent change:

> Raised → assessed → approved → implemented → communicated → verified

Identify where information was lost or work had to be repeated.

#### 4. When teams disagree, who decides and who closes the matter?

Clarify:

- Decision authority.
- Escalation route.
- Required evidence.
- Notification.
- Closure record.
- Difference between task completion and accepted delivery.

### Card summary

- Principal coordination bottleneck.
- Unclear or overlapping responsibilities.
- Repeated change issue.
- Roles or evidence still missing.

---

## Card 4 — User Task Observation

### Replaces

“Front-line work card—how is AI used in everyday work?”

### MRO title

> **How is the work actually performed, and where is assistance most valuable?**

### Participants

- Validators.
- Analysts.
- Reviewers.
- Operational users.
- FDE lead.

This should be completed separately for materially different roles or IVTs.

### Questions

#### 1. Walk through one recent representative task

Record:

> Input → activity → tool → decision → output → review

Where possible, observe a demonstration rather than relying only on a description.

#### 2. Which step is repetitive, time-consuming or error-prone?

Record:

- Specific activity.
- Frequency.
- Approximate time.
- Common mistakes.
- Rework.
- Impact on quality or cycle time.

Do not force an estimate if the user does not know.

#### 3. What technology is currently used?

Include:

- MARM.
- Jira or Confluence.
- Excel, Python or other analytics.
- Copilot or prompts.
- Local scripts.
- Existing agents.
- Manual workarounds.

Ask:

- What works well?
- What requires manual correction?
- What has been abandoned?
- What should be retained?

#### 4. What must remain under human control?

Record:

- Required professional judgement.
- Review and challenge.
- Approval.
- Interpretation.
- Exception handling.
- Escalation.
- Evidence requirements.

### Card summary

- Most burdensome task.
- Controls that must remain.
- Representative samples available for testing.
- Candidate task for further analysis.

### Important safeguard

This is a process-discovery exercise, not an assessment of individual employee performance.

---

## Card 5 — Systems, Data, Access and Support

### Replaces

“Digital foundation card—what can existing systems, data and permissions support?”

### MRO title

> **What existing technology and information can support the improvement?**

### Participants

- Process SME.
- MARM or relevant platform representative.
- Data owner.
- Security/access representative.
- AI Tech & Tooling.
- Envoy representative where applicable.

### Questions

#### 1. Which existing systems already support the process?

Record:

- System.
- Purpose.
- Owner.
- Current users.
- Strengths.
- Limitations.
- Support arrangement.
- Capabilities that should be reused.

Do not assume existing systems must be replaced.

#### 2. Where are authoritative records and evidence held?

Record:

- Source.
- Owner.
- Format.
- Version control.
- Retention.
- Data quality.
- How users find and verify the current version.

#### 3. What information may be used for discovery, testing or AI?

Confirm:

- Data classification.
- Permitted purpose.
- Access method.
- Confidentiality.
- Retention.
- Masking or synthetic alternatives.
- Prohibited information.
- Approval required.

Do not record passwords, secrets, API keys or sensitive content on the card.

#### 4. What is required for a controlled pilot?

Record:

- Integration or interface.
- Environment.
- Identity and permissions.
- Support owner.
- Deployment route.
- Monitoring.
- Recovery.
- Minimum security and control requirements.

### Card summary

- Existing capabilities that can be reused.
- Minimum conditions that must be established.
- Platform or data constraints.
- Boundaries that cannot be crossed.

---

## Card 6 — Agreed Current-State Workflow

### Replaces

“Business and AI current-state consensus card.”

### MRO title

> **What is the agreed current process, including tools and human decisions?**

### Participants

- Process owner.
- Representative users.
- IVT/domain owners.
- SMEs.
- Platform representatives.
- FDE lead.

### Workflow table

| Process step | Owner and output | Technology and human activity | Pain point/evidence |
|---|---|---|---|
| Step 1 | Role, input and output | System, tool, manual activity and judgement | Delay, issue or source |
| Step 2 | Role, input and output | System, tool, manual activity and judgement | Delay, issue or source |
| Step 3 | Role, input and output | System, tool, manual activity and judgement | Delay, issue or source |
| Step 4 | Role, input and output | System, tool, manual activity and judgement | Delay, issue or source |
| Step 5 | Role, input and output | System, tool, manual activity and judgement | Delay, issue or source |

Also record:

- Process trigger.
- Completion point.
- Common MRO steps.
- Domain-specific IVT variants.
- Exceptions.
- Confirmed facts.
- Conflicting accounts.
- Unrepresented roles.
- Outstanding questions.

### Card output

A process map that the process owner confirms as a sufficiently accurate basis for option assessment.

Only agreed elements should be treated as fact. Unresolved differences remain explicitly marked.

---

## Card 7 — Intervention and Delivery Route

### Replaces

“Transformation direction consensus card.”

### MRO title

> **Which intervention should be tested, and what should not yet be built?**

### Participants

- Process owner.
- AI Tech & Tooling/FDE.
- Architecture or platform representatives.
- Relevant SMEs.
- Steering forum where a formal decision is required.

### Questions

#### 1. What business outcome are we trying to achieve?

Restate the outcome without naming a preferred tool or platform.

#### 2. What interventions could deliver the outcome?

Consider a maximum of three viable directions drawn from:

- Stop unnecessary work.
- Simplify the process.
- Standardise templates or methods.
- Improve guidance or training.
- Reuse an existing MARM/enterprise capability.
- Configure an existing platform.
- Locally managed Copilot assistance.
- Deterministic workflow automation.
- Specialist analytical tooling.
- AI assistant or agent.
- New custom application.

#### 3. What supports or weakens each option?

| Option and expected outcome | Supporting evidence | Missing conditions/risks | Conclusion |
|---|---|---|---|
| Option 1 | Evidence and reuse | Gaps and dependencies | Test, gather evidence or pause |
| Option 2 | Evidence and reuse | Gaps and dependencies | Test, gather evidence or pause |
| Option 3 | Evidence and reuse | Gaps and dependencies | Test, gather evidence or pause |

#### 4. Which option should be tested first?

Record:

- Preferred option and rationale.
- Alternatives retained.
- Out-of-scope elements.
- Evidence still needed.
- Proposed delivery team.
- Process, tool and platform ownership.
- Governance implications.
- Decision-maker.

### Important statement

> Selecting an option for validation does not approve a build, procurement, production release or resource commitment.

---

## Card 8 — Experiment and Next-Step Agreement

### Replaces

“Pilot and next-action card.”

### MRO title

> **What will we test next, who will do it and what decision will the evidence support?**

### Participants

- Process owner.
- FDE lead.
- Proposed builder.
- Test users.
- Data or platform owner.
- AI use-case owner, where required.

### Questions

#### 1. What specific question will the next step answer?

Choose one or more:

- Continue discovery.
- Validate the workflow.
- Reproduce the baseline.
- Test an existing platform.
- Test technical feasibility.
- Build a limited vertical slice.
- Prepare a controlled pilot.
- Pause or close.

#### 2. What exactly is in and out of scope?

Record:

- Process scenario.
- Users and IVTs.
- Representative samples.
- Inputs.
- Expected outputs.
- Human controls.
- Explicit exclusions.

#### 3. How will value and control effectiveness be assessed?

Record:

- Current baseline.
- Success measure.
- Quality/control threshold.
- Human review.
- Failure and stop criteria.
- Effort and running cost.
- Evidence required for the next decision.

#### 4. Who will prepare each input or action?

| Action or evidence | Owner | Due date | Method/dependency |
|---|---|---|---|
| Action 1 | Named person/role | Date | Source or prerequisite |
| Action 2 | Named person/role | Date | Source or prerequisite |
| Action 3 | Named person/role | Date | Source or prerequisite |

Also record:

- Experiment sponsor.
- Process owner.
- Users/testers.
- Data authoriser.
- Builder.
- Review date.
- Expected decision at the next meeting.

### Important statement

> This card agrees an evidence-gathering step. It does not constitute approval for a full project, production implementation, procurement or ongoing support commitment.

# 4. How the cards should be used in practice

## Before the session

The FDE lead should:

- Select only the relevant cards.
- Identify the correct participants.
- Review existing Jira and Confluence information.
- Pre-populate known evidence.
- Mark unverified information as assumptions.
- Explain that the discussion is process-led and technology-neutral.

Not every participant needs to complete all eight cards.

## During the session

The FDE lead or FDE Assistant should:

- Ask for recent examples.
- Distinguish evidence from opinion.
- Avoid leading questions.
- Record disagreements rather than forcing agreement.
- Ask who can verify uncertain information.
- Capture evidence links.
- Identify owners for open questions.
- Keep the conversation focused on one workflow or sub-process.

## After the session

The FDE Workbench should:

1. Produce a structured summary.
2. Separate evidence, views, assumptions and questions.
3. Link supporting material.
4. Identify contradictions and missing roles.
5. Ask interviewees to verify the record.
6. Update the current-state workflow.
7. Generate proposed next steps.
8. Present matters requiring human decision.
9. Freeze the approved stage record.

The AI assistant can draft and challenge the record, but the relevant person must confirm it.

# 5. Recommended card routing

You do not need to use every card for every case.

### Simple local improvement

Use:

- Card 4 — User Tasks.
- Card 5 — Systems, Data and Access.
- Card 8 — Experiment and Actions.

### Cross-IVT process improvement

Use:

- Card 1 — Leadership Outcome.
- Card 2 — Process and Controls.
- Card 3 — Ownership and Handoffs.
- Card 4 — User Tasks for representative IVTs.
- Card 6 — Current-State Consensus.
- Card 7 — Intervention and Route.
- Card 8 — Experiment and Actions.

### AI or agent candidate

Use all relevant discovery cards, with particular emphasis on:

- Card 2 — Human judgement and controls.
- Card 4 — Current technology and correction.
- Card 5 — Data, access and Envoy readiness.
- Card 7 — AI versus non-AI alternatives.
- Card 8 — Evaluation and stop criteria.

# 6. Integration with the FDE Workbench

Each card should become a structured Workbench module rather than just a static form.

The FDE Assistant can:

- Select cards based on case type.
- Pre-populate fields from approved sources.
- Conduct guided interviews.
- Draft workflow diagrams.
- Highlight unsupported claims.
- Compare IVT responses.
- Identify ownership gaps.
- Search for existing MARM capabilities and MRO tools.
- Draft the option assessment.
- Produce the next steering decision pack.

The Workbench should retain:

- Original responses.
- AI-generated summary.
- Interviewee corrections.
- Final confirmed record.
- Evidence sources.
- Decision and rationale.
- Version history.

# 7. Connection to the existing MRO workstream

The cards can be used without changing the current sprint structure significantly:

- Joe or another FDE lead coordinates discovery.
- MRO volunteers can support interviews and workflow mapping.
- Process owners and users provide the business evidence.
- AI Tech & Tooling assesses the technical options.
- Platform representatives confirm reuse and integration routes.
- Card 8 creates the discovery or experiment actions.
- Approved development items then enter the existing Jira sprint.
- Sprint demos show both delivery progress and FDE findings.

A completed set of cards should not automatically generate development tasks. The route decision must first confirm whether the work belongs with:

- The process team.
- The existing volunteer workstream.
- MARM/P&A.
- Envoy.
- AI Tech & Tooling.
- Another funded delivery squad.

# Overall recommendation

The card set is very useful, particularly because it makes FDE repeatable and evidence-based. The main adaptations are:

- Replace “AI transformation” with “MRO process outcome and improvement.”
- Replace “customer” with “process owner, user or stakeholder.”
- Add controls, independence and professional judgement.
- Add common MRO versus IVT-specific variants.
- Consider non-build and existing-platform options explicitly.
- Require named process, solution, AI-use-case and platform ownership.
- Separate permission to test from permission to build.
- Preserve human approval at every material gate.

Used this way, the cards could form the **structured discovery layer of the MRO Tech & Tooling FDE Workbench** and help your team scale FDE without conducting every discussion informally from the beginning.