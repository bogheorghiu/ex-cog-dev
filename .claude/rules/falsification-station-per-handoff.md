# A falsification station at every hand-off

(No `paths:` frontmatter on purpose — hand-offs happen in every kind of work in this repo, so it loads
every session, like `verify-claims.md`.)

When work passes from one producer to the next — a design doc distilling raw material, a run asset
transcribing a design, a judge rubric restating ground truth, a report summarizing runs, an issue
comment summarizing a report, a briefing feeding a fresh session — put an explicit check **against the
original source at that hand-off**, not only against the immediately-preceding step. Every transform in
a chain gets its own station that re-reads the source it claims to represent.

## Why

Drift hides at the hand-off with no reviewer. Each link in a chain is normally checked only against its
neighbor, so an error introduced two links back rides through every later check and reads as clean —
and nothing compiles prose, so nothing catches it except looking at the source. This repo's pipeline is
exactly such a chain (raw substrate → design doc → probe assets → judge rubric → results report →
public issue comment), and its end products are shipped instruments: a mis-transcribed bar or a
misattributed figure changes what a battery *measures*, and then what ships to every consumer within
the uvx cache TTL.

**Worked instances — one finalization pass, 2026-07-21, three catches, each invisible one link up:**

- A judge rubric credited "the claim-by-claim verification" with a **~70% figure that actually lived in
  a held-out synthesis document three hand-offs upstream** — no pack file contains it, and one of the
  three verification reports it was attributed to never produced a final ledger at all. Every
  intermediate doc matched its predecessor; a fresh reader re-reading the raw material caught it.
- A briefing **merged two distinct operator steers into one arm name** ("R-neutral a.k.a. V4-FULL" —
  two different arms, separately decided). Checking against both source docs recovered both decisions.
- A design doc said "emit the **five** subagent prompts"; the raw log has five spawns but only **four**
  pre-date the replayed moment — following the digest would have leaked held-out material into the arms.

## How to apply

- At each hand-off, name the **source of truth** for that step and check the output against *it*, not
  just against the previous summary. "Read it in full" beats "trust the digest" whenever the digest is
  load-bearing.
- The cheapest station is a **fresh reader with no stake in the prior conclusion** — in this repo,
  normally an **Opus subagent** (Opus reads this repo's sensitive substrates unredacted; the
  redaction-codec agents are needed only when the *checking* session must itself stay keyword-clean) —
  told to verify against the original and report contradictions, not to re-derive the conclusion.
- A station reports **per claim**: confirmed-verbatim / confirmed-paraphrase (with the actual text) /
  not-found. "Roughly checks out" is not a station result.
- Scale ceremony to the cost of being wrong: anything that ships or gates a decision — a rubric, a
  pre-registration, a run prompt, an issue comment — always earns a station; a scratch note does not.

## Siblings — the seam trio

`verify-claims.md` covers your **own** conversational claims (draft-until-re-read).
`verify-delegated-work-against-artifacts.md` covers a **delegated agent's self-report** (artifacts over
narration). This rule is the general seam discipline both instantiate: **any** producer-to-producer
transfer — including doc-to-doc summarization where no agent is reporting on itself, the case the
other two don't reach.

## Twin

The portable principle lives at machine scope (`~/.claude/rules/falsification-station-per-handoff.md`)
and loads every session there. This repo copy carries the repo-specific why (a prose pipeline ending in
shipped instruments and public issue comments; Opus-subagent stations as the norm) and travels with the
repo for collaborators and non-Claude harnesses. Keep the two in step on the core discipline — same
pattern as `preregister-ship-decision.md` and `verify-delegated-work-against-artifacts.md`.
