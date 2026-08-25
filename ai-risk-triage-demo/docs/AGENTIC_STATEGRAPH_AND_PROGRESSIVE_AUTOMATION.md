# Agentic StateGraph and Progressive Automation

**Status:** current implementation detail for the local demo. The authoritative topology is
in [ARCHITECTURE.md](ARCHITECTURE.md). All materiality, 2LoD, pattern, profile, sampling and
autonomy rules described here are illustrative.

## Control model

The single Coordinator implements an exception-driven control loop:

1. observe the complete Case State;
2. obtain a deterministic structured `SupervisorDecision`;
3. select a mandatory action deterministically, or permit the bounded LLM to recommend one
   action from supplied allowlists;
4. run the immediate deterministic Action Authorizer;
5. invoke one registered typed tool;
6. verify identity, version, confidence, citations and authority;
7. update only the corresponding governed state fields;
8. reassess objectives, waits, Governance Loops, budgets and completion;
9. selectively replan or pause.

This is agentic orchestration, not autonomous risk judgement.

## Supervisor and budgets

The supervisor evaluates profile assignment/downgrade, action/tool permissions, current
objective, lifecycle, domain phase, active Governance Loop, expected external event,
readiness, Case/rule versions, completion candidacy and four independent limits:

- tool calls;
- tool retries;
- evidence cycles;
- total Coordinator loops.

A limit or unknown state cannot be solved by asking the LLM. It creates a Control Exception
and stops capability execution.

## Progressive Automation profiles

Profiles are system-assigned from protected governed-pattern metadata and declared risk
facts. Normal user input cannot select one. The LLM cannot upgrade or downgrade a profile.

| Profile | Implemented illustrative permission behavior |
|---|---|
| `human_governed` | Every applicable judgement loop is human-owned; empty exception review is not triggered |
| `conditional_review` | Clean bounded preparation may proceed; final triage/publication remain human; exceptions/elevation restore review |
| `exception_based` | Eligible low-risk fixtures may skip later review unless exception, ineligibility, elevation or protected sampling triggers it |
| `straight_through_demo` | One tightly bounded eligible fixture may auto-confirm later demo decisions and publish locally only |

`straight_through` remains a stored-data compatibility alias. Straight-through behavior is not
a production authority model.

## Governance Loop triggers

| Loop | Trigger |
|---|---|
| Evidence Resolution | Current mandatory evidence gap or conflict |
| Material Fact Confirmation | Profile/risk facts require confirmed engine input |
| Exception Interpretation | Current gap accepted for continued review, conflict, rule-supported pattern exception, or elevated interpretation point |
| Final Triage Decision | Profile/policy requires accountable confirmation or override |
| Publication Approval | Local publication requires AIRO under the effective profile |
| Control Exception Review | No safe automatic transition, authorization/result failure, exhausted budget, timeout or completion blocker |

Gate numbers are retained as UI/audit labels for the five original human decision types. The
control model is not a fixed five-stop sequence.

## Evidence state and external waits

The Coordinator separately stores candidate facts, AIRO-confirmed facts, deterministic gaps,
conflicts, LLM/tool advisory observations and confirmed exceptions. Submitted documents are
untrusted. Source-linked extraction is still a candidate until AIRO confirmation when
material-fact policy requires it.

Missing supplier assurance can create `AWAITING_EXTERNAL_EVENT`. The event contract binds
event ID/type, Case/correlation IDs, source, schema and Case State version. Valid events append
evidence and selectively rerun extraction, consistency, citation and supplier checks.
Duplicate IDs are idempotent; mismatches are rejected; timeout creates a Control Exception.

## Deterministic assessment and decisions

The readiness guard prevents premature engines. Materiality and independent 2LoD tools then
produce versioned, hashed proposals from questionnaire facts only. A bounded challenge tool
may add labelled advisory observations; only deterministic rule-supported exceptions and
AIRO-confirmed issues control exception routing.

AIRO can confirm or override the proposal with rationale. Review pack and publication draft
generation are governed local preparation. Publication is `local-demo://` only.

## Replanning, recovery and completion

Changed dependencies create invalidation records, preserve superseded values, mark stale
outputs and create specific rework objectives. Evidence-only changes do not blindly rerun
unaffected deterministic engines; material questionnaire changes do.

Control Exception recovery is version-bound and explicit. Retry/fallback is hidden when the
tool budget cannot support it. Cancellation and failed-safe closure do not represent a risk
rejection.

The deterministic completion guard requires closed objectives/actions, no blocking issues or
open Control Exception, current materiality/2LoD/review pack, final decision and reconciled
local publication. Only then does lifecycle become `COMPLETED`.
