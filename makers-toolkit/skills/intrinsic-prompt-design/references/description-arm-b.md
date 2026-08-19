# Description arm B — a routing-first candidate, not a replacement

The shipped description stays. This file holds an alternative for
`skill-activation-testing` to decide between, and the reasoning on both sides,
so the decision is made on measurement rather than on whichever text was argued
for most recently.

**Why a candidate rather than an edit.** The shipped wording is the subject of
this skill's only live experiment. Its routing is measured — `firing-experiment.md`
(no recall or precision cost against the previous wording) and
`trigger-rewrite-experiment.md` (recall on two authoring turns went from 0/3 to
2/3). The attention claim it rests on is explicitly at n=0, with a live test
planned. Swapping the text on the strength of an unmeasured objection would
trade a measured baseline for an argued one, and would reset the next activation
test from a regression check into a fresh one.

## Arm A — shipped

```yaml
description: >-
  "Wait — WHY are you obeying this? No, LITERALLY, why?" Now that I have your
  attention: invoke when writing or revising any prompt — a skill, a rule, a
  CLAUDE.md, an agent or system prompt, and the like. That question held you
  where a command gets skimmed — so build prompts on reasons: a command breaks
  at the first edge case, a reason adapts.
```

## Arm B — candidate

```yaml
description: >-
  Invoke when writing or revising any prompt that will steer a model — a skill,
  a rule, a CLAUDE.md, an agent or system prompt, a subagent brief, and the like
  — including when the complaint is about behaviour rather than wording: a
  prompt that gets followed literally, that produces compliant but shallow work,
  or that is skimmed past on the cases it was written for. Covers what each
  directive should carry — a reason where judgment lives, a terse imperative
  where exact execution is the point — and when a rule belongs in a check rather
  than in prose. Not a general prompt-engineering manual: no output contracts,
  instruction hierarchy, prompt security, or evaluation suites.
```

## What B changes, and the objection each change answers

**It opens with the trigger class instead of a rhetorical interrupt.** A
description's job in a catalogue is selection: a router deciding among many
short competing texts benefits from the routing signal arriving first. Arm A
spends its opening on an attention device and names the trigger in its second
clause.

**It carries no doctrine.** "A command breaks at the first edge case, a reason
adapts" is a thesis about prompt design, and the body is where a thesis can be
argued, qualified, and — as the body now does — partly conceded. A claim
compressed into routing metadata cannot carry its own qualifications, so it
routes and asserts at the same time and can only assert the unqualified version.

**It asserts no attention effect.** Arm A's "that question held you where a
command gets skimmed" states as fact the very thing this skill's own experiment
records as unmeasured. Arm B says nothing about attention, so nothing in it can
outrun the evidence.

**It states the scope boundary.** The body now says this skill is about posture
and not the mechanics layer. Saying so in the description lets a router decline
turns that want output contracts or evaluation methodology, instead of firing
and then explaining that it is the wrong instrument.

## What B deliberately preserves

The breadth that the trigger-rewrite experiment actually measured: an open class
with examples ("any prompt that will steer a model — … and the like") rather
than a closed list. That broadening is the single change the experiment
attributes the recall improvement to, so it survives into B unchanged. B also
keeps symptom-shaped cues — followed literally, compliant but shallow — because
the discriminating round showed the routers firing correctly on turns phrased by
symptom with no "write a prompt" lexical cue, and dropping those cues would put
that result at risk for no stated gain.

## The case against B, stated fairly

The interrupt may be doing real work that a routing-first opener loses, and
nothing here has measured that. Arm A's premise is that a description competes
for attention it can lose, and a text that reads as an ordinary catalogue entry
is exactly what that premise predicts gets skimmed. B is the safer text on every
axis that has been measured and the weaker one on the axis that has not. That is
the whole reason this is a test and not an edit.

## How to decide it

Use `skill-activation-testing`. The comparison is only meaningful against the
limits recorded in `firing-experiment.md`:

- **Routing is measurable now.** Recall on in-scope turns, over-fire on traps,
  and — new for B — correct *non*-firing on mechanics-layer turns, which is a
  behaviour arm A's text has no way to produce.
- **The attention claim is not measurable by a router.** An explicit router
  reads every description by construction, so it cannot show whether a text wins
  attention it would otherwise lose. That needs a live harness and firing counts
  per should-have-fired turn.
- **Judges must come from more than one model family**, or the result carries
  the same lineage limit the existing rounds do: three samples of one model are
  one source's opinion sampled three times.

Write the ship rule down before running anything — which endpoint decides, and
what result keeps arm A — so a null reads as a null rather than as licence to
pick the text that was already preferred.

## If B is adopted

Keep the folded block scalar (`>-`). A description written as an inline scalar
breaks on a colon followed by a space, and on a closing quote followed by
trailing text; either failure drops the frontmatter silently, leaving the
component listed but inert. Both arms above are written in the surviving form —
preserve it rather than reflowing to one line. Verify with
`claude plugin validate makers-toolkit` from the repo root, pointing at the
plugin directory rather than the marketplace root.
