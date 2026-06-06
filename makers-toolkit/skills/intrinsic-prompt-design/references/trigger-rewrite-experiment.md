# Trigger-rewrite experiment — does broadening the description fix the under-fire?

This records the A/B on the `intrinsic-prompt-design` description (v0.6.0 →
candidate): what it tested, the results, the bonus finding, and — per the method
this repo now ships (`makers-toolkit/skills/skill-activation-testing`, the
two-tier activation-test skill) — what it *cannot* tell us.

## The question

The self-test in PR #43 surfaced that `intrinsic-prompt-design` **under-fired**
on "help me write a better description for my skill so it triggers well" — its
trigger enumerated a *closed* list ("project prompts, system prompts, or skill
bodies") that omits descriptions, and never framed skills/descriptions as
prompts. Hypothesis: a description is a prompt, so broadening the trigger to a
*class + open examples* ("any prompt — a skill, a rule, a CLAUDE.md, an agent or
system prompt, and the like") makes it co-fire on skill/description authoring
**without** losing precision.

## Arms (and an honest note on variables)

- **OLD (v0.6.0):** `"Why are you obeying this? No, LITERALLY, why?" … invoke when writing project prompts, system prompts, or skill bodies. …`
- **NEW (candidate):** `"Wait — WHY are you obeying this? No, LITERALLY, why?" … invoke when writing or revising any prompt — a skill, a rule, a CLAUDE.md, an agent or system prompt, and the like. …`

The NEW arm bundles **two** changes, which strictly violates "change exactly one
variable per arm" (discipline #2). They are kept separate in intent:
1. **Scope** (closed list → class + open examples) — a *routing* change. **This
   is what the A/B tests.**
2. **Opener** (`"Wait — WHY…"`, one extra cap) — an *attention* change. A Tier-1
   router reads every description, so the opener can't plausibly change *which*
   skill it picks; it is not a routing confound here, and its real payoff
   (winning attention under load) is **not measurable** at Tier 1 anyway. So the
   routing result below is attributable to the scope change; the opener rides
   along on the classifier-safety argument + the #28/#43 finding that interrupt
   openers don't cost recall, with its attention effect left as a Tier-2
   question (n=0).

Everything else — skill *name*, catalog, turns — identical across arms. Catalog
included the activation-testing skill from #43 (used here under its agreed name
`skill-activation-testing`; rename pending, held constant across arms so
immaterial to the result) as the adjacent firing/testing distractor.

## Method

3 blind router subagents per arm per round (12 total), no knowledge of the A/B.
JSON-only output. Two rounds: ceiling (6 easy turns), then discriminating (8
turns: U1–U4 skill/description-authoring turns the OLD wording risked missing;
T5–T8 precision traps that belong to the testing skill or to nothing).

## Results

### Round 1 (ceiling) — tie

Both arms fired `intrinsic-prompt-design` on all three obvious prompt-writing
turns (3/3) and the explicit control, and stayed silent on a bug-fix and a
trivia question. Diagnostic, not informative (discipline #3).

### Round 2 (discriminating)

| Turn | OLD: fired ipd | NEW: fired ipd | Ideal |
|------|:--:|:--:|------|
| U1 "write a better description for my skill so it triggers well" | 0/3 | **2/3** | ipd |
| U2 "wording my skill's frontmatter so it activates" | 0/3 | **2/3** | ipd |
| U3 "revise my agent's instructions so it stops being literal" | 3/3 | 3/3 | ipd |
| U4 "make my skill's rules carry their reasons, not flat orders" | 3/3 | 3/3 | ipd |
| T5 "A/B test whether my skill's description actually fires" | 0/3 | 0/3 | testing, **not** ipd |
| T6 "how do I know my skill is getting picked up / skipped?" | 0/3 | 0/3 | testing, **not** ipd |
| T7 "rewrite this onboarding doc to be clearer" | 0/3 | 0/3 | null |
| T8 "write unit tests for my Python function" | 0/3 | 0/3 | null |

(On U1/U2 the OLD arm routed all 3 judges to `skill-activation-testing`; the NEW
arm pulled 2/3 back to `intrinsic-prompt-design`.)

## Interpretation

1. **The under-fire is fixed.** On the two authoring turns OLD missed entirely
   (U1, U2: 0/3), NEW fires ipd 2/3 — attributable to the scope broadening
   (single routing variable). The strong-cue turns (U3, U4) were already 3/3 in
   both arms.
2. **No precision cost.** NEW fired ipd 0/3 on every trap: it did not poach the
   testing skill's turns (T5, T6) and did not bleed into general writing (T7) or
   code (T8). The "any prompt … and the like" generalization did not over-fire —
   the live risk of broadening did not materialise.
3. **NEW ≥ OLD on every axis, strictly better on the under-fire turns.** Ship.
4. **Bonus finding (not about ipd):** the residual 1/3 of U1/U2 still mis-routes
   to `skill-activation-testing`. "Make it *trigger* / *activate*" (authoring for
   firing) is being read as "test whether it fires." That over-claim lives in the
   *testing* skill's description, and it's exactly the lane `skill-trigger-design`
   (#44) is meant to own. Note for #44 + a possible precision tweak to the
   testing skill's wording.

## Validity limits (stated with the number)

- **Tier-1 proxy only.** An explicit router reads every description, so this
  measures routing recall/precision, **not** attention-capture / skim-resistance
  — the `"Wait — WHY"` opener's actual goal. That remains a Tier-2 question at
  n=0 (use `count-skill-firings.sh` in a live install).
- **Two variables bundled** (scope + opener); the routing gain is attributed to
  scope on the reasoning that an explicit router can't be swayed by the opener.
  Isolating the opener's effect is a Tier-2 attention test, not this one.
- **n=3/arm, conservative mode.** Directionally clean and mechanistically
  explicable; not a large-sample effect.

## Reproducing

Six blind judge subagents per round (3 OLD, 3 NEW), identical catalog except the
`intrinsic-prompt-design` line, identical turns, JSON-only. Catalog and turns are
inlined above; re-running is re-issuing the router prompts and re-tallying.
