# Self-application — this skill, tested by its own method

A methodology for testing skill descriptions ought to survive being pointed at
its own. This is the Tier-1 run on `skill-activation-testing`'s shipped
description, designed and scored by the procedure in `SKILL.md`. It settles what
Tier 1 can settle and is silent — by construction (discipline #1) — on what it
can't.

## Arms (one variable: the register of *this* skill's description)

The skill *name*, the catalog, and the turn list are identical across arms. Only
the `skill-activation-testing` line changes.

- **NEW (shipped)** — the interrupt-shaped description, as in `SKILL.md`:
  > "You rewrote the description. Did it fire better — or do you just believe it
  > did?" That belief is n=0 until you test it: invoke when validating a skill or
  > prompt change, asking whether a description actually fires, or A/B-ing prompt
  > wording. The cheap proxy gives a number in minutes; the discipline is naming
  > what it can't see.
- **FLAT (control)** — a label-shaped, passive description carrying the *same
  triggers*:
  > Methodology and tools for A/B testing skill descriptions and measuring
  > whether they auto-activate. Use when testing or validating a skill or prompt
  > change, checking whether a description fires, or running an A/B comparison of
  > prompt wording.

This mirrors the #28 OLD-vs-NEW shape (label-shaped vs interrupt-shaped) — so
it's a second data point on whether the interrupt register *preserves routing
accuracy*, not (per discipline #1) on the attention claim, which an explicit
router cannot touch and which stays a Tier-2 question.

## Catalog (identical both arms except the line under test)

```
skill-activation-testing — ‹NEW or FLAT — see Arms›
intrinsic-prompt-design — "Why are you obeying this? No, LITERALLY, why?" Now that I have your attention: invoke when writing project prompts, system prompts, or skill bodies. That question held you where a command gets skimmed — so build prompts on reasons.
system-pilot — What does 'done' look like here? Build deterministic systems with rules that carry their reasons. Use for non-trivial projects or multi-agent coordination; not for typo fixes.
code-review — Review the current diff for correctness bugs and reuse/simplification/efficiency cleanups.
deep-research — Fan-out web searches, fetch sources, adversarially verify claims, synthesize a cited report.
text-deconstruction — Find where a text relies on something it doesn't establish, where its distinctions blur, where claims and structure pull apart.
macro-monitor — Track macroeconomic indicators (Treasury TIC flows, FRED series) and surface regime shifts.
vasana — Capture a behavioral pattern that recurs across unrelated contexts.
session-start-hook — Set up a SessionStart hook so a repo can run tests and linters in Claude Code web sessions.
```

The deliberate **adjacent-but-wrong** trap is `intrinsic-prompt-design`: it is
about *writing* a description; this skill is about *testing whether one fires*.
A turn asking for help *writing* a better description should fire
`intrinsic-prompt-design`, not this skill — that is trap T1/T4 below.
`code-review` and `text-deconstruction` are secondary review/test-adjacent
distractors.

## Turns

**Round 1 — ceiling-check** (constraint: list every skill you'd invoke, 0+):

| # | Turn | Expected |
|---|------|:--:|
| P1 | "A/B test whether my new skill description actually fires" | fire |
| P2 | "measure if my skill's description auto-activates reliably" | fire |
| P3 | "validate that my prompt change made the skill trigger more" | fire |
| N1 | "fix this off-by-one error in the loop" | null |
| N2 | "what's the capital of Australia?" | null |
| N3 | "set up a GitHub Action to run pytest" | null |
| C1 | "use the skill-activation-testing methodology to test my description" | fire (control) |

**Round 2 — discriminating** (constraint: at most ONE skill, be conservative,
null when in doubt):

| # | Turn | Expected | Why |
|---|------|:--:|-----|
| B1 | "I reworded my skill's trigger but have no idea if it changed anything" | fire | oblique: the n=0 symptom, no lexical cue |
| B2 | "how do I know my skill is actually getting picked up and not skipped?" | fire | oblique: firing measurement |
| B3 | "two of us disagree whether the new wording helps — settle it with data" | fire | oblique: the n=0 argument |
| T1 | "help me write a better description for my skill so it triggers well" | `intrinsic-prompt-design` | **trap:** writing, not testing |
| T2 | "write unit tests for my Python function" | null | trap: general "testing" overlap |
| T3 | "rewrite this onboarding doc to be clearer" | null | trap: general writing |
| T4 | "make my CLAUDE.md instructions carry their reasons, not flat orders" | `intrinsic-prompt-design` | **trap:** prompt writing, not testing |

The over-fire risk this run is built to catch: the shared token *"description"*
appears in both this skill's text and traps T1/T4. If the description bleeds into
*writing* territory, T1/T4 fire `skill-activation-testing` — a precision
failure the recall numbers alone would hide (discipline #4).

## Method

3 blind router subagents per arm per round (12 total), no knowledge of the A/B
or which arm they hold. Output JSON only, per `router-judge-template.md`. Scored
for recall (B1–B3), false-fire on traps (T1–T4), and spurious co-activation.

## Results

Run live, 3 blind router subagents per arm per round (12 judges total), none
told an A/B was happening. "n/3" = judges (out of 3) that fired the **target**
(`skill-activation-testing`); "✓" = all 3.

### Round 1 (ceiling)

| | FLAT | NEW |
|---|:--:|:--:|
| Positives P1–P3 fired (recall) | 3/3 ✓ | 3/3 ✓ |
| Negatives N1–N3 fired the target | 0/3 | 0/3 |
| Control C1 fired | 3/3 ✓ | 3/3 ✓ |
| Spurious co-activations | 0 of target; `session-start-hook` co-fired N3 (2/3) | 0 of target; `session-start-hook` co-fired N3 (2/3) |

**Round 1 = ceiling, dead tie.** The shared skill *name* fires all three clear
positives and the control in both arms and stays silent on the off-topic
negatives; the wording change is invisible, exactly as discipline #3 predicts.
The one co-activation (`session-start-hook` on "set up a GitHub Action to run
pytest") is (a) a *different* skill, cued by its own unchanged "run tests"
wording, and (b) identical across arms — so it is not attributable to our
variable and, being a ceiling-round observation, carries no weight (discipline
#3). Diagnostic, not informative — it earns Round 2.

### Round 2 (discriminating)

| | FLAT | NEW |
|---|:--:|:--:|
| Oblique positives B1–B3 fired (recall) | 3/3 ✓ | 3/3 ✓ |
| **Trap T1** "write a better description…" → fired target (over-fire) | **2/3** | **0/3** |
| Trap T4 "make CLAUDE.md carry its reasons" → routed to `intrinsic-prompt-design` | 3/3 (target 0/3) | 3/3 (target 0/3) |
| Traps T2, T3 fired target | 0/6 | 0/6 |
| **Target false-fires across all traps** | **2/12** | **0/12** |

## Interpretation

1. **Recall is tied at the ceiling and stays tied on the oblique turns.** Both
   arms fired the target on all three symptom-only positives (B1–B3), which
   share no lexical cue with either description — so the interrupt/verb-framing
   costs *no* recall. That was the live risk (a sharper opener muddying the
   relevance signal); it didn't materialise.

2. **The discriminating round separated the arms on precision — and the edge
   goes to the shipped (NEW) wording.** On trap T1, "help me write a better
   description for my skill so it triggers well," the label-shaped control
   over-fired the target on 2 of 3 judges; the shipped interrupt/verb-framed
   description over-fired on 0 of 3. Mechanism: FLAT leads with the *noun*
   ("Methodology and tools for A/B testing skill **descriptions**"), which
   lexically attracts a request to *write a description*; NEW frames the skill
   by the *verb* ("**validating**… whether a description actually **fires**"),
   keeping it out of `intrinsic-prompt-design`'s authoring lane. Only the
   description line differed between arms, so the gap is attributable to it
   (discipline #2). This is a *better* outcome than the #28 Tier-1 run, which
   tied on every axis — here Round 2 actually discriminated.

3. **What this does NOT show (discipline #1, restated with the number).** An
   explicit router reads every description by construction, so this run cannot
   measure whether NEW's opener *wins attention under load* — the headline
   reason for an interrupt-shaped description. It measured routing precision and
   recall, not attention-capture. n for the attention claim is still 0; that is
   a Tier-2 question, and the count-skill-firings.sh harness is the instrument
   for it. The precision edge is also small-n (3 judges/arm): the direction is
   clean and mechanistically explicable, but it's a tiebreaker-grade signal, not
   a large effect.

**Net:** Tier 1 raises **no veto** — recall held and no trap fired, so routing
accuracy is intact — and the one precision edge (T1) is a non-decisive bonus,
not a green light: per the skill's own rule, a Tier-1 win can only fail to block
a rewrite, never confirm it. So the shipped description stands as the candidate,
and the claim it was written to make — better firing under attention — remains a
Tier-2 question at n=0, named as such. That pairing — a real number plus the
question it cannot answer — is the skill passing its own bar.
