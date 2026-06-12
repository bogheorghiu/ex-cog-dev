---
paths:
  - ".claude/rules/**"
---

# Rule design — scoping and composing rules

Designing or editing a rule in `.claude/rules/`. **Apply `skill-design.md`'s
scoping logic to rules** — it transfers almost wholesale; this rule adds only the
rule-specific delta. (Written by *composing with* `skill-design.md` rather than
copying it — which is the principle both rules share.)

## Inherit from `skill-design.md`

The same heuristics govern rules:

- **Tight scope that composes beats broad scope that bundles.** One job per rule;
  several narrow rules that each load only when relevant beat one sprawling rule.
- **Compose, don't fork.** To build on another rule's logic, *reference* it and add
  your delta — don't copy its text (copies drift apart and rot). This rule is the
  worked example.
- **Don't over-tighten.** Avoid splitting into a lattice of micro-rules; if you
  can't articulate why a split earns its cost, it doesn't.

## Split or merge? The tiebreakers

"One job per rule" and "don't over-tighten" pull in opposite directions, and
the gap between them is exactly where a session picks wrong *with this rule in
context* (it happened: PR #122 first bundled speculative-structure and
drive-by-edits under one test-shaped name, `trace-changes-to-the-request`;
owner review split it — the worked example behind issue #124). When the two
heuristics conflict, break the tie with these, any one of which is sufficient
to split:

- **The candidate name names a shared *test*, not a *behavior*.**
  `trace-changes-to-the-request` named the test both halves run;
  `no-drive-by-edits` and `no-speculative-structure` each name a behavior. A
  test-shaped name is the bundling tell.
- **Each half has its own established prior-art name** (YAGNI; "surgical
  changes"). Independent lineage is independent evidence they're separate
  concerns — the anti-reinvention check doubles as a scoping check.
- **The halves fail independently** — a session can over-build without
  drive-by editing, and vice versa. Independent failure modes want
  independent rules.

## When this rule actually loads (firing mechanics — read before authoring)

This rule is path-scoped to `.claude/rules/**`, and the documented trigger is
the **Read tool on a matching file** (verified against the Claude Code memory
docs, 2026-06-12). The docs are **silent** on whether Write-*creating* a new
matching file, Edit, or a Bash `cat` triggers the load — so assume they don't.
The consequence is the failure mode issue #124 records: rule-*creation* is this
rule's highest-value moment and may be exactly when it isn't loaded (the PR
#122 session had only `cat`-ed it). The discipline that closes the gap:
**before creating or renaming a rule, Read this file with the Read tool** — a
`cat` puts the text in front of you but, as far as the docs guarantee, not into
the rule-loading machinery.

## The rule-specific delta (where rules differ from skills)

- **Triggering is path-scope, not a description.** A rule either declares `paths:`
  frontmatter (loads only when a matching file is open — the default; cheap and
  scoped) or has no frontmatter (loads **every session**, the same standing context
  cost as `CLAUDE.md` — reserve that for always-relevant prose conventions).
  Choosing the right `paths:` is the rule's analog of writing a skill's trigger —
  but there is **no firing / attention-scarcity** problem to design around: a
  matched rule simply loads.
- **Rules are not shipped.** They're development guidance, never carried by a plugin
  (a marketplace plugin ships skills / MCPs / agents / hooks — never `CLAUDE.md` or
  rules). So a rule change needs **no version bump**, and a rule can encode a dev
  convention freely without affecting what consumers install.
- **One rule, many paths is fine.** A single coherent concern (e.g. descriptions)
  can path-scope to several file types without splitting into multiple rules — that
  isn't bundling, it's one job that shows up in more than one place.

## Naming

Name a rule with an **imperative action verb** where the name names an action —
`verify-claims`, not `verifying-claims` or `claims-verification`. A rule is itself a
command, so a command-shaped name fits it (the same command-shaped-beats-label-shaped
logic the repo applies to skill descriptions) — and it doesn't undercut
`intrinsic-prompt-design`, because Rule 1 (state the why) keeps the command reasoned,
not bare. A **topic-noun** name stays fine where there's no single action
(`skill-design`, `github-references`, `mcp-interface-contract`): the convention is
*imperative over gerund/infinitive*, not *verb over noun*.

## When it's working

Each rule has one job and loads exactly when it's relevant; rules reference each
other instead of repeating; the path scope is neither so broad the rule loads as
noise nor so narrow it misses its own cases.
