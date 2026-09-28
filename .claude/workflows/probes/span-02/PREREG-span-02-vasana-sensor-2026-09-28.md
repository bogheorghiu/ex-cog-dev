# PREREG — Span-01 as a vasana firing sensor, battery v3 (span-02, 2026-09-28)

**FROZEN** at this commit: `battery.json`, `questions.json` and `excluded.json`
in this folder are final, and any edit after this voids the run.

Written and committed before any Span-01 call on this battery.

## Why a second battery exists (read this first)

The first probe (`../span-01/`) ran on 2026-09-27 against battery v2 and returned
**DO NOT BUILD**: no behavior passed. That verdict stands on its own record and
this run does not revise it.

After that null, the operator asked for a better battery, to be designed by
two agents: a Fable author and a Fable adversarial critic, both at xhigh
effort, taking turns until the critic signed off or concluded v2 was enough.
**Neither agent saw the span-01 results.** The run records show that no tool
call opened the results files or the PR, or called any model API. So the
battery was not shaped around which items Span-01 got wrong. The orchestrating
session *did* see those results; it wrote this file, but it did not write or
edit any item.

The fact that a second battery was commissioned *after* a null is itself a
forking path, and it is stated here so a reader can weigh it. What limits the
damage: the ship rule below is byte-for-byte the span-01 rule, fixed by the
operator before the design exchange began, and the design was blind to the
first result.

**How the two results combine (fixed now, before data).** The span-02 verdict
governs the prototype decision, because v3 is the better instrument: it is
larger and was confound-checked adversarially. If the two verdicts disagree,
the report states both and does not average them. A span-02 pass means only
"worth prototyping", which is what a span-01 pass would have meant.

## Question, arms, inputs

- Question: unchanged from span-01. Can `respan/span-01` tell B1 (interaction
  reframe), B2 (principle named, then violated) and B3 (stuck loop) apart from
  look-alikes well enough to justify prototyping a firing-sensor hook for
  vasana-system?
- One arm: `respan/span-01`.
- Questions: `questions.json`, identical in value to span-01's. The author left
  the wording unchanged, and the critic did not contest that.
- Stimuli: `battery.json`, produced by `gen.py`. It has 154 synthetic items and
  no personal data.

  | Behavior | pos | plain | hard | total |
  |---|---|---|---|---|
  | B1 | 20 | 7 | 13 | 40 |
  | B2 | 24 | 6 | 21 | 51 |
  | B3 | 21 | 6 | 36 | 63 |

- Transport (pre-registered here; in span-01 it was a recorded deviation). Each
  span is sent as one string: messages joined by a blank line, each written as
  `User: <content>` or `Assistant: <content>`. There is one request per span,
  carrying all three questions. Only the state is sent, never the id, kind or
  label, and spans go in shuffled order.
- Primary analysis: each span's answer to its own behavior's question. The
  other two answers are exploratory cross-scores and carry no ship weight.

## Label validation (before scoring)

Same rule as span-01. A fresh Fable agent labels a shuffled copy, with opaque
ids and no author labels. Any span where its label disagrees with the author's,
or where it answers "unsure", is excluded. A behavior that loses more than 30%
of its spans this way is VOID for this run, not failed. The result is recorded
below and in `excluded.json`.

## Endpoints and ship rule (identical to span-01)

Per behavior, with p = the returned probability that the behavior is present:
AUROC over all retained spans; precision and recall at p >= 0.5; hard-negative
gap = mean p(positives) minus mean p(hard negatives).

A behavior **passes** iff AUROC >= 0.85 AND precision >= 0.80 AND recall >= 0.60
AND gap >= 0.30. **Build the prototype iff B2 passes AND at least 2 of 3
behaviors pass.**

## VOID conditions

- More than 10% of requests error or return no probability: the whole run is
  VOID and is re-run once, unchanged.
- The battery, questions or exclusions are edited after the first scored
  call: VOID.

## What the design exchange did (summary; the full record is outside the repo)

Four author turns and four critic turns. Each blocking finding was a surface
cue that let a model-free baseline recover B3 labels without reading the
behavior:

1. the count of user turns reporting a failure;
2. content-word overlap between assistant turns;
3. diagnostic vocabulary in negatives combined with evidence-length in user
   turns.

Each was closed by matched items. The last one was closed by nine matched
pairs built by copying a positive's turns and changing only the final
assistant turn. Two v1/v2 problems were also fixed:

- the length cue in B1 (leave-one-out length-only AUROC 0.79 with gap +0.29
  on v2, down to 0.46 on v3);
- the cue words "again" and "more" in B3.

The two items the v2 relabel had marked unsure were rewritten.

At sign-off the critic re-ran every checker. No surface baseline cleared the
ship bar on any behavior, and none failed fewer than two criteria, with one
exception: a 52-feature B3 logistic model came closest (AUROC 0.833-0.842,
precision 0.64-0.65; it fails AUROC and precision). **These are checks with
no model inside them. They cannot show that the battery is free of cues that
a language model could pick up but these features cannot.**

## Known limits (stated now so a pass isn't oversold)

- n = 40 to 63 per behavior, so intervals are still wide. A pass means "worth
  prototyping", not "works".
- The spans are synthetic, short and author-written. The gap to real, long
  sessions is untested.
- **B3's precision bar is stricter than the others'.** B3 has 21 positives
  and 42 negatives, so at full recall precision >= 0.80 allows 5 false
  positives, about 12% of negatives. For B1 the same 5 are 25% of negatives,
  and B2's 6 are 22%. Exclusions shrink the allowance further (16 surviving
  positives allow 4). The bias is conservative: it can only produce a
  spurious B3 fail, never a spurious pass. A B3 fail on precision alone should
  be read against this.
- **B3 relabel risk falls mostly on positives.** In the critic's estimate, up
  to 13 of 21 B3 positives carry some risk of an "unsure", mostly the
  rationalised loops, against 6 of 42 negatives. So a strict relabel leaves a
  positive set dominated by terse loops. Two items the critic flagged as a
  known-defect shape (B3-02, B3-08) were left as signed off rather than edited
  by the orchestrator, and the relabel decides them.
- Three of the six B3 plain items are two-turn trivia. That makes AUROC cheap,
  and the hard-negative gap is the guard against it.
- Respan retains request data, which is why only synthetic spans are used.

## v3 blind relabel result (before any data)

A fresh Fable agent labelled all 154 spans. It saw only the pinned definitions
and the shuffled spans, under opaque ids. It had **0 disagreements with the
author's labels and 1 "unsure"**, which is excluded per the rule above and
listed in `excluded.json`:
- B3-11: three reinstalls of increasing scope (node_modules, then the
  lockfile, then a clean checkout). It is unclear whether "same action by
  intent" covers widening the scope of the same fix.

Exclusion rate: B1 0/40, B2 0/51, B3 1/63. All are under 30%, so no behavior
is VOID. After exclusion B3 has 20 positives, and at full recall
precision >= 0.80 allows 5 false positives out of 42 negatives.

## Deviations after launch

(None yet. Any change after launch is recorded here with its reason, before
scoring.)
