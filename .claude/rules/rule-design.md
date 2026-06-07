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

## When it's working

Each rule has one job and loads exactly when it's relevant; rules reference each
other instead of repeating; the path scope is neither so broad the rule loads as
noise nor so narrow it misses its own cases.
