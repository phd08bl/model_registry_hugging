# AI Risk Triage Version 1 Blueprint

## Purpose

This blueprint describes the quickest operational version of the AI Risk Triage workflow. It uses Power Apps only for the Model Owner intake, where the screen needs to load a versioned, configurable question template. SharePoint Lists hold configuration and Case records, while Power Automate performs deterministic processing. Standard SharePoint views and forms support the initial AIRO review unless user testing demonstrates a need for a tailored review Power App. The version does not use LLMs or agents.

## Design principle

> The system validates, calculates and proposes. AI Risk Oversight reviews and confirms. Power Automate executes only approved follow-up actions.

## 1. User journey

```mermaid
flowchart TD
    A["Model Owner completes intake<br/>Focused Power App loads the active question template<br/>Capture answers, rationale, use-case details and evidence"]

    A --> B["Power Automate validates the submission<br/>Check required answers, rationale and evidence<br/>Assign the input and configuration versions"]

    B -->|Incomplete| C["Power Automate initiates follow-up<br/>Return only the relevant questions<br/>Send notification and record the request"]

    C --> A

    B -->|Complete| D["Power Automate applies approved deterministic rules<br/>Calculate score and rating<br/>Identify deal-breakers and proposed 2LoD triagers"]

    D --> E["Store the transparent triage proposal in SharePoint<br/>Retain answers, evidence and version references<br/>Record score breakdown, matched rules and reason codes"]

    E --> F{"AIRO review and decision<br/>Standard SharePoint view or focused Power App if required"}

    F -->|Request more information| I["Power Automate records and executes the request<br/>Update Case status, send the email or notification<br/>Create the required follow-up action"]

    I --> A

    F -->|Escalate| J["Power Automate records and executes the escalation<br/>Update Case status, notify the authorised party<br/>Create an escalation task and audit event"]

    J --> K["Wait for the authorised response or decision"]
    K --> F

    F -->|Confirm or authorised override| G["Power Automate records the confirmed decision<br/>Capture approver, timestamp and override rationale<br/>Keep the system proposal separate from the AIRO decision"]

    G --> H["Power Automate executes approved actions<br/>Update Case fields and status<br/>Send notifications, create 2LoD tasks and generate the final pack"]

    H --> L["Store the final triage result in SharePoint<br/>Retain the complete versioned audit trail"]
```

## 2. Technical design

```mermaid
flowchart TD
    subgraph UX["User experience — Power Apps only where required"]
        U1["Model Owner intake Power App<br/>Loads the active question template<br/>Captures answers, rationale, details and evidence"]

        U2["AIRO SharePoint review view<br/>Reviews evidence, proposal and reason codes<br/>Selects the controlled outcome"]

        U3["Optional AIRO review Power App<br/>Used only if SharePoint does not provide<br/>a sufficient review experience"]
    end

    subgraph CFG["Controlled, versioned configuration in SharePoint"]
        C1["Question templates and response options<br/>Rationale and evidence requirements"]

        C2["Scores, weights and rating bands"]

        C3["Deal-breakers and 2LoD routing rules"]

        C4["Decision authorities and action mappings<br/>Notification and document templates"]
    end

    subgraph PA["Power Automate processing"]
        P1["Validate submission and assign versions<br/>Check required fields and evidence references<br/>Pin input and configuration versions"]

        P2["Apply approved deterministic rules<br/>Calculate score and rating<br/>Identify deal-breakers and proposed 2LoD triagers"]

        P3["Validate and process the AIRO decision<br/>Check authority and required rationale<br/>Create the approved action instructions"]

        P4["Execute approved actions<br/>Apply duplicate prevention and retry controls<br/>Record execution status"]
    end

    subgraph SP["SharePoint Case data, evidence and audit records"]
        S1["Live Case and input records<br/>Answers, rationale and evidence metadata<br/>Input and configuration versions"]

        S2["System-generated triage proposal<br/>Score breakdown, matched rules<br/>Reason codes and proposed 2LoD triagers"]

        S3["AIRO decision and final result<br/>Confirmation or authorised override<br/>Approver, rationale and timestamp"]

        S4["Action outbox and delivery status<br/>Action type, recipient and Case reference<br/>Pending, completed or failed status"]

        S5["Append-only audit events<br/>Case changes, calculations, decisions<br/>actions, retries and outcomes"]
    end

    subgraph OUT["Automated outputs and follow-up"]
        O1["Model Owner emails and information requests"]

        O2["2LoD notifications, referrals and tasks"]

        O3["Case status updates and final triage pack"]
    end

    C1 --> U1
    U1 --> P1
    C1 --> P1

    P1 --> S1
    S1 --> P2
    C2 --> P2
    C3 --> P2

    P2 --> S2
    P2 --> S5

    S1 --> U2
    S2 --> U2

    U2 -. "Optional enhanced interface" .-> U3
    U2 --> S3
    U3 --> S3

    C4 --> P3
    S3 --> P3
    P3 --> S4
    P3 --> S5

    S4 --> P4
    C4 --> P4

    P4 --> O1
    P4 --> O2
    P4 --> O3

    P4 --> S1
    P4 --> S4
    P4 --> S5

    O1 -. "New or updated submission" .-> U1
```

## 3. What is configurable in Version 1

| Configuration | Storage | Change approach |
|---|---|---|
| Questionnaire wording, choices and order | SharePoint question-template list | Power Apps loads the approved active questionnaire version |
| Mandatory answer and rationale requirements | SharePoint configuration list | Update a draft configuration and publish after testing |
| Scores and weights | SharePoint scoring-rule list | Configuration change using existing rule operators |
| Materiality rating bands | SharePoint rating-band list | Approved configuration change |
| Deal-breakers | SharePoint deal-breaker list | Approved configuration change and regression test |
| 2LoD triagers | SharePoint routing-rule list | Approved configuration change with relevant 2LoD agreement |
| Notification templates | SharePoint template list | Controlled template update |

Power Automate must read one approved, effective rule-set version and record that version against the Case. A change to an active configuration must create a new version rather than overwrite the version already used for earlier Cases.

## 4. Minimum SharePoint records

```text
AI_Use_Cases
Case_Answers
Evidence_Register
Triage_Proposals
Triage_Result_Details
AIRO_Decisions
Triage_Audit_Log
Questionnaire_Register
Triage_Rule_Sets
Materiality_Rules
Materiality_Bands
Deal_Breaker_Rules
Second_Line_Routing_Rules
Notification_Templates
```

## 5. Minimum control requirements

- Stable Case ID and input version.
- Questionnaire and rule-set versions frozen for each calculation.
- Score contribution and reason code for every matched rule.
- Original system proposal stored separately from the AIRO decision.
- AIRO override authority and mandatory override rationale.
- No confirmation of stale results after material input changes.
- Append-oriented audit records covering submission, calculation, review, decision and follow-up actions.
- Idempotency controls to prevent duplicate calculations, emails and tasks.
- Development, test/UAT and production release controls.
- Reconciliation and failure queues for incomplete or failed processing.

## 6. When Power Apps becomes justified

Version 1 uses one focused Power App for the Model Owner intake because it needs to render configurable questions. Avoid building additional Power Apps unless operational use demonstrates a material need for:

- more complex conditional question display than the initial intake app supports;
- a single AIRO screen combining answers, rationale, evidence and decision controls;
- better save-and-resume handling than the initial form provides;
- controlled administration and preview of questionnaire versions.

For the quick first version, authorised administrators can maintain draft configurations through controlled SharePoint Lists. Add a separate configuration Power App only after the configuration process and control requirements are stable.
