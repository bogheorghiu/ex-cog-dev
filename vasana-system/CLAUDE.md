# Vasana System - Plugin Context

> Vasana (वासना, "that which lingers") — a pattern that persists across contexts.
> This system explores the possibility that some behavioral patterns recur across
> unrelated domains, situations, and scales.
>
> Etymology: √vas (to dwell, to remain, to perfume).
> Shankara's commentary on Mandukya Upanishad (4th verse). Yoga Sutras IV.8-9.

## Canonical Pattern-Library Location

The live pattern-library is at the user's local path, NOT in the plugin cache.
Default: `~/ClaudeShared/pattern-library/` (or wherever the user configured it).

**Path notation:** Linux/macOS and WSL use `~/ClaudeShared/...` (expands via `$HOME`). Windows-native shells (CMD, PowerShell) treat `~` inconsistently — substitute `%USERPROFILE%\ClaudeShared\...` (CMD/PowerShell) or the equivalent shell-specific form. For a shared Windows/WSL setup where Windows tools need to see the same files as WSL, point both at the Windows-side path (`/mnt/c/Users/<user>/ClaudeShared/...` from WSL; `C:\Users\<user>\ClaudeShared\...` from Windows).

All pattern reads/writes go to the canonical location. The bundled `skills/pattern-library/patterns/` directory is seed data — used only if no canonical location is configured.

A `CLAUDE.md` at the canonical location has the full operational rules (naming convention, guardrails, write destinations).

## Naming Rule

"Vasana" only for system name, entry skill (`vasana`), hook (`vasana.sh`), and the Vasana section in each skill. Everything else uses "pattern."

## Patterns Are Neutral

Patterns are observations, not anti-patterns. Groove-deepening is also mastery. Framework-dissolution can be premature. The library presents what recurs; application skills apply their own lens.

## Self-Replication Principle (ENFORCED)

Every pattern contains the Vasana section — an invitation to notice and capture new patterns. The instruction to propagate is IN each pattern.

**Required:** When modifying or sharing patterns, keep the Vasana section intact. The system must be able to grow.

## Mechanism-Not-Metaphor Guardrail

Before recording any cross-domain pattern, check: does the similarity reflect genuine shared mechanism (shared math, shared causal structure, shared constraint), or just surface resemblance (shared vocabulary, shared shape)? Reference: `patterns/mechanism-not-metaphor.md` in the canonical library.

## Testing Rule

A pattern that doesn't produce observable difference isn't working. Before relying on one:
1. **Trigger test**: Does it invoke when conditions match?
2. **Emergence test**: Does the dynamic actually happen?
3. **Value test**: Does human report usefulness?

## MCP Servers

This plugin bundles two MCP servers for pattern persistence:
- **relational-memory** — multi-layered memory for cross-session pattern tracking
- **edge-graph** — weighted relation tracking (weight = repetition frequency)

## Key Concepts

- **Repetition as primitive** — patterns don't exist until they repeat (edge-graph weight, groove-deepening, rhythm)
- **Retrieval is generation** — recalling a pattern regenerates it (pattern-seeds unfold on parsing, never exact replay)
- **Agency disrupts predictability** — repetition is default; genuine engagement introduces discontinuity

## Axioms

The system's founding axioms are in [`AXIOMS.md`](AXIOMS.md) — a reading key plus A/A′/B/C/D/E. They formalize the three Key Concepts above (repetition-as-primitive → **A**; retrieval-is-generation → under **C**; agency-disrupts → **A′**) and carry the working definition of a vasana: the whole corpus *is* the definition, with no separate one-liner.

**Living document — keep rewriting them.** The axioms are provisional by design, meant to be continually revised rather than frozen — that revisability *is* the ethos (a vasana does not survive its own recognition unchanged, axiom C). So treat `AXIOMS.md` as a draft that improves, not a settled spec.
