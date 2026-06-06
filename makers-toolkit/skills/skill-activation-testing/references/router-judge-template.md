# Router-judge prompt template (Tier 1)

A fill-in-the-blanks prompt for a **blind** judge that plays the skill router.
Hand it to a fresh agent (a subagent with no other context is ideal — it can't
know an A/B is happening). Run **N≥3 judges per arm per round**; between arms,
swap **only** the line marked `‹VARIABLE UNDER TEST›` and change nothing else.

## The I/O contract (define this before you run anything)

- **In:** a skill catalog (one `name — description` per line) + a numbered turn list.
- **Out:** a JSON array, one object per turn, no prose. This is the whole point of
  "JSON only" — prose answers can't be tallied mechanically, and a judge that
  narrates is a judge you're scoring by hand and by mood.
- **Shape:** `[{"turn": <int>, "skill": "<name>" | null}, ...]` (Round 2 adds the
  "at most one" constraint; Round 1 may allow a list — see below).

## Template

> You are the skill router for a Claude Code session. Skills auto-invoke when a
> user's turn matches what they're for. For each turn below, decide which
> skill — **if any** — you would auto-invoke for that turn.
>
> ‹CONSTRAINT›
>
> ### Available skills
>
> ```
> ‹CATALOG — every skill as `name — description`; exactly ONE line is the
>  ‹VARIABLE UNDER TEST›, the only thing that differs between arms›
> ```
>
> ### Turns
>
> ```
> ‹TURNS›
> ```
>
> ### Output
>
> Return **only** a JSON array, no commentary, one object per turn:
> `[{"turn": 1, "skill": "<skill-name-or-null>"}, ...]`
> Use `null` when no skill should fire. Everything you need is above — answer
> from the catalog and turns alone; do not look anything up.

## Slots to fill

- **`‹VARIABLE UNDER TEST›`** — the one catalog line that differs between arms
  (e.g. the OLD vs NEW `intrinsic-prompt-design` description). *Nothing else
  changes between arms.* If you change two lines, you've run two experiments and
  can attribute neither.
- **`‹CATALOG›`** — a realistic catalog: the skill under test **plus distractors**,
  including at least one *adjacent-but-wrong* skill that an over-eager
  description would steal turns from. Identical across both arms.
- **`‹TURNS›`** — the round's turn list (below). Identical across both arms.
- **`‹CONSTRAINT›`** —
  - *Round 1 (ceiling):* `"List every skill you would invoke for each turn (zero, one, or more)."` — leaving room for spurious co-activations to show up.
  - *Round 2 (discriminating):* `"Invoke at most ONE skill per turn, and only when you are confident it is the right one. When in doubt, return null. Be conservative."` — forcing the selectivity that reveals over-fires.

## Turn-list design

| Round | Turn kind | How to write it | Expected |
|---|---|---|---|
| 1 | on-topic positive | uses the skill's own vocabulary | fire |
| 1 | off-topic negative | unrelated work (a bug fix, a trivia question) | null |
| 1 | explicit control | `"use the <skill> methodology…"` | fire (proves the pipeline) |
| 2 | **oblique** positive | the skill's *symptom*, with **no** word the description uses | fire |
| 2 | **over-fire trap** | adjacent-but-wrong (general writing vs prompt design; writing a description vs *testing* one) | null |

The oblique positives are the test of the *wording* (a lexical-match positive
fires on the name alone and tells you nothing). The traps are the test of
*precision*. A round with only obvious positives measures the skill name, not
the description.

## Scoring

Per arm, per round, tally from the JSON:

- **Recall** = should-fire turns that fired / should-fire turns.
- **False-fire rate** = trap turns that fired / trap turns.
- **Spurious co-activations** = non-target skills that fired (Round 1, where the
  constraint permits a list).
- Note **agreement** across the N judges (`✓` = all judges agree it fired).
  A 2/3 split is itself a finding — the description is near the routing boundary.

Then write the result with its validity limit attached (see `SKILL.md`,
discipline #1). A proxy number without its limit is the failure this whole
method exists to prevent.
