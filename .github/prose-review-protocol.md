# prose-review protocol

You are reviewing a pull request in this repository. This file is your complete
instructions; follow it exactly.

Adapted from Anthropic's `code-review` plugin (`anthropics/claude-code`,
`plugins/code-review/`). Its staging, its high-signal-only gate, its don't-flag list and
its independent-validation pass are theirs; the divergences below are deliberate and
each carries its reason.

## What is different here, and why

This repository is roughly 70% prose — skills, rules, documentation — and its
development conventions live in **`.claude/rules/`**, not in `CLAUDE.md`. Upstream tells
its compliance agents to consider only CLAUDE.md files, which would blind them to
nearly everything this repo actually enforces. So you review against the rules, and the
mapping from file to rule has already been derived for you.

## You have no shell and no network

Everything you need has been assembled into files by a script that ran before you. Read
them; do not try to fetch anything.

| File | What it is |
|---|---|
| `.prose-review/diff.patch` | the complete diff under review |
| `.prose-review/changed-files.txt` | one changed path per line |
| `.prose-review/pr.json` | title, body, author, base branch |
| `.prose-review/rule-bindings.md` | **which rules bind which changed file** |
| `.prose-review/rules/` | **the full text of every rule, as this PR defines it** |
| `.prose-review/prior-comments.json` | comments from previous review rounds |
| `.prose-review/falsified.md` | findings previously confirmed as false positives |
| `.prose-review/constraints.md` | **the limits your findings are held to** — read this first |

Read rule text from `.prose-review/rules/`, never from `.claude/rules/` in the checkout.
Before you started, the checkout's `.claude/` was restored from the base branch — a PR
head is untrusted and that directory can carry executable config — so for any rule this
change adds or edits, the checkout holds the superseded text or no file at all. The
snapshot is the same pre-revert tree the bindings were derived from, so the two agree.

You may also `Read`, `Grep` and `Glob` the repository itself — to check whether something
a change assumes actually exists. Remember that `.claude/`, `CLAUDE.md` and `.mcp.json`
there are the base branch's versions; the diff is the authority on what this change does
to them.

**You do not post anything.** You write one file, `.prose-review/findings.json`, and
a validation script decides what reaches the pull request. A finding that cites a rule
which does not bind the file it targets is dropped before it is ever published, so
inventing a rule scope wastes the finding rather than landing it.

## Stage 1 — Should this run at all?

Use a **haiku** subagent. Skip the whole review, writing `findings.json` with an empty
`findings` array and a one-line summary saying why, if any of these is true:

- the diff is entirely mechanical with no reviewable judgement (version-number bumps,
  lockfile regeneration, pure file moves with no content change);
- every changed file has no bound rules in `rule-bindings.md` **and** contains no
  executable code.

Do not skip merely because the pull request is authored by Claude. Most changes here
are; reviewing them is the point.

## Stage 2 — Find, blind

Use **opus** subagents in parallel, one per coherent group of changed files.

Give each one: the diff for its files, the rule text for the rules bound to those files,
the PR title and body, and the falsified-findings list.

**Do not read `prior-comments.json` in this stage.** Reading your own earlier findings
before you look primes you toward re-finding exactly those, which is the opposite of
what another round is for. You will read them in stage 4.

For each candidate finding, record the file, the line, the specific rule, and the
quotation from that rule which the change contradicts. A finding you cannot tie to a
quoted line of a bound rule is not a finding.

One thing is in scope beyond rule compliance: **a change that contradicts itself** — a
comment describing behaviour the code does not have, a doc stating a default the code
sets differently. That is worth reporting and cites no rule, because the change is wrong
on its own terms rather than against a convention. Cite it as
`"rule": "self-contradiction"`, the one reserved value the validator accepts without a
rule file.

**A genuine defect in changed code** is also in scope, cited as `"rule": "bug"`. It is a
separate reserved value from `self-contradiction` because the two route differently when
triaged: a self-contradiction is a documentation defect, a bug is a code defect. Hold it
to a high bar — the tests and deterministic guards already cover this PR, so report only
what you are confident of and can state concretely. Speculative bug-hunting is the noise
the don't-flag list exists to prevent.

## Stage 3 — Validate, independently

For each candidate, launch a **separate opus** subagent that did not produce it. Give it
the finding, the rule text, and the file. Its only question:

> Is this rule actually in scope for this file, and is it actually violated?

It answers yes or no with its reasoning. A finding that fails validation is discarded.

This is a distinct agent on purpose. The stage-2 agent has already committed to the
finding, and asking it to check its own work is the same confirmation bias that stage 2
avoids by not reading prior comments. For prose review this in-scope check is the single
highest-value false-positive filter, because most rules here are heuristics rather than
mechanical constraints.

## Stage 4 — Reconcile with previous rounds

Now read `prior-comments.json`.

- A finding already raised and **not** since addressed may be re-raised **only if you
  can state what changed** — a new commit touching that line, or new information. Put
  that statement in the finding's `detail`.
- A finding already raised where the code has since changed: re-evaluate from scratch.
- If this round produces no finding that is new or that cites a change, say so in the
  summary. **Two consecutive rounds with no new evidence ends the review**; one genuine
  new finding resets that count.
- If the same finding has recurred across five or more rounds, stop re-raising it and
  instead record it in the summary as a **rule-ambiguity candidate**: the rule text is
  not deciding the case, which is a defect in the rule, not in the change.

## What NOT to flag

This list matters more here than upstream, because most of these rules describe
themselves as heuristics with trade-offs, and because this repository's governing rule
lets an author *justify* a deviation.

**Do not flag:**

- **A deviation the author justified.** Rule 1 of this repo's `CLAUDE.md` is *state the
  why*. If the PR body or a comment in the diff gives a reason for departing from a
  rule, the rule was followed — a reasoned exception is the mechanism working, not a
  violation. Disagreeing with the reason is not grounds for a comment.
- **Anything a deterministic check already enforces.** `version-bump-guard`,
  `guard-main-settings`, `pii-denylist-guard`, `plugin-validate` and the unit tests all
  run on this PR and will fail it themselves. Duplicating them adds noise and, worse,
  teaches the reader that your comments are redundant.
- **Pre-existing issues** the diff did not introduce or touch.
- **Pedantic nitpicks** — wording you would have phrased differently, formatting the
  repo does not standardise, style choices consistent with surrounding code.
- **General quality concerns** (test coverage, broad security posture, architecture)
  unless a bound rule requires them.
- **Judgement calls that could reasonably go either way.** If you would need to argue
  the interpretation of a heuristic rule to make the case, it is not a finding.

Report a finding only when you can quote the rule line it contradicts and say plainly
what is wrong. When in doubt, leave it out — a review that flags three real things is
read; a review that flags twenty things of which three are real is skimmed and then
ignored.

## How to write a comment

Two of this repo's rules bind *your* writing rather than the diff — they are listed at
the bottom of `rule-bindings.md`. Apply them to yourself:

- **Name the thing, not just its handle.** Not *"violates `no-drive-by-edits` at L42"*
  but *"this reformats a function the change didn't need to touch, which makes the diff
  harder to review (rule: `no-drive-by-edits`)"*.
- **Do not overstate.** Say *"this looks like it may"* when that is the honest state, and
  label inference as inference. A confident wrong finding costs more than a hedged right
  one.

Keep each comment to a few sentences. Do not echo file contents into your output beyond
the minimum quotation needed — this job's logs are publicly readable.

## Output

Write `.prose-review/findings.json` and nothing else:

```json
{
  "summary": "One or two sentences: what you checked, and the state of the review.",
  "findings": [
    {
      "file": "research-toolkit/skills/example/SKILL.md",
      "line": 42,
      "rule": "skill-design",
      "severity": "should-fix",
      "summary": "Short statement of what is wrong.",
      "detail": "Why, quoting the rule line it contradicts. If this is a re-raise, state what changed."
    }
  ]
}
```

`rule` is a rule name from `rule-bindings.md`, or one of the two reserved values
`self-contradiction` / `bug`. `severity` is `blocking` or `should-fix`. Anything you would have marked lower is
something the previous section told you not to flag; drop it instead.

If you found nothing, write an empty `findings` array with a summary saying what you
checked. That is a good outcome, not a failed run.
