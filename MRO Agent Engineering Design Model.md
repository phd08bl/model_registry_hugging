# MRO Agent Engineering Design Model

## Harness, Graph and Loop

### 1. Purpose

For MRO, an AI agent should not be designed simply as **LLM + prompt + tools**. A production-ready agent needs a controlled operating environment, an explicit process structure, and bounded rules for iteration and stopping.

A useful engineering model is to assess every MRO agent through three complementary views:

> **Harness — Can the agent work safely and reliably?**
> **Graph — Can we control where the process goes?**
> **Loop — Can we determine when the agent should continue, retry, stop or escalate?**

These are best treated as **three engineering views of the same agent system**, rather than three completely separate technology layers.

Conceptually:

```text
                    HARNESS
      Controlled operating environment
       ┌──────────────────────────────┐
       │                              │
       │            GRAPH             │
       │    Controlled process path   │
       │   ┌──────────────────────┐   │
       │   │                      │   │
       │   │        LOOPS         │   │
       │   │ Evidence-driven      │   │
       │   │ iteration / stopping │   │
       │   │                      │   │
       │   └──────────────────────┘   │
       │                              │
       └──────────────────────────────┘
```

In practice, the boundaries can overlap. For example, checkpoints may be provided by the harness but used by the graph; retries may be runtime features but governed by loop policies. The objective is not to argue about terminology, but to ensure that **all three engineering questions have been explicitly designed**.

---

# 2. Harness Engineering — Give the Agent a Controlled Working Environment

A model by itself can generate text. A harness turns the model into an agent that can operate within a controlled system.

| Harness area          | What it provides                                                       |
| --------------------- | ---------------------------------------------------------------------- |
| Context               | Instructions, task context, retrieved evidence and applicable policies |
| Tools and APIs        | Controlled interfaces to systems, data and actions                     |
| State and checkpoints | Ability to maintain progress and resume safely                         |
| Workspace             | Controlled files, artefacts and working data                           |
| Permissions           | Least-privilege access and action restrictions                         |
| Human approval        | Mechanisms to pause for review or authorisation                        |
| Runtime controls      | Timeouts, retries, resource limits and fallback                        |
| Evidence and logging  | Trace of model, tool and human actions                                 |
| Observability         | Ability to inspect, replay and diagnose execution                      |
| Evaluation            | Ability to assess whether the agent is behaving correctly              |

The key Harness question is:

> **What is the agent allowed to know and do, under what controls, and how can its actions be evidenced and recovered?**

Without good harness engineering, typical failures include losing state, calling the wrong tools, excessive permissions, inconsistent context, inability to resume a process, and poor auditability.

For MRO, the generic mechanics should ideally come from the enterprise platform such as **Envoy**, while MRO defines its specific control profiles, permissions, evidence requirements and human approval rules.

---

# 3. Graph Engineering — Make the Process Explicit and Controllable

Graph engineering defines **how work progresses through the process**.

A graph normally contains:

```text
Nodes
= units of work

Edges
= permitted transitions

State
= shared structured information

Routing conditions
= rules determining what happens next

Checkpoints
= controlled points for persistence/recovery
```

A node does not have to be an LLM.

For MRO, nodes may be:

```text
[D] Deterministic code
[A] Agent / LLM reasoning
[T] Tool or platform service
[H] Human review / decision
```

For example:

```text
[D] Validate inputs
        ↓
[A] Understand model
        ↓
[A] Propose testing approach
        ↓
[H] Validator review
        ↓
[T] Execute evaluation
        ↓
[D] Calculate metrics
        ↓
[A] Interpret evidence
        ↓
[H] Final judgement
```

This is particularly important for MRO because **not every decision should be delegated to an LLM**.

The key Graph question is:

> **What stages exist, which component is responsible for each stage, what routes are allowed, and where must human control exist?**

Graph engineering becomes especially valuable when there are:

* branches;
* parallel activities;
* multiple agents;
* human approval;
* shared state;
* recovery paths;
* complex dependencies.

For example, Independent Validation is naturally graph-like because:

```text
Scenario
    ↓
Evaluation Plan
    ↓
Evaluation Run
    ↓
Results
    ↓
Evidence Assessment
    ↓
Insufficient evidence?
       ↓ Yes
Additional Scenario / Evaluation
       ↓
      ↺
```

The validation path therefore cannot always be represented effectively as a simple fixed sequence.

---

# 4. Loop Engineering — Make Iteration Evidence-Driven and Bounded

Agents often need to repeat work. The engineering challenge is not simply enabling repetition; it is controlling **why the agent repeats, what evidence it uses, and when repetition must stop**.

A robust loop generally contains:

```text
Trigger / Goal
      ↓
Action
      ↓
Tool / execution
      ↓
Evidence / result
      ↓
Assessment
      ↓
Continue / Retry / Stop / Escalate
```

The key Loop question is:

> **Based on the evidence produced, should the system continue, retry, stop or escalate?**

A well-engineered loop should define:

| Loop control         | Example                                     |
| -------------------- | ------------------------------------------- |
| Trigger              | Evidence is incomplete                      |
| Objective            | Resolve a defined validation question       |
| Permitted actions    | Retrieve evidence or propose another test   |
| Success criteria     | Required evidence threshold satisfied       |
| Maximum iterations   | e.g. two additional attempts                |
| Time/resource budget | Prevent unlimited execution                 |
| Failure condition    | Approved tools cannot resolve the issue     |
| Escalation           | Route to validator                          |
| Human checkpoint     | Approval before material additional testing |

The critical principle is:

> **A loop must be bounded by evidence and stopping rules.**

“Keep trying until the model thinks it has succeeded” is not an adequate production control.

---

# 5. How the Three Work Together

A useful shorthand is:

> **Harness makes the agent able to work.**
> **Loop makes its behaviour evidence-driven.**
> **Graph makes the overall process controllable.**

For example:

```text
HARNESS
Provides:
tools / permissions / state / audit / HITL / context

                       ↓

GRAPH
Defines:
Plan → Test → Analyse → Review → Conclude

                       ↓

LOOPS
Operate where required:
insufficient evidence
    → additional testing
    → analyse results
    → reassess evidence
    → stop or escalate
```

The three are complementary rather than alternatives.

---

# 6. Conditions for an Agent to Move Beyond a Demo

Harness, Graph and Loop are important because many agent demos hide production engineering problems.

A credible MRO agent should demonstrate five conditions:

| Condition                           | Production question                                                             |
| ----------------------------------- | ------------------------------------------------------------------------------- |
| **Harness is ready**                | Can it safely access the right context, tools and permissions and retain state? |
| **Loop is bounded**                 | Are success, failure, retry, stopping and escalation rules explicit?            |
| **Graph is visible and controlled** | Can we see and control the permitted process paths and human checkpoints?       |
| **Evaluation is replayable**        | Can we replay traces, compare versions and detect behavioural regression?       |
| **Operations are supportable**      | Can we monitor versions, failures, costs, exceptions and human interventions?   |

This is an important qualification:

> **Harness + Graph + Loop provide a strong design foundation, but production readiness also requires evaluation and operational controls.**

---

# 7. Why This Model Is Particularly Suitable for MRO Agents

MRO agents frequently operate within validation, oversight, review, classification and governance processes. These processes require more control than an ordinary productivity chatbot.

The model naturally addresses core MRO requirements:

```text
MRO requirement                    Engineering response

Controlled access            →     Harness permissions
Policy enforcement           →     Harness control profile
Auditability                 →     Harness evidence / trace

Defined process              →     Graph
Human accountability         →     Human nodes / approval gates
Separation of duties         →     Node and permission boundaries

Evidence-based judgement     →     Loop
Additional testing           →     Controlled loop
Uncertainty                  →     Escalation rule
No endless autonomous action →     Stop / budget conditions
```

It also encourages an important MRO architecture principle:

> **Agents reason and orchestrate; controlled services execute authoritative operations; humans retain accountable decisions where required.**

For example:

```text
Agent recommends an evaluation
              ↓
Validator / policy gate
              ↓
Evaluation Engine executes
              ↓
Structured result
              ↓
Agent interprets evidence
              ↓
Validator challenges and concludes
```

This is considerably easier to govern than allowing an unconstrained agent to select, execute, interpret and approve its own work.

---

# 8. A Practical MRO Agent Design Test

For every proposed MRO agent, the design team should be able to answer three groups of questions.

### Harness — **Can it operate safely?**

What context can it see? What tools can it call? What permissions does it have? What state is retained? Where is human approval required? What evidence is captured? How are failures, recovery and monitoring handled?

### Graph — **Can we control the process?**

What are the nodes and stages? Which are deterministic, agentic, tool-based or human? What are the permitted transitions? Where are the branches, checkpoints and escalation routes? What structured state moves between nodes?

### Loop — **Can we control iteration?**

What triggers repetition? What evidence determines success? How many retries are allowed? What are the time/cost limits? What causes a stop? What causes escalation to a person?

If a design cannot answer these questions clearly, it is likely still closer to a **demo or prompt workflow** than a robust agent system.

If it can answer them explicitly, the design is much more likely to be:

> **implementable, testable, explainable, auditable, recoverable, policy-governable and maintainable.**

That does not prove that the agent will be good by itself — evaluation is still required — but it demonstrates that the **architecture is capable of being governed and operationalised properly**.

---

# 9. What MRO Should Reuse vs Own

For the long term, MRO should not attempt to rebuild generic agent infrastructure already provided by Envoy.

A sensible separation is:

| Enterprise / Envoy               | MRO AI Tech & Tooling            |
| -------------------------------- | -------------------------------- |
| Generic agent runtime            | MRO Harness control profiles     |
| Sessions / memory infrastructure | MRO state and context policies   |
| MCP / tool framework             | MRO tool permissions             |
| Generic HITL mechanism           | MRO approval requirements        |
| Graph/orchestration primitives   | MRO workflow graphs              |
| Retry/runtime functionality      | MRO loop and escalation policies |
| Audit/telemetry infrastructure   | MRO evidence standards           |
| Deployment/registry              | MRO agent release definitions    |
| Evaluation infrastructure        | MRO-specific conformance tests   |

The principle is:

> **Envoy provides the mechanics; MRO defines how those mechanics must be used for MRO processes.**

---

# 10. Build Reusable MRO Engineering Patterns

Harness, Graph and Loop should therefore become part of a reusable **MRO Agent Engineering Standard**, rather than being redesigned independently for every agent.

For example:

```text
MRO HARNESS PROFILES
- High-Control Assessment
- Read-Only Review
- Controlled Action
- Drafting

MRO GRAPH PATTERNS
- Governed Assessment
- Evidence Review
- Independent Validation
- Draft–Review–Approve
- Discovery / FDE

MRO LOOP PATTERNS
- Evidence Sufficiency
- Scenario Refinement
- Testing Gap
- Recovery / Retry
- Human Escalation
```

Each reusable pattern can package:

```text
state schema
+ node contracts
+ tool permissions
+ graph routes
+ loop policies
+ HITL requirements
+ evidence requirements
+ evaluation tests
```

This is much more valuable strategically than building another generic agent framework.

---

# 11. Recommended MRO Engineering Principle

The team can summarise the approach with one statement:

> **A well-designed MRO agent must have a controlled environment, an explicit process, and bounded evidence-driven behaviour. Harness, Graph and Loop engineering provide the three complementary design views needed to achieve this.**

Or more simply:

> **Harness controls what the agent can do.
> Graph controls where the process can go.
> Loop controls when the agent should continue or stop.**

For MRO, if these three elements are explicitly designed, versioned and tested — with appropriate evaluation and operational controls — the resulting agent is far more likely to move successfully from **demo to a governed, reusable and maintainable production capability**.
