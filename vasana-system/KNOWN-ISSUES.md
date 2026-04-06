# Vasana System — Known Issues

## Pattern Library: Read-Only in Remote Plugin (ARCHITECTURAL FLAW)

**Reported:** 2026-04-06 (Claude Cowork session)
**Status:** Not started
**Severity:** Architectural — undermines core purpose

### Problem

When vasana-system is installed as a remote plugin (e.g., from `bogheorghiu/ex-cog`),
the pattern library is read-only. Users can browse patterns but never grow the library.
The whole point of vasanas is they emerge from interaction and need capture in-situ.

A read-only library is a library you can read but never grow.

### Why It Matters

- `record-pattern` skill instructs users to capture patterns — but can't write to plugin files
- `vasana` hook detects patterns — but has nowhere persistent to store them
- The self-replication principle (every pattern contains invitation to grow) is broken
- Remote plugin files are conceptually read-only; writes get overwritten on update

### Possible Fixes

1. **Local writable overlay** — Pattern library reads from plugin (base) + local dir (user additions).
   Something like `~/.claude/local/vasana-patterns/` or `.claude/local/vasana-patterns/`.
   Pattern-library skill merges both at read time. New patterns write to local only.

2. **Relational-memory as pattern store** — Already bundled as MCP.
   `record-pattern` writes to relational-memory instead of files.
   `pattern-library` reads from both files (shipped patterns) AND relational-memory (user patterns).
   Pro: Already works, cross-session, searchable. Con: Different format than file-based patterns.

3. **Edge-graph as pattern index** — Use edge-graph for pattern relationships/weights,
   relational-memory for pattern content. The graph tracks which patterns co-occur,
   strengthen, or conflict. File-based patterns become seed data; the living library is in MCP.

4. **Hybrid: files for stable patterns, MCP for emerging** — Ship known patterns as files.
   New observations go to relational-memory. When a pattern in memory reaches threshold
   (observed N times, confirmed useful), it graduates to a file (manual or automated).
   This mirrors the vasana lifecycle: groove → recognition → named pattern.

### Recommended Approach

Option 4 (hybrid) best matches the vasana philosophy — patterns earn their way into
the library through repetition, not through one-time capture. But option 2 is the
quickest to implement and already has infrastructure.

### Implementation Notes

- The `record-pattern` skill needs a storage backend parameter or auto-detection
- The `pattern-library` skill/command needs to merge sources
- The vasana hook needs write access to whichever backend is chosen
- Consider: should user patterns sync back to the published repo? (PR workflow?)
