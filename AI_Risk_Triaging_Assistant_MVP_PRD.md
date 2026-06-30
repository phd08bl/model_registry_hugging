# Product Requirements Document  
## AI Risk Triaging Assistant Tool – MVP Requirements

---

## 1. Purpose

This document sets out the proposed MVP requirements for the **AI Risk Triaging Assistant Tool**.

The objective is to align with **AI Risk Oversight**, **AI Tech & Tooling**, and **PwC** on the required workflow, key users, process pain points, and MVP capabilities before moving into detailed technical design.

At this stage, the focus is on **what the tool needs to support**, not the final technology or implementation platform. Technical architecture, integrations, and deployment approach are to be confirmed later.

---

## 2. MVP Positioning

The MVP should be positioned as an:

> **AI Risk Oversight-led Triaging Assistant**

The tool should support the AI Risk Oversight Team in managing the AI use case triage process more consistently and efficiently.

The tool is **not intended to be a full governance platform for all second-line teams at MVP stage**.

For MVP:

- AI Risk Oversight is the primary user of the tool.
- Use Case Teams / Model Owners do **not** need direct access to the tool.
- Other 2LoD risk teams do **not** need direct access to the tool.
- Use Case Teams and 2LoD risk teams participate through existing channels, such as intake forms, tracker submissions, SharePoint / Confluence pages, emails, review packs, response templates, or other agreed mechanisms.
- AI Risk Oversight uses the tool to prepare, manage, consolidate, and evidence the triage process.

---

## 3. Background and Current Pain Points

Based on discussion with AI Risk Oversight, the current triage process includes more than initial classification.

The current process involves:

- Gathering use case information from multiple sources.
- Reviewing whether the information is complete enough.
- Asking the use case team for missing information.
- Identifying which risk specialists need to review the case.
- Sharing relevant information with other 2LoD risk teams.
- Capturing risk-area-specific views.
- Consolidating the final outcome.
- Recording rationale, evidence, conditions, and next actions.

AI Risk Oversight has highlighted that a significant amount of team capacity is currently spent on **upfront triage**, particularly intake and ingestion of use case information.

Therefore, the MVP should place strong emphasis on:

1. Streamlining upfront intake and ingestion.
2. Making the Use Case Team / Model Owner journey visible across the process.
3. Supporting the broader AIRO triage and assessment workflow, not only initial triage.
4. Reducing manual effort in preparing and consolidating review packs.
5. Creating a clear evidence trail.

---

## 4. Design Principles

### 4.1 AIRO-led

AI Risk Oversight should remain the owner of the workflow, judgement, and final outcome.

The tool supports AIRO, but does not replace AIRO decision-making.

### 4.2 Intake-first

The MVP should prioritise the intake and ingestion stage because this is a key current pressure point.

### 4.3 Use Case Team visible across the workflow

The Use Case Team / Model Owner should be shown across the lifecycle, even though they do not need direct access to the tool.

Their involvement includes submitting information, responding to questions, providing clarification, receiving outcomes, and notifying changes.

### 4.4 Human-in-the-loop

All key outputs should be reviewed and approved by AIRO before being shared or finalised.

### 4.5 Technology-agnostic

The workflow should not assume a specific platform.

Confluence, SharePoint, Jira, email, workflow tools, or a dedicated platform may be considered, but the implementation choice is **TBC**.

### 4.6 Evidence by design

The tool should help retain a clear record of the information used, the review performed, specialist inputs, final rationale, and outcome.

---

## 5. Users and Participants

### 5.1 Direct MVP Users

#### AI Risk Oversight Team

AIRO is the main user of the MVP.

AIRO uses the tool to:

- Ingest and structure use case information.
- Check information completeness.
- Generate follow-up questions.
- Identify relevant 2LoD risk areas.
- Generate review packs.
- Capture 2LoD inputs.
- Consolidate final outcome.
- Prepare and retain evidence.

#### AI Tech & Tooling Team

AI Tech & Tooling supports the build, configuration, testing, and iteration of the MVP.

---

### 5.2 Indirect Process Participants

#### Use Case Team / Model Owner

The Use Case Team / Model Owner does **not** need direct tool access for MVP.

They participate by:

- Submitting use case information through existing channels.
- Providing supporting documents or evidence.
- Responding to follow-up questions.
- Providing clarification if requested during 2LoD review.
- Receiving final outcome, actions, and conditions.
- Notifying material changes if re-engagement is required.

#### Other 2LoD Risk Teams

Other 2LoD risk teams do **not** need direct tool access for MVP.

They participate by:

- Reviewing a structured review pack.
- Providing their risk-area-specific assessment.
- Requesting more information if needed.
- Providing comments, conditions, concerns, or escalation points.
- Returning input through an agreed review mechanism.

---

## 6. High-level MVP Workflow

The proposed MVP workflow is:

```text
1. Intake & ingestion
2. Structure use case profile
3. Completeness & quality check
4. Use case team follow-up, if needed
5. Risk-area mapping and routing
6. Generate targeted review pack
7. Share pack for 2LoD specialist review
8. Capture 2LoD risk team input
9. Capture use case team clarification, if needed
10. Consolidate outcome
11. AIRO final review and approval
12. Record final outcome and evidence
13. Communicate outcome to use case team
14. Record material change / re-engagement triggers
```

---

## 7. Use Case Team / Model Owner Journey

The tool should make the Use Case Team / Model Owner journey visible across the workflow.

| Stage | Use Case Team / Model Owner role | Direct tool access required for MVP? |
|---|---|---:|
| Intake | Submit use case information | No |
| Completeness check | Respond to follow-up questions | No |
| Specialist review | Provide clarification or additional evidence if requested | No |
| Final outcome | Receive outcome, actions and conditions | No |
| Future change | Notify material changes if re-engagement is required | No |

The tool should support AIRO in managing these interactions, but the Use Case Team / Model Owner should not be required to log into the tool.

---

## 8. MVP Capabilities

### 8.1 Intake and Ingestion Support

#### Requirement

The tool should help AIRO bring together use case information from existing sources and convert it into a structured raw intake pack.

#### Potential input sources

- Intake form / submission.
- Governance tracker.
- Responsible AI tracker.
- SharePoint agent output.
- Existing use case documentation.
- Supporting evidence.
- Documents provided by the use case team.
- Email or other communication records.
- Manual copy / paste or file upload.

#### Key functions

The tool should support AIRO to:

- Capture information from multiple sources.
- Organise information by source.
- Identify duplicate, missing, or inconsistent information.
- Create a raw intake pack.
- Record where key information came from.

#### Output

- Raw intake pack.
- Source summary.
- Initial extracted facts.

#### Technical details

**TBC.**

---

### 8.2 Use Case Profile Structuring

#### Requirement

The tool should convert intake information into a standard use case profile.

#### The profile should include

- Use case name.
- Use case owner / model owner.
- Business area.
- Business purpose.
- AI capability.
- Model type.
- Data used.
- Users and impacted parties.
- Outputs.
- Decision impact.
- Human oversight.
- Deployment context.
- Third-party / supplier involvement.
- Existing controls.
- Known limitations.
- Change / re-engagement considerations.

#### Key functions

The tool should support AIRO to:

- Generate a structured profile.
- Review and edit the profile.
- Separate factual information from assumptions.
- Retain source references where possible.

#### Output

- Structured use case profile.

#### Technical details

**TBC.**

---

### 8.3 Completeness and Quality Check

#### Requirement

The tool should help AIRO identify whether the use case information is complete enough to proceed.

#### Key functions

The tool should support AIRO to:

- Identify missing information.
- Identify unclear or inconsistent information.
- Highlight information needed before 2LoD specialist review.
- Generate follow-up questions for the Use Case Team / Model Owner.
- Allow AIRO to edit and approve the questions before sending.

#### Possible completeness outcomes

- Complete enough to proceed.
- Proceed with caveats.
- More information required.

#### Output

- Completeness assessment.
- Missing information list.
- Follow-up question list.

#### Technical details

**TBC.**

---

### 8.4 Use Case Team Follow-up Support

#### Requirement

The tool should support AIRO in managing follow-up with the Use Case Team / Model Owner without requiring direct tool access for the use case team.

#### Key functions

The tool should support AIRO to:

- Generate follow-up questions.
- Export or copy questions into existing communication channels.
- Record that questions have been sent.
- Capture responses received from the use case team.
- Update the use case profile based on responses.
- Retain a record of questions and responses.

#### Output

- Follow-up request.
- Response log.
- Updated use case profile.

#### Technical details

**TBC.**

---

### 8.5 Risk-area Mapping and Routing

#### Requirement

The tool should help AIRO identify which 2LoD risk areas may need to review the use case.

#### Key functions

The tool should support AIRO to:

- Identify relevant risk areas.
- Explain why each risk area may be relevant.
- Highlight the information that triggered the risk area.
- Recommend which 2LoD teams should review.
- Allow AIRO to approve, edit, or override the recommendation.
- Capture rationale for overrides.

#### Example risk areas

- Model Risk.
- Data / Privacy.
- Technology / IT.
- Conduct.
- Supplier.
- Change / Business Continuity.
- Payments.
- Customer & Product.
- Market Conduct.
- Other relevant risk specialists.

#### Output

- Risk-area mapping.
- Routing recommendation.
- Rationale for specialist engagement.

#### Technical details

**TBC.**

---

### 8.6 Targeted Review Pack Generation

#### Requirement

The tool should generate a structured review pack that can be shared with relevant 2LoD risk teams.

The review pack should be technology-agnostic and suitable for use in existing collaboration channels.

#### Review pack should include

1. Use case summary.
2. Key extracted facts.
3. Completeness gaps or caveats.
4. Risk-area mapping.
5. Relevant information by risk area.
6. Review questions for each 2LoD team.
7. Standard response template.
8. Evidence / source references.

#### Key functions

The tool should support AIRO to:

- Generate a review pack.
- Edit and approve the review pack.
- Export or copy the pack into a shared review channel.
- Produce team-specific sections where needed.

#### Output

- Targeted review pack.
- Standard response template.

#### Technical details

**TBC.**

---

### 8.7 2LoD Specialist Review Input

#### Requirement

The tool should support AIRO in capturing 2LoD specialist input without requiring 2LoD teams to access the full tool.

#### Key functions

The tool should support AIRO to capture:

- Risk area.
- Reviewer.
- Review status.
- Assessment outcome.
- More information required.
- Comments.
- Conditions.
- Concerns.
- Escalation requirement.
- Review date.

#### Possible review statuses

- Not started.
- In progress.
- More information required.
- Completed.
- Escalated.
- Not applicable.

#### Possible assessment values

- Low.
- Medium.
- High.
- Not applicable.
- Unable to assess.

#### Output

- Risk team input register.
- Open questions.
- Specialist comments and conditions.

#### Technical details

**TBC.**

---

### 8.8 Clarification Support During 2LoD Review

#### Requirement

Where 2LoD teams require more information, the tool should help AIRO manage clarifications with the Use Case Team / Model Owner.

#### Key functions

The tool should support AIRO to:

- Capture 2LoD information requests.
- Convert requests into clear questions for the use case team.
- Record responses received.
- Link responses back to the relevant risk team request.
- Update the assessment record.

#### Output

- Clarification log.
- Updated risk team input.
- Updated evidence record.

#### Technical details

**TBC.**

---

### 8.9 Consolidation and Final Outcome

#### Requirement

The tool should support AIRO in consolidating specialist views and forming a final outcome.

#### Key functions

The tool should support AIRO to:

- Summarise all 2LoD inputs.
- Highlight missing specialist responses.
- Highlight conflicting views.
- Summarise conditions and actions.
- Draft a consolidated assessment.
- Draft final outcome rationale.
- Allow AIRO to review, edit, and approve the final outcome.

#### Output

- Consolidated assessment.
- Final risk outcome.
- Rationale.
- Conditions and actions.

#### Technical details

**TBC.**

---

### 8.10 Evidence Record and Export

#### Requirement

The tool should create a final evidence record for the triage process.

#### Evidence record should include

- Intake sources.
- Raw intake pack.
- Structured use case profile.
- Completeness assessment.
- Follow-up questions and responses.
- Risk-area mapping.
- 2LoD specialist inputs.
- Clarifications from use case team.
- Final assessment.
- Final outcome.
- Rationale.
- Conditions and actions.
- Communication record.
- Re-engagement triggers.

#### Output

- Final evidence pack.
- Exportable final assessment record.

#### Technical details

**TBC.**

---

### 8.11 Re-engagement / Material Change Trigger

#### Requirement

The tool should record whether future re-engagement may be needed if the use case changes.

#### Key functions

The tool should support AIRO to record potential triggers, including:

- Change in model.
- Change in data.
- Change in purpose.
- Change in use.
- Change in controls.
- Change in environment.
- Incident or issue.
- Regulatory or policy change.

#### Output

- Re-engagement trigger checklist.
- Change notification instruction.

#### Technical details

**TBC.**

---

## 9. MVP Access Model

The MVP access model should be deliberately simple.

| User group | Direct tool access for MVP? | Interaction model |
|---|---:|---|
| AI Risk Oversight Team | Yes | Primary users of the tool |
| AI Tech & Tooling Team | Yes | Build, support and administration |
| Use Case Team / Model Owner | No | Submit information and respond through existing channels |
| Other 2LoD Risk Teams | No | Review shared pack and provide structured input |
| PwC | TBC | Support design / methodology; access to bank data subject to approval |

Broader direct access, role-based permissions, reviewer portals, and workflow automation can be considered as future enhancements.

---

## 10. Key Outputs

The MVP should produce:

1. Raw intake pack.
2. Structured use case profile.
3. Completeness assessment.
4. Follow-up questions for use case team.
5. Risk-area mapping and routing recommendation.
6. Targeted review pack.
7. 2LoD input register.
8. Clarification log.
9. Consolidated assessment.
10. Final risk outcome.
11. Evidence record.
12. Re-engagement trigger record.

---

## 11. What Is Not Required for MVP

The MVP does not require:

- Direct tool access for use case teams / model owners.
- Direct tool access for all 2LoD risk teams.
- A full enterprise governance platform.
- Dedicated portals for all participants.
- Full role-based access management.
- Deep integration with all existing systems on day one.
- Full workflow automation.
- Automated approval or rejection.
- Final risk decisions without AIRO judgement.

These may be considered later if the MVP proves useful.

---

## 12. Architecture and Technical Design

Detailed technical design is **TBC**.

At this stage, the agreed requirement is that the MVP should include the following logical components:

1. Intake and ingestion component.
2. Use case profile structuring component.
3. Completeness and follow-up question component.
4. Risk-area mapping and routing component.
5. Review pack generation component.
6. 2LoD input capture component.
7. Consolidation component.
8. Evidence record and export component.
9. Re-engagement / change trigger component.

Potential implementation options may include existing workflow tools, document repositories, Confluence, SharePoint, Jira, forms, manual templates, or a dedicated platform interface.

The implementation approach should be confirmed after workflow and requirements are agreed.

---

## 13. Human Review and Approval Points

AIRO should review and approve the following before they are shared or finalised:

1. Structured use case profile.
2. Completeness assessment.
3. Follow-up questions.
4. Risk-area mapping and routing.
5. Review pack.
6. Consolidated assessment.
7. Final risk outcome.
8. Evidence record.

The tool should assist decision-making but should not replace AIRO judgement.

---

## 14. Success Criteria

The MVP should be considered successful if it can:

1. Reduce manual effort in upfront intake and ingestion.
2. Help AIRO identify missing information earlier.
3. Make the Use Case Team / Model Owner journey clear across the process.
4. Produce a standard use case profile.
5. Produce a targeted review pack for relevant 2LoD teams.
6. Allow 2LoD input to be captured without requiring direct tool access.
7. Support consolidation of specialist views.
8. Produce a clear final assessment and evidence record.
9. Support AIRO’s end-to-end triage workflow.
10. Avoid overbuilding into a full platform at MVP stage.

---

## 15. Open Questions for AIRO and PwC

### Intake and ingestion

1. What are the main intake sources today?
2. What does the SharePoint agent currently capture?
3. What fields are mandatory for initial triage?
4. Which fields are most often missing or unclear?
5. What information is needed before specialist review can begin?

### Use case team journey

6. At which points does the use case team usually need to provide more information?
7. How are follow-up questions sent today?
8. How are responses tracked today?
9. How should final outcome and actions be communicated?

### 2LoD specialist review

10. Which risk teams are commonly engaged?
11. What information does each risk team need?
12. What response format should 2LoD teams use?
13. How are conflicting views resolved?
14. What is the minimum evidence needed from each specialist team?

### Final outcome and evidence

15. What are the possible final risk outcomes?
16. What conditions or actions need to be recorded?
17. Where should the final evidence record be stored?
18. What should trigger re-engagement after changes?

### Implementation

19. Which existing review channel is preferred for MVP?
20. Should the review pack be exported manually first, or published into an existing workspace?
21. What technical details should be deferred until after requirements are agreed?

---

## 16. Future Enhancements

Future releases may consider:

- Direct access for 2LoD reviewers.
- Direct access for Use Case Teams / Model Owners.
- Role-based access control.
- Automated workflow tasks.
- Automated reminders.
- Reviewer portal.
- Use case team portal.
- Integration with SharePoint, Confluence, or Jira.
- Dashboard and MI reporting.
- Linkage to validation workflow.
- Linkage to post-go-live monitoring.
- Formal system-of-record integration.

---

## 17. Summary

The MVP should focus on agreeing and supporting the **AI Risk Oversight workflow**, rather than building a full platform from day one.

The proposed MVP is an AIRO-led triaging assistant that helps with:

- Stronger upfront intake and ingestion.
- Use case profile structuring.
- Completeness checks.
- Follow-up question generation.
- Risk-area mapping.
- Targeted review pack generation.
- 2LoD input capture.
- Consolidation of final outcome.
- Evidence record generation.
- Re-engagement trigger capture.

Use Case Teams / Model Owners and other 2LoD teams do not need direct tool access for MVP. They should participate through existing channels, while AIRO uses the tool to manage, consolidate, and evidence the process.
