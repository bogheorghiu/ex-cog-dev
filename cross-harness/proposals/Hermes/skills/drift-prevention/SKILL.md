---
name: drift-prevention
description: "Prevent drift: never restate code or skills in prose."
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Drift, Prose, Documentation, SingleSourceOfTruth, Authoring]
---

# Drift Prevention — one copy per fact, prose for what code cannot say

A discipline for authoring and reviewing prose next to executable artifacts:
comments, docstrings, READMEs, rule files, skill bodies, docs about skills.
It prevents silent drift — the case where a prose copy of a fact is true the
day it is written and then goes stale with nothing firing, while still
reading as authoritative. It does NOT mean "fewer comments" (some prose is
obligatory — that is the second half) and it does NOT catch real code
defects (a separate job). It is a judgment discipline with a falsification
test, not a script — no dependencies.

## When to Use

- Writing or reviewing any comment, docstring, README, rule doc, or doc ABOUT a skill/agent
- A doc restates what the code or a skill already says
- User says "don't duplicate prose and code", "why not what", "avoid drift"
- Tempted to add an INDEX.md / TOC / manifest when the tree + filenames already index
- A review flag of the shape "this prose restates the artifact"

## The law (most general form)

**Every fact has exactly one authoritative copy.** A second copy of the same
fact — prose restating code, a doc restating a skill, an index restating a
tree — is a liability, not a convenience. Copies are true the day they are
written; nothing fires when the original changes; the copy drifts silently
and keeps reading as authoritative while wrong. Measured, not hypothetical:
in one corpus (ex-cog-dev PR #195), 17 of 21 posted review findings were
prose restating what the code already said.

The general test that applies to ANY artifact pair (comment↔code,
README↔skill, index↔folder tree, doc↔config): **could a fresh reader derive
the second copy from the first?** If yes, the second copy is duplication.
This is the general form — when you meet a new instance (e.g. "don't make an
INDEX.md when the folder tree + filenames already serve as the index"),
reduce it to this law rather than adding a new rule.

## The preference order (most specific form)

For any statement that needs to exist, home it in this order — never nowhere:

1. **In the code itself** — naming, structure, a named guard, a test whose
   name states the invariant. A variable named `redacted_files` says more
   than a comment about a "collapse-then-redact" flow, and cannot go stale.
2. **Change the code so the sentence is unnecessary** — a wrong *reason*
   explained in a comment is still prose that rots; tighten the condition so
   there is nothing left to explain.
3. **A comment** — only when it genuinely cannot live in code. Reserve it
   for what code cannot say: why X was chosen over Y, a historical incident,
   a cost trade-off, a decision that binds a future reader.
4. **A separate document** — one file holding the few genuinely important
   things code cannot hold (design rationale, incident record, trade-off
   ledger). Never bloat it; every addition faces the same test as a comment.

Skills and agent definitions are CODE here, not documents: they are the
executable the harness runs. A doc that restates what a skill already says
is the same duplication and rots the same way.

## Quick Reference

- Prose documents **why**, code documents **what** — never restate the what in prose.
- Comments explain **why, not how**; skip a comment whose content the code already expresses.
- A stated **reason** is prose too — it drifts the same way as a stated behavior.
- Never duplicate across: prose↔code, doc↔skill, index↔tree, doc↔config.
- In-code pointer beats restatement: a comment citing the canonical source
  (e.g. `see #234 for the full discussion`) instead of re-copying the rationale.
- For a list of "what exists", prefer the filesystem as the catalog
  (`read_file`/`search_files` the tree) over a hand-maintained inventory file.
- Prefer making it discernible from code BEFORE writing prose — prose is the fallback, not the first move.
- The why may never go nowhere: if it can't live in code, it MUST live in prose. This rule is not "fewer comments".

## Procedure

1. **Inventory the pair.** Before writing prose, ask: which executable
   artifact does this sit next to? What does it already express?
2. **Try code first.** Rename the variable, restructure, add the named
   guard, write the test whose name is the invariant.
3. **Try changing the code** so the sentence is unnecessary — especially
   for stated *reasons*: a tighter condition beats a better explanation.
4. **If it still can't live in code, write it — never abstain.** The why
   exists; only the home was undecided.
5. **Point, don't restate.** For rationale that lives in another canonical
   place (an issue, a design doc), write a one-line pointer in the code
   comment, not a copy of the rationale.
6. **Falsify.** Hand the code WITHOUT the comment to a fresh reader (a
   floor-model agent is the cheap version) and ask if they can say what the
   comment says. Yes → duplication; cut it or push it into code. No → the
   comment earned its place.
7. **For docs about skills/artifacts:** same test — could a fresh reader
   derive the doc from the skill itself? If yes, the doc is the second copy;
   delete it or reduce it to a pointer.

## Pitfalls

- **Misreading as "fewer comments".** The rule is "one copy per fact, prose
  for what code cannot say" — a session that reads it as "minimize prose"
  has made the rule worse than its absence. The why must exist.
- **The doc that restates the skill.** A SKILL.md is the executable; a
  separate doc describing the same skill is a second copy and will rot when
  the skill changes. Point to the skill (`skill_view`), don't summarize it.
- **The INDEX.md trap.** A hand-written index of files is a copy of the
  filesystem that nothing keeps in sync. Use `search_files` (target=files)
  on the tree, or generate the index mechanically — never hand-maintain one.
- **Status/contradiction drift.** A doc header saying "not yet enforced"
  while CI enforces the rule is already a diverged copy. Derive status
  claims from the enforcement mechanism, not from prose.
- **Restating the what as a "helpful summary".** A comment narrating a
  script's steps, a header enumerating which tests touch disk — each is true
  today and false after the next commit.
- **Overselling.** Prose rules do not catch code defects; don't claim they do.

## Verification

Single falsification check: take the code (or skill) WITHOUT the candidate
prose, hand it to a reader who did not write it (a fresh `delegate_task`
with a cheap model works), and ask what the prose would say. If the reader
reproduces the prose's content from the artifact alone → delete the prose or
push the fact into the artifact. If the reader cannot → the prose stays.
