The PDF is very useful, but it should be used as an **FDE facilitator checklist**, not sent to every MRO stakeholder as a 26-question form.

It complements the eight discovery cards:

- The cards structure individual interviews and workshops.
- The checklist ensures that the FDE lead has covered the important questions before recommending a solution or delivery route.
- The FDE Workbench records the evidence, responses, decisions and outstanding gaps.

The original checklist is too centred on whether an AI project should proceed. The MRO version should ask whether the process problem is worth addressing and what the proportionate intervention should be.

# MRO FDE Discovery and Readiness Checklist

## Section 1 — Is this a priority MRO problem?

### 1. What MRO outcome or process problem are we trying to improve?

Capture:

- Leadership priority.
- Process affected.
- Teams or IVTs affected.
- Recent example.
- Supporting evidence.
- Consequences of doing nothing.

### 2. What is the underlying problem, rather than the requested feature?

Ask:

- What currently prevents the desired outcome?
- Is this a process, ownership, capacity, data, system, control or skills problem?
- What workaround is currently used?
- Why is the workaround insufficient?

A request for “an agent” or “automation” is not itself the problem statement.

### 3. What would materially improve if the problem were resolved?

Consider:

- Quality and consistency.
- Validation cycle time.
- Evidence readiness.
- Control effectiveness.
- Capacity.
- User experience.
- Auditability.
- Ability to focus on professional judgement.

Record how any released capacity is expected to be used.

### 4. What is the scale and materiality of the problem?

Record:

- Frequency.
- Case volume.
- Number of teams affected.
- Effort and waiting time.
- Risk or control impact.
- Regulatory or audit importance.

A low-frequency activity may still be a priority where the potential impact is high.

### 5. How will MRO know that the intervention created value?

Define:

- Current baseline.
- Target outcome.
- Quality and control measures.
- Cycle-time or effort measures.
- User and adoption measures.
- Evidence required.
- Review period.

The value case must go beyond whether the proposed technology appears impressive.

### Section 1 decision

- Prioritise for discovery.
- Request more evidence.
- Combine with another case.
- Defer.
- Close.

---

# Section 2 — What is the real end-to-end process?

## 6. Where does the process start and end?

Define:

- Trigger.
- Required inputs.
- Completion event.
- Outputs.
- Downstream recipient.
- Evidence of completion.

Avoid examining only the step initially raised by the requester.

## 7. What happens immediately upstream and downstream?

Identify:

- Who provides the inputs.
- What must happen before the activity begins.
- Who uses the output.
- What happens if the output is late, incomplete or incorrect.
- Dependencies on other teams or systems.

## 8. Who and what performs each stage?

For every process stage, distinguish:

- Human activity.
- Existing system activity.
- Manual rules.
- Quantitative or analytical methods.
- AI or Copilot use.
- Human-system interaction.
- Required approval or challenge.

This helps determine whether the need is process change, deterministic automation, specialist analytics or AI.

## 9. Where are the delays, queues and returns?

Record:

- Active working time.
- Waiting time.
- Approval delay.
- Evidence delay.
- Rework.
- Handoffs.
- Return-to-origin points.
- Reason for each delay.

Use data where available and clearly label estimates.

## 10. Which exceptions and failures occur?

Ask about:

- Missing evidence.
- Conflicting information.
- Unclear rules.
- System failures.
- Data-quality issues.
- Unusual model types.
- Late changes.
- Disagreement between reviewers.
- Escalation and resolution.

The solution must support important exceptions, not only the happy path.

## 11. How are professional judgements made?

Establish:

- Whether criteria are documented.
- Whether an expert can explain them.
- Evidence required.
- Whether different IVTs use different criteria.
- Which variations are justified by model type.
- Which variations reflect historical practice.
- Which decisions must remain human.

## 12. Can the process owner demonstrate a recent real case?

Walk through one case from trigger to completion, including:

- Inputs and evidence.
- Decisions.
- Tools used.
- Handoffs.
- Exceptions.
- Rework.
- Output.
- Approval and closure.

A real case is generally more reliable than an abstract description of the intended process.

### Section 2 decision

The process owner confirms:

- The as-is workflow is sufficiently accurate.
- Common steps and IVT variants are distinguished.
- Human judgement points are identified.
- Major pain points are evidenced.
- Outstanding disagreements are recorded.

---

# Section 3 — Can the systems, data and knowledge support improvement?

## 13. What data, documents and evidence does the process require?

Record:

- Authoritative source.
- Owner.
- Location.
- Format.
- Frequency.
- Version.
- Retention.
- How it is currently retrieved.
- Whether it can be accessed consistently.

Include evidence contained in documents, spreadsheets, emails, workflow systems and local files.

## 14. Is the information sufficiently complete, accurate and traceable?

Assess:

- Completeness.
- Accuracy.
- Timeliness.
- Consistency.
- Structure.
- Lineage.
- Version control.
- Labelling.
- Missing or conflicting records.

Data cleaning and process correction may be required before automation is appropriate.

## 15. Can existing systems support discovery, pilot and production?

Assess separately:

- PoC access.
- Production access.
- APIs or integration.
- Identity and permissions.
- Data movement restrictions.
- Monitoring.
- Support.
- Deployment route.

Consider existing MARM/P&A, Confluence, Jira, Envoy and MRO specialist capabilities before proposing a new application.

## 16. Is there sufficient expert knowledge and representative history?

Identify:

- Process guidance.
- Validation methodology.
- Policies and standards.
- Practical examples.
- Historical cases.
- Known exceptions.
- Representative test samples.
- SMEs who can explain and assess the process.

For AI cases, these may also form the basis of knowledge sources and evaluation datasets.

## 17. What information cannot be accessed, processed or retained?

Confirm:

- Confidentiality.
- Data classification.
- Access restrictions.
- Permitted purpose.
- Retention.
- Cross-system transfer.
- Masking or synthetic-data needs.
- Prohibited information.
- Approval requirements.

Never record passwords, keys or sensitive raw content in the discovery checklist.

### Section 3 decision

Classify readiness as:

- Ready using existing capabilities.
- Ready subject to stated conditions.
- Requires data or access remediation.
- Requires platform involvement.
- Not currently feasible.

---

# Section 4 — Are risk, ownership and adoption clear?

## 18. What errors are tolerable, and what decisions require human control?

Identify:

- Acceptable and unacceptable failure.
- Materiality of incorrect outputs.
- Human review.
- Approval.
- Challenge.
- Override.
- Escalation.
- Prohibited autonomous actions.

Findings, ratings, approvals and material risk judgements should normally retain meaningful human accountability.

## 19. What happens when the solution or underlying service fails?

Define:

- Manual fallback.
- Safe failure.
- Exception queue.
- User notification.
- Incident reporting.
- Recovery.
- Rollback.
- Data reconciliation.
- Service restoration.
- Decision on continued use.

## 20. Who owns each aspect of the solution?

Confirm separately:

- Executive sponsor.
- Common MRO process owner.
- Local IVT process owner.
- Methodology/control owner.
- AI use-case or model owner.
- Solution/product owner.
- Developer.
- Runtime/hosting owner.
- Data owner.
- Operational support owner.
- Change-approval authority.
- Funding owner.

MARM or Envoy ownership of a platform does not transfer ownership of MRO methodology or control decisions.

## 21. Will users adopt the changed process?

Assess:

- User involvement.
- Current pain.
- Additional workload.
- Training.
- New responsibilities.
- Change fatigue.
- Confidence in the solution.
- Effect on accountability.
- Support available.
- Distribution of costs and benefits.

## 22. Is the process owner prepared to remain involved?

Confirm availability for:

- Discovery.
- Workflow verification.
- Requirements.
- Providing examples.
- Testing.
- Decision-making.
- Pilot support.
- Adoption.
- Benefits review.
- Ongoing change control.

FDE cannot manufacture domain knowledge or assume the process owner’s accountability.

### Section 4 decision

Before progressing, require:

- Named ownership.
- Clear human-control boundaries.
- Viable failure and fallback.
- Process-owner participation.
- Defined governance route.
- Credible adoption plan.

---

# Section 5 — Is the next experiment and long-term route credible?

## 23. What specific hypothesis will the experiment test?

Define:

- Question to be answered.
- Current baseline.
- Representative users and cases.
- In-scope and out-of-scope activities.
- Inputs and expected outputs.
- Success thresholds.
- Failure and stop criteria.
- Review date.

A PoC validates assumptions; it is not production approval.

## 24. Who will operate, monitor and change the solution after launch?

Define:

- Operational owner.
- Monitoring.
- Incident handling.
- Model, prompt or rule changes.
- Knowledge-source updates.
- Regression testing.
- User support.
- Documentation.
- Release process.
- Business continuity.
- What happens when the original FDE contributors are unavailable.

## 25. Which elements are MRO-specific and which are reusable?

Distinguish:

- Common MRO process pattern.
- Domain-specific IVT methodology.
- General workflow component.
- Reusable agent skill.
- Platform capability.
- Standard data object.
- Evaluation asset.
- Case-specific logic.

Do not turn every request into a permanent product feature. Promote components into the common pattern only after evidence of reuse.

## 26. Is there sufficient commitment to proceed?

Confirm that the relevant parties will:

- Provide time.
- Provide authorised evidence.
- Participate in workshops.
- Test representative cases.
- Review outputs.
- Make decisions.
- Accept failure or redesign.
- Support iteration.
- Take responsibility for adoption.

If commitment is insufficient, pause the case rather than allowing FDE or AI Tech & Tooling to become the de facto process owner.

### Section 5 decision

- Continue discovery.
- Reproduce the baseline.
- Test an existing capability.
- Run a technical experiment.
- Build a limited vertical slice.
- Prepare a controlled pilot.
- Route to another delivery team.
- Pause.
- Stop.

# How this checklist fits with the discovery cards

| Checklist section | Relevant MRO cards | FDE output |
|---|---|---|
| 1. Priority and value | Card 1 and Card 2 | Outcome, sponsor and priority |
| 2. End-to-end process | Cards 2, 3, 4 and 6 | Agreed workflow and pain points |
| 3. Data and systems | Card 5 | Readiness and constraints |
| 4. Risk and ownership | Cards 2, 4 and 7 | Controls, ownership and governance |
| 5. Experiment and operation | Cards 7 and 8 | Delivery route and experiment charter |

# How to use it in practice

The FDE lead should not ask all 26 questions in one meeting.

## Initial leadership discussion

Use questions:

- 1–5.
- 20.
- 22.

## Process-owner and SME discovery

Use questions:

- 6–12.
- 16.
- 18.

## User observation

Use questions:

- 7–12.
- 21.

## Data and platform discussion

Use questions:

- 13–17.
- 19.
- 24.

## Solution and delivery-route workshop

Use questions:

- 18–26.

After each discussion:

1. Record evidence, views, assumptions and questions separately.
2. Link supporting documents.
3. Identify conflicting accounts.
4. Assign an owner to every material gap.
5. Ask the interviewee to verify the summary.
6. Update the FDE Workbench.
7. Freeze the confirmed stage record.
8. Escalate only the decisions requiring leadership or steering approval.

# Important changes from the original PDF

The adapted MRO checklist:

- Starts from a leadership-prioritised outcome, not an AI request.
- Treats frequency and efficiency as only part of the value case.
- Adds quality, control, evidence and independence.
- Distinguishes common MRO process ownership from IVT variants.
- Considers MARM and other existing platforms before building.
- Separates process, methodology, product, code and runtime ownership.
- Adds AI governance and human judgement where applicable.
- Requires operational support and change control.
- Allows “simplify”, “reuse”, “pause” and “stop” as successful FDE outcomes.
- Keeps build and production commitments outside discovery.

The PDF therefore provides a very good foundation. In the MRO model, it should become the **quality-control checklist behind the FDE Discovery Cards and Workbench**, ensuring that a case does not proceed merely because the proposed tool is attractive or because a prototype can be built.