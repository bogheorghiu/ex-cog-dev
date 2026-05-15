# HANDOFF — Static catalog in SKILL.md vs dynamic discovery in /pattern-library

**Priority:** ASAP — every new pattern added today silently slips through this gap.
**Filed:** 2026-05-15

## The problem

There are two different "catalogs" of patterns in this skill and they drift:

1. **`SKILL.md` → "Available Patterns" section** is a hand-maintained numbered list
   (currently 1–9). When a model loads this skill, this is the catalog it sees.
   New `vasanas/*.md` files are invisible here until someone manually edits the list.

2. **`commands/pattern-library.md` (the `/pattern-library` browse command)**
   does dynamic discovery — it lists every file in `vasanas/`. So the slash command
   sees new patterns immediately, but the in-skill list doesn't.

Concrete evidence: `vasanas/false-consciousness-as-behavior.md` was dropped in
correctly (proper frontmatter, vasana section, template-conformant) but is NOT in
SKILL.md's numbered list. The model would never reach for it from pattern-library
context alone. A second pattern is reportedly inbound — it will have the same fate
unless this is fixed.

## Why it matters

- `record-pattern` tells authors where to save (`vasanas/[name].md`) but says nothing
  about updating SKILL.md. So the natural authoring path produces invisible patterns.
- The static list also calcifies pattern descriptions: each numbered entry has a
  hand-written one-liner that can drift from the file's own frontmatter `description:`.
  Two sources of truth for the same metadata.
- `SKILL.md`'s top-level `description:` frontmatter (the field that controls when
  the skill triggers) also doesn't reflect new patterns' trigger surfaces. Adding
  `false-consciousness-as-behavior` arguably extends what this skill should fire on
  (preaching-fails, information-campaigns-don't-change-behavior) — but nobody is
  updating that field either.

## Options (pick one — don't half-do it)

### Option A — Make SKILL.md dynamic too
Replace the hardcoded list with an instruction: "Read `vasanas/*.md` and synthesize
the catalog from each file's frontmatter `description:`." Cost: every skill
invocation now reads N files. Benefit: one source of truth (the pattern file itself).

### Option B — Generate the list, don't hand-maintain it
Add a pre-commit hook or `scripts/regenerate-pattern-catalog.py` that rewrites
the "Available Patterns" section of SKILL.md from `vasanas/*.md` frontmatter.
`record-pattern` skill then ends with: "run the regen script before committing."
Cost: a script + a hook. Benefit: SKILL.md stays a static, fast-loading file.

### Option C — Make `record-pattern` responsible for both edits
Bake the SKILL.md update into the `record-pattern` skill's instructions, so the
model that adds a pattern also edits the catalog. Cheapest, weakest — relies on
the model remembering. The current gap exists *because* this wasn't enforced.

### Recommendation
**Option B.** Keeps SKILL.md fast to load (matters because skills are loaded eagerly),
removes the maintenance burden, and the regen script is ~30 lines of Python. Wire
it into `record-pattern`'s "Where to Save" step.

## What also needs deciding
- Should the numbered-list entry format be normalized? Newer patterns
  (`false-consciousness-as-behavior`) use YAML frontmatter; older ones use
  `# Title \n **Principle**: ...`. Pick one. The template in `record-pattern`
  uses YAML frontmatter — older patterns should probably be migrated.
- Should the skill's top-level `description:` field be regenerated too, or stay
  hand-tuned for trigger calibration? (Probably stay hand-tuned, but document
  that explicitly so future authors don't get confused.)

## Until this is fixed
When adding a new pattern by hand: **also append an entry to SKILL.md's
"Available Patterns" section.** Do not assume the slash command's dynamic
discovery is enough — the in-skill catalog is the one the model actually reads
when reasoning about which pattern to apply.
