# security-toolkit

Threat-detection and dangerous-action-blocking hooks for Claude Code.

All hooks register automatically via `hooks/hooks.json` once the plugin is installed — no manual `settings.json` editing required.

## What this is — and isn't

These hooks are **guardrails against accidents and foot-guns**, not an adversarial security boundary. They catch the common dangerous *mistake* — an autonomous `rm -rf`, a push to `main`, a `--no-verify` — and surface suspicious tool output; they do **not** contain a determined or adversarial actor. `block-dangerous-git.sh` in particular documents its own bypasses inline (wrapper-execs like `bash -c` / `eval` / `xargs`, dangerous commands chained after a non-`cd` segment, base64/hex obfuscation, quoted-space paths, bare subshells, long-form flags). Treat them as defense-in-depth that lowers the odds of a costly slip — not a sandbox, and not a policy to rely on against malice.

## Hooks

| Hook | Event | Matcher | What it does |
|---|---|---|---|
| `detect-prompt-injection.sh` | PostToolUse | `*` | Scan tool outputs (including MCP) for prompt-injection patterns. Tiered: HIGH_CONFIDENCE matches emit an in-session warning + log entry; LOW_CONFIDENCE matches log silently. Allowlist via `PROMPT_INJECTION_ALLOWLIST_GLOB` env var to suppress self-triggering on docs that describe the patterns. |
| `block-dangerous-git.sh` | PreToolUse | `Bash` | Block `gh pr merge`, push to main/master, force push, `--no-verify`, `--admin`, `git checkout --`, `git stash drop`, `git reset --hard`, `git clean -fd`, `rm -rf` on directories, direct GitHub API merge calls. |
| `block-dc-config.sh` | PreToolUse | `mcp__desktop-commander__*` | Block autonomous modification of Desktop Commander settings (`set_config_value`). |
| `block-dc-execute.sh` | PreToolUse | `mcp__desktop-commander__*` | Block `start_process` / `execute_command` (bypasses sandbox; use the Bash tool instead). |

> No separate "detect-dc-injection" hook is needed. Desktop Commander tool outputs are covered by `detect-prompt-injection.sh`'s `*` matcher — the `tool` field in the JSONL log lets you filter for `mcp__desktop-commander__*` if you want DC-only audit.

## `hooks.json` quoting convention

The hook commands are written as `"\"${CLAUDE_PLUGIN_ROOT}/hooks/<name>.sh\""` — JSON-escaped outer double-quotes wrap the shell-level double-quoted path. The inner quotes are intentional: they protect against word-splitting when `$CLAUDE_PLUGIN_ROOT` resolves to a path containing spaces. Don't "simplify" them away.

## Tests

Tests are co-located with each hook:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/hooks/detect-prompt-injection.test.sh
bash ${CLAUDE_PLUGIN_ROOT}/hooks/block-dangerous-git.test.sh
```

Both currently passing. `block-dc-config.sh` and `block-dc-execute.sh` do not yet have test suites — adding these is tracked in the parent handoff.

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

## Logs

Two log destinations:

- **`~/.claude/logs/prompt-injection-detections.log`** — JSONL, one entry per detection (tiered: `confidence`, `high_count`, `low_count`, `preview`). Filter by the `tool` field to see MCP-specific events.
- **`$CLAUDE_PROJECT_DIR/.claude/hooks/logs/blocked-attempts.log`** (falls back to `./.claude/hooks/logs/` if `$CLAUDE_PROJECT_DIR` is unset) — plain text, one entry per `block-dangerous-git.sh` block. Project-scoped so different projects can audit independently.
