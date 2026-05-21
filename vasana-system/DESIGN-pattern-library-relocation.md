# DESIGN — Pattern-library relocation (deferred plugin work)

**First captured**: 2026-05-21 (during canonical-library setup work)
**Status**: Manual workaround operational; automated path deferred

## Trigger

Storing new patterns in the plugin cache (`skills/pattern-library/patterns/`) loses them on `/plugin update` — the cache is overwritten by the bundled library. The plugin needs a user-writable canonical location that survives updates, plus a sane merge strategy when the bundled library changes.

## User's design (verbatim, with light reformatting)

> 1. **Now**: create a local folder like `~/.claude/.pattern-library/` (or for now on `/mnt/c/` to share with Windows where another tool/agent operates — some tools don't see WSL paths reliably).
>
> 2. **Deferred (this doc)**: modify the `vasana-system` plugin so that on install it:
>    - Creates the local folder (asks the user where, or defaults to cwd-at-install-time, or some sensible default).
>    - Copies its current library there (so user additions/edits aren't lost on plugin update — which would happen if the live library stayed in the plugin cache).
>    - Lets the user make additions/changes there freely.
>    - Optionally reminds the user that upstream PRs are welcome for some/all of their additions; discuss with the user, assess fit, etc.
>
> 3. **On plugin update**: the new library from upstream is evaluated against the user's current local one. If straightforward (only additions on the upstream side) → additions are copied over. If more complex → branch (discussed when reached).
>
> 4. **Bonus / cross-link**: this can serve as a way to approach **VIKASA-type functionality** (see VIKASA note below) by proposing a two-way plugin-update ecosystem.

## Current state (manual workaround)

The plugin's `KNOWN-ISSUES.md` describes the operational workaround. In short:

1. The user creates a canonical pattern-library at a writable location (default convention: `~/ClaudeShared/pattern-library/`).
2. The user seeds it from the plugin's bundled `skills/pattern-library/patterns/` directory.
3. The user adds a `CLAUDE.md` at that location declaring it the single source of truth (with canonical-location statement, write-destinations table, naming rule, mechanism-not-metaphor guardrail, self-replication principle).
4. The user's project `CLAUDE.md` or user-scope rules point sessions at the canonical path.

The `vasanas/` → `patterns/` folder rename in the plugin source happened separately (concept references in `mcp-servers/` are intentionally left alone — they refer to the abstract concept, not the folder). All plugin skill bodies and command files now reference the canonical-library convention and fall back to the bundled `skills/pattern-library/patterns/` only when no canonical location is configured.

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

## On the bidirectional flow

Structurally, item 4 (two-way contribution flow) is [[convergence-by-accumulation]] applied to a plugin ecosystem: the plugin developer's source and the user's customizations converge by mutual contribution rather than by parallel maintenance.
