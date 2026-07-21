# Redaction-codec workflow — keyword-clean orchestration over restricted substrates

**When this applies — and when it doesn't.** This workflow exists for exactly one situation: the
orchestrating session is a model whose content filter refuses on a substrate's *keywords* (in current
practice, a Fable designer session), while the work requires that substrate to be read, quoted, or
checked. An Opus orchestrator reads the material natively — it skips all of this and works raw. Don't
route through the codec when the orchestrator doesn't need it; every hop costs fidelity and time.

## Roles — who touches what

- **The orchestrator (keyword-clean) reads and writes the probe texts itself, as much as possible.**
  Meta-level artifacts — designs, run prompts, judge rubrics, reports — rarely trip the filter, and
  the orchestrator reasons best in direct contact with what is actually processed. Delegating
  authorship it could do itself loses design quality for nothing (worked instance, 2026-07-21: a
  delegated writer introduced a stale factual claim into a prompt header; the orchestrator's own
  direct read caught it).
- **`restricted-domain-reader` = redact-on-read.** For material that genuinely trips the filter (raw
  session bundles, dense pack contents), the reader returns a redacted faithful copy (b2), an
  obfuscated result (b3), or a per-claim verification (b4). The orchestrator works from the rendering;
  `[REDACTED:*]` tokens stay stable via the reader's persistent legend.
- **`probe-writer` = un-redact-on-write.** When the orchestrator's drafts carry redaction tokens that
  must resolve to real strings before an asset ships, the writer substitutes tokens per the legend and
  diff-verifies that nothing else changed. It authors text itself only as a last resort (substrate so
  dense even its redacted form trips the orchestrator — confirm the orchestrator actually tried), and
  then the orchestrator still reviews the non-quoted framing directly afterward.

Two invariants define the workflow; everything else is adaptable:

1. **The orchestrator never ingests domain keywords** — not from files, not from tool output, not
   from an agent's reply.
2. **No producer verifies its own work** — every verification runs through a channel independent of
   the agent that produced the artifact (see below).

## Verifying output the orchestrator cannot read

The orchestrator must judge work whose content it must not see. Two safe channels exist; use both,
matched to what's being checked:

- **Deterministic, content-free checks** — commands whose *output* is only numbers, booleans, hashes,
  or exit codes. `grep -icf <denylist-file> <artifact>` (a count; never `-o`/`-l`, which print content
  and filenames), `cmp -s` / `sha256sum` for byte-identity claims, `diff --stat` / hunk counts for
  "only the tokens changed" audits, `find … | wc -l` instead of `ls` when a directory's *names* might
  carry keywords. Why this is safe by construction: keyword risk lives in content reaching the
  orchestrator, and a count can't carry it. Prefer this channel for every mechanical property.
- **An independent reader station** — a *fresh* `restricted-domain-reader` spawn in b4 mode, with no
  stake in the artifact it checks (never the instance that produced it), verifying semantic
  properties: substituted strings match the legend and the named source spans; a rendering is faithful
  (spot-check K claims against the source; on disagreement, a third read decides). This is the
  `falsification-station-per-handoff` discipline applied inside the codec — a producer's self-report
  is never the evidence (`verify-delegated-work-against-artifacts`).

**Transcript (jsonl) audits — the trap to know about.** Raw transcripts can carry keywords in file
paths, tool arguments, and quoted spans — so the orchestrator must not grep them open-endedly. Audit
jsonl through the same two channels only: count/boolean greps (`grep -c`, `grep -q`), or delegate the
content-level audit to a reader-b4 spawn. The gates that matter (which tools fired, network purity,
model per turn) are all expressible as counts and exit codes.

## The optimization license

The orchestrator may **restructure this workflow mid-run whenever it sees a better shape.** The
protocol exists to hold the two invariants above, not to prescribe steps — and mid-run the
orchestrator sees what this doc's authors couldn't. Any adaptation that preserves both invariants is
legitimate without asking. If an adaptation proves worthwhile in practice, **propose it as a change to
this doc and the agent definitions** (a PR, with the evidence from the run) — that is how this
workflow is meant to evolve, and how it got its current shape (three revisions in its first live day,
each from an observed failure: metadata-only under-use → content-level b2/b4; full-delegation
authoring → codec-only; vault-blocked legend → machine-local legend with session-local fallback).

## Lineage

Assembled 2026-07-21 during the M11-real finalization (operator-directed, three revisions same day).
Agents: `.claude/agents/restricted-domain-reader.md` (canonical copy at user scope on the design
machine) and `.claude/agents/probe-writer.md` (repo-native). Sibling disciplines:
`.claude/rules/falsification-station-per-handoff.md`,
`.claude/rules/verify-delegated-work-against-artifacts.md`.
