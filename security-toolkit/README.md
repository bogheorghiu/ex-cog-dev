# security-toolkit

Threat-detection and dangerous-action-blocking hooks for Claude Code, plus security skills.

All hooks register automatically via `hooks/hooks.json` once the plugin is installed — no manual `settings.json` editing required. The plugin also ships one command (`/pr-merge-guard`) and one skill (`pr-merge-guard`) for the optional PR-merge guard — see [The PR-merge guard](#the-pr-merge-guard) — plus the [`windows-wsl-security-verification`](#the-windows-wsl-security-verification-skill) and [`pii-gate`](#the-pii-gate-skill-and-installer) skills.

## What this is — and isn't

These hooks are **guardrails against accidents and foot-guns**, not an adversarial security boundary. They catch the common dangerous *mistake* — an autonomous `rm -rf`, a push to `main`, a `--no-verify` — and surface suspicious tool output; they do **not** contain a determined or adversarial actor. `block-dangerous-git.sh` in particular documents its own bypasses inline (wrapper-execs like `bash -c` / `eval` / `xargs`, dangerous commands chained after a non-`cd` segment, base64/hex obfuscation, quoted-space paths, bare subshells, long-form flags). Treat them as defense-in-depth that lowers the odds of a costly slip — not a sandbox, and not a policy to rely on against malice.

## Hooks

| Hook | Event | Matcher | What it does |
|---|---|---|---|
| `detect-prompt-injection.sh` | PostToolUse | `*` | Scan tool outputs (including MCP) for prompt-injection patterns. Tiered: HIGH_CONFIDENCE matches emit an in-session warning + log entry; LOW_CONFIDENCE matches log silently. Allowlist via `PROMPT_INJECTION_ALLOWLIST_GLOB` env var to suppress self-triggering on docs that describe the patterns. |
| `block-dangerous-git.sh` | PreToolUse | `Bash` | Block push to main/master, force push, `--no-verify`, `--admin`, `git checkout --`, `git stash drop`, `git reset --hard`, `git clean -fd`, `rm -rf` on directories, direct GitHub API merge calls. Blocking `gh pr merge` is **off by default** — turn it on with the `/pr-merge-guard` command or the `EXCOG_BLOCK_PR_MERGE` env var (see [The PR-merge guard](#the-pr-merge-guard)). |
| `block-dc-config.sh` | PreToolUse | `mcp__desktop-commander__*` | Block autonomous modification of Desktop Commander settings (`set_config_value`). |
| `block-dc-execute.sh` | PreToolUse | `mcp__desktop-commander__*` | Block `start_process` / `execute_command` (bypasses sandbox; use the Bash tool instead). |
| `announce-pr-merge-guard.sh` | SessionStart | — | One-time, sentinel-gated notice that the optional PR-merge guard exists and is off by default. **Fires only on a recognized Claude Code surface**: excludes Cowork / Dispatch explicitly (`CLAUDE_CODE_IS_COWORK` / `CLAUDE_CODE_BRIEF`), then announces only with `CLAUDECODE=1` and an allowlisted `CLAUDE_CODE_ENTRYPOINT` (`cli` / `remote_*`) — silent everywhere else, where this git-workflow notice would only confuse a non-Code user. Then fires once per machine (writes `~/.claude/security-toolkit/.pr-merge-guard-introduced`) and stays silent. Pure announcer: never blocks, always exits 0. |

> No separate "detect-dc-injection" hook is needed. Desktop Commander tool outputs are covered by `detect-prompt-injection.sh`'s `*` matcher — the `tool` field in the JSONL log lets you filter for `mcp__desktop-commander__*` if you want DC-only audit.

## The windows-wsl-security-verification skill

The hooks above are the *prevention* layer; this skill is the *detection/recovery* layer — what you reach for when prevention may have already failed. It guides an "am I compromised?" IOC triage of a **Windows + WSL2 dev box** after a supply-chain scare (a poisoned npm/PyPI package, a trojaned VS Code extension, a backdoored dependency that ran as you), then a surface-reduction pass. It fires on "am I hacked / did I get owned", on a named bad package or CVE in your dependency chain, or on an AV detection you're unsure how to read.

What it carries beyond a checklist: the discriminators that keep triage honest in both directions — filename IOCs via `find -name` not content-grep (your own notes match a researched term), VirusTotal *named-family* verdicts over the aggregate "popular threat label" (grayware vs. a trojan wearing the app's name), web-filter blocks read as destination-reputation events rather than infections, and the third-party-AV/Defender active-passive interplay (one full scan, not two).

Honest limits, stated in the skill itself: it is **Windows/WSL-specific** (macOS and bare-Linux siblings are future work, not covered here); it **verifies, it does not harden** (it hands off to a hardening track at the end); and a clean result **raises confidence without proving** a machine clean — a good rootkit's job is to hide.

## The `pii-gate` skill and installer

Everything else here is scoped to a session or a machine — the hooks watch what Claude does in a session, the WSL skill triages a box after the fact. This one is scoped to a *repository*: `pii-gate/` is a drop-in gate that blocks personal names from reaching a remote — a pre-commit hook (staged diff), a pre-push hook (everything a push carries), and a CI workflow (tracked tree, full history, and gitleaks for secrets). The skill fires on `git init`, adding a remote, or a first push; `pii-gate/install.sh <repo>` does the install.

Everything the gate does and how to run it lives in `skills/pii-gate/SKILL.md` and the installer's own output — not repeated here. Three things this README is the right place for:

**The shipped denylist template is empty, permanently.** `pii-gate/pii-denylist.local.template` carries no terms and must never carry any: a denylist committed to a repo *is* the leak it exists to prevent. The installer copies it to a gitignored `pii-denylist.local` that the operator fills in. An optional `PII_DENYLIST_DEFAULT` env var can point at a private standing list, and is unset by default so the installer can never ship one maintainer's terms to everyone who runs it. `pii-gate/payload-parity.test.sh` asserts the zero-terms property on every PR.

**This repo both runs the gate and ships it, and the running copy is the reference.** `.githooks/` and `.github/workflows/pii-denylist-guard.yml` are what actually gate this repository; `pii-gate/` is the copy consumers install. The shipped copy is exercised by nobody here — it is inert data until someone installs it — so drift in it fails first for a consumer, in their repo. `payload-parity.test.sh` compares the two on every PR: hooks byte-for-byte, workflows job-list and body. Change one side and the check tells you to change the other.

**Installing it is not arming it.** The skill's "Prove it can fail" section is the step that matters and the one most likely to be skipped; it explains why a green run means nothing until the gate has blocked once, and walks through making it block on purpose.

## `hooks.json` quoting convention

The hook commands are written as `"\"${CLAUDE_PLUGIN_ROOT}/hooks/<name>.sh\""` — JSON-escaped outer double-quotes wrap the shell-level double-quoted path. The inner quotes are intentional: they protect against word-splitting when `$CLAUDE_PLUGIN_ROOT` resolves to a path containing spaces. Don't "simplify" them away.

## Tests

Tests are co-located with each hook:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/hooks/detect-prompt-injection.test.sh
bash ${CLAUDE_PLUGIN_ROOT}/hooks/block-dangerous-git.test.sh
bash ${CLAUDE_PLUGIN_ROOT}/hooks/announce-pr-merge-guard.test.sh
bash ${CLAUDE_PLUGIN_ROOT}/hooks/block-dc.test.sh
```

The PII gate carries three more. All three are written repo-root-relative, because the last two live outside the plugin and no plugin-root path can name them:

```bash
bash security-toolkit/pii-gate/payload-parity.test.sh   # shipped copy == running copy
bash .githooks/pre-push.test.sh                         # the pre-push hook's own behaviour
bash .githooks/layer-parity.test.sh                     # the gate's layers agree with each other
```

They answer three different questions, and only the first looks at the payload. `payload-parity` compares `security-toolkit/pii-gate/` against `.githooks/` (and resolves its own location, so it runs from any working directory). `pre-push.test.sh` drives *this repo's running hook* against throwaway scratch repos. `layer-parity` checks that the hooks, the gitignore and the CI workflow still agree about what a denylist is and where it lives — it ships to consumers too, and the workflow's `parity` job runs it on every push.

All currently passing, and every hook here now has one: `block-dc-config.sh` and `block-dc-execute.sh` are both covered by `hooks/block-dc.test.sh`, which CI runs alongside the rest. (This sentence previously said those two were untested; that stopped being true when that suite landed.)

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
