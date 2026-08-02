# External contributions: this repo does not take them, and automation assumes that

This repository accepts pull requests from the owner only. Ideas and reports are welcome
as issues; code arrives through an issue and a maintainer-authored change. That is a
standing posture, not a case-by-case judgement — and the CI automation here is built on
top of it, so relaxing it silently would quietly unsafe several other things.

(No `paths:` frontmatter on purpose — this constrains what may be automated anywhere in
the repo, so it loads every session, like `no-sensitive-data-in-repo.md`.)

## The principle underneath

An agentic tool that runs in CI is safe to automate only when **both** hold:

1. **Its input is trusted.** An agentic reviewer reads the diff, so the diff can
   *instruct it*. There is no hardening that makes untrusted input safe to feed an
   instruction-following model — Anthropic says so plainly about their own Actions.
2. **It has no power to act.** Whatever the input persuades it to do, it can only do
   what its credentials and tools permit.

Neither alone is enough. A trusted-input tool with write access is one compromised
account away from a problem; an untrusted-input tool with no power to act is merely
noisy rather than dangerous. The prose-review workflow is built to satisfy (2)
regardless — the model has no shell, no network, and no way to reach the pull request
except through text a validation script chose to send — precisely so that a failure of
(1) is survivable rather than catastrophic.

Stated that precisely because the precision *is* the safety argument. "No power to act"
is a claim about what an injection could achieve, and it holds for the comment path
because a script screens every finding against the rule bindings, the diff, and the
limits. It does not extend to every byte the model emits, and the two exceptions are not
screened alike. The job publishes its work directory as a build artifact, which a
credential scrub rewrites just before upload — that and nothing more. It also prints the
reviewer's closing text to a world-readable log, and that gets **no screen at all**: the
scrub rewrites files on disk, and those bytes were emitted several steps earlier. Both are
real public channels, one weakly guarded and one unguarded, and a rule governing what may
be automated here has to say which is which rather than round either to zero. Whether they
should exist at all is issue #197.

## What this means in practice

- **Fork pull requests get no review.** GitHub gives a fork PR no secrets and downgrades
  its token to read-only whatever the workflow's `permissions:` block says, so a
  credentialed reviewer cannot run there even if we wanted it to. The workflow detects
  this and skips with a clear message rather than failing opaquely three steps later.
- **"Require approval for all external contributors"** stays enabled in the repository's
  Actions settings. Without it, a stranger's first PR runs workflows before any human
  looks at the diff.
- **Do not add a `pull_request_target` or `workflow_run` workflow** to review external
  code. Both run with the base repository's secrets while checking out the contributor's
  code — the exact combination condition (2) exists to prevent. `actions/checkout`
  refuses this by default from **v4.4.0** onward (backported from v7), which is the
  version pinned here — so the backstop is already active, and opting out of it would
  take an explicit `allow-unsafe-pr-checkout: true`. A backstop, not a reason to try.

## If the posture ever changes

It would need all of: a review path that runs on untrusted input with no credentials at
all; a maintainer gate before anything privileged runs; and a re-read of what each
workflow's token can reach. Until then, an outside PR gets a reply pointing at the issue
tracker.

**Background.** Issue #86 records the original analysis and its discussion. This rule is
the distilled standing posture, kept here so a session acts on it without needing to
find the issue.
