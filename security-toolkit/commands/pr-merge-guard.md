---
description: Show or change the PR-merge guard (whether Claude is blocked from running `gh pr merge`). Off by default. Usage: /pr-merge-guard [status|on|off]
argument-hint: "[status|on|off]"
allowed-tools: Bash(mkdir:*), Bash(rm:*), Bash(printf:*), Bash(cat:*), Bash(test:*), Bash(echo:*)
---

# PR-merge guard — show or change the setting

**Why this command exists:** the security-toolkit can block Claude from running
`gh pr merge` (so a human always does the merge). It is **OFF by default** —
`gh pr merge` already passes through GitHub branch protection, so the block is an
extra belt-and-suspenders, not a safety floor. This command lets you (or Claude)
see and flip that setting **without editing files or exporting environment
variables by hand**. It writes a per-user state file that the guard re-reads on
every git command, so a change takes effect **immediately** — no restart.

The argument is in `$ARGUMENTS` (one of `status`, `on`, `off`; empty means
`status`). Do **exactly** the matching step below, then stop.

## If `$ARGUMENTS` is empty or `status` → report the current state

Run this block verbatim and show the user its output:

```bash
STATE_FILE="$HOME/.claude/security-toolkit/pr-merge-guard"
ENV_VAL="${EXCOG_BLOCK_PR_MERGE:-}"
if [[ "$ENV_VAL" =~ ^(1|true|yes)$ ]]; then
  echo "PR-merge guard: ON  (forced by EXCOG_BLOCK_PR_MERGE=$ENV_VAL in your environment)"
  echo "  → While that env var is set, it overrides the on/off file below."
elif [[ "$ENV_VAL" =~ ^(0|false|no)$ ]]; then
  echo "PR-merge guard: OFF (forced by EXCOG_BLOCK_PR_MERGE=$ENV_VAL in your environment)"
  echo "  → While that env var is set, it overrides the on/off file below."
elif [[ -f "$STATE_FILE" ]] && [[ "$(tr -d '[:space:]' < "$STATE_FILE")" =~ ^(1|true|yes|on)$ ]]; then
  echo "PR-merge guard: ON  (set via /pr-merge-guard on; file: $STATE_FILE)"
  echo "  → Claude is blocked from running 'gh pr merge'. Turn off with: /pr-merge-guard off"
else
  echo "PR-merge guard: OFF (default)"
  echo "  → Claude may run 'gh pr merge'. Turn on with: /pr-merge-guard on"
fi
```

Then report the state in one plain sentence. Do not change anything.

## If `$ARGUMENTS` is `on` → turn the block ON

```bash
mkdir -p "$HOME/.claude/security-toolkit"
printf '1' > "$HOME/.claude/security-toolkit/pr-merge-guard"
echo "PR-merge guard is now ON. Claude is blocked from running 'gh pr merge'; a human must merge. Effective immediately. Turn off with: /pr-merge-guard off"
```

If `EXCOG_BLOCK_PR_MERGE` is also set in the environment to a non-truthy value
(`0`/`false`/`no`), tell the user it will override this file and keep the guard
OFF until they unset it — the env var wins.

## If `$ARGUMENTS` is `off` → turn the block OFF (the default)

```bash
rm -f "$HOME/.claude/security-toolkit/pr-merge-guard"
echo "PR-merge guard is now OFF (default). Claude may run 'gh pr merge'. Turn on with: /pr-merge-guard on"
```

If `EXCOG_BLOCK_PR_MERGE` is set in the environment to a truthy value
(`1`/`true`/`yes`), tell the user the guard will stay ON despite this, because
that env var overrides the file — they'd need to unset it (or remove it from
their settings.json `env`) to actually allow merges.

## Anything else in `$ARGUMENTS`

Say you didn't recognize it and show the three valid forms: `/pr-merge-guard`
(status), `/pr-merge-guard on`, `/pr-merge-guard off`.
