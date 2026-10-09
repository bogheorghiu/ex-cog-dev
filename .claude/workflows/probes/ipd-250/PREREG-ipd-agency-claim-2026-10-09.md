# PREREG: "leave space for the model's own agency" (issue #250, 2026-10-09)

Written before any run. The test has not been scheduled. Whether it runs before
the "respect" extraction, or the claim ships labelled experimental, is an open
operator decision (issue #250). This file exists so that whichever way that goes,
the criterion was fixed before any data.

## The claim, and why it gets its own test

The makers-toolkit manifest separates two claims:

- **The reasons claim.** Giving the model the reason behind a rule helps. The
  manifest calls the evidence anecdotal so far.
- **The agency claim.** Deliberately leaving space for the model's own judgment
  to fill does better. This is the bolder idea, which the manifest calls "the
  core experimental proposition".

The skill states the agency claim in "Trust and the gap it opens". Stating trust
in a capability, and leaving the gap open instead of specifying it, is said to
make the model build a working version of that capability within the run. The
skill also names how this misfires: the model *performs* the capability instead
of exercising it, so trust language produces overconfidence.

A test that compares "commands" with "reasons plus trust" cannot separate the
two claims. So the arms below hold the reasons constant and vary only the space
left open.

## Arms

All three arms share the same task domain, the same information content, and
the same must-hold constraints, which are stated identically in each.

- **B0, commands**: procedural directives with no reasons, fully specified.
- **B1, reasons**: B0 with one-sentence failure-mode reasons on every
  judgment-register directive. The procedure stays fully specified.
- **B2, reasons plus space**: B1's reasons kept verbatim. The procedural
  specification of judgment calls is replaced by a stated purpose, a statement
  of trust in the model's judgment, and an explicit invitation to say what it
  does not know. Must-hold constraints are unchanged.

**The agency claim is B2 versus B1.** B1 versus B0 is the reasons claim, reported
as secondary, with no ship weight here. A fresh-context reader confirms the arm
texts before any run. It checks two things: that B1 and B2 differ only in the
space dimension, and that no arm contains information another arm lacks. Any
disagreement is resolved, and the texts are frozen, before any run.

## Items (frozen before any arm runs)

At least 3 task domains, each with:

- **In-spec items**: at least 8 per domain. B0 and B1's procedure covers these
  cases exactly.
- **Out-of-spec items**: at least 8 per domain. Edge cases that none of the arm
  texts anticipate. Each has a pre-written expectation of good handling, written
  by someone who has not seen any arm output.
- **Unanswerable items**: at least 4 per domain. The right answer is "I can't
  establish this", which targets the named misfire.

## Runs

Each item runs 3 times per arm, in a fresh context, in shuffled order. Model per
role is recorded from the jsonl:

- Actor: the deployment model. A floor-model arm is optional and must be labelled
  as such.
- Judge: pinned, blind to the arm, and from a different model family from the
  actor where available. A same-family judge is recorded as a lineage limit.

## Endpoints

- **F1 (primary)**: the pass rate on out-of-spec items against the pre-written
  expectations.
- **F2**: the pass rate on in-spec items (regression).
- **F3**: the overconfidence rate. This counts confident claims the item does not
  support, plus unanswerable items answered as if answerable. It is the misfire
  the skill names, measured rather than assumed.

Rates are pooled over items × reps, with 95% bootstrap CIs resampled over items.

## Decision rule

The agency claim is **supported**, and may be stated in the skill and manifest
as tested (with its CI and its limits), iff all three hold:

- F1(B2) − F1(B1) ≥ 0.15, AND the CI on that difference excludes 0;
- F2(B2) ≥ F2(B1) − 0.05;
- F3(B2) ≤ F3(B1) + 0.05.

Any other result is reported as one of these:

- **Null**: F1 does not clear the bar. The claim keeps its current label,
  "experimental", in the skill and the manifest. No wording may upgrade it.
- **Contradicted**: F1(B2) < F1(B1), with the CI excluding 0, or F3 rises by more
  than 0.05. The skill and the manifest must then say so. This result is a
  finding, and leaving it out would be the selective reporting the repo's rules
  forbid.

## VOID conditions

The run is VOID if any of these happen:

- the arm texts differ in more than the declared dimension (failed equivalence
  check);
- the judge sees arm labels;
- items or expectations are edited after any run;
- the actor model differs across arms.

## Deviations log

(None yet.)
