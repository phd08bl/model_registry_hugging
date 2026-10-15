# MRO FDE Stage 3 Discovery — methodology v0.1

Discover the process before designing the solution. FDE leads; SMEs participate.
Stage 3 converts a leadership priority into an evidenced understanding of the real
process and actionable improvement opportunities. Ask: how does the selected process
actually work, where are the material problems, what evidence supports them, and which
opportunities are worth taking forward?

Stage 4 owns solution options, selection, architecture, PRD/technical design and
implementation approach. A small throwaway concept may test a specific discovery
hypothesis; label it as such and record its findings. It never replaces the Discovery
Visual or implies an approved solution.

## Before interviewing

Read and preserve available Stage 1/2 context: Candidate Brief, Process Problem,
Process Owner, Desired Outcome, Existing Capabilities / Potential Solutions, Leadership /
SLT Priority, Stage 2 Decision, Discovery Boundary, Initial Discovery Wave, Discovery
Question, existing evidence/documentation and known users/SMEs. Record missing context
as unknown; do not invent a Stage 2 decision.

Separate known facts, contradictions, gaps, and facts the FDE can investigate directly.
Inspect available artefacts, documentation, code, systems and capability research first.
Ask SMEs only high-value unresolved questions. Respect access restrictions; when access
is unavailable record the gap and who can resolve it instead of claiming inspection.

## Principles that control the interview

1. **P1 — Process before technology.** Understand what happens before proposing technology.
2. **P2 — Evidence before assumption.** Distinguish verified and partially verified evidence,
   SME statements, assumptions, hypotheses, FDE analysis/findings and open questions.
3. **P3 — Challenge whether technology is required.** Process or operating-model change
   may be sufficient; a new tool is not the default outcome.
4. **P4 — Existing capability first.** Investigate enterprise, platform, MRO and team
   capabilities before suggesting new development.
5. **P5 — Non-AI before AI.** Consider process change, operating-model change,
   guidance/templates, existing applications, workflow automation, low-code, analytics
   and conventional automation before AI/agents, where relevant.
6. **P6 — No premature solution design.** Only a small, explicitly labelled hypothesis
   test belongs here; detailed architecture belongs to Stage 4.
7. **P7 — Outcome over requested solution.** “We need an agent / Power App / automation”
   is a proposed solution. Ask what process outcome is failing and why it matters.
8. **P8 — FDE investigates independently.** Do not outsource available research to SMEs.
9. **P9 — Materiality matters.** Establish frequency, cost, risk, time or strategic
   importance sufficient to justify intervention.
10. **P10 — Baseline where useful.** Measure when practical and decision-relevant;
    distinguish measurements from estimates. Never manufacture numbers for a template.
11. **P11 — Surface constraints early.** Cover material policy, control, data, access,
    security, technology, ownership and operating-model constraints.
12. **P12 — Decision-sufficient, not exhaustive.** Stop when a sound Gate 3 / Stage 4
    decision is supported. Do not ask low-value questions for coverage alone.

## Five discovery lenses, not a fixed questionnaire

Choose the lens with the greatest material uncertainty, then its highest-value question.
Use dependency/frontier questioning with up to three independent questions per round.
The lenses are INTERNAL coverage areas, not a visible checklist. Each card asks one
material question, with a short reason, optional concise options and a grounded optional
suggestion. Keep trade-off detail in Discuss / Explore deeper. Never recommend an
unsupported historical fact or disguise a research task as a suggested answer.

| Lens | Reasoning coverage |
|---|---|
| 1. Process Reality | Purpose, trigger, genuine completion, boundary, inputs/outputs, end-to-end flow, meaningful subprocesses, variants, exceptions, representative recent cases. |
| 2. People, Judgement & Controls | Responsible roles, input providers, recipients, handoffs, approvals, human judgement, controls, escalation, failure ownership, waiting/rework. |
| 3. Systems, Data & Evidence | Systems/tools, authoritative sources, ownership/access, interfaces, traceability, quality, restrictions, production considerations, existing tools/PoCs/initiatives. |
| 4. Pain, Baseline & Root Cause | Process location, users, frequency/scale, impact, evidence, symptom versus root cause, workarounds, useful baseline, desired improvement. |
| 5. Opportunity & Reuse | Evidence-backed opportunities, existing capabilities, local/common elements, parent/child treatment, Stage 4 readiness, targeted discovery still needed. |

Assign the appropriate answer owner internally, not as a card label: FDE, SME, Process Owner,
Evidence-required, Technology SME, or Control / Risk SME. No new UI field is required.
Maintain a short coverage/gaps summary, not a compulsory list of answered fields.

## Conversational question UX

**Simple conversation on the surface; rigorous evidence structure underneath.**
The SME need not understand the evidence model or manually label their answer. Follow
SKILL.md's one-card contract. The FDE/skill does the structuring and verification work.

Choose one conceptual action before making a card:

| Action | Who does the work | Example |
|---|---|---|
| ASK USER | Person with relevant domain/process knowledge | “What happens when the reviewer sends it back?” |
| FDE INVESTIGATE | FDE inspects accessible sources/capabilities | Read validation requirements; check MRO/enterprise tools or Power Platform capability. |
| EVIDENCE CHECK | FDE validates an obtained claim | Inspect recent review history; distinguish workflow timestamps from active effort. |

Only ASK USER normally becomes a question card. Persist other actions as a lightweight
`discovery.followUps` list: action type, task, related claim/question/evidence IDs, owner
if known, status, and result/source when obtained. This is a convention within the
existing discovery record, not a new schema or workflow engine. Preserve it on resume.
Review the list when selecting the next frontier and before Gate 3; a completed task
without corroborating evidence does not upgrade a claim automatically.

Ask internally: already known? Can the FDE find it? Does it affect a decision now? Can it
wait? Must evidence be reviewed first? Never make the SME research enterprise capability.
If access is unavailable, record that and ask only for the needed access/contact when
material. A user may point to relevant guidance or examples without auditing their fit.

Use familiar language: “Do we have anything that confirms this?”, “Which parts need a
validator's judgement?”, “What normally happens next?” Avoid evidence-required,
traceability checkpoint, source-backed decomposition, materiality assessment,
authoritative artefact, production constraint taxonomy and decision-sufficient evidence
in user-facing cards unless genuinely needed and explained. Use the user's role names.

Collect evidence incrementally: first the useful fact, then assess whether stronger
support matters. Prefer an FDE evidence action to another SME question. If the user is
needed, ask separately “Do we have a recent example that confirms this?” with suitable
choices: Yes / Partly / Only an estimate or recollection / FDE to investigate / Ask another
SME / Not relevant. Do not demand source, date, owner, status, confidence, process step
and finding linkage together. Cite available sources yourself; ask metadata only when it
changes a material decision. Uncertainty is useful information, never a failed answer.

Do not immediately re-ask an unknown question in different words. Record the gap, its
resolution action and whether it blocks progression. “Not relevant” is a scope claim to
consider, not permission to silently drop a required control.

See [validation-report golden example](validation-report-question-ux.md) for card style,
natural-answer extraction and reviewer acceptance checks. These examples are not a
fixed sequence to ask regardless of available context.

## Representative real-case walkthrough

Where practical inspect at least one recent representative case:
Input → user action → tool/system → human judgement → handoff → active time → waiting
→ rework → control → exception → output.
Compare the stated standard process with actual events; expose hidden handoffs,
duplication, workarounds, waiting, rework, judgement, exceptions and system boundaries.
If none is available, record an evidence limitation and its decision impact; do not
automatically block all discovery.

## Opportunity and reuse judgement

Check relevant MRO tools, enterprise capabilities, Microsoft Copilot, Power Platform,
platform functionality, workflows, analytics, PoCs, initiatives and reusable components.
Record the source and limits of the check. Stage 3 identifies potential fit; Stage 4
assesses feasibility and selects solutions. Unresearched capability is Unknown, not absent.

Classify reuse as Local / Potentially Common / Clearly Common / Unknown with a short
rationale. One leadership priority may yield several distinct Oxx opportunities; do not
force them into one solution. Child Case Required? = Yes / No / TBD, with disposition
remain within parent case or create child FDE case and rationale. No numerical scoring.

## Playback and Gate 3

Before completion prepare a short current-state playback: boundary, subprocesses,
variants, roles, handoffs, judgement, controls, systems/data, material pains/root causes,
exceptions and important uncertainties. Record Process Owner status exactly as
Confirmed / Confirmed with comments / Not yet confirmed. Capture who confirmed and the
comments/source where available; never infer confirmation from silence.

Gate 3 asks “Is the process sufficiently understood to act?” Apply per material
opportunity. Recommendations: Proceed to Stage 4; Continue Targeted Discovery;
Merge with Existing Initiative; Remain within Parent Case; Create Child FDE Case;
Defer; Stop. Distinguish progression from parent/child disposition where both apply.
Each recommendation includes rationale, supporting Fxx and Exx, key remaining
uncertainty and next action. No evidence may warrant continued discovery/defer/stop,
not a fabricated opportunity. State absence of supporting IDs explicitly.

## Ownership

- MRO FDE Operating Model Owner owns alignment with the wider 8-stage model.
- Stage 3 Methodology / Quality Owner maintains principles, coverage, evidence standards,
  Gate 3 readiness criteria and golden-case tests; assures discovery quality.
- FDE Technical Maintainers own skill implementation, UI/server integration, GitHub
  Copilot compatibility and technical tests.

SMEs provide domain knowledge. FDE owns and leads discovery. The skill structures and
challenges it. The methodology/checklist owner assures quality.
