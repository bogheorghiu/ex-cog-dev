# Verify a delegated agent's work against artifacts, not its self-report

When you delegate to a subagent, a headless run, or a Fable/Opus orchestrator, judge what it did by
the **artifacts it changed** (file contents, mtimes) and its **timestamped transcript** (the jsonl)
— never by its own account of what it did.

**Why.** An agent's self-narration is generated text, not a log. It can be confidently, specifically
wrong about its own history, and it arrives already shaped as a conclusion — so it propagates
unchallenged. This repo runs on delegated evaluation (Fable design passes, headless probe batteries,
Opus reader subagents), so the failure mode is live here, not hypothetical. Worked instance
(rt-v4, 2026-07-19): a delegated Fable agent sent an unprompted *"correction"* claiming it had
finished its work **before** the resume that un-stuck it; the transcript timestamps disproved it
outright — every edit ran *after* the resume. The confident self-report was wrong; the artifact
record was right. Nothing compiles an agent's prose, so nothing catches this except looking.

**How to apply.**
- Check the **files:** do the claimed changes exist, exactly once (not duplicated by a redundant
  re-run), with mtimes consistent with the claimed sequence?
- Check the **jsonl:** tool-use entries and their timestamps are the authoritative record of what ran
  and when. `Edit`/`Write` calls are ground truth for "did it actually change anything."
- **A transcript can lag its work** — reading it mid-run may show a stale snapshot ("no edits yet"
  can mean "not yet flushed"). Re-check the artifacts before concluding either way.
- Verify the **model** actually took (the `model` field per assistant turn), not the spawn parameter
  — an in-session subagent can silently revert to the parent model.
- Applies to relaying too: if you already told the operator something from an agent's self-report and
  the artifacts contradict it, correct it explicitly.

**Adjacent.** This is the delegation-shaped case of `verify-claims.md` (draft-until-re-read on one's
own claims) and `falsification-station`-style hand-off checking; it generalizes the same
"verify from the raw jsonl, not the prose" discipline as the instrument-credit lesson (makers-toolkit
A13). The full reliable-delegation recipe (data-only orientation, refusal-risk map, freedom frame,
usage-limit resume) is makers-toolkit **B6**.

**Twin.** The portable principle lives at machine scope
(`~/.claude/rules/verify-delegated-work-against-artifacts.md`) and loads every session. This repo
copy travels with the repo for collaborators and non-Claude harnesses; keep the two in step on the
core discipline (same pattern as `preregister-ship-decision.md`).
