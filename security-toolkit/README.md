# security-toolkit

Threat-detection and dangerous-action-blocking hooks for Claude Code, plus security skills.

All hooks register automatically via `hooks/hooks.json` once the plugin is installed — no manual `settings.json` editing required. The plugin also ships one command (`/pr-merge-guard`) and one skill (`pr-merge-guard`) for the optional PR-merge guard — see [The PR-merge guard](#the-pr-merge-guard) — and the [`windows-wsl-security-verification`](#the-windows-wsl-security-verification-skill) skill.

## What this is — and isn't

These hooks are **guardrails against accidents and foot-guns**, not an adversarial security boundary. They catch the common dangerous *mistake* — an autonomous `rm -rf`, a push to `main`, a `--no-verify` — and surface suspicious tool output; they do **not** contain a determined or adversarial actor. `block-dangerous-git.sh` in particular documents its own bypasses inline (wrapper-execs like `bash -c` / `eval` / `xargs`, dangerous commands chained after a non-`cd` segment, base64/hex obfuscation, quoted-space paths, bare subshells, long-form flags). Treat them as defense-in-depth that lowers the odds of a costly slip — not a sandbox, and not a policy to rely on against malice.

## Hooks

| Hook | Event | Matcher | What it does |
|---|---|---|---|
| `detect-prompt-injection.sh` | PostToolUse | `*` | Scan tool outputs (including MCP) for prompt-injection patterns. Tiered: HIGH_CONFIDENCE matches emit an in-session warning + log entry; LOW_CONFIDENCE matches log silently. Allowlist via `PROMPT_INJECTION_ALLOWLIST_GLOB` env var to suppress self-triggering on docs that describe the patterns. |
| `block-dangerous-git.sh` | PreToolUse | `Bash` | Block push to main/master, force push, `--no-verify`, `--admin`, `git checkout --`, `git stash drop`, `git reset --hard`, `git clean -fd`, `rm -rf` on directories, direct GitHub API merge calls. Blocking `gh pr merge` is **off by default** — turn it on with the `/pr-merge-guard` command or the `EXCOG_BLOCK_PR_MERGE` env var (see [The PR-merge guard](#the-pr-merge-guard)). |
| `block-dc-config.sh` | PreToolUse | `mcp__desktop-commander__*` | Block autonomous modification of Desktop Commander settings (`set_config_value`). |
| `block-dc-execute.sh` | PreToolUse | `mcp__desktop-commander__*` | Block `start_process` / `execute_command` (bypasses sandbox; use the Bash tool instead). |
| `announce-pr-merge-guard.sh` | SessionStart | — | One-time, sentinel-gated notice that the optional PR-merge guard exists and is off by default. **Fires only on a recognized Claude Code surface** (gated on `CLAUDECODE` + an allowlisted `CLAUDE_CODE_ENTRYPOINT`); stays silent in Cowork / Dispatch, where this git-workflow notice would only confuse a non-Code user. Then fires once per machine (writes `~/.claude/security-toolkit/.pr-merge-guard-introduced`) and stays silent. Pure announcer: never blocks, always exits 0. |

> No separate "detect-dc-injection" hook is needed. Desktop Commander tool outputs are covered by `detect-prompt-injection.sh`'s `*` matcher — the `tool` field in the JSONL log lets you filter for `mcp__desktop-commander__*` if you want DC-only audit.

## The windows-wsl-security-verification skill

The hooks above are the *prevention* layer; this skill is the *detection/recovery* layer — what you reach for when prevention may have already failed. It guides an "am I compromised?" IOC triage of a **Windows + WSL2 dev box** after a supply-chain scare (a poisoned npm/PyPI package, a trojaned VS Code extension, a backdoored dependency that ran as you), then a surface-reduction pass. It fires on "am I hacked / did I get owned", on a named bad package or CVE in your dependency chain, or on an AV detection you're unsure how to read.

What it carries beyond a checklist: the discriminators that keep triage honest in both directions — filename IOCs via `find -name` not content-grep (your own notes match a researched term), VirusTotal *named-family* verdicts over the aggregate "popular threat label" (grayware vs. a trojan wearing the app's name), web-filter blocks read as destination-reputation events rather than infections, and the third-party-AV/Defender active-passive interplay (one full scan, not two).

Honest limits, stated in the skill itself: it is **Windows/WSL-specific** (macOS and bare-Linux siblings are future work, not covered here); it **verifies, it does not harden** (it hands off to a hardening track at the end); and a clean result **raises confidence without proving** a machine clean — a good rootkit's job is to hide.

## `hooks.json` quoting convention

The hook commands are written as `"\"${CLAUDE_PLUGIN_ROOT}/hooks/<name>.sh\""` — JSON-escaped outer double-quotes wrap the shell-level double-quoted path. The inner quotes are intentional: they protect against word-splitting when `$CLAUDE_PLUGIN_ROOT` resolves to a path containing spaces. Don't "simplify" them away.

## Tests

Tests are co-located with each hook:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/hooks/detect-prompt-injection.test.sh
bash ${CLAUDE_PLUGIN_ROOT}/hooks/block-dangerous-git.test.sh
bash ${CLAUDE_PLUGIN_ROOT}/hooks/announce-pr-merge-guard.test.sh
```

All three currently passing. `block-dc-config.sh` and `block-dc-execute.sh` do not yet have test suites — adding these is tracked in the parent handoff.

Skills are prose artifacts, so their *structure* is what gets unit-tested: `skills/test_skill_structure.py` (a twin of the research-toolkit/vasana-system linters, kept logic-identical) asserts every SKILL.md's frontmatter parses, `name == dir`, description ≤ 1024 chars, and exactly one `## Vasana` section — CI runs it on every PR. Triggering (does the skill actually fire on the right turns?) is a separate, tiered measurement — see `.claude/rules/skill-verification.md`.

## Requirements

- `jq` (used by all hooks for JSON parsing of the hook input protocol)
- Bash 4+ (uses arrays and `[[ ... ]]`)

## Configuration

### `PROMPT_INJECTION_ALLOWLIST_GLOB`

Colon-separated globs. File paths matching any glob skip prompt-injection detection. Setting this env var **replaces** the defaults (which cover the hook's own docs and a few common locations). Set to empty string to disable allowlisting entirely.

Example:

```bash
export PROMPT_INJECTION_ALLOWLIST_GLOB='*/docs/security/*:*/PROMPT-INJECTION-AWARENESS*'
```

### The PR-merge guard

The guard blocks Claude from running `gh pr merge` so a human always does the
merge. It is **OFF by default** — `gh pr merge` already goes through GitHub branch
protection (required checks/reviews), so blocking it client-side is an *extra*
"a human merges" preference, not a safety floor. The paths that actually *bypass*
review — push to main, force push, `--admin`, direct GitHub API merge calls — stay
unconditionally blocked regardless of this guard.

There are two ways to turn it on; the hook resolves them in this order:

**1. The `/pr-merge-guard` command (interactive, immediate).** The simplest path —
no files or env vars to edit by hand:

```
/pr-merge-guard          # show current state
/pr-merge-guard on       # block gh pr merge (a human merges)
/pr-merge-guard off      # allow gh pr merge (the default)
```

It writes a per-user state file at `~/.claude/security-toolkit/pr-merge-guard`,
which the hook re-reads on every git command — so a change takes effect
**immediately**, no restart. The `pr-merge-guard` **skill** explains the feature
and can flip it for you when you ask ("stop auto-merging," "lock down main," "can
you merge PRs?"). A one-time `SessionStart` notice (`announce-pr-merge-guard.sh`)
tells you the feature exists the first time you start a Claude Code session after
installing — it stays silent in Cowork / Dispatch, where the notice would only
confuse a non-Code user.

**2. The `EXCOG_BLOCK_PR_MERGE` env var (declarative, for config-as-code / CI).**
`1`/`true`/`yes` = on, `0`/`false`/`no` = off. When set to a recognized value it
is **authoritative and overrides the state file** (so CI or a committed
`settings.json` can force the guard on or off regardless of the local toggle):

```json
{
  "env": { "EXCOG_BLOCK_PR_MERGE": "1" }
}
```

Note that `settings.json` `env` only re-applies at session start, whereas the
command takes effect immediately — prefer the command for interactive use.

## Logs

Two log destinations:

- **`~/.claude/logs/prompt-injection-detections.log`** — JSONL, one entry per detection (tiered: `confidence`, `high_count`, `low_count`, `preview`). Filter by the `tool` field to see MCP-specific events.
- **`$CLAUDE_PROJECT_DIR/.claude/hooks/logs/blocked-attempts.log`** (falls back to `./.claude/hooks/logs/` if `$CLAUDE_PROJECT_DIR` is unset) — plain text, one entry per `block-dangerous-git.sh` block. Project-scoped so different projects can audit independently.
