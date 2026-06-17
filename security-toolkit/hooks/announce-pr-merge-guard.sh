#!/bin/bash
# SessionStart hook: one-time announcement of the PR-merge guard feature.
#
# WHY: the security-toolkit ships an optional PR-merge guard that is OFF by
# default (see block-dangerous-git.sh). A user who installs the plugin should
# learn the feature exists without having to read the README or dig through
# settings — but exactly once, not on every session. This hook injects a short
# notice the first time it runs, then writes a sentinel so it stays silent
# forever after.
#
# WHY SessionStart (not UserPromptSubmit): a UserPromptSubmit hook would run on
# every single prompt for the life of the install just to deliver a one-time
# message — needless per-turn execution. SessionStart runs once per session, and
# the sentinel narrows that to once ever. The cost is that a *mid-session* plugin
# install + /reload-plugins will not fire SessionStart until the next session
# (it is a session-lifecycle event, not a plugin-load event) — that gap is
# acceptable because the guard is OFF by default (nothing surprising happens in
# the meantime) and the `pr-merge-guard` skill covers the topic reactively in the
# current session if the user raises it.
#
# The hook is a pure announcer: it never blocks, always exits 0, and emits the
# notice to stdout (which SessionStart adds to the model's context, the same
# mechanism vasana-system/hooks/vasana.sh relies on).
#
# WHY THE CONTEXT GATE (below): this plugin also runs under non-Code surfaces
# built on the Claude Agent SDK — Cowork and Dispatch — where the SessionStart
# hook still fires. There the notice is pure noise: it describes a `gh pr merge`
# git workflow a Dispatch/Cowork user never drives, and it confused a real
# Dispatch user (the notice surfaced mid-task in an unrelated research session).
# A prose "only announce in Code" instruction can't fix this — it asks the model
# to self-suppress and the model may emit it anyway. So we gate in the script,
# on the environment, BIASED TO SILENCE: announce only when we positively
# recognize a Claude Code surface; on anything unrecognized (Cowork, Dispatch,
# headless SDK) stay quiet. The deliberate cost: on an unrecognized Code surface
# we skip a one-time tip — strictly better than confusing a non-Code user. No env
# var is *documented* to separate Code from the Agent SDK, but real Cowork +
# Dispatch environment dumps show both set CLAUDE_CODE_IS_COWORK=1 (Dispatch also
# CLAUDE_CODE_BRIEF=1, entrypoint `local-agent`). So the gate excludes those
# surfaces explicitly AND, biased to silence, allowlists only known-interactive
# entrypoints — widen the allowlist only against a verified entrypoint value
# (see is_claude_code_surface).
#
# Sentinel path is overridable via EXCOG_PR_MERGE_INTRO_SENTINEL (the test uses
# this for isolation); default lives under the user's ~/.claude state dir so it
# survives plugin updates (the plugin cache is wiped on update).

set -u

# Positive detection of an interactive Claude Code surface. Returns 0 (announce)
# only for a recognized Code entrypoint; 1 (stay silent) for everything else.
is_claude_code_surface() {
    # Cowork and Dispatch (Agent-SDK "local-agent" surfaces) both set
    # CLAUDE_CODE_IS_COWORK=1; Dispatch also sets CLAUDE_CODE_BRIEF=1. These are
    # the non-interactive surfaces this git-workflow notice must stay out of —
    # confirmed from real Cowork + Dispatch env dumps. Exclude them first and
    # explicitly, so the gate holds even if their CLAUDE_CODE_ENTRYPOINT ever
    # changes to a value the allowlist below would otherwise accept.
    [[ -n "${CLAUDE_CODE_IS_COWORK:-}" ]] && return 1
    [[ -n "${CLAUDE_CODE_BRIEF:-}" ]] && return 1
    # Must be a Claude-Code-spawned process at all (CLAUDECODE=1 is set in every
    # Code subprocess, incl. hooks). Absent → not Code → silent.
    [[ "${CLAUDECODE:-}" == "1" ]] || return 1
    # Bias to silence: announce only on entrypoints confirmed to be interactive
    # Claude Code a human reads —
    #   cli       — the terminal CLI (including an IDE's integrated terminal)
    #   remote_*  — Claude Code on the web / mobile (remote execution, e.g.
    #               remote_mobile)
    # — and stay silent on anything unrecognized (e.g. local-agent).
    case "${CLAUDE_CODE_ENTRYPOINT:-}" in
        cli | remote_*) return 0 ;;
        *) return 1 ;;
    esac
}

# Not a recognized Claude Code surface → stay silent, and do NOT touch the
# sentinel (so a Cowork/Dispatch run can't consume the one-time Code announcement
# when HOME is shared with a Code install on the same machine).
if ! is_claude_code_surface; then
    exit 0
fi

SENTINEL="${EXCOG_PR_MERGE_INTRO_SENTINEL:-${HOME}/.claude/security-toolkit/.pr-merge-guard-introduced}"

# Already announced once → stay silent.
if [[ -f "$SENTINEL" ]]; then
    exit 0
fi

cat <<'EOF'
<security-toolkit-notice>
ANNOUNCE ONCE to the user (briefly, then continue with whatever they asked):

The security-toolkit plugin includes an optional **PR-merge guard**. It is
**OFF by default**, which means you (Claude) may run `gh pr merge` on PRs you
author — those still pass through GitHub branch protection, so review/checks
are not bypassed. If the user wants a hard rule that a human always does the
merge, they can turn the guard ON.

Tell the user, in one or two sentences, that this setting exists and is off by
default, and that they can:
  • see it:      /pr-merge-guard
  • turn it on:  /pr-merge-guard on
  • turn it off: /pr-merge-guard off
  • or just ask you about it (the pr-merge-guard skill will explain and can
    toggle it for them).

Do not nag or repeat this in later turns. This is a one-time heads-up.
</security-toolkit-notice>
EOF

# Record that the notice has been shown, so it never fires again. Best-effort:
# if the state dir can't be created/written, we simply exit 0 — re-announcing on
# a later session is a far better failure mode than breaking session startup.
mkdir -p "$(dirname "$SENTINEL")" 2>/dev/null && : > "$SENTINEL" 2>/dev/null

exit 0
