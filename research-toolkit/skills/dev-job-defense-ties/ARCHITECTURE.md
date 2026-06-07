# dev-job-defense-ties — architecture & decisions

> SDD artifact (system-pilot Step 4): the durable record of *what the system is*
> and *why it's shaped this way*. The implementation satisfies this; if they drift,
> this wins or gets updated — don't let them silently diverge.

## Three independently swappable parts

| Part | Lives in | Layer | Swappable? |
|------|----------|-------|-----------|
| **Mechanism** | `SKILL.md` | conductor/spec | no — it's what the skill *is* |
| **Domain** (what we scan for) | `reference/domain-*.md` (ships) + `<config>/domain/*` (user) | spec/data | yes — extend/narrow per field |
| **Profile** (the operator's line) | `<config>/profile/*` (never shipped) | data | yes — per operator |

The public repo ships **no profile** (no politics). It ships a **generic-dev** domain pack as the default and a **gamedev** overlay as an example; a user's own profile and any extra overlays live outside the plugin so they survive reinstalls.

## Config store (external, OS-agnostic)

```
<config>/                 # $XDG_CONFIG_HOME|%APPDATA%|~/.config → /dev-job-defense-ties
  location                # pointer (canonical base only) → a custom dir, if set
  profile/threshold.md    # the red line
  profile/settings.md     # engagement (ask|always|never), chosen field/domain
  domain/<name>.md        # installed overlays, one file each
```

**Why element-per-file (decoupled):** amend-in-place is then non-destructive — changing engagement rewrites `settings.md` only, never the threshold. The deterministic layer does whole-*element* IO; decoupling keeps "whole element" small.

**Why a script, not just files:** "where does this land, OS-correctly, surviving reinstall, never in `/tmp` or the plugin cache?" is a determinism question — the one thing the model does unreliably. The script owns *only* that (locate + element IO + path safety + self-description). Everything about *content* (the questions, the prose, edits, interpretation) stays with the model.

## Script interface (`scripts/config.py`) — SOLID

- **Single responsibility:** `ConfigStore` = locate + element IO + safety. CLI = dispatch only.
- **Open/closed:** elements are addressed generically as `<category>/<name>`; new categories (profile, domain, …future) need no code change.
- **Self-describing (MCP-style):** `describe` emits the interface for the *model*, so SKILL.md doesn't hard-code usage that can drift.
- **Safety:** `<category>` and `<name>` must each match `^[a-z0-9][a-z0-9-]*$` (no dots/slashes) → no path traversal; `set-location` refuses `/tmp` and cache-like paths.

| Command | Job (deterministic) |
|---|---|
| `describe` | print the interface + resolved location + current elements, for the model |
| `locate` / `set-location <dir>` / `clear-location` | resolve / redirect / reset the config dir |
| `list` | list stored elements as `category/name` |
| `get <cat/name>` | print element, or `NO_ELEMENT` |
| `put <cat/name>` | write stdin → element |
| `remove <cat/name>` | delete element |

## First-run onboarding (conductor)

1. *(skippable, non-dev-safe)* offer to point at an existing config elsewhere; "if this means nothing to you, skip."
2. opt-in (if auto-fired) → 2–4 threshold questions (partial allowed) → field/domain pick (default generic-dev; offer to install the gamedev overlay).
3. persist choices (`put profile/threshold`, `put profile/settings`); engagement `ask|always|never`.
4. **edit-in-place:** "add X to hard-stops" / "switch me to always" → `get → model edits → put` the one element.

## Tests (TDD)

- `scripts/test_config.py` — interface + round-trips + decoupled-edit + path safety + OS-agnostic resolution.
- `test_screen_efficiency.py` — lexicon-coverage proxy over the shipped domain pack(s).
- `test_skill_structure.py` — frontmatter/convention linter (kept in sync with the vasana-system copy it was lifted into).

## Crediting / composition

Built per `makers-toolkit:system-pilot` (layers, schema-first, verify-in-hand) and `intrinsic-prompt-design` (SKILL.md register). Firing/activation is **not** tested here — that's `makers-toolkit:skill-activation-testing` (Tier-1 proxy + the `count-skill-firings` hook), referenced, not duplicated. Threshold derivation composes with `research-toolkit:cui-bono` (Framework Clarification) + `dialectic-spiral`.
