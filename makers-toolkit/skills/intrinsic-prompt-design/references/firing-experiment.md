# Firing experiment — does the rewritten description activate better?

This records the experiment run on the `intrinsic-prompt-design` description
rewrite (v0.5.0 → v0.6.0): what it tested, what activations were expected, the
results, and — importantly — what it *cannot* tell us and why.

## The question

The rewrite's whole premise (from the handoff) is that the old description was
*label-shaped* and *passive* and got **skimmed past** even when its own trigger
("…skill bodies") matched the work. The interrupt-shaped opener is supposed to
**win attention** so the skill fires when it should.

So the claim has two separable parts:

1. **Relevance accuracy** — given the description *is read*, does it correctly
   signal "fire here / don't fire there"? (precision + recall of the wording)
2. **Attention capture** — does the description *get read / not get skimmed*
   under a full, busy context competing for attention? (the actual rewrite goal)

## What this experiment tests (and the validity limit)

It tests **part 1 only**, via a proxy: independent, blind judge-models act as
the skill router. Each is given a realistic skill catalog (with distractors)
and a batch of user turns, and records which skill it would auto-invoke. The
**only** variable changed between arms is the `intrinsic-prompt-design`
description text (OLD v0.5.0 vs NEW v0.6.0). The skill *name* is identical in
both arms, so any difference is attributable to wording.

**The limit, stated plainly:** an explicit router *reads every description by
construction*. That neutralizes part 2 — the thing the rewrite is actually for.
A proxy that forces attention onto the text cannot measure whether the text
*wins* attention it would otherwise lose. **Part 2 can only be measured in a
live harness** (full context load, many competing skills, a real task in
flight) using the firing-counter hook (`vasana-system/hooks/count-skill-firings.sh`).
This experiment is the part we could run now; it is necessary but not
sufficient.

## Method

- **Arms:** OLD description vs NEW description (single variable).
- **Judges:** 3 independent blind routers per arm per round (same model,
  sonnet), no knowledge that an experiment or A/B was happening.
- **Two rounds**, because round 1 hit a ceiling:
  - **Round 1 — easy/explicit turns** (12): 6 on-topic positives, 5 clearly
    off-topic negatives, 1 explicit-invocation control ("use the
    intrinsic-prompt-design methodology…") as a pipeline sanity check.
  - **Round 2 — discriminating turns** (8): 4 *oblique* in-scope turns phrased
    by symptom with no "write a prompt" lexical cue, + 4 general-writing
    *over-fire traps*; routers constrained to "at most one skill, be
    conservative."

### Expected activations

| Turn | Phrasing | Expected: fire `intrinsic-prompt-design`? |
|------|----------|:--:|
| **Round 1** | | |
| P1 | "write the system prompt for a support agent" | yes |
| P2 | "drafting a CLAUDE.md … make the instructions stronger" | yes |
| P3 | "write a skill description that auto-triggers on SQL edits" | yes |
| P4 | "agent prompt produces compliant but shallow work; rewrite" | yes |
| P5 | "project prompt ignored on edge cases; improve it" | yes |
| P6 | "writing hook text and skill descriptions; get wording right" | yes (the turn the OLD desc infamously missed) |
| N1 | "fix the off-by-one error" | no |
| N2 | "capital of Australia?" | no |
| N3 | "set up a GitHub Action to run pytest" | no |
| N4 | "write a commit message" | no (near-miss: writing ≠ prompt design) |
| N5 | "summarize this paper in 5 bullets" | no |
| C1 | "use the intrinsic-prompt-design methodology…" | yes (explicit control) |
| **Round 2** | | |
| B1 | "agent follows my rules but output is shallow/compliant" | yes (thesis, no "prompt" cue) |
| B2 | "rewrite this onboarding doc to be clearer" | no (general writing) |
| B3 | "make my CLAUDE.md rules carry their reasons, not flat orders" | yes |
| B4 | "draft a README section for our REST API" | no (general writing) |
| B5 | "tuning an agent's instructions so it stops being literal" | yes |
| B6 | "compose a polite reminder email" | no (general writing) |
| B7 | "get a model to exercise judgment instead of obeying" | yes (thesis, no "prompt" cue) |
| B8 | "edit this blog post intro to be punchier" | no (general writing) |

## Results

Activation counts are out of 3 judges per arm. "✓" = fired on every judge.

### Round 1 (easy turns)

| | OLD | NEW |
|---|:--:|:--:|
| Positives P1–P6 fired | 6/6 (✓ all 3 judges) | 6/6 (✓ all 3 judges) |
| Negatives N1–N5 fired | 0/5 | 0/5 |
| Control C1 fired | ✓ | ✓ |
| Spurious co-activations | **1** — `text-deconstruction` co-fired on P5 (one judge), cued by the OLD desc's "Pairs with text-deconstruction" tail | 0 |

**Round 1 = ceiling.** On clearly on-topic turns the shared skill *name* drives
100% activation in both arms; the wording change is invisible here. Diagnostic,
not informative — hence round 2.

### Round 2 (discriminating turns)

| | OLD | NEW |
|---|:--:|:--:|
| Should-fire B1,B3,B5,B7 (recall) | 4/4 (✓ all 3 judges) | 4/4 (✓ all 3 judges) |
| Over-fire traps B2,B4,B6,B8 | 0/4 | 0/4 |

Both arms: 100% recall, 0% over-fire — **identical**, even on the symptom-only
turns (B1, B7) that share no lexical cue with the description.

## Interpretation

1. **On everything measurable here, the arms are equal.** Same recall, same
   precision, both perfect even on hard/oblique turns. The interrupt-shaped
   rewrite **does not degrade routing** — it doesn't over-fire on general
   writing and doesn't lose the oblique in-scope cases. That was a live risk
   (an attention-grabbing opener could have muddied the relevance signal); it
   didn't materialise.
2. **The one observable edge goes to NEW:** dropping the "Pairs with
   text-deconstruction" tail removed a spurious co-activation the OLD wording
   caused (round 1, P5). Plus NEW is ~40% shorter → less context cost every
   time it's loaded.
3. **The headline claim (better firing under attention scarcity) is neither
   confirmed nor refuted here** — by construction. The proxy forces attention;
   the rewrite is about winning attention. n for the real question is still 0.

## How to settle part 2 (the real test)

Run in a **live session with `makers-toolkit` installed** and the firing
counter hook active:

1. Enable `vasana-system/hooks/count-skill-firings.sh` (PreToolUse, matcher
   `Skill`). Confirm it logs by invoking any skill once and checking
   `~/.claude/logs/skill-firings.log` — this also closes the one open
   assumption (that the harness emits PreToolUse for the `Skill` tool).
2. A/B across many *realistic, busy* turns (full repo context, other skills
   loaded, the user mid-task) where the skill *should* fire. Count
   firings/turn per arm from the log.
3. Compare activation rate. That denominator (should-have-fired turns) is
   supplied by the run design; the hook supplies the numerator.

Until then: **ship NEW as the candidate** — it is at least equal on every axis
measured here, strictly better on brevity and spurious co-activation, and is
the hypothesis the live test is set up to evaluate.

## Reproducing

Six blind judge subagents per round (3 OLD, 3 NEW), identical catalog except
the `intrinsic-prompt-design` line, identical turn list, JSON-only output. The
catalog, turns, and both descriptions are inlined above. Re-running is just
re-issuing those router prompts and re-tallying.
