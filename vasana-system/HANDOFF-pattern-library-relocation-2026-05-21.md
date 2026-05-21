# HANDOFF — Pattern-library relocation (deferred plugin work)

**Created**: 2026-05-21
**Context session**: work on an AI-dev scaffold project produced two new vasanas; storing them in the plugin cache loses them on `/plugin update`; an ex-cog-dev clone outside the canonical plugin source is confusing as a source/destination.

## What the user proposed (verbatim, with light reformatting)

> 1. **Now**: create a local folder like `~/.claude/.pattern-library/` (or for now on `/mnt/c/` to share with Windows where Cowork operates — Cowork doesn't see WSL paths reliably).
>
> 2. **Deferred (this HANDOFF)**: modify the `vasana-system` plugin so that on install it:
>    - Creates the local folder (asks the user where, or defaults to cwd-at-install-time, or some sensible default).
>    - Copies its current library there (so user additions/edits aren't lost on plugin update — which would happen if the live library stayed in the plugin cache).
>    - Lets the user make additions/changes there freely.
>    - Optionally reminds the user that upstream PRs are welcome for some/all of their additions; discuss with the user, assess fit, etc.
>
> 3. **On plugin update**: the new library from upstream is evaluated against the user's current local one. If straightforward (only additions on the upstream side) → additions are copied over. If more complex → branch (discussed when reached).
>
> 4. **Bonus / cross-link**: this can serve as a way to approach **VIKASA-type functionality** (see VIKASA note below) by proposing a two-way plugin-update ecosystem.

## What's already done (the "now" half)

- A rename script renames `skills/pattern-library/vasanas/` → `patterns/` in the plugin source. Concept references in `mcp-servers/` are intentionally left alone — they refer to the abstract concept, not the folder.
- A setup script creates `/mnt/c/Users/<user>/ClaudeShared/pattern-library/patterns/`, seeds from the renamed plugin source, copies the two staged vasanas in place with the `STAGED-` prefix stripped.
- The two staged vasanas (`frame-pushback`, `convergence-by-accumulation`) wait in the hub at `STAGED-pattern-*.md`.

User must run those two scripts (sandbox blocks Claude from doing it).

The rename script creates a sibling worktree at
`~/ClaudeCodeHub/.worktrees/Claude-Code-Projects/wt-rename-vasanas-to-patterns/`
on branch `refactor/rename-vasanas-to-patterns` (per the user-scope worktrees rule: never main, always branch, always sibling). The main working tree is untouched. After running, the user reviews in the worktree, commits, pushes, opens a PR.

```bash
bash ~/ClaudeCodeHub/STAGED-rename-vasanas-to-patterns.sh
# review in the worktree, commit + push + PR from there

# After PR merges into main:
bash ~/ClaudeCodeHub/STAGED-setup-local-pattern-library.sh

# OR, to seed from the worktree before merge (handy if you want to use the
# local library immediately while the PR is in review):
CCP_SOURCE=~/ClaudeCodeHub/.worktrees/Claude-Code-Projects/wt-rename-vasanas-to-patterns/projects/ex-cog-dev/vasana-system/skills/pattern-library \
  bash ~/ClaudeCodeHub/STAGED-setup-local-pattern-library.sh

# After everything settles:
rm ~/ClaudeCodeHub/STAGED-pattern-*.md
cd <plugin-source-repo>
git worktree remove ~/ClaudeCodeHub/.worktrees/Claude-Code-Projects/wt-rename-vasanas-to-patterns
git worktree prune
```

## What needs to be done (the deferred half)

### 1. Plugin install hook — copy library to user-controlled location

**Where**: a `PostInstall`-style mechanism in the `vasana-system` plugin. Investigate whether Claude Code plugins have a formal post-install hook; if not, this falls to the plugin's `SKILL.md` first-run guidance plus a setup command (e.g., `/pattern-library:setup-local`).

**Behavior**:
- Detect existing local library at a configured path (default: per-OS — `~/.claude/pattern-library/` on Linux/Mac; on Windows-from-WSL maybe `/mnt/c/Users/<user>/ClaudeShared/pattern-library/` if the user wants Windows-visibility).
- If absent: prompt user (or honor a `~/.claude/vasana-system.local.md` setting) for the path.
- Copy current bundled library to that path.
- Set up a config file recording where the live library is.

### 2. Plugin runtime — read from user location, not cache

Every skill in `vasana-system` that reads `skills/pattern-library/patterns/*.md` needs to read from the configured user location instead. Implementation options:
- Symlink the cache path to the user path (simplest; some OSes have issues).
- Override paths in skill bodies via env var or config lookup (more code, more portable).
- A small library helper that resolves "pattern library root" once.

### 3. Plugin update — three-way merge

On `/plugin update`:
- Compare bundled-library@new vs bundled-library@old vs user-library@current.
- If user only added files (no edits to existing patterns), copy the new files in (additions-only path).
- If patterns were edited on both sides (true conflict), surface the conflict to the user with a clear diff and either:
  - Block the update until resolved.
  - Apply the upstream version under a side-name (`framework-dissolution.upstream.md`) and let the user decide.
- If the upstream removed a pattern the user kept locally, *don't* delete the user's copy. Warn instead.

### 4. Two-way contribution flow ("VIKASA-type" — see below)

After the user has added/edited patterns locally:
- A command (`/pattern-library:propose-upstream`) that:
  - Identifies user-local patterns not present upstream.
  - Identifies user edits to existing patterns.
  - Generates a branch in the plugin source repo with these changes applied.
  - Optionally opens a PR (gh CLI).
- The point: closes the loop. User adds value locally → easy path to push that value back to the shared library.

## VIKASA note

The user mentioned "VIKASA-type functionality" without elaborating. **I don't know what VIKASA refers to specifically** — it could be:
- The Sanskrit word *vikāsa* / *vikasita* meaning "unfoldment, blossoming, development" — fits the "bidirectional development" theme thematically.
- A specific project, framework, or paper the user is working with elsewhere (possibly Cowork-related, given the Windows-sharing context).
- An internal acronym.

What the user said it MEANS in this context: "a two-way plugin-update ecosystem(-ish)" — i.e., upstream → user is the normal direction; user → upstream becomes a first-class path too, with tooling support. The ecosystem improves both ways simultaneously.

This is structurally [[convergence-by-accumulation]] applied to a plugin ecosystem: the plugin developer's source and the user's customizations converge by mutual contribution rather than by parallel maintenance. (Cross-link the staged vasana when it lands.)

**If Cowork picks this file up**, the question for Cowork: is VIKASA a defined concept in your project? If yes, hook the precise definition into this HANDOFF and into the eventual plugin design.

## Why this is in the hub, not in the work repo

The relocation work is plugin-side (`vasana-system`), not scaffold-side. The scaffold session captured the *trigger* (we wanted to store vasanas; the cache was the wrong place), but the *fix* lives in a different project. Hub is the cross-project coordination point.

## Reference links from work-repo's HISTORY

The 2026-05-21 entries in the work-repo's `HISTORY.md` cover the trigger — the two patterns were staged and the user noted the relocation issue. This HANDOFF picks up from there.
