# Ponytail — A/B findings, self-audit and alternatives (2026-10-15)

Follow-up to `ponytail-evaluation-2026-10-14.md` (this folder), which reviewed the plugin
and recorded a first, small-task A/B screen (§4). A second, pre-registered round followed. The
experiments ran in a **private Python code repository**: its tasks, code and per-run records
stay there. This document carries only what generalises.

Subject: `ponytail` 5.2.0, commit `2961b52`; Claude Code 2.1.299; model `claude-opus-5-5`.
Tags: GROUNDED (measured, from an artifact), UNRESOLVED, Inference.

## 1 · Round 1

Recorded in full in `ponytail-evaluation-2026-10-14.md` §4: on 4 small tasks, the plugin
against nothing came out null (12/12 checks each; larger median diff and higher median cost
with the plugin). Not repeated here.

## 2 · Round 2 — harder tasks, five deliveries

4 harder changes (a reference fix of about 66 lines): a grading-panel option, a
record-selection rule, chained config inheritance with cycle detection, and a geometry
comparison fix. Each had a hidden check that failed on the base for the intended reasons and
passed on a reference fix. 60 runs, isolation passed 60/60. Arms:

- **a:** the plugin, via `--plugin-dir`, with `PONYTAIL_MAP=0` and
  `PONYTAIL_SUBAGENT_MATCHER=general-purpose`.
- **b:** upstream's own `AGENTS.md` appended to `CLAUDE.md`, with no hooks.
- **c:** a one-line pointer in `CLAUDE.md` to that text, held in a separate file.
- **d:** [ilindaniel/ponytail-lite](https://github.com/ilindaniel/ponytail-lite) at
  `e7b42dc`, appended to `CLAUDE.md`.
- **e:** nothing.

| Arm | Checks | Median production-code lines | Median cost |
|---|---|---|---|
| a plugin | 12/12 | 17.0 | $0.402 |
| b text in CLAUDE.md | 12/12 | 17.5 | $0.417 |
| c pointer | 11/12 | 17.0 | $0.410 |
| d ponytail-lite | 12/12 | 18.5 | $0.453 |
| e nothing | 12/12 | 32.5 | $0.434 |

Pre-registered decisions:

- **a, b and d each beat nothing.** They passed the same checks with about half the
  production code, at the same or lower median cost. On every task they wrote fewer lines
  than nothing.
- **c did not.** Its one failure was real: the change worked where it was made, but missed a
  second place it had to reach.
- **Plugin vs. text:** the plugin is preferred by the rule's letter, on a 3.7% median cost
  margin. That is inside what 3 runs per cell can resolve.
- **Upstream text vs. ponytail-lite:** upstream's text is preferred on cost.

GROUNDED.

**The reversal.** On round 1's small tasks the fixed context cost more than it saved. On harder ones
the saved work dominated. A single-size screen would have shipped the wrong verdict.
Inference, from two sizes.

**Subagent reach** (separate probe, 3 sessions per arm, each spawning one Agent-tool subagent):

| Delivery | Reached the subagent |
|---|---|
| plugin `SubagentStart` hook | 3/3 |
| ruleset text in `CLAUDE.md` | 3/3 (canary in the subagent's reply, and the text present in its own transcript) |
| one-line pointer to a file | 0/3 |
| positive control (a canary line alone in `CLAUDE.md`) | 3/3 |

So the hook's one exclusive function is also done by a file. A pointer is not followed by
subagents: they receive the pointer, not the file. GROUNDED. **Consequence for any delivery
that prints path-scoped rules as pointers** (for example the `shared-rules` plugin in cloud
sessions): what reaches subagents is only the pointer.

**Exploratory, after scoring:**

- **Documentation.** The ruleset arms wrote far fewer new docstring lines (median 1–3,
  against 9.5 with no rules). None deleted existing comments. Repositories that value long
  docstrings should override the "comment in one line" rule.
- **Already-default behaviours.** Reading the reply endings showed that the "name what you
  skipped" behaviour, and adding tests, happened in every arm, including the one with no
  rules. So enforcement hooks for those two would add little for this model.

## 3 · The plugin audited by its own first rule ("does it need to exist?")

Measured by running each hook by hand. GROUNDED.

| Event | Injected into context |
|---|---|
| SessionStart (startup, resume, `/clear`, compaction) | 2,861 B ruleset + codebase map (826 B in the test repo; capped at 2,000 chars) + ~540 B status-line nudge, first session only |
| SubagentStart | 2,988 B per subagent |
| UserPromptSubmit | 0 B on ordinary prompts |
| skill listing | 1,677 chars across 6 descriptions |

| Part | Verdict |
|---|---|
| ruleset text | the product, and upstream ships it as a plain `AGENTS.md` (2,721 B); the hook text equals that file plus a mode header and a levels table |
| levels, mode files, prompt tracker | a feature that only switches which text is injected |
| codebase map | noise in a repo with many one-off scripts: first name per file, no file names, private names dropped |
| status line and nudge | cosmetic; the script is re-copied into `~/.claude` every session start (by design: upstream issue #1032, PR #1033) and, once wired up, runs on every refresh |
| SubagentStart | redundant with `CLAUDE.md` text (§2 probe) |
| multi-harness plumbing | 17 harness install sections plus a rules-file path for about 9 more; six harness branches in the runtime. Inference: injected text is the only delivery all of them share, which is likely why the ruleset is a paragraph rather than a check |

Enforcement: none. Every rule is text.

## 4 · Upstream status (read-only survey, 2026-10-15)

- **Injection overhead:** raised and declined upstream ("The resident ruleset is the
  product"): DietrichGebert/ponytail issue #685, issue #597, PR #797. The documented opt-out is
  `PONYTAIL_SUBAGENT_MATCHER`.
- **Status-line recopy:** deliberate (issue #1032 / PR #1033). Within the searches made, no
  issue covers its supply-chain side: an unpinned script, overwritten every session and run on
  every refresh, with no pin or opt-out. Those searches were "statusline" (99 hits) and
  "status line" (23 hits), all read; "pin" was read on page 1 only. UNRESOLVED beyond them. A
  draft issue exists and is held unposted by the operator.

The survey read page summaries, not raw text, and did not enumerate all of upstream's
1,119 issues and PRs.

## 5 · No-hook alternatives

None enforces anything; all are text.

- **ilindaniel/ponytail-lite:** a single `AGENTS.md`. Closest to the ruleset, used as arm d.
- **1ssb/ponytail-adapter:** `AGENTS.md`; drops the test and skipped-line rules.
- **TheYan3/ponytail-skills:** skills only.
- **ramigb/buzzcut:** a ruleset plus a small reminder hook.
- **ramaikn/ponycave:** mixed with a terse-speech style.

Upstream's 8,817 forks were not enumerated.

## 6 · Recommendations (Inference)

- **Deliver the ruleset as plain text where a project wants it.** That means `CLAUDE.md`,
  `AGENTS.md`, or an always-loaded rule, **not** the plugin. It matched the plugin on every
  measured endpoint within noise, reaches subagents, and runs no third-party code on every
  event.
- **Not as a pointer.** A pointer missed a check the full text caught, and never reaches
  subagents.
- **Override the comment rule** where a repository keeps long docstrings on purpose.
- **Screen at more than one task size** before judging a ruleset. The size and cost effect
  reversed between rounds.
- **`ponytail-evaluation-2026-10-14.md` §4's verdict for prose and skill repositories still stands**, which these rounds
  did not test: there, the ruleset costs context and adds little.

## 7 · What this cannot show

- One repository, one model and 12 runs per arm. The cost differences between the text
  deliveries are smaller than the design resolves.
- No arm had a shell, so tests were written but never run by the model.
- No diff was read blind for quality.
- The tasks were written by a session that had ponytail active. A replication with a
  ponytail-free author is under way, in a separate session.
