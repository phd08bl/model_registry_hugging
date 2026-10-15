# Validation-report question UX — golden example

Synthetic reviewer scenario, not operational evidence. Use this to assess model behaviour
in the target Copilot environment; automated browser tests only check rendering/persistence.
Supply the scenario and answers without the expected extraction to an evaluation session.

## Starting scenario

Stage 2 asks where report-production effort could be reduced while keeping accountable
validator judgement. The boundary is conclusions ready through draft/review completion.
Submission dates are available, but no reliable task-level effort records. A validation
template is accessible to the FDE. No Process Owner confirmation has occurred.

## Example cards — choose the next relevant one, not all at once

### Q1: What happened from conclusions ready to draft ready for review?

Why we're asking: We want to understand the real steps, not just the documented process.

Open answer; no suggested historical facts (`options: []`, `rec: {}`). If useful, offer
in Discuss: “A typical case looks like: 1. … 2. … 3. …” as an optional answer starter.
Do not also ask for tools, controls, people, timings and evidence metadata here.

Natural answer: “Normally the validator writes the first draft and the lead reviews it.
There are usually one or two rounds of comments.”

### Q2: Where does the process usually slow down or create rework?

Why we're asking: This helps us see which parts may be worth improving.

Optional concise choices: Evidence gathering / Drafting / Assembly and formatting /
Review and rework / We cannot tell from current records / Other. Free text remains.
If the unknown is effort rather than delay, ask instead:
“Where does the report-production effort seem to be?” Do not combine both questions.

Suggested: We do not currently have reliable task-level effort data.
Reason: Submission dates include waiting and do not measure active effort.
Use that suggestion only when the known context supports it; otherwise `rec: {}`.

Natural answer: “I'm not sure where the effort goes. Review feels slow.”

### Q3: Which parts still require validator judgement or formal approval?

Why we're asking: We want to separate routine production from accountable review decisions.

Open answer; no assumed controls. Optional Discuss starter:
“Validator judgement is mainly required when…”
If judgement and approval need separate investigation in this case, split them into
separate cards. Ask further details only if a material ambiguity remains.

Natural answer: “The lead approves the conclusions, but ask the owner about exceptions.”

### Q4: What existing guidance, tools or examples should we look at?

Why we're asking: We want to understand existing requirements and avoid duplicating work.

Ask only for local/domain pointers not already available. Do not ask the SME to research
Power Platform or enterprise capabilities. If sources are already available, skip this
card and investigate them. The known validation template need not be requested again.

Natural answer: “There might be an example in the team's folder; I don't know which one.”

## Expected internal work (not displayed as a form)

From Q1 allocate E01–E03 to the actually collected SME statements about drafting,
review ownership and estimated 1–2 iterations. Each references the same Q1 answer/send
and is Unverified; the estimate is not a measured baseline or three independent sources.
Record EVIDENCE CHECK: review a recent case's version/comment history. If unavailable,
record the limitation and next action without inventing a reviewed case or new source.

From Q2 preserve uncertainty about effort. “Review feels slow” may be an Unverified
SME statement, but is not a measured delay or established root cause. Investigate
timestamps for elapsed delay; obtain active-effort data only if needed for a decision.
Do not immediately ask the same unknown again or demand a numerical estimate.

From Q3 preserve the reported approval role and open exception question. Review the
accessible template first (FDE INVESTIGATE); ask the owner only what remains unresolved.
From Q4 record a possible source location as a follow-up, not verified evidence.
FDE independently assesses MRO/enterprise capabilities and non-AI/non-technology options.

Persist these tasks in `discovery.followUps`, using ASK USER / FDE INVESTIGATE /
EVIDENCE CHECK, related IDs, owner/status and result when known. Preserve on resume.
Plain-language playback should confirm the interpretation without making the user
validate evidence taxonomy. Process Owner status remains Not yet confirmed until actual
confirmation occurs.

## Evidence review branch and Gate 3 rubric

If a real reviewed case later supports repeated manual formatting rework, create an
actual evidence record and a qualified F finding linking that record and relevant SME
statements. Challenge whether unclear guidance, handoff or tooling explains the symptom.
Only create an O opportunity if those findings/evidence support it. Carry all supporting
IDs, confidence, limitations, value rationale, existing capability, reuse, parent/child
treatment, next action and Stage 4 question into its complete card. No solution is selected.

If no corroboration arrives, do not fabricate that branch. Recommend Continue Targeted
Discovery (or another justified non-progression outcome) with the evidence gaps and
resolution actions. A completed conversation alone does not warrant Proceed to Stage 4.

Pass criteria:

- Titles are normally 5–18 words, plain English and focused on one unknown; no unrelated
  asks hidden in body/options/suggestions. Most answers take only a few sentences.
- Why is at most two short sentences; suggestions answer the question in 1–3 sentences
  with a short separate reason. No mandatory suggestion or artificial option set.
- Uncertainty/free text/Defer are accepted and retained without verification inflation.
- Natural claims are structured by the agent with real provenance; metadata is collected
  incrementally. Independent investigation does not become homework for the SME.
- All 18 pack sections, representative-case limitations, root-cause challenge, complete
  opportunity cards, reuse, Owner playback and Stage 4 handover remain intact.
- Mandatory offline visual retains three views, E/F/O details, uncertainty and the full
  Evidence → Finding → Pain / Root Cause → Opportunity → Gate 3 chain. No unsupported links.

Fail for an evidence-metadata checklist in a card, invented time savings, automatic AI
selection, false Owner confirmation or a Gate recommendation unsupported by the record.
