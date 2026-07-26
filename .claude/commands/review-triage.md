---
description: Sort the prose reviewer's comments on a PR into real / false positive / rule gap
argument-hint: <pr-number>
allowed-tools: Task, Read, Grep, Glob, Bash(gh pr view:*), Bash(gh pr diff:*), Bash(gh api:*)
---

Triage the prose reviewer's comments on pull request **$1**.

## Why this is a command and not a second CI job

The reviewer runs in the cloud on untrusted input with no power to act. This runs on the
operator's machine with real tools. Feeding the first's output into the second is a
privilege boundary, so it is crossed deliberately, by the operator asking for it — not
automatically when comments land.

## What to do

1. Fetch the reviewer's comments on PR $1:

   ```
   gh api repos/{owner}/{repo}/pulls/$1/comments --paginate
   ```

   The reviewer's comments carry a trailing `<!-- prose-review:<rule> -->` marker. Ignore
   comments without it — those are human.

2. Launch the `review-triage` agent with those comments, the PR diff, and the rule text
   for every rule cited. It returns a verdict per comment.

3. Present the verdicts to the operator grouped by category, shortest first. For each,
   show the reviewer's claim in one line, the verdict, and the reasoning in one or two.

4. **Do not post anything and do not edit any file until the operator says which
   verdicts to act on.** The agent that read PR-derived content does not hold the pen,
   and neither do you until asked.

5. Once approved:
   - **real** → apply the fix, or note it for the author.
   - **false positive** → post a brief reply on the comment thread saying why, and add a
     one-line comment to the falsified-findings issue describing the *pattern* (not this
     instance).
   - **rule gap** → the rule text did not decide the case. Propose the rule edit as its
     own change; do not fold it into the PR under review.

## The point of the exercise

The reviewer's findings measure the change. The reviewer's **errors** measure the rules.
A false positive means the reviewer applied the rule text faithfully and still got the
wrong answer, which makes the text the defect. That is the only signal in this loop that
improves the rules rather than the code, so it is worth the extra step to capture.
