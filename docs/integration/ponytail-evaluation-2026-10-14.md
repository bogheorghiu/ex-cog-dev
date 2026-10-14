# Evaluation — the `ponytail` plugin (DietrichGebert/ponytail)

**Written:** 2026-10-14. **Subject:** ponytail 5.2.0 at commit `2961b52`, a third-party "lazy
senior developer" persona plugin, unrelated to this repository. **Why it is filed here:** it
is a test run under this repository's methodology (pre-registered decision rules, results
read from artifacts, a blind verifier). Running it also exposed a defect in this
repository's `skill-activation-testing` dev recipe, which is fixed separately (PR #256). The
plugin-scope questions it raised are in issue #257.

Tags: GROUNDED (observed, or confirmed by an independent check), UNRESOLVED (the evidence
doesn't settle it), Inference (reasoned, not measured).

## Verdict

**Off by default, in every kind of repository; switch it on deliberately.** The security
risk at this commit is low. In prose and skill repositories it adds little. In a small
code-repository A/B it saved neither diff size nor cost (§4).

## 1. What runs

Three hooks, plus six on-demand skills. GROUNDED, from the code at `2961b52`:

- **SessionStart** injects a ruleset of about 5 KB, plus a "codebase map" of top-level names
  read via `git ls-files`. Once per machine it also tells the model to offer to edit
  `~/.claude/settings.json` (to add a status line).
- **SubagentStart** injects about 3 KB of rules into every subagent while the mode is on.
- **UserPromptSubmit** reads each prompt only to match the mode-switch commands.

`claude plugin details` reports these hooks as having no model-context cost. In fact the
SessionStart and SubagentStart output is model context.

## 2. Security

**Low risk at `2961b52`.** This session read the hook code, then a blind reviewer (a
separate model, given open questions) did the same. Both found:

- no network access;
- process execution only of `node` and `git ls-files`, with constant arguments and no shell;
- writes confined to `~/.claude` and `~/.config/ponytail`;
- no prompt text echoed or stored.

The reviewer corrected one claim of this session's. The codebase map is a **narrow but real
prompt-injection channel**: identifier-shaped words from repository paths and names reach
the model (e.g. a folder named `IMPORTANT-ignore-previous-instructions/`), though spaces,
newlines and punctuation cannot. It matters only for untrusted repositories, where
`PONYTAIL_MAP=0` turns the map off.

**The real risk is trust over time.** The hooks run Node with the user's privileges on every
session, prompt and subagent spawn, from one maintainer's repository. A review of one commit
says nothing about the next. Whether a marketplace entry can be pinned to a commit is
UNRESOLVED.

## 3. Contamination of experiments — the finding that matters

The finding is not specific to ponytail: **any plugin enabled at user scope rides along into
test runs.** Ponytail exposed it because its hooks inject context. GROUNDED; four live runs
on 2026-10-14, each judged from an artifact rather than from the model:

| Run style | Ponytail present? | Evidence |
|---|---|---|
| `claude -p --plugin-dir X` | **yes** | its mode file appeared for the run's working directory |
| same, plus `--setting-sources project` | no; X's own hook still fired | no mode file; X's marker file written |
| `claude plugin eval` | no | the trace's plugin list held only the plugin under test plus built-ins |
| a subagent (Agent tool) | **yes** | its ruleset in the subagent's own transcript |

The fix for headless runs is PR #256. Subagents and workflow stages inherit whatever the
driving session loaded, and no flag reaches them, so a session that drives skill tests
should not run with persona plugins installed (issue #257).

## 4. Value

**Prose and skill repositories (like this one): little.** Its core duplicates
`no-speculative-structure.md` and `no-drive-by-edits.md`. The codebase map covers code files
only. It adds context to every session and subagent. The author's benchmark (−53% code, −26%
cost on coding tasks, correctness unchanged) is UNRESOLVED: it was run by the author and has
not been replicated.

**Code repositories: an A/B screen came out null.** Written before any run: the verdict
"keep it on in code repositories" stands iff ponytail passes at least as many checks on
every task **and** lowers median diff size or median cost. VOID if the isolation check fails.

Design: one private code repository; 4 small real tasks (T1–T4), each with a check that
runs code; 3 runs per task and arm (24 runs), alternating arms; headless `claude -p` on
`claude-opus-5-5`; both arms with `--setting-sources project`, WITH adding ponytail via
`--plugin-dir`; each run in a throwaway worktree of one commit; no shell for either arm.
Isolation was checked from ponytail's mode file: created in every WITH run, absent after
every WITHOUT run.

| Run | Task | Arm | Check | Diff lines | Of which test | Of which docs | Cost USD | Turns |
|---|---|---|---|---|---|---|---|---|
| 1 | T1 | WITH | pass | 31 | 23 | 0 | 0.616 | 13 |
| 2 | T1 | WITHOUT | pass | 49 | 39 | 0 | 0.419 | 16 |
| 3 | T2 | WITH | pass | 16 | 11 | 0 | 0.255 | 7 |
| 4 | T2 | WITHOUT | pass | 15 | 11 | 0 | 0.235 | 8 |
| 5 | T3 | WITH | pass | 27 | 14 | 3 | 0.294 | 9 |
| 6 | T3 | WITHOUT | pass | 41 | 17 | 5 | 0.317 | 9 |
| 7 | T4 | WITH | pass | 30 | 16 | 0 | 0.289 | 13 |
| 8 | T4 | WITHOUT | pass | 20 | 0 | 0 | 0.237 | 8 |
| 9 | T4 | WITH | pass | 32 | 18 | 0 | 0.284 | 13 |
| 10 | T1 | WITHOUT | pass | 11 | 0 | 0 | 0.281 | 8 |
| 11 | T1 | WITH | pass | 31 | 23 | 0 | 0.370 | 13 |
| 12 | T2 | WITHOUT | pass | 15 | 11 | 0 | 0.207 | 6 |
| 13 | T2 | WITH | pass | 13 | 9 | 0 | 0.276 | 8 |
| 14 | T3 | WITHOUT | pass | 36 | 17 | 0 | 0.265 | 7 |
| 15 | T3 | WITH | pass | 29 | 13 | 4 | 0.300 | 9 |
| 16 | T4 | WITHOUT | pass | 20 | 0 | 0 | 0.229 | 8 |
| 17 | T1 | WITH | pass | 51 | 32 | 11 | 0.396 | 13 |
| 18 | T1 | WITHOUT | pass | 73 | 63 | 0 | 0.365 | 11 |
| 19 | T2 | WITH | pass | 15 | 11 | 0 | 0.282 | 8 |
| 20 | T2 | WITHOUT | pass | 16 | 12 | 0 | 0.232 | 7 |
| 21 | T3 | WITH | pass | 27 | 14 | 3 | 0.282 | 9 |
| 22 | T3 | WITHOUT | pass | 28 | 12 | 0 | 0.270 | 7 |
| 23 | T4 | WITH | pass | 30 | 16 | 0 | 0.281 | 12 |
| 24 | T4 | WITHOUT | pass | 17 | 0 | 0 | 0.239 | 8 |

| | WITH | WITHOUT |
|---|---|---|
| Checks passed | 12/12 | 12/12 |
| Median diff lines | 29.5 | 20.0 |
| Median cost (USD) | 0.287 | 0.252 |
| Median turns | 10.5 | 8.0 |

**Decision: the verdict does not stand.** There was no regression, but both median diff size
and median cost were higher with ponytail.

Exploratory, outside the rule (claiming either would need a new pre-registered run):

- Lines outside tests and docs: median 9 with ponytail against 13.5 without. Counting only
  tests out (docs left in), the medians are 13 against 13.5, flat: the difference is docs
  lines, added in 4 WITH runs against 1 WITHOUT run. With ponytail, runs added tests in 12/12 runs, against 8/12
  without; the larger total diff is the tests.
- On a one-word prompt, a WITH session cost about three times a WITHOUT one ($0.0087
  against $0.0027). That suggests the injected context is a fixed cost per request
  (Inference).

What the screen cannot show: every run passed, so the checks did not discriminate; the tasks
were small; nobody judged diff quality; and it covered one repository, one model and three
runs per cell.

The run data came from a separate session on that repository. Its aggregates were recomputed
here from the per-run rows rather than taken from that session's summary. That caught one
miscount (9/12 for 8/12) before this record was written.

## 5. If it stays installed

- `PONYTAIL_DEFAULT_MODE=off`; turn it on with `/ponytail` for code-heavy sessions.
- Type `stop ponytail` before any probe battery or skill-firing run. The subagent hook then
  injects nothing (GROUNDED, from the code).
- `PONYTAIL_SUBAGENT_MATCHER` names the agent types that receive the rules (an unanchored,
  case-insensitive regex; a subagent whose type is missing still gets them). Set it to the
  code-writing types you use. Review and research work delegated as `general-purpose`, the
  default type, keeps getting the rules unless the regex leaves that type out (GROUNDED, from
  the code).
- `PONYTAIL_MAP=0` in untrusted repositories.
- Read the `hooks/` diff before accepting a new version.

## Not checked

Behavioural effects of the persona on research or probe outcomes; ponytail's adapters for
other agent harnesses; whether workflow `agent()` stages receive the SubagentStart
injection (likely, unmeasured); diff quality in the A/B.
