# Pre-register the ship decision before the test that gates it

When a change to a plugin's behavior (a skill body, a guard, a hook, a directive) will be
**gated on an empirical test** — a probe battery, an A/B ablation, a firing check — write the
**ship/no-ship criterion to disk before running the test**, not after reading the results. A
`PREREG-*.md` stating "ships iff <observable> clears <bar>" committed ahead of any data.

(No `paths:` frontmatter on purpose — this is an always-relevant shipping convention for a
test-driven repo, so it loads every session, like `no-sensitive-data-in-repo.md`. It fires only
when you're actually gating a change; most sessions it's inert standing context.)

## Why

Every plugin change here reaches all consumers within the uvx cache TTL, with green CI as the only
gate (see CLAUDE.md "Release / publish"). So "we shipped a thing that felt right after glancing at
the runs" is a live failure mode, not a hypothetical. Fixing the criterion *before* the data is
what makes a **null result reportable as a null** instead of quietly reinterpreted into a ship —
the same p-hacking drift that `verify-claims.md` guards against in prose, applied to the ship
button. Once the goalpost is on disk, no goalpost motion is available.

Worked instance: the issue #173 router-directive battery (2026-07-21). The pre-registered rule
("directive ships iff D1 > D0 on invocation AND no verdict/sizing shift") turned a 0/3 = 0/3
result into a clean "does not ship, here's the corrected experiment" — because success was defined
before the runs, a genuine null could not be spun into a ship.

## How to apply

- **Before running the gating test**, write `PREREG-<change>-<date>.md` with: the arms, the
  endpoint(s) and how each is measured (from artifacts/jsonl, not the model's self-report — see
  `verify-claims.md`), the VOID/gate conditions, and the **explicit ship rule**.
- **Any deviation from the design decided after launch is recorded in the prereg with its reason**,
  before scoring — a mid-flight rescope is legitimate only if it's on record ahead of the data it
  affects.
- **Null on the ship criterion ⇒ it does not ship on that evidence** — record the null, route the
  change back to design. Do not re-derive a new "success" from the same runs.
- Scale the ceremony to the blast radius: a behavior-changing ship to all consumers always earns a
  prereg; a typo fix does not.

**Lineage.** Standard scientific pre-registration; the ship-button instance of the same
don't-outrun-your-evidence discipline as `verify-claims.md` ("n=0 is a claim, not a result") and
makers-toolkit learning A8 (pre-register N/k). Full write-up: makers-toolkit learnings **A14**
(`ClaudeShared/research-toolkit-updates/MAKERS-TOOLKIT-LEARNINGS-from-rt-v4-2026-07-18.md`).

**Twin.** The portable, repo-agnostic principle lives at machine scope
(`~/.claude/rules/preregister-ship-decision.md`) and loads in every session. This repo copy is the
public, multi-harness instance — it carries the ex-cog-dev-specific *why* (uvx consumers + green CI
as the only gate) and travels with the repo for collaborators and non-Claude harnesses who don't
have the machine-scope rule. Keep the two in step on the core discipline (same pattern as
`no-speculative-structure.md` ↔ its wikipediai twin).
