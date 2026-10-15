# MRO FDE Discovery Visual — v0.1

Draw one self-contained offline HTML file at `<session>/visual.html`, using the existing
subagent/inline lifecycle in [SKILL.md](SKILL.md#subagent-or-inline). Use kind `diagram`.
This mandatory visual explains current process and evidence, not a proposed solution.

## Read first

Read `state.json`: topic, intent, terms, questions/discussions, `discovery` (context,
process, cases, evidence, findings, pains/root causes, opportunities, playback, Gate 3),
and `visual.thread`. Read the current Discovery Pack at `state.doc` if present. On
redraw inspect existing HTML and preserve unaffected layout. Read
`methodology/evidence-model.md`. Do not invent evidence, IDs, links or confirmation.
An accepted answer is not automatically verified. Show absent evidence and unresolved
contradictions explicitly. Open recommendations are proposals, never asserted facts.

## Header

Prominently show **MRO FDE DISCOVERY VISUAL**, Case / Topic, Discovery Question,
Discovery status (including continued-discovery/defer/stop where relevant), Process
Owner confirmation status (Not yet confirmed if unknown), and methodology version.
Include the exact visible sentence:

Stage 3 discovery evidence — not an approved solution design.

Exported artifacts do not imply Gate approval. Start with an HTML comment naming the
source questions/records, uncertain regions and changes in this version.

Use plain labels such as Evidence, Finding, Root cause, Opportunity and Next step.
“Next step” may label the display, but retain the full Gate 3 recommendation, IDs,
confidence/status and traceability in the details. Simplify labels, not the evidence chain.

## Three views in one artifact

Use three simple accessible buttons/tabs, labelled arrows, readable confidence/status
text (not colour alone), system fonts and restrained styling. Prefer grouping or
scrollable sections to tangled large diagrams. No graph framework is needed.

### Current Process

Show start/end, meaningful subprocesses, roles/swimlanes where useful, handoffs, systems,
human judgement, controls, waiting/rework, exceptions and material pains. Attach real E/F
references to supported steps/pains. Mark variants and uncertainty. Do not depict a
proposed target solution as the current process.

### Evidence Chain (most important)

Visually map Evidence → Findings → Pain / Root Cause → Improvement Opportunity → Gate 3
Recommendation. Use explicit real E01, F01, RC01 (where assigned) and O01 IDs with labelled
connections. Example topology only, never fixture evidence:
E01 + E04 → F03 → RC01 → O02 → Proceed to Stage 4.
Selecting an Evidence, Finding or Opportunity node must show its details in one reusable
panel. Where practical highlight the entire connected chain and dim unrelated nodes.
Support keyboard selection and a reset. Missing links are visible gaps, not invented
arrows. Empty evidence/opportunity sets are legitimate and explained.

### Opportunities

A compact card for each material opportunity: ID, opportunity, pain point, supporting
findings/evidence, confidence, desired outcome, indicative value/rationale, existing
related work, reuse potential, Gate 3 recommendation and Stage 4 question. No scores.

## Reusable detail panel

- Evidence: ID, type, source, statement, verification status, what it supports.
- Finding: ID, finding, supporting evidence, confidence, limitations.
- Opportunity: ID, desired outcome, supporting findings/evidence, value, constraints,
  reuse, Gate 3 outcome, Stage 4 question.

Use textContent or escape source text before inserting HTML. Avoid executable source
content. Keep source references readable as text; do not make network links/assets.

## Offline file contract

One HTML file: inline CSS/JavaScript, inline SVG/HTML diagrams, system fonts. No network
requests, CDN, Mermaid CDN, external fonts, images, imports, fetch/XHR/WebSocket, workers,
iframes, forms, remote or relative resources. Fragment links are fine. Use inline SVG
instead of images. No runtime dependencies or build step.
Put this CSP immediately after `<head>` before any resources/scripts, for defence in
depth when the exported file is opened outside the interview iframe:

```html
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; font-src 'none'; connect-src 'none'; base-uri 'none'; form-action 'none'">
```

The SVG namespace `http://www.w3.org/2000/svg` is an identifier, not a request.
Use no other URLs in resource attributes. The finalization check conservatively rejects
resource tags/attributes and network APIs; do not evade it with encoding/dynamic scripts.
Check in a browser offline: tabs, node details, long labels, unknown data and keyboard
access. `finalize` validates structure/freshness and basic offline constraints, not
truthfulness or visual quality.

## Delivery

Return one line saying what changed, naming relevant IDs. Do not return markup in chat.
The interviewer verifies file change, records version and follows queue/stale rules.
At Finish reconcile with the final pack before the version bump and `finalize`.
A failed draw must never bump version. A secondary hypothesis prototype may inform pack
findings, but must not replace this mandatory visual.
