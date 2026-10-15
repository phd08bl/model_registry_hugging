# MRO FDE Discovery Grill v0.1

**Discover the process before designing the solution.** An internal discovery copilot
for Stage 3 of the MRO FDE Operating Model, adapted from
[jasonku09/grill-with-ui](https://github.com/jasonku09/grill-with-ui).
Upstream attribution and the [MIT licence](LICENSE) are preserved.

Stage 3 converts a leadership priority and Stage 2 discovery question into an evidenced
understanding of the current process, material pains/root causes and improvement
opportunities. It is not a generic design grill or an automatic AI-solution generator.
Stage 4 owns solution options, selection, architecture, PRD/technical design and implementation.

- SMEs provide domain knowledge.
- FDE owns and leads discovery, including independent evidence/capability investigation.
- The skill structures and challenges discovery using five lenses and an evidence chain.
- The methodology/checklist owner assures quality.

## Install with GitHub Copilot

Node 20+ and a local Copilot agent with shell/file access are required. No npm runtime
dependencies or build step. Copy this skill folder into your project's
`.github/skills/mro-fde-discovery-grill/`, or into your personal
`~/.copilot/skills/mro-fde-discovery-grill/`. Include `SKILL.md`, `server.mjs`,
`discovery-output.mjs`, `page.html`, `visual-brief.md`, `methodology/`, `templates/`
and `LICENSE`; do not copy only SKILL.md. A directory symlink/junction also works.
The repository root itself need not be renamed if installed through a link.

See [GitHub's agent skills installation documentation](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills).
Use a local Copilot chat/CLI session for this local browser workflow; remote/cloud agents
may not expose their loopback server to your browser. Model behaviour and listening
support should be pilot-tested in your organisation's chosen Copilot environment.

## Start and resume

In Copilot agent chat, use the exact natural-language invocation:

```text
mro fde discovery grill: investigate the monthly reconciliation evidence process
```

Supply the Candidate Brief, Process Owner, Desired Outcome, leadership priority, Stage 2
decision/question, boundary, initial wave, evidence and known SMEs where available.
The agent reads those first and investigates facts it can obtain independently before
asking up to three high-value independent questions at a time. Missing context remains
explicitly unknown. The five lenses guide reasoning rather than a fixed questionnaire.

Open the local URL returned by the agent. Answer cards, accept recommendations, select
multiple options where offered, or use free text. Discuss, Explore deeper, Defer, Reopen,
staged sends and the feedback thread retain upstream behaviour. An accepted SME answer
is not automatically verified evidence. Stop once discovery is decision-sufficient.

Resume from the same project:

```text
mro fde discovery grill: resume
```

Queued sends are replayed; the server reuses its old port where possible. Legacy upstream
sessions remain readable; on migration the skill preserves their history, adopts the new
output contract and treats prior design proposals as claims rather than evidence.

A running page server does not wake an ended agent turn. Without a persistent Monitor,
the agent must keep the foreground `wait` loop active. If interrupted or paused, sends
remain queued until resume; do not assume a visible browser means the agent is listening.

## How to answer the Grill

**Simple conversation on the surface; rigorous evidence structure underneath.**
The Grill asks one short question per card. Answer naturally in a few sentences;
Joe / Charles and other FDEs do not need to complete every methodology field during
the conversation. The skill structures natural answers into evidence, findings and
opportunities, while preserving what is unverified or uncertain.

- Say when you are unsure; “I don't know” is useful discovery information.
- Do not invent data or guess a number to complete an answer.
- Cite evidence if readily available; you do not need to prepare an evidence register.
- Use Defer when another person or evidence is needed, or explain this in free text.
- Use Discuss for detail; suggestions are optional, and free text is always available.

Normal workflow: Stage 2 context → simple discovery conversation → FDE investigation /
evidence checks → playback → Discovery Pack + Discovery Visual → Gate 3.
The FDE investigates accessible documentation and capabilities independently and checks
claims incrementally. A natural answer is not automatically verified evidence. The full
output requirements and Gate 3 traceability remain unchanged. See the
[validation-report example](methodology/validation-report-question-ux.md).

## Two mandatory outputs

Finish Discovery processes staged answers, creates the pack, reconciles the visual,
exports and verifies both, and only then marks the session finished:

```text
docs/monthly-reconciliation-fde-discovery-pack.md
docs/monthly-reconciliation-discovery-visual.html
```

The self-contained pack has 18 sections, including the evidence register, FDE findings,
root causes, complete Oxx opportunity cards, reuse/parent-child assessments, Process Owner
playback, Gate 3 recommendations and Stage 4 handover. Normally `Solution Selected: NO`.
Measured baselines, estimates, hypotheses and evidence limitations remain distinct.

**Discovery Visual is mandatory even if nobody presses the button.** Pressing it early
provides a preview with Current Process, Evidence Chain and Opportunities views, selectable
nodes/details and visible uncertainty. It is one standalone offline HTML file, with inline
CSS/JS/SVG, system fonts, no CDN, fonts or remote assets. The header explicitly says it is
Stage 3 evidence, not an approved solution design. A hypothesis prototype is secondary.

Ordinary answers mark a visual stale without redrawing. Regenerate or feedback requests
a redraw; versions, queued draws and the Use subagent preference are preserved. Without
a subagent tool the agent draws inline. Finish also carries this preference before the
first visual. If drawing/export fails the pack survives, the session stays unfinished,
and the agent reports the failure with a retry path.

`server.mjs finalize` verifies both artifacts, basic pack/visual structure, offline
constraints, no pending sends/draws, and fingerprints of state, pack and visual bytes.
A draw records its source at launch so answers arriving while it draws cannot silently
be called current. These checks do not prove evidence quality or semantic accuracy;
the FDE must reconcile content and inspect the visual. The server never calls an LLM.

## Gate 3 and ownership

Gate 3 asks **Is the process sufficiently understood to act?** Each material opportunity
has a rationale, supporting findings/evidence, remaining uncertainty and next action.
Recommendations include Proceed to Stage 4, Continue Targeted Discovery, Merge with
Existing Initiative, Remain within Parent Case, Create Child FDE Case, Defer and Stop.
Completion of the artifacts does not imply approval or Process Owner confirmation.
No-technology and existing-capability outcomes are valid; one priority may yield several
opportunities rather than one solution.

The MRO FDE Operating Model Owner maintains alignment with the eight-stage model.
The Stage 3 Methodology / Quality Owner maintains principles, coverage, evidence standards,
Gate criteria and golden cases. FDE Technical Maintainers maintain implementation,
Copilot compatibility and technical tests. No personal ownership is hard-coded.

## Files and runtime

Session storage remains `~/.grill-with-ui/sessions/<project-key>/<timestamp>/` for
compatibility (`GRILL_HOME` overrides it). State is agent-owned through atomic `patch`;
`events.jsonl` is server-appended. `server.json` remembers URL/port/PID; `visual.html`
is the agent-generated working visual. The project key uses the git common root across
worktrees, or cwd outside git. `state.discovery` persists the evidence/discovery record.

```text
node server.mjs new --topic TOPIC [--intent INTENT] [--doc PATH]
node server.mjs serve --session DIR [--port N]
node server.mjs sessions [--all]
node server.mjs pending --session DIR
node server.mjs wait --session DIR --after N [--timeout SECONDS]
node server.mjs url --session DIR
node server.mjs patch --session DIR --file PATCH.json
node server.mjs finalize --session DIR
```

`finalize` does not generate content: the skill must author the pack and generate/reconcile
the visual first. It fails without completing if either is missing/stale. Custom pack
paths must retain `-fde-discovery-pack.md`; the visual uses the same directory and slug.
On Windows use `--file` for patches; run the server in a managed shell session or a
hidden background process. The listening/wait rules in SKILL.md still apply.

## Validation and pilot

```sh
node --test test/*.test.mjs
node test/page.e2e.mjs
node test/manual-visual.e2e.mjs
node test/subagent-toggle.e2e.mjs
node test/discovery.e2e.mjs
```

Browser tests require Playwright + Chromium only as development dependencies.
Set `PLAYWRIGHT_PKG` to an installed Playwright module URL/path if it is not local.
On Windows use a `file:///C:/.../index.mjs` URL. `PLAYWRIGHT_EXECUTABLE_PATH` can select
an installed Chrome/Chromium executable instead of Playwright's bundled browser.
Tests simulate agent writes; they do not prove a model follows the discovery methodology.
See [golden cases](methodology/golden-cases.md) for behavioural evaluation and
[the template](templates/fde-discovery-pack.md) for the output contract. Historical upstream
design records and demos in `docs/` and `design/` are retained, not current MRO outputs.

Before pilot, run all five cases in the actual Copilot environment, test interruption/
resume and Finish without a prior visual in both drawing modes, review evidence chains
and Owner status, and open the exported HTML offline in the corporate browser.
