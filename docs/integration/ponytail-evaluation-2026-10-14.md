# Evaluation — the `ponytail` plugin (DietrichGebert/ponytail)

**Written:** 2026-10-14. **Subject:** ponytail 5.2.0, commit `2961b52`, as installed at user
scope in this repo's cloud environment (`~/.claude/settings.json`, marketplace source
`github: DietrichGebert/ponytail`). **Decision it serves:** whether to keep ponytail
installed where this repo is developed, and how.

Every claim below is tagged GROUNDED (observed directly or confirmed by an independent
check), UNRESOLVED (the evidence doesn't settle it) or Inference.

---

## 1. What it is

A "lazy senior developer" persona for coding agents: YAGNI, reuse before writing, stdlib
before dependencies, the smallest complete change, a test for any non-trivial logic, and a
closing line naming what was skipped. Delivered through three hooks plus six skills
(`ponytail`, `-review`, `-audit`, `-debt`, `-gain`, `-help`). No MCP server, no agents.

What runs in a Claude Code session (GROUNDED, from the code at `2961b52`):

| Hook | When | What it does |
|---|---|---|
| `SessionStart` | startup, resume, clear, compact | Writes a mode flag under `~/.claude`; injects the ruleset (~5.4 KB); runs `git ls-files` and injects a "codebase map" of top-level names; once, injects a nudge telling the model to offer to add a status line to `~/.claude/settings.json` |
| `SubagentStart` | every subagent spawn | Injects the ruleset (~3 KB) into the subagent while the mode is on |
| `UserPromptSubmit` | every prompt | Matches `/ponytail …`, "stop ponytail" and "normal mode", and switches the mode flag; otherwise emits nothing |

`claude plugin details` reports the hooks as "no model context cost". That is wrong in
practice: the SessionStart and SubagentStart output *is* model context.

## 2. Security

**Code at `2961b52`: low risk.** From this session's own read of the code; the
independent blind review is recorded in §6:

- No network access anywhere in the hook path.
- Process execution: `node` (its own map script) and `git ls-files` with constant
  arguments. No shell, and no external text is interpolated into a command.
- Writes are confined to `~/.claude` (or `$CLAUDE_CONFIG_DIR`) and `~/.config/ponytail`.
  The status-line script copy uses temp-file-then-rename, so it cannot write through a
  planted symlink.
- The codebase map reads only git-tracked files, skips symlinked files (`lstat`), filters paths
  through an allowlist regex, and emits only identifier-shaped names within ~2,000 characters.
  That leaves a **narrow but real** prompt-injection channel from repository content: words
  glued with `-` or `_` in directory or function names (e.g. a folder named
  `IMPORTANT-ignore-previous-instructions/`) reach the model, but spaces, newlines and
  punctuation cannot. Relevant only when opening untrusted repositories.
- The prompt hook reads every prompt but only regex-matches it. Nothing is stored or sent.
- `git ls-files` runs with the repository's own `.git/config`. Whether any config-defined
  helper fires for that command is UNRESOLVED; Claude Code runs git in the same repository
  anyway, so this adds little exposure of its own.

**The real risk is trust over time.** These hooks run arbitrary Node with your privileges
on every session start, prompt and subagent spawn, from a single maintainer's repository.
A review of one commit says nothing about the next one. In this cloud environment the
plugin is installed fresh when each container starts (Inference from the install timestamp
matching container start), so every session effectively runs whatever is at the
repository's HEAD that day. Whether a marketplace entry can be pinned to a ref or commit
is UNRESOLVED. `claude plugin marketplace add --help` (2.1.299) shows no such flag.

**One behavioural flag.** The SessionStart output tells the model to "proactively offer"
to edit `~/.claude/settings.json`. That is the plugin's legitimate setup path, not an
attack, but it is still a hook steering the model toward editing user settings. Declining
is safe: the plugin only nudges once. Accepting has a lasting effect: the hooks refresh
`~/.claude/ponytail-statusline.sh` from the plugin every session, and once `statusLine`
points at it, that script runs on every status refresh, outside the hook path, updated
silently with each plugin version. Benign in 5.2.0 (it prints a badge).

## 3. Interaction with this repo — the finding that matters

**Ponytail contaminates experiments run in this environment.** GROUNDED by the files the
hooks wrote and by transcripts, not by asking a model:

| Run style | Ponytail present? | Evidence |
|---|---|---|
| `claude -p --plugin-dir X` (the skill-testing dev recipe) | **Yes** | its mode file appeared for the run's cwd hash |
| same, plus `--setting-sources project` | No, and X's own hook still fired | no mode file; X's SessionStart marker written |
| `claude plugin eval` | No | trace `init.plugins` = plugin under test + built-ins only |
| Subagents (Agent tool) | **Yes** | "PONYTAIL MODE ACTIVE" in the subagent's own transcript |

So:

- Headless skill-firing runs pick up an extra persona in every arm. Fixed in this PR: the
  `skill-activation-testing` dev recipe now passes `--setting-sources project`.
- The probe-battery workflow (`.claude/workflows/probe-battery.js`) runs actor and judge as
  subagents, so ponytail's ruleset reaches both. That workflow `agent()` goes through the
  same SubagentStart path is an Inference, not measured. Its CANARY probe checks that
  plugins loaded, not that nothing extra did, so it would not catch this.
- Research-toolkit's investigation agents (orchestrator, critic, falsifier) also receive a
  "smallest version that does the core job" persona. Whether that makes sweeps shallower is
  UNRESOLVED (unmeasured). It is the direction to worry about, since those agents exist to
  go wide.

## 4. Value for this repo

- **Mostly duplicates existing rules.** `no-speculative-structure.md` (YAGNI) and
  `no-drive-by-edits.md` already carry the core. Ponytail's closing "what I skipped" line
  matches the operator's own skipped-check discipline.
- **What it adds:** an ordered reuse ladder (codebase → stdlib → installed dependency →
  new code), a `shortcut: <limit>, <when to upgrade>` comment convention that
  `/ponytail-debt` harvests, and on-demand review skills (`/ponytail-review`,
  `/ponytail-audit`) aimed at over-engineering. The review skills overlap the built-in
  `/simplify`.
- **Fit:** this repo is mostly prose and skills. The codebase map covers only code files,
  and the ruleset speaks to code. For skill and rule work it costs context and adds little.
- **Minor tension:** "comment only the why, in one line" against
  `reserve-prose-for-what-code-cannot-say.md` step 3, which says to write the why at
  whatever length it needs and never abstain.
- **The author's benchmarks** (−53% code, −26% cost, correctness level at 87/90 against
  86/90 with no skill) are UNRESOLVED: run by the author, who has a stake, and not
  independently replicated. The method is disclosed and the harness ships in
  `benchmarks/agentic/`, so the claims can be checked. What the numbers themselves report
  is "smaller and cheaper on coding tasks, no correctness gain". They make no claim about
  research or prose work.

## 5. Recommendations

1. **Don't run it always-on in this environment.** If it stays installed, set
   `PONYTAIL_DEFAULT_MODE=off` in the environment and switch it on with `/ponytail` for
   code-heavy sessions (the MCP servers, `.github/scripts`). Reason: low marginal value
   here, a measured experiment confound, and per-session context cost.
2. **Before any probe battery or skill-firing run in a session where it is on**, type
   `stop ponytail` (the subagent hook then injects nothing; GROUNDED from the code), or
   use `claude plugin eval`, which is already isolated.
3. **Optional scoping:** `PONYTAIL_SUBAGENT_MATCHER` limits subagent injection to agent
   types matching a regex (e.g. `general-purpose`), which keeps it out of research-toolkit
   agents.
4. **Treat updates as new code.** Re-read the `hooks/` diff before accepting a new
   version, or install from a fork you control.
5. **Decline the status-line nudge in cloud sessions.** `~/.claude` does not survive the
   container, so the edit buys nothing.

## 6. Verification record

- Hook code: read in full by this session, then given to a blind reviewer (separate model,
  open questions, no conclusions supplied). Result: agrees on every
  point of the low-risk read (no network, no shell, constant process arguments, writes
  confined to the config dirs, no prompt text echoed). It corrected one claim: this
  session first called injection through the codebase map "near zero"; the reviewer showed
  it is a real, low-bandwidth channel (now stated in §2). Further items it raised, each
  needing write access the attacker would already have or unverified Claude Code behaviour:
  a crafted git index plus a symlinked intermediate directory could make the map read
  identifier names from outside the project; the flag file's raw content is echoed
  unvalidated; whether a project's settings `env` can redirect `CLAUDE_CONFIG_DIR` for
  hooks is untested.
- Contamination table: four live runs on 2026-10-14, Claude Code 2.1.299, haiku. Each is
  judged by an artifact: a mode file, a hook marker file, an eval trace, a subagent
  transcript.
- **Not checked:** behavioural effects of the persona on research or probe outcomes (no A/B
  was run); ponytail's other-harness adapters (OpenCode, Pi, Hermes, Cursor and the rest
  never run under Claude Code); whether ref pinning is possible; whether workflow `agent()`
  calls trigger SubagentStart.
