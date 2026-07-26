---
paths:
  - "**/*.py"
  - "**/*.sh"
  - "**/*.js"
  - "**/*.ts"
  - ".github/workflows/**"
  - ".github/scripts/**"
---

# Run a local code review before opening a PR that contains consequential code

Before opening a pull request whose diff includes executable code that **runs in CI,
touches a credential, or gates a merge**, run `/code-review` locally and address what it
finds. Say in the PR body that you did, and what it caught.

## Why this exists rather than leaving it to CI

The CI reviewer in this repo (`.github/prose-review-protocol.md`) checks changes against
`.claude/rules/`. It deliberately holds bug reports to a high bar and is told that the
tests and deterministic guards already cover code correctness. That is the right posture
for a conventions reviewer, and it leaves a real gap: **nothing on the PR path hunts for
bugs.** The unit tests catch what they were written to catch, which by definition is not
the class of mistake nobody anticipated.

Anthropic's `/code-review` plugin is built for exactly that gap — parallel bug agents
with an independent validation pass. Running it locally, before the push, is also the
cheaper place: a defect caught pre-push costs one edit, the same defect caught in review
costs a round trip, and caught after merge it costs a revert on a branch other people
have already built on.

Two things that would otherwise make it unsafe do not apply locally. It is not holding
repository credentials, and it is not reading a diff that an untrusted party wrote.

## The trigger is consequence, not size

A line count is the wrong test. Ask instead:

- Does this code **run in CI**? A workflow step, a script a workflow invokes, a hook.
- Does it **touch a credential** — read a token, pass one to a subprocess, write one to a
  file or an output?
- Does it **gate a merge**, or decide what gets published, posted, or deleted?

Any one of those, review it. A 30-line validator that decides what reaches a public
comment earns the pass; a 300-line refactor of a local scratch script does not.

## What "address what it finds" means

Not "agree with all of it." A finding you judge wrong is a finding you say is wrong, in a
sentence, in the PR body — which is this repo's governing rule (*state the why*) applied
to a review verdict. What is not acceptable is running it, seeing findings, and pushing
without mentioning them.

## Scope note

`/code-review` is Anthropic's plugin, used here for what it is good at: bugs in code. It
is **not** a substitute for the CI prose reviewer, and the CI reviewer is not a substitute
for it — one reads code for defects, the other reads changes against this repo's written
conventions. Neither has been made to do the other's job, deliberately.
