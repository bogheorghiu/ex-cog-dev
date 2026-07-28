# When the review-addressing loop ends — you decide, and here is the criterion

(No `paths:` frontmatter on purpose: this governs how any pull request in this repo is
driven to completion, not a file type, so it loads every session.)

Addressing review comments is a loop — read what was posted, fix, push, and the push
starts a fresh review. **Stop when a round posts zero comments, then run one more round
and stop when that also posts zero.** Not "when I have addressed the findings", which is a
claim about your own work rather than a result.

## Why this lives here and not in the reviewer's instructions

It used to be in them, and it had to be removed: every round is a separate CI job, so
nothing carries one round's *outcome* into the next. The reviewer is handed each previous
round's posted comments — that is what its reconcile stage reads — but a list of what was
posted cannot express a round that posted nothing. So it can see the previous rounds and
still has no way to know whether one of them was quiet, which is the only fact this
criterion turns on. A rule its reader cannot evaluate is worse than no rule, because it
reads as a live control while being inert.

You *can* evaluate it: you have the run history in front of you. So the criterion is real
here and was fiction there.

## Zero posted, not zero worth fixing

The signal is **comments posted**, not your judgement of their importance. Severity is
already filtered before anything is posted — so a round that posts only nitpicks means
that filter is too loose, which is a defect to fix in the filter, not a reason to declare
the loop finished. Keeping the criterion mechanical is what stops "these are only small
ones" from ending a loop that is still finding things.

## The confirming round is the point, not a formality

A single quiet round is also what you get from a reviewer that silently failed, from a
flaky model round, and from a change so large the finders spread thin. The second round is
what distinguishes those from a genuinely settled change, and it costs one push.

Read both rounds from the run history and the posted comments — not from any agent's
account of what it did, including your own summary of the round you just drove.

## What a quiet round does *not* establish

A round can post nothing because it found nothing, or because everything it found was
argued down internally. Those are opposite facts about the change, and the run's record is
where you tell them apart. Treat "zero posted" as satisfying the stopping rule, not as
evidence the change is clean.
