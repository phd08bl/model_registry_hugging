# MRO Agent Engineering Standard

**Document type:** Engineering Standard  
**Applies to:** Model Risk Office (MRO) AI Tech & Tooling and MRO teams designing, building, testing, deploying, or operating AI agents  
**Status:** Draft for team adoption  
**Primary owner:** MRO AI Tech & Tooling  
**Scope:** MRO agent engineering, including graph, loop, state, human-control, evidence, and harness design  
**Implementation frameworks:** Framework-agnostic. May be implemented using LangGraph, Google ADK, Envoy-supported frameworks, or other approved technologies.

---

## 1. Purpose

This standard defines how MRO agents should be designed and engineered so that they are:

- controlled;
- auditable;
- testable;
- reusable;
- evidence-driven;
- human-accountable;
- portable across agent frameworks;
- suitable for MRO validation, oversight, and analytical processes.

The standard separates agent engineering into three related disciplines:

1. **Graph Engineering** — how work is decomposed, connected, routed, and controlled.
2. **Loop Engineering** — how iterative behaviour is bounded, evidence-driven, convergent, and escalated.
3. **Harness Engineering** — the controlled operating environment in which the agent runs.

The standard is intentionally **framework-independent**. The MRO design should be defined first; implementation in LangGraph, Google ADK, Envoy, or another framework follows afterwards.

---

## 2. Core Design Philosophy

MRO agents should be designed using the following principle:

> **Design the controlled process first. Implement it in the agent framework second.**

MRO should avoid beginning with:

> “Let us build a LangGraph agent.”

Instead, teams should begin with:

> “Let us engineer the state, graph, loops, controls, evidence, and human accountability required for this process.”

The implementation technology may change. The MRO engineering design should remain stable.

---

## 3. MRO Agent Engineering Model

The MRO engineering model has four connected views:

### 3.1 State

**Question:** What does the process know, and what is authoritative?

State represents the structured information that the graph reads and updates.

Examples:

- model information;
- validation scope;
- identified risks;
- validation plan;
- scenarios;
- evaluation plans;
- run status;
- results;
- evidence;
- findings;
- human decisions;
- exceptions.

### 3.2 Graph

**Question:** Where can the process go next?

The graph defines:

- nodes;
- edges;
- routing;
- subgraphs;
- parallelism;
- human decision points;
- failure paths;
- completion paths.

### 3.3 Loop

**Question:** When should the process continue, repeat, stop, or escalate?

Loops define controlled iteration based on:

- evidence;
- objectives;
- convergence criteria;
- iteration limits;
- budgets;
- escalation rules.

### 3.4 Harness

**Question:** Under what controlled environment can the graph execute?

The harness defines:

- models;
- tools;
- APIs;
- identity;
- permissions;
- memory;
- state persistence;
- checkpoints;
- files/workspace;
- human approval mechanics;
- runtime controls;
- recovery;
- observability;
- evidence and audit;
- deployment controls.

---

## 4. High-Level Relationship

```text
                    MRO Agent Engineering

                         STATE
                           |
          -------------------------------------
          |                 |                 |
          v                 v                 v
        GRAPH              LOOP             HARNESS
     Where can the      When should       Under what
     process go?        it iterate?       controls?
          |                 |                 |
          -------------------------------------
                           |
                        EVIDENCE
```

State and evidence are cross-cutting and connect all three engineering disciplines.

---

# Part 1 — Graph Engineering

## 5. Objective of Graph Engineering

Graph Engineering converts an MRO process into an explicit, controlled, and testable execution graph.

A well-engineered graph should make clear:

- what work is performed;
- what information moves between steps;
- which activities are independent;
- which activities must be sequential;
- what decisions determine the next path;
- where human intervention is required;
- where tools or systems are invoked;
- what happens when execution fails;
- when the process completes;
- when the process must escalate.

---

## 6. Core Graph Engineering Principles

### 6.1 Nodes are bounded jobs

Each node should have one clear responsibility.

If a node performs several materially different activities joined by “and”, consider splitting it.

**Poor example**

```text
Understand model, identify risks, generate tests, and draft findings
```

**Preferred**

```text
Understand Model
      |
      v
Identify Risks
      |
      v
Design Tests
      |
      v
Analyse Results
      |
      v
Draft Findings
```

### 6.2 Classify every node

Every graph node should be explicitly classified as one of the following:

| Type | Meaning | Typical examples |
|---|---|---|
| `[A]` | Agent / LLM reasoning | model understanding, risk analysis, result interpretation |
| `[D]` | Deterministic logic | schema validation, thresholds, aggregation, routing |
| `[T]` | Tool / external system | model runner, evaluation engine, retrieval service |
| `[H]` | Human decision | approval, challenge, escalation, final conclusion |

This classification is mandatory for material MRO agents.

### 6.3 Edges represent real dependencies

An edge should exist because information or control genuinely depends on the preceding node.

Do not create an edge simply because one human activity historically happened before another.

For each edge, ask:

> **What exact object or decision crosses this edge?**

If there is no clear answer, reconsider whether the edge is necessary.

### 6.4 Prefer structured contracts

Material nodes should exchange structured, validated objects rather than relying only on free-text conversation.

Examples:

```text
ModelUnderstanding
IdentifiedRisk[]
ValidationPlan
ScenarioSet
EvaluationPlan[]
EvaluationResult[]
EvidenceAssessment
Finding[]
HumanDecision
```

Structured contracts improve:

- testability;
- reproducibility;
- validation;
- versioning;
- portability;
- observability.

### 6.5 Use deterministic logic for deterministic work

Do not use an LLM where ordinary code is sufficient.

Typical deterministic activities include:

- filtering;
- sorting;
- joining;
- deduplication;
- schema validation;
- threshold comparison;
- aggregation;
- routing from approved classifications;
- version checking;
- completeness checks.

> **Use agents for judgement; use code for plumbing.**

### 6.6 Parallelise genuinely independent work

Independent activities should be allowed to run in parallel where this improves performance without weakening control.

```text
                  Identified Risks
                       |
        ---------------------------------
        |               |               |
        v               v               v
   Grounding        Robustness        Security
    Analysis          Analysis         Analysis
        |               |               |
        ---------------------------------
                       |
                       v
               Risk Consolidation
```

Do not parallelise simply because the framework supports concurrency.

### 6.7 Synchronise only when required

Use fan-in barriers only where downstream work genuinely requires the complete upstream result set.

```text
Grounding Evaluation ----\
Robustness Evaluation -----\
Safety Evaluation ----------> Evidence Sufficiency Assessment
Security Evaluation --------/
```

If downstream work can proceed with partial results, do not unnecessarily block the graph.

### 6.8 Route explicitly

Material routes should be defined and controlled.

Preferred pattern:

```text
Agent judgement
      |
      v
Structured classification
      |
      v
Deterministic router
      |
      +--> Route A
      +--> Route B
      +--> Human Escalation
```

Avoid giving the model unrestricted authority to invent arbitrary routes for material MRO processes.

### 6.9 Verify before material propagation

Material outputs should be verified before they influence a final conclusion.

Possible verification mechanisms include:

- schema validation;
- evidence-reference checks;
- deterministic reconciliation;
- challenge agents;
- cross-checking;
- human review.

Verification should be proportionate to materiality.

### 6.10 Contain failures

A failure in one branch should not unnecessarily destroy the whole graph.

Successful work should be preserved where possible.

Examples:

- one failed evaluation should not erase all successful evaluations;
- a temporary tool timeout should use a technical retry policy;
- missing evidence should route to an evidence-gap path;
- unresolved ambiguity should route to human review.

### 6.11 Human accountability must be explicit

For material MRO processes, the graph should clearly identify:

- where human judgement is required;
- what the human is approving;
- what information is presented;
- what happens if the human rejects or edits the proposal;
- where the final accountable decision sits.

Agents may support, analyse, recommend, and draft. Material MRO conclusions should remain subject to appropriate human accountability.

### 6.12 Dynamic behaviour must be bounded

Dynamic planning may be useful, but MRO agents should operate within an approved graph envelope.

Prefer:

```text
Approved parent graph
      |
      v
Agent selects permitted subgraph
      |
      v
Policy / HITL gate
      |
      v
Approved execution
```

Avoid:

```text
Goal
 |
 v
LLM invents arbitrary graph
 |
 v
Executes arbitrary actions
```

Dynamic behaviour should be constrained by:

- approved node types;
- approved subgraphs;
- approved tools;
- maximum depth;
- maximum iterations;
- permission boundaries;
- budget;
- human gates;
- evidence requirements.

---

## 7. Graph Engineering Design Process

### Step 1 — Define the Agent Objective

Before drawing the graph, define:

- agent name;
- business/process owner;
- technical owner;
- purpose;
- users;
- supported decision;
- excluded decisions;
- human accountability;
- intended operating environment.

### Step 2 — Define the Authoritative State

Do not start with prompts.

Define the state model first.

```text
ValidationProjectState

project
model
model_understanding
identified_risks
validation_plan
scenarios
evaluation_plans
model_runs
evaluation_runs
results
evidence
testing_gaps
findings
human_decisions
report
exceptions
```

For each state object define:

| Field | Description |
|---|---|
| Name | Name of the state object |
| Purpose | What it represents |
| Schema | Structured representation |
| Created by | Node responsible for creation |
| Updated by | Nodes permitted to change it |
| Consumers | Downstream users/nodes |
| Persistence | temporary / session / project |
| Versioned | yes / no |
| Evidence relevance | yes / no |

> **Chat history is not the authoritative state for material MRO processes.**

### Step 3 — Decompose the Process into Nodes

Break the process into bounded jobs.

Each node should have:

- one clear responsibility;
- clear inputs;
- clear outputs;
- explicit node type `[A] [D] [T] [H]`;
- known failure paths;
- known evidence requirements.

### Step 4 — Define Node Contracts

A detailed Node Contract is mandatory for each material node.

See Section 18.

### Step 5 — Define Edges as Data Dependencies

For each edge document:

- source node;
- destination node;
- object passed;
- required/optional dependency;
- routing condition if applicable;
- failure behaviour.

### Step 6 — Identify Parallelism

Identify:

- fan-out points;
- parallel branches;
- concurrency limits;
- partial-failure tolerance;
- fan-in points;
- synchronization requirements.

### Step 7 — Define Routing

For each routing decision define:

- condition;
- source of judgement;
- permitted routes;
- deterministic vs agentic decision;
- human gate if required;
- default route;
- unsupported/unknown route.

### Step 8 — Define Verification Gates

For material outputs define:

- evidence checks;
- schema checks;
- deterministic checks;
- independent challenge;
- human review;
- reconciliation rules.

### Step 9 — Define Failure and Recovery

For every material node define:

- expected failure modes;
- retry policy;
- fallback;
- branch isolation;
- escalation;
- state preservation;
- evidence of failure.

### Step 10 — Engineer Loops

Loop Engineering is defined in Part 2 below and is mandatory for every graph containing cycles or iterative reasoning.

### Step 11 — Review Graph Topology

Review:

- unnecessary serial dependencies;
- opportunities for parallelism;
- excessive barriers;
- repeated large-context transfer;
- expensive model nodes;
- redundant LLM calls;
- long critical paths;
- failure amplification.

### Step 12 — Perform Governance Review

Before implementation, confirm:

- human accountability;
- allowed tools;
- prohibited actions;
- model restrictions;
- state ownership;
- evidence retention;
- auditability;
- escalation;
- versioning.

### Step 13 — Implement in the Approved Framework

Only after the engineering design is sufficiently complete should the graph be implemented in:

- LangGraph;
- Google ADK;
- Envoy-supported framework;
- another approved orchestration framework.

---

## 8. Recommended MRO Node Types

### `[A]` Agent / LLM Node

Use for interpretation, synthesis, complex reasoning, qualitative analysis, draft generation, and evidence-based recommendation.

Avoid for deterministic transformation, simple thresholds, exact arithmetic, and schema validation.

### `[D]` Deterministic Node

Use for data transformation, thresholds, schema validation, routing, aggregation, deduplication, consistency checks, and completeness checks.

### `[T]` Tool / Service Node

Use where execution belongs to a controlled external capability, for example:

- Evaluation Engine;
- Model Runner;
- retrieval service;
- policy search;
- evidence store;
- database;
- API;
- MCP tool.

### `[H]` Human Node

Use where judgement, accountability, or approval must remain with an authorised person, for example:

- approve validation plan;
- approve material change to testing scope;
- challenge finding;
- resolve conflicting evidence;
- approve final validation conclusion.

---

## 9. Graph Review Checklist

Before implementation, reviewers should be able to answer **Yes** to the following.

### State

- Is authoritative state explicitly defined?
- Is state separate from chat history?
- Are state writers and readers defined?
- Is state persistence defined?
- Are material state objects versioned?

### Nodes

- Does each node have one bounded responsibility?
- Is each node classified as `[A]`, `[D]`, `[T]`, or `[H]`?
- Does each material node have a structured contract?
- Are allowed and prohibited actions clear?

### Edges

- Does every edge represent a real dependency?
- Is the data crossing the edge explicit?
- Are unnecessary serial dependencies removed?

### Routing

- Are material routes explicitly defined?
- Is deterministic routing used where possible?
- Can the agent bypass required human review?
- Is unsupported/uncertain routing handled?

### Parallelism

- Are independent activities parallelised where appropriate?
- Are barriers used only where required?
- Is partial failure handled?

### Verification

- Are material outputs verified?
- Are evidence references checked?
- Are material conclusions subject to appropriate human challenge?

### Failure

- Are expected failure modes defined?
- Are successful branches preserved?
- Are retries separated from business loops?
- Are escalation paths defined?

### Governance

- Are tool permissions defined?
- Are model choices controlled?
- Are evidence requirements clear?
- Is the graph versioned?
- Is execution reproducible?

---

# Part 2 — Loop Engineering

> **Part 2 is physically included within the Graph Engineering Standard because loops are graph structures. It is separated conceptually because iterative agent behaviour requires additional controls.**

## 10. Objective of Loop Engineering

Loop Engineering defines how an agent may revisit earlier work based on new evidence or unresolved objectives.

Every loop must answer:

- why iteration is necessary;
- what changes between iterations;
- what the loop is trying to achieve;
- what actions are allowed;
- how many iterations are permitted;
- when the loop succeeds;
- when the loop stops;
- when a human must intervene.

---

## 11. Core Loop Engineering Principles

### 11.1 No loop without an objective

Every loop must have a specific purpose.

Examples:

- resolve an evidence gap;
- improve scenario coverage;
- investigate inconsistent results;
- complete an incomplete evaluation;
- reconcile conflicting evidence.

### 11.2 Every iteration should change state or evidence

A valid loop should create new information.

Poor loop:

```text
Retry analysis
      |
      v
Retry same analysis
      |
      v
Retry same analysis
```

Preferred:

```text
Evidence gap identified
      |
      v
Propose additional test
      |
      v
Execute test
      |
      v
Add new evidence to state
      |
      v
Reassess evidence sufficiency
```

> **If the state or evidence does not materially change, the loop should normally not continue.**

### 11.3 Technical retries are not business loops

Separate technical retries such as timeout, transient API error, rate limit, or temporary service failure from methodology/reasoning loops such as insufficient evidence, incomplete scenario coverage, or conflicting validation evidence.

### 11.4 Loops must be bounded

Each loop must define:

- maximum iterations;
- timeout;
- cost/token/tool-call budget where applicable;
- maximum depth;
- escalation rules.

Unbounded autonomous loops are not acceptable for material MRO agents.

### 11.5 Loops must converge

Every loop requires objective convergence criteria.

Examples:

- all material risks have sufficient evidence;
- scenario coverage reaches approved criteria;
- contradictory evidence is resolved;
- required evaluations complete successfully;
- human reviewer accepts the revised plan.

### 11.6 Escalation is part of loop design

A loop should not simply terminate when it fails. It should define what happens next, for example:

- human review;
- manual investigation;
- unsupported-case handling;
- methodology owner review;
- process termination with documented exception.

---

## 12. Loop Policy Template

Every material loop should have a documented Loop Policy.

### Loop Name

`Evidence Sufficiency Loop`

### Purpose

Resolve material evidence gaps before findings are finalised.

### Trigger

```text
EvidenceAssessment.status == "INSUFFICIENT"
```

### Objective

Obtain sufficient evidence to support or challenge the material validation conclusion.

### State Read

```text
identified_risks
evaluation_results
evidence
testing_gaps
```

### State Updated

```text
evaluation_plans
evaluation_results
evidence
testing_gaps
human_decisions
```

### Allowed Activities

```text
inspect existing results
retrieve additional evidence
propose additional scenarios
propose additional evaluations
execute approved tests
reassess evidence sufficiency
```

### Prohibited Activities

```text
change validation methodology
modify the model under test
approve the final validation conclusion
bypass required human review
```

### State Change Required per Iteration

```text
new_evidence_count > 0
OR
testing_gap_status changes
OR
human_decision recorded
```

### Maximum Autonomous Iterations

Example: `2`

### Maximum Tool Calls

Defined by use case.

### Time / Cost Budget

Defined by use case.

### Success Condition

```text
all material validation questions have sufficient supporting evidence
```

### Stop Condition

```text
objective achieved
```

### Escalation Condition

```text
maximum iterations reached
material uncertainty remains
approved test unavailable
contradictory evidence persists
tooling cannot complete required test
```

### Human Gate

Define whether approval is required before:

- a materially new test category;
- expansion of validation scope;
- materially higher-cost execution;
- conclusion-changing action.

### Evidence Retained per Iteration

- loop iteration number;
- state before;
- action taken;
- tool calls;
- evidence added;
- state after;
- reason for continuation;
- reason for stop or escalation.

---

## 13. Loop Review Checklist

Before a loop is approved, confirm:

- Is the objective explicit?
- Is the trigger explicit?
- Does every iteration create new state or evidence?
- Are allowed actions defined?
- Are prohibited actions defined?
- Is maximum iteration count defined?
- Is time/cost/tool-call budget defined where relevant?
- Is the success condition objective?
- Is the stop condition explicit?
- Is the escalation path explicit?
- Are human gates defined?
- Is evidence retained for every iteration?
- Is the loop distinguishable from a technical retry?

---

# Part 3 — Harness Engineering

> **Part 3 is intentionally provisional. MRO should complete the full Harness Engineering Standard after understanding Envoy capabilities, boundaries, and operating model. MRO should reuse enterprise harness capabilities wherever possible rather than rebuild them.**

## 14. Objective of Harness Engineering

Harness Engineering defines the controlled operating environment in which an MRO agent executes.

The harness should answer:

> **What can the agent access, what can it do, under what permissions, with what state, using what models and tools, and with what runtime, evidence, recovery, and approval controls?**

---

## 15. Harness Engineering Principle

The target approach is:

> **Envoy provides generic agent mechanics and runtime capabilities wherever available; MRO defines how those capabilities are used for MRO processes.**

MRO should avoid rebuilding generic enterprise capabilities where Envoy or another approved platform already provides them.

MRO should retain ownership of:

- MRO-specific agent behaviour;
- MRO graph design;
- MRO loop policies;
- MRO tool permissions;
- MRO human-control requirements;
- MRO evidence requirements;
- MRO structured state/schema definitions;
- MRO validation/oversight methodology;
- MRO conformance tests.

---

## 16. Provisional Harness Design Domains

The final Harness Standard should cover at least the following domains.

### 16.1 Planning and Context

Define:

- system instructions;
- task instructions;
- context sources;
- context limits;
- approved knowledge sources;
- grounding requirements;
- prompt/configuration versioning.

### 16.2 Model / LLM Interface

Define:

- approved models;
- model profiles;
- model selection rules;
- model parameters;
- fallback models;
- data restrictions;
- model versioning;
- reproducibility requirements.

### 16.3 Memory, State, and Checkpoints

Define:

- short-term state;
- project state;
- session state;
- checkpointing;
- resume behaviour;
- long-term memory;
- retention;
- memory write permissions;
- memory read permissions.

### 16.4 Files and Workspace

Define:

- permitted files;
- upload rules;
- read/write permissions;
- temporary workspace;
- code execution;
- artefact storage;
- data classification restrictions.

### 16.5 Tools and APIs

Define:

- approved tool catalogue;
- API/MCP patterns;
- tool schemas;
- authentication;
- read/write permissions;
- tool versioning;
- tool timeout;
- tool retry;
- high-risk action controls.

### 16.6 Sub-agents and Skills

Define:

- approved sub-agents;
- delegated responsibilities;
- allowed hand-offs;
- hierarchy;
- termination;
- evidence passed between agents;
- skill versioning.

### 16.7 Permissions, Policy, and Human Approval

Define:

- user identity;
- agent identity;
- service identity;
- roles;
- least privilege;
- approval roles;
- approval timeout;
- reject/edit/resume behaviour;
- prohibited actions.

### 16.8 Runtime, Recovery, and Long-Running Tasks

Define:

- runtime environment;
- timeout;
- technical retry;
- fallback;
- pause/resume;
- recovery;
- long-running jobs;
- asynchronous execution;
- failure-state handling.

### 16.9 Trace, Evidence, and Evaluation

Define:

- trace requirements;
- audit record;
- model calls;
- tool calls;
- graph route;
- loop iterations;
- human decisions;
- evidence lineage;
- test/evaluation results;
- retention.

### 16.10 Deployment and Operations

Define:

- local development;
- integration environment;
- Envoy onboarding;
- Golden Path;
- CI/CD;
- security gates;
- release version;
- rollback;
- support;
- monitoring;
- incident management;
- ownership.

---

## 17. Envoy Capability Assessment Before Finalising Harness Standard

Before MRO finalises Part 3, the team should create an **Envoy Harness Capability Matrix**.

| Harness capability | MRO requirement | Envoy capability | MRO responsibility | Gap / action |
|---|---|---|---|---|
| Agent runtime | managed runtime | TBD | use/configure | assess |
| Sessions | persistent session | TBD | define state | assess |
| Checkpoints | pause/resume | TBD | define checkpoint policy | assess |
| Memory | controlled memory | TBD | define allowed memory | assess |
| Tool integration | API/MCP | partial/known | define tools/permissions | assess |
| Human approval | HITL | TBD | define approval policy | assess |
| Audit | trace/audit | TBD | define evidence schema | assess |
| Observability | tracing/metrics | TBD | define MRO monitoring | assess |
| CI/CD | Golden Path | known | own tests/releases | confirm |
| Deployment | Envoy runtime | known in principle | own release | confirm |
| Identity | enterprise identity | TBD | define MRO roles | assess |
| UI interaction | external UI | limited | define MRO UI needs | assess |

The Harness Standard should then be based on:

```text
MRO requirement
      |
      +--> Reuse Envoy capability
      |
      +--> Configure Envoy capability
      |
      +--> Extend with MRO-specific control
      |
      +--> Build only where a genuine gap remains
```

---

# Part 4 — Mandatory Engineering Artefacts for Every MRO Agent

## 18. Core Artefact Set

Every material MRO agent should have the following engineering artefacts.

### Artefact 1 — Agent Charter

**Purpose:** Defines why the agent exists and where accountability sits.

Required fields:

```text
Agent name
Business/process owner
Technical owner
Purpose
Users
In-scope activities
Out-of-scope activities
Decisions supported
Decisions prohibited
Human accountable role
Critical dependencies
Intended deployment environment
```

### Artefact 2 — State Model

**Purpose:** Defines the authoritative structured state used by the agent.

Required content:

- state objects;
- schemas;
- writers;
- readers;
- persistence;
- versioning;
- evidence relevance;
- retention.

```text
ValidationProjectState
├── Model
├── IdentifiedRisks
├── ValidationPlan
├── Scenarios
├── EvaluationPlans
├── Runs
├── Results
├── Evidence
├── Findings
└── HumanDecisions
```

### Artefact 3 — Graph Specification

**Purpose:** Defines how the process progresses.

Required content:

- graph diagram;
- node types `[A] [D] [T] [H]`;
- edges;
- routing;
- subgraphs;
- fan-out;
- fan-in;
- human gates;
- failure routes;
- completion conditions.

### Artefact 4 — Node Contracts

**Purpose:** Defines every material work unit in the graph.

#### Standard Node Contract Template

**Node ID:**  
**Node Name:**  
**Node Type:** `[A] / [D] / [T] / [H]`  
**Purpose:**  
**Owner:**  

**Inputs**

```text
...
```

**Outputs**

```text
...
```

**Input schema:**  
**Output schema:**  
**State read:**  
**State updated:**  
**Allowed tools:**  
**Prohibited actions:**  
**Human approval required:** `Yes / No`  
**Routing outputs:**  
**Failure modes:**  
**Retry policy:**  
**Failure route:**  
**Evidence recorded:**  
**Acceptance criteria:**  
**Version:**  

### Artefact 5 — Edge and Routing Register

**Purpose:** Makes dependencies and routing explicit.

| From | To | Data contract | Condition | Decision source | Human gate |
|---|---|---|---|---|---|

No material edge should remain undocumented.

### Artefact 6 — Loop Policies

**Purpose:** Defines controlled iterative behaviour.

Each loop must document:

- trigger;
- objective;
- state read;
- state updated;
- allowed actions;
- prohibited actions;
- required state change;
- maximum iterations;
- budget;
- success;
- stop;
- escalation;
- human gate;
- evidence per iteration.

### Artefact 7 — Harness Profile

**Purpose:** Defines how the generic enterprise harness is configured for this specific MRO agent.

Until the final Harness Standard is complete, every agent should still have a provisional Harness Profile.

Required sections:

```text
Approved models
Allowed tools
Tool permissions
State/checkpoint policy
Memory policy
Files/workspace policy
Human approval policy
Evidence/audit requirements
Runtime requirements
Retry/recovery policy
Deployment profile
Observability requirements
```

---

## 19. Additional Recommended Artefacts

The following should be mandatory where relevant.

### Artefact 8 — Tool and Permission Register

Use where the agent accesses multiple tools, systems, or APIs.

| Tool | Purpose | Read/Write | Authentication | Data accessed | Approval required | Owner |
|---|---|---|---|---|---|---|

### Artefact 9 — Evidence and Audit Profile

Use for material MRO processes.

Define what must be retained:

```text
agent version
graph version
node version
loop policy version
model name/version
prompt/configuration version
tool version
input references
output references
routing decisions
human decisions
errors
technical retries
loop iterations
timestamps
evidence lineage
```

### Artefact 10 — Test and Conformance Plan

Define how the agent will be tested.

Minimum areas:

- node-level tests;
- schema tests;
- deterministic routing tests;
- loop boundary tests;
- tool failure tests;
- HITL tests;
- adversarial tests where relevant;
- regression tests;
- evidence/audit tests;
- end-to-end scenario tests;
- framework/platform conformance tests.

### Artefact 11 — Failure and Recovery Matrix

| Failure | Detection | Retry | Fallback | Escalation | State preserved | Evidence |
|---|---|---|---|---|---|---|

### Artefact 12 — Release and Deployment Profile

Define:

- development environment;
- target runtime;
- framework;
- dependencies;
- release version;
- CI/CD route;
- approval gates;
- rollback;
- support owner;
- production monitoring.

### Artefact 13 — Risk and Exception Register

Use where there are known engineering or control limitations.

Examples:

- unsupported tool;
- unsupported model;
- incomplete Envoy feature;
- temporary local execution;
- unresolved hosting dependency;
- manual workaround;
- accepted exception.

---

## 20. Minimum Artefact Set by Agent Stage

### Prototype

Minimum:

1. Agent Charter
2. State Model
3. Graph Specification
4. Node Contracts for material nodes
5. Loop Policies
6. Provisional Harness Profile

### Controlled Pilot

Add:

7. Edge and Routing Register
8. Tool and Permission Register
9. Evidence and Audit Profile
10. Test and Conformance Plan
11. Failure and Recovery Matrix

### Production / BAU

Add:

12. Release and Deployment Profile
13. Risk and Exception Register
14. Operational monitoring/support documentation
15. Approved version baseline

---

# Part 5 — Standard MRO Agent Design Workflow

## 21. Recommended Engineering Sequence

```text
1. Understand the MRO process
        |
        v
2. Define Agent Charter
        |
        v
3. Define authoritative State Model
        |
        v
4. Decompose process into bounded Nodes
        |
        v
5. Classify [A] [D] [T] [H]
        |
        v
6. Define Node Contracts
        |
        v
7. Define real dependency Edges
        |
        v
8. Identify fan-out / fan-in
        |
        v
9. Define Routing
        |
        v
10. Define Human Gates
        |
        v
11. Add Verification Gates
        |
        v
12. Define Loop Policies
        |
        v
13. Define Failure and Recovery
        |
        v
14. Define provisional Harness Profile
        |
        v
15. Review State / Evidence / Permissions
        |
        v
16. Review topology / cost / latency
        |
        v
17. Review governance / accountability
        |
        v
18. Implement in LangGraph / ADK / Envoy
        |
        v
19. Test and run conformance suite
        |
        v
20. Controlled release
```

---

# Part 6 — Example: Independent Validation Agent

## 22. Illustrative Graph

```text
START
  |
  v
[A] Model Understanding
  |
  v
[A] Risk Identification
  |
  v
[A] Validation Planning
  |
  v
[H] Validator Plan Approval
  |
  v
[A] Scenario Design
  |
  v
[A] Evaluation Planning
  |
  v
[T] Model Execution
  |
  v
[T] Evaluation Execution
  |
  v
[D] Metric Calculation
  |
  v
[A] Results Analysis
  |
  v
[D/A] Evidence Sufficiency Assessment
  |
  +--> Sufficient
  |       |
  |       v
  |   [A] Findings Draft
  |
  +--> Evidence Gap
  |       |
  |       v
  |   [A] Additional Testing Proposal
  |       |
  |       v
  |   [H] Approval if material
  |       |
  |       v
  |   [T] Additional Testing
  |       |
  |       +----------------------+
  |                              |
  +------------------------------+
  |
  +--> Material Uncertainty
          |
          v
      [H] Human Escalation

[A] Findings Draft
  |
  v
[A] Report Draft
  |
  v
[H] Final Validator Review
  |
  v
END
```

---

## 23. Illustrative Agent Artefact Structure

```text
Independent Validation Agent
|
+-- Agent Charter
|
+-- State Model
|   +-- Model
|   +-- Risks
|   +-- Validation Plan
|   +-- Scenarios
|   +-- Evaluation Plans
|   +-- Runs
|   +-- Results
|   +-- Evidence
|   +-- Findings
|   +-- Human Decisions
|
+-- Graph Specification
|   +-- Parent Graph
|   +-- Risk Assessment Subgraph
|   +-- Evaluation Subgraph
|   +-- Evidence Assessment Subgraph
|
+-- Node Contracts
|
+-- Edge and Routing Register
|
+-- Loop Policies
|   +-- Evidence Sufficiency Loop
|   +-- Testing Gap Loop
|   +-- Execution Recovery Loop
|
+-- Harness Profile
|   +-- Approved Models
|   +-- Allowed Tools
|   +-- Permissions
|   +-- HITL Policy
|   +-- State / Checkpoints
|   +-- Evidence Requirements
|   +-- Runtime Profile
|
+-- Tool and Permission Register
|
+-- Evidence and Audit Profile
|
+-- Test and Conformance Plan
|
+-- Failure and Recovery Matrix
|
+-- Release and Deployment Profile
|
+-- Risk and Exception Register
```

---

# Part 7 — Engineering Review Gates

## 24. Design Gate

Before implementation:

- Agent Charter approved.
- State Model defined.
- Graph Specification reviewed.
- Material Node Contracts complete.
- Loop Policies complete.
- Human accountability explicit.
- Provisional Harness Profile documented.

## 25. Build Gate

Before controlled integration:

- node schemas implemented;
- deterministic routing tested;
- tools integrated through approved interfaces;
- loop limits enforced;
- failure routes implemented;
- evidence capture implemented;
- human approval paths implemented.

## 26. Pilot Gate

Before controlled user pilot:

- end-to-end tests passed;
- tool failure tests passed;
- HITL tests passed;
- loop boundary tests passed;
- evidence/audit review passed;
- known limitations documented;
- risk/exception register reviewed.

## 27. Production / BAU Gate

Before production use:

- deployment route approved;
- CI/CD controls complete;
- runtime and support ownership clear;
- monitoring defined;
- release version controlled;
- rollback defined;
- conformance suite passed;
- material exceptions approved;
- operating documentation complete.

---

# Part 8 — Framework Mapping

## 28. LangGraph Mapping

| MRO design concept | LangGraph implementation |
|---|---|
| State Model | State schema / typed state |
| Node | graph node |
| Edge | `add_edge()` |
| Conditional route | conditional edges / `Command(goto=...)` |
| Human gate | `interrupt()` + checkpoint + resume |
| Loop | conditional edge back to prior node |
| Technical retry | retry policy |
| Subgraph | nested graph |
| Checkpoint | checkpointer |
| Persistent memory | store / external persistence |
| Tool | tool node / callable integration |

LangGraph is an implementation framework. It does not replace the MRO engineering standard.

## 29. Google ADK / Envoy Mapping

The detailed mapping should be completed after the Envoy capability assessment.

At minimum the team should map:

```text
MRO Graph requirement
MRO Loop requirement
MRO State requirement
MRO Harness requirement
        |
        v
Google ADK / Envoy primitive or service
        |
        v
Gap / extension / MRO control
```

---

# Part 9 — Ownership Model

## 30. MRO vs Enterprise Platform Responsibilities

### MRO should own

- MRO agent purpose;
- MRO graph design;
- MRO state model;
- MRO loop policies;
- MRO validation/oversight logic;
- MRO tool permissions;
- MRO evidence requirements;
- MRO human-control requirements;
- MRO testing/conformance;
- MRO release decisions.

### Enterprise platform should provide where available

- agent runtime;
- generic session infrastructure;
- identity integration;
- generic memory;
- generic tool connectivity;
- CI/CD;
- Golden Path;
- deployment runtime;
- security controls;
- observability platform;
- generic audit infrastructure.

> **Enterprise platforms provide generic mechanics. MRO defines how those mechanics are used for MRO processes.**

---

# Part 10 — Final Design Principles

## 31. Required Team Principles

1. **State before prompts.**
2. **Graph before framework.**
3. **One bounded responsibility per material node.**
4. **Every material node has a contract.**
5. **Every material edge represents a real dependency.**
6. **Use deterministic logic for deterministic work.**
7. **Use agents for judgement, not plumbing.**
8. **Parallelise only genuine independence.**
9. **Material routes are explicit and controlled.**
10. **Human accountability is designed into the graph.**
11. **No loop without an objective.**
12. **No loop without state change.**
13. **No loop without convergence, limits, and escalation.**
14. **Technical retries are separate from reasoning loops.**
15. **Dynamic autonomy is bounded by approved graph, tools, and permissions.**
16. **Evidence and audit are designed in, not added later.**
17. **Harness capabilities should be reused from Envoy wherever possible.**
18. **MRO owns the MRO-specific engineering layer.**
19. **Local development should remain service-ready and deployment-ready.**
20. **The framework may change; the engineering standard should remain.**

---

# Appendix A — Quick Design Template

## Agent

**Name:**  
**Purpose:**  
**Business owner:**  
**Technical owner:**  
**Human accountable role:**  

## State

```text
...
```

## Graph

```text
...
```

## Nodes

| ID | Name | Type | Purpose | Input | Output |
|---|---|---|---|---|---|

## Routing

| From | Condition | To | Decision type |
|---|---|---|---|

## Loops

| Loop | Trigger | Objective | State change | Max iterations | Stop | Escalation |
|---|---|---|---|---:|---|---|

## Human Gates

| Gate | Decision | Role | Resume behaviour |
|---|---|---|---|

## Harness Profile

```text
Models:
Tools:
Permissions:
State/checkpoint:
Memory:
Files/workspace:
HITL:
Evidence:
Runtime:
Deployment:
```

## Test Plan

```text
Node tests:
Routing tests:
Loop tests:
Tool tests:
HITL tests:
Failure tests:
Evidence tests:
End-to-end tests:
```

---

# Appendix B — One-Page Review Checklist

### Agent definition
- [ ] Purpose and scope clear
- [ ] Human accountability clear
- [ ] Out-of-scope decisions defined

### State
- [ ] Authoritative state defined
- [ ] State separate from chat history
- [ ] Writers/readers controlled
- [ ] Persistence/versioning defined

### Graph
- [ ] Nodes bounded
- [ ] Nodes classified `[A][D][T][H]`
- [ ] Node Contracts complete
- [ ] Edges represent real dependencies
- [ ] Routing explicit
- [ ] Parallelism reviewed
- [ ] Human gates explicit
- [ ] Failure paths explicit

### Loops
- [ ] Trigger defined
- [ ] Objective defined
- [ ] State change required
- [ ] Max iterations defined
- [ ] Budget defined where relevant
- [ ] Stop condition defined
- [ ] Escalation defined
- [ ] Evidence retained

### Harness
- [ ] Models controlled
- [ ] Tools controlled
- [ ] Permissions defined
- [ ] Checkpoint/state policy defined
- [ ] Human approval mechanics defined
- [ ] Evidence/audit requirements defined
- [ ] Runtime/deployment profile defined

### Testing
- [ ] Node tests
- [ ] Routing tests
- [ ] Loop boundary tests
- [ ] Tool failure tests
- [ ] HITL tests
- [ ] Regression tests
- [ ] Evidence/audit tests
- [ ] End-to-end tests

---

**End of Standard**
