# Evidence and traceability — v0.1

Keep a lightweight, persistent record in `state.discovery` using `patch`. This top-level
object is replaced whole, so preserve its previous contents when updating it. Suggested
keys are `context`, `coverage`, `process`, `cases`, `evidence`, `findings`, `pains`,
`opportunities`, `playback`, `openQuestions`, `gate`, `nextWave`. No new browser fields
or rigid database schema are needed. Record independently researched facts here too;
the visual and final pack must not depend on the agent remembering unpersisted analysis.

## Evidence register

Allocate E01, E02… only to actual collected items. IDs identify records, not verification.
Never invent sources or supporting evidence to fill a gap. Types:
Observed Case; System / Data Record; Document / Artefact; SME Statement; FDE Analysis.
Status: Verified / Partially Verified / Unverified. Record what was verified and how;
an SME statement starts Unverified unless corroboration warrants another status.

Each record: ID, type, source (retrievable reference or named interview/date where known),
statement, what it supports, process step, status, owner/date where known, limitations.
Separate assumptions and hypotheses from evidence; leave unknown source/date unknown.
FDE Analysis should identify its inputs and method, not corroborate itself circularly.

## Natural answer → structured record

The agent structures the answer; the SME does not fill this model. Preserve the original
answer in the question history. Extract only what it actually says, retain qualifiers,
and reference the source question/send. Use existing event dates when available; do not
invent speaker identity, case dates, sources or measurements. Split distinct claims when
useful without presenting them as independent corroboration of one another.

Example: “Normally the validator writes the first draft and the lead reviews it.
There are usually one or two rounds of comments.” Internally record:

- SME Statement: validator prepares initial draft — Unverified.
- SME Statement: validation lead reviews it — Unverified.
- SME Statement: usually 1–2 review iterations — Unverified estimate, not measured data.
- EVIDENCE CHECK: FDE reviews a representative recent case's review history.

Assign actual E IDs to those collected statements, citing the same original answer.
A planned evidence check is not collected evidence: do not allocate a fictional source
or treat its completion as assured. Store it in `discovery.followUps` until investigated.
“I don't know” records uncertainty and a possible follow-up, not a factual E record
proving absence. Ask a short clarifier only when ambiguity materially changes meaning.

After review, link real corroboration/contradictions, update statuses with reasons,
then derive F findings, assess symptoms/root causes and support O opportunities and Gate
recommendations. Unsupported causes remain hypotheses; uncertainty may justify targeted
discovery rather than progression. All IDs, confidence, limitations, opportunity-card
fields, playback, reuse assessment and Stage 4 handover requirements remain mandatory
where applicable. Easier answers must not imply easier Gate 3 evidence standards.

## Findings and root causes

Allocate F01, F02… to FDE findings: statement, supporting E IDs, confidence High / Medium /
Low, limitations. Distinguish observations from interpretations. Challenge a claimed root
cause: what evidence distinguishes it from a symptom or alternative explanation?
Use RC01, RC02… when useful, linking the pain/root cause to findings and evidence.
An unsupported root-cause claim remains a hypothesis. Do not upgrade status/confidence
because an answer or recommendation was accepted in the cards.

## Required chain

Evidence → Finding → Pain / Root Cause → Improvement Opportunity → Gate 3 Recommendation.

Every material O01, O02… must cite supporting F IDs and E IDs, including the links through
pain/root cause. Keep IDs stable across redraws/resume; do not renumber or recycle them.
Check that every cited ID exists and actually supports the claim. Make contradictory
sources and gaps explicit. Never produce an opportunity merely because it sounds useful.

## Improvement Opportunity Card (all fields required)

- Opportunity ID; Opportunity; Pain Point Addressed; Process Step; Affected Users
- Supporting Findings; Supporting Evidence
- Evidence Confidence: High / Medium / Low
- Desired Outcome
- Indicative Value: High / Medium / Low plus short rationale (no weighted scores)
- Constraints
- Existing Related Work / Capability (including check source and uncertainty)
- Reuse Potential: Local / Potentially Common / Clearly Common / Unknown plus rationale
- Child Case Required?: Yes / No / TBD and parent/child disposition rationale
- Recommended Next Action
- Stage 4 Question

Where a field is unknown, say so and describe the decision impact. Gate recommendations
also reference F/E IDs and remaining uncertainty. See the pack template for the handover.
