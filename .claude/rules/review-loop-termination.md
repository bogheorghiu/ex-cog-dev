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

## A green check is not a quiet round — it never was

**The prose-review job exits 0 whether it posted ten comments, none, or never ran at
all.** Posting is the job doing its work, not a failure, so a round that found ten
problems reports exactly what a clean round reports: a green tick. And a round that was
gated off — a draft, a fork, Dependabot, the opt-out label — exits 0 deliberately too, so
that an opted-out pull request does not leave a required check pending forever.

So the tick tells you the job started. It does not tell you the reviewer ran, and it
never tells you what it said.

So "all checks pass" is not a reading of the round. Count the posted comments — from
the PR page, or from the API **with `--paginate`** — every time:

```bash
gh api --paginate repos/OWNER/REPO/pulls/N/comments \
  --jq '.[] | select(.user.login=="github-actions[bot]") | "\(.created_at)  \(.path)"'
```

`--paginate` is not optional here. Without it `gh api` returns one page, and a long-lived
pull request outgrows a page quickly — this rule's own branch passed 45 review comments —
so the fetch silently drops the newest round and hands you exactly the false zero the next
bullet describes. Listing each comment with its timestamp beats asking for a count: a
number cannot show you that it stopped early.

Two ways this goes wrong, both observed on PR #195:

- **Believing the tick.** Round 10 posted three findings, every check went green, and the
  three sat unread for five days because the checks looked done.
- **Believing a bad count.** Twice in one session a comment count came back zero from a
  filter comparing `created_at` against a local-clock timestamp — and the timestamps are
  UTC, so the cutoff was hours in the future and matched nothing. A zero you computed is a
  claim; a zero you can see on the PR is a result. Prefer listing the comments with their
  timestamps and looking, over filtering and trusting the number.

Making the job fail when it posts would fix the first half and break more than it fixes:
the reviewer would gate merges on prose judgement, which is the authority this design
deliberately withholds from it. So the check stays green and the reader carries the duty.

**Siblings.** `verify-delegated-work-against-artifacts` is the general form of the
instruction above — judge what ran by its artifacts, not by any agent's account, this rule
being the review-round instance. `verify-claims` carries the same don't-outrun-your-evidence
discipline for your own conversational claims, which is what "a zero you computed is a
claim" applies here.

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
