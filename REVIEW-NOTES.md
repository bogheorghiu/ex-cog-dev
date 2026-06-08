# Review working notes — TRANSIENT (delete before this branch merges to main)

Persistent scratch state for the rules-review effort. Session context gets
compacted aggressively, so this file is the source of truth a fresh context
should read FIRST. Branch: `claude/maine-repo-review-UCZaS` → draft PR #104.

---

## THE ACTUAL TASK — do not drift again (tracked: issue #107)

> With the plugins loaded, run the repo's OWN skills — relevant ones, primarily
> **`intrinsic-prompt-design`** (which references others) — **against the rules in
> `.claude/rules/`, to improve the RULES.**

- **Skills = instruments. Rules = target.** "make them better" → *them* = the rules.
- A prior pass inverted this and reviewed the *skills* instead (wrong target). The
  drift rode in on a context-heavy sequence: branch merge → "stop" → revert →
  "build the review methodology yourself." The skill-side findings are still useful,
  but the scope was wrong.
- Sequencing decision (operator): **finish the in-flight skill cleanup first, THEN
  do the rules pass.**

---

## Current branch / PR state

- Draft **PR #104** → `main`. Don't merge to main directly (auto-updated via workflow).
- **KEEP (landed, agreed):**
  - `frame-rotation`: `## Vasana` section moved top → bottom (matches research-toolkit convention). Re the broader "should non-vasana skills even carry it" question → issue **#55**; `macro-monitor` left as-is for #55 to decide.
  - Vasana naming rule extracted to `.claude/rules/vasana-naming.md` (path-scoped `vasana-system/**`); removed the duplicate from `vasana-system/CLAUDE.md`; the shipped `vasana` skill keeps its in-band copy.
  - Version bumps: research-toolkit `3.3.1 → 3.3.3` (3.3.2 collided with main from an earlier merge), vasana-system `2.5.3 → 2.5.4`.
- **REVERTED (were over-eager; revisit deliberately):**
  - `deep-investigation-protocol`: restored the inline source-omission table. Consolidating it into a reference to `source-omission-analysis` risks dropping nuance — **do it together** (the standalone table is a superset, but "superset" ≠ "safe").
  - `self-improving-investigation`: restored the ``See `layers/improvement-notes.md` `` reference. It's intended logic of a draft skill → **preserve as data** (issue #106).

---

## KEY INSIGHT: dead references = stale monorepo paths = DATA, not garbage

`ex-cog-dev` was extracted from a monorepo (**Claude-Code-Projects**). Dead
references (missing files/dirs) are likely **stale paths to files that existed
there**. Treat them as **data to RECOVER** (fetch from the old repo), NOT to delete.
The operator is gathering these files.

- **Convention needs a permanent home** — candidate: a short note in root `CLAUDE.md`
  ("a dangling path may be a stale monorepo ref; recover before removing"). NOT a rule.
  *(Pending operator decision on placement.)*

---

## Recovered file content — PENDING RESTORATION

### `.claude/rules/research-logs-vs-methodology.md`
Referenced by `research-toolkit/CLAUDE.md:28` ("applies across all plugins") but the
file is missing. Operator provided the content from the old monorepo (verbatim below).
**Do not restore piecemeal** — batch with other recovered files in the rules phase.
Note: original has no `paths:` frontmatter (it's cross-cutting); restore as-is unless
we deliberately decide to path-scope it.

```markdown
# Research Logs vs Methodology

## Distinction (ENFORCED)

- **Research logs**: Specific investigations with sources, dates, verdicts. These are temporal — they capture what was found, when.
- **Methodology updates**: Patterns discovered through research that improve future investigations. These are durable — they change how we work.

**Don't treat specific conclusions as permanent truth.** Research findings change. Methodology improves.

## Where Research Logs Go

- **Session transcripts**: `~/.claude/transcripts/` (auto-saved by SessionEnd hook)
- **Relational memory**: `memorize`/`recall` via relational-memory MCP (cross-session)
- **Published analyses**: `docs/reference/` (committed, shareable findings)

## Where Methodology Goes

- **Skill files**: SKILL.md updates when a pattern improves investigation quality
- **Rules files**: `.claude/rules/` for cross-cutting behavioral patterns

## Example

From a 2026-01 session:
- **Research log**: "OpenAI $12B loss claim — TRUE (Microsoft 10-Q)" → transcript or memory MCP
- **Methodology insight**: "Double-antithesis pattern — after synthesis, check externality framing" → skill file
```

---

## Issues filed this session

- **#105** — remove `<EXTREMELY_IMPORTANT>` from `break-pattern` + `deep-investigation-protocol`; needs **Tier-2 live** (plugins pre-installed). Tier-1 can't see attention-capture.
- **#106** — `self-improving-investigation` draft assessment/rewrite/extract; preserve as data.
- **#107** — scope anchor: run skills (esp. intrinsic-prompt-design) against the rules.

---

## Findings from the (mis-scoped but useful) skill pass — status

Numbering follows the operator's walk-through.

1. **ralph-wiggum / `iterative-loop-engine`** — term decayed; lean on the *mechanism*, demote "ralph-loop" to a lineage note. The blind-worker/orchestrator variant is already described in `self-improving-investigation` + `investigation-orchestrator` agent → extraction question in #106. *(discussion only, no edit)*
2. **changelog in SKILL.md** — `deep-investigation-protocol` has a `changelog:` in frontmatter; `self-improving-investigation` has a body-changelog. Both belong out of SKILL.md (CHANGELOG/relational-memory). *(no edit yet; #106 covers the self-improving one)*
3. **source-omission** — (a) survey's real finding: description's "more reliably than what it says" is a borderline overclaim, one clause could justify it. (b) my table-dedup was reverted — do jointly.
4. **check-assumptions Skeptic's Stance** — survey rejected its own suggestion (adversarial-by-design). **No action.**
5. **EXTREMELY_IMPORTANT** — only 2 skills. → issue #105.
6. **inquiry-to-system** — self-declares "not an AI skill"; it's a pattern mis-filed as a skill. Operator: move it to the pattern library, refactor as needed. *(QUEUED complex item — one at a time)*
7. **dev-job-defense-ties "register collapse"** — survey rejected it ("exemplary, not broken"). **No action.**
8. **self-improving-investigation** — draft skill. → issue #106. (dead-ref restored, not deleted.)
9. **Vasana-section placement** — `frame-rotation` moved to bottom (done); `macro-monitor` left for #55.
10. **vasana naming rule** — extracted to `.claude/rules/vasana-naming.md` (done).

---

## Open queue / next

- **Finish current**, then start rules pass (#107).
- Restore `research-logs-vs-methodology.md` (+ other recovered files) — rules phase.
- Decide home for the "stale-monorepo-refs = data" note (CLAUDE.md?).
- `inquiry-to-system` → pattern migration (#6 above) — complex, one at a time.
- Table consolidation in DIP (#3b) — do jointly.
- CI on PR #104: version-bump-guard was failing on a stale-main version collision; fixed to 3.3.3. Re-verify green after each push.
