# Vasana System — Known Issues

## Pattern Library: Read-Only in Remote Plugin (RESOLVED)

**Reported:** 2026-04-06 (Claude Cowork session)
**Resolved:** 2026-05-21 (canonical library at user-writable location)
**Severity:** Was architectural — now solved

### Problem (historical)

When vasana-system was installed as a remote plugin, the pattern library was read-only. Users could browse but never grow the library. The self-replication principle was broken.

### Resolution

The canonical pattern-library now lives at a user-writable location (`ClaudeShared/pattern-library/` by default). All reads and writes go there. The plugin's bundled patterns serve as seed data for first-time setup.

The full design of the install hook, runtime path resolution, and three-way merge on plugin update is captured in `HANDOFF-pattern-library-relocation-2026-05-21.md`, bundled at the plugin root. The deferred items in this file summarize what's pending; the bundled handoff has the full rationale and implementation sketches. See also PR #419 for the rationale of the current canonical-library approach.

### Current workaround (single-user)

Until the install hook (item 1 below) lands, set up the canonical location manually:

1. Create `~/ClaudeShared/pattern-library/` (or pick your own path).
2. Seed it from the plugin's bundled `skills/pattern-library/patterns/` directory, or grab the latest from the upstream repo.
3. Add a `CLAUDE.md` at that location containing at minimum:
   - **Canonical-location statement:** "this directory is the single source of truth for pattern content."
   - **Write destinations table:** `_drafts/[pattern-name].md` for new patterns; `patterns/[pattern-name].md` for promoted ones; `patterns/pattern-seeds/[seed-name].md` for seeds; `_notes/[descriptive-name].md` for research/connections.
   - **Naming rule:** "vasana" for system-level names and the propagation section in each pattern file; "pattern" everywhere else.
   - **Mechanism-not-metaphor guardrail:** before recording, check that the cross-domain claim reflects a shared mechanism (math, causal structure, constraint), not just shared vocabulary.
   - **Self-replication principle:** every pattern keeps its Vasana section intact.
4. Have your project's `CLAUDE.md` (or user-scope rules) point Claude at the canonical path.

The `/pattern-library browse` and `/pattern-library update` commands assume `~/ClaudeShared/pattern-library/` by default and fall back to the plugin-bundled `skills/pattern-library/patterns/` if no canonical location is set — so the commands stay operable even before manual setup.

### Remaining deferred work

1. **Plugin install hook** — auto-copy bundled library to user location on first install
2. **Runtime path resolution** — skills auto-detect canonical location instead of hardcoded path
3. **Three-way merge on update** — reconcile upstream changes with user additions
4. **Two-way contribution flow** — user patterns can be proposed upstream via PR

These are tracked in the HANDOFF file above.
