#!/usr/bin/env bash
# Install the PII gate into a git repo: hooks + CI workflow + gitignore
# entries + denylist template. Idempotent — safe to re-run to pick up
# template updates (it overwrites hooks/workflow, never the repo's
# pii-denylist.local).
#
# Usage: install.sh /path/to/repo
#
# Run BEFORE the repo gets any remote: the gate must exist before the first
# push, because pushed history is effectively permanent. A name in a commit
# survives a later delete of the file that carried it, and a private repo is
# one visibility toggle away from public.
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)"
REPO="${1:?usage: install.sh /path/to/repo}"
TOP="$(git -C "$REPO" rev-parse --show-toplevel)"

# Refuse to run from a LINKED WORKTREE. `git config core.hooksPath` writes to the repository's
# SHARED config, but the hook files land only in the worktree we were pointed at — so every other
# worktree, main included, would point core.hooksPath at a directory it does not have and run NO
# hooks at all. The gate would read as installed while being off everywhere but here, which is the
# worst state a gate can be in. Reproduced before this guard existed.
GIT_DIR_PATH="$(git -C "$TOP" rev-parse --path-format=absolute --git-dir)"
COMMON_DIR_PATH="$(git -C "$TOP" rev-parse --path-format=absolute --git-common-dir)"
if [ "$GIT_DIR_PATH" != "$COMMON_DIR_PATH" ]; then
  echo "REFUSING: $TOP is a linked worktree." >&2
  echo "  core.hooksPath is shared across all worktrees, but these hook files are not — installing" >&2
  echo "  here would disable hooks in every other worktree, silently." >&2
  echo "  Run the installer against the main worktree: $(dirname "$COMMON_DIR_PATH")" >&2
  exit 1
fi

# Never take over an existing hooks path blind. A repo using husky, or a machine-wide hooks dir,
# would lose those hooks with no warning and no record of what was there — this installer doing
# quietly to someone else's guardrails what this whole gate exists to prevent.
#
# Read the EFFECTIVE value, across every scope. `--local --get` cannot see a --global or --system
# setting by definition, so the machine-wide case was precisely the one an earlier version could
# not detect: the refusal never fired, a repo-level core.hooksPath was written, and it overrode the
# global one.
#
# The test is not "is one set" but "would anything STOP FIRING" — and that question has an answer
# even when core.hooksPath is UNSET. Setting it makes git look in .githooks INSTEAD of the default
# $GIT_DIR/hooks, so a repo using the pre-commit framework, lefthook, husky v4, or a hand-copied
# hook has live hooks there and no core.hooksPath at all. Gating the whole check on "a value is
# set" skipped exactly that repo and killed its hooks in silence. Measured: a .git/hooks/pre-commit
# fires with hooksPath unset and stops the moment it is set.
#
# So resolve the directory git is using NOW, whichever way it got there, and enumerate it.
# This gate's pre-commit chains a GLOBAL hooks path and only that, so a pre-commit is exempt only
# in that one case; everywhere else — repo scope (husky), system scope, or the default hooks dir —
# it would stop firing like any other hook. Refuse only if something real is left, and name it: a
# blanket refusal would block the common machine whose global hooks dir holds just a pre-commit,
# which loses nothing.
CURRENT_HOOKSPATH="$(git -C "$TOP" config --get core.hooksPath || true)"
LOCAL_HOOKSPATH="$(git -C "$TOP" config --local --get core.hooksPath || true)"
GLOBAL_HOOKSPATH="$(git -C "$TOP" config --global --get core.hooksPath || true)"
if [ "$CURRENT_HOOKSPATH" != ".githooks" ]; then
  CHAINED_PRECOMMIT=0
  if [ -z "$CURRENT_HOOKSPATH" ]; then
    HOOKSPATH_SCOPE="git's default"
    HOOKSDIR="$(git -C "$TOP" rev-parse --path-format=absolute --git-path hooks)"
    DISPLAY_HOOKSPATH="$HOOKSDIR"
  else
    if [ -n "$LOCAL_HOOKSPATH" ]; then
      HOOKSPATH_SCOPE="this repo"
    elif [ -n "$GLOBAL_HOOKSPATH" ] && [ "$GLOBAL_HOOKSPATH" = "$CURRENT_HOOKSPATH" ]; then
      HOOKSPATH_SCOPE="your global git config"
      CHAINED_PRECOMMIT=1
    else
      HOOKSPATH_SCOPE="your system git config"
    fi
    # Resolve relative to the repo, as git itself does.
    case "$CURRENT_HOOKSPATH" in
      /*) HOOKSDIR="$CURRENT_HOOKSPATH" ;;
       *) HOOKSDIR="$TOP/$CURRENT_HOOKSPATH" ;;
    esac
    DISPLAY_HOOKSPATH="$CURRENT_HOOKSPATH"
  fi
  ORPHANED=""
  if [ -d "$HOOKSDIR" ]; then
    for h in "$HOOKSDIR"/*; do
      [ -f "$h" ] && [ -x "$h" ] || continue
      case "$(basename "$h")" in
        pre-commit)
          # Exempt only when this gate will actually chain it — see CHAINED_PRECOMMIT above.
          if [ "$CHAINED_PRECOMMIT" -eq 1 ]; then continue; fi
          ;;
        *.sample|*.md|*.txt) continue ;;
      esac
      ORPHANED="$ORPHANED $(basename "$h")"
    done
  fi
  if [ -n "$ORPHANED" ]; then
    if [ "${PII_GATE_REPLACE_HOOKSPATH:-}" != "1" ]; then
      echo "REFUSING: this repo already runs hooks from ${DISPLAY_HOOKSPATH} (${HOOKSPATH_SCOPE})." >&2
      echo "  Pointing it at .githooks would take precedence, and these hooks would STOP FIRING" >&2
      echo "  for this repo:${ORPHANED}" >&2
      if [ "$CHAINED_PRECOMMIT" -eq 1 ]; then
        echo "  (pre-commit is not in that list because this gate chains a GLOBAL one.)" >&2
      fi
      echo "  Copy them into ${TOP}/.githooks, or re-run with PII_GATE_REPLACE_HOOKSPATH=1 to" >&2
      echo "  accept losing them here. Nothing has been written yet." >&2
      exit 1
    fi
    echo "NOTE: taking over hooks from ${DISPLAY_HOOKSPATH} (${HOOKSPATH_SCOPE}); these stop firing here:${ORPHANED}"
  fi
fi

mkdir -p "$TOP/.githooks" "$TOP/.github/workflows"
# pre-push.test.sh ships with the hooks on purpose: the suite is what makes a change to pre-push
# checkable in the repo that runs it, and a copy that drifts from its tests is the thing this gate
# cannot afford. Living in the hooks directory is harmless — git dispatches only exact hook names.
cp "$SRC/githooks/pre-commit" "$SRC/githooks/pre-push" "$SRC/githooks/overwrite-ci-denylist" \
   "$SRC/githooks/pre-push.test.sh" "$SRC/githooks/layer-parity.test.sh" "$TOP/.githooks/"
chmod +x "$TOP/.githooks/pre-commit" "$TOP/.githooks/pre-push" "$TOP/.githooks/overwrite-ci-denylist" \
         "$TOP/.githooks/pre-push.test.sh" "$TOP/.githooks/layer-parity.test.sh"
cp "$SRC/workflows/pii-denylist-guard.yml" "$TOP/.github/workflows/pii-denylist-guard.yml"

# BOTH denylist filenames, because the hooks accept both and their error text advertises both.
# Ignoring only one leaves a contributor who follows that advice with an untracked file of real
# names — visible in git status, IDE trees, screen shares and backups. That is a surface no gate
# reaches, because no gate runs in the working tree.
#
# Each name is tested SEPARATELY. A single guard on `pii-denylist.local` looked equivalent and was
# not: a repo that already ignored that one name skipped the whole block, so `pii-denylist.txt`
# stayed committable — the exact hole the both-names append exists to close — and the shipped
# workflow's `parity` job then failed on every push, since it asserts .gitignore covers every name
# pre-push accepts.
[ -f "$TOP/.gitignore" ] || : > "$TOP/.gitignore"
gi_added=0
for n in pii-denylist.local pii-denylist.txt .pii-denylist.synced; do
  if ! grep -qx -- "$n" "$TOP/.gitignore"; then
    if [ "$gi_added" -eq 0 ]; then
      printf '\n# PII denylist — personal terms, must NEVER be committed (see .githooks/)\n' >> "$TOP/.gitignore"
      gi_added=1
    fi
    printf '%s\n' "$n" >> "$TOP/.gitignore"
  fi
done

git -C "$TOP" config core.hooksPath .githooks

# Seed only when the repo has NO denylist under EITHER accepted name. Testing just
# `pii-denylist.local` repeats the mistake fixed in the gitignore block above, and here it is
# worse than a missing ignore line: retrofitting a repo whose denylist is named
# `pii-denylist.txt` would drop an EMPTY `pii-denylist.local` beside it, and both hooks search
# `.local` before `.txt` and stop at the first hit — so the gate would read the empty file,
# normalize it to nothing, and report itself INACTIVE while the operator's real terms sat
# unread one filename away. Step 3 below would then write that empty template into the CI
# secret. Retrofitting an existing repo is a supported case, so this path has to be right.
existing_denylist=""
for n in pii-denylist.local pii-denylist.txt; do
  if [ -f "$TOP/$n" ]; then existing_denylist="$n"; break; fi
done

if [ -n "$existing_denylist" ]; then
  echo "Keeping this repo's existing $existing_denylist (not overwritten)."
else
  # Seed from the EMPTY shipped template by default. If you keep a standing
  # denylist of your own (the same personal terms recur across your repos),
  # point PII_DENYLIST_DEFAULT at it and the installer seeds from that
  # instead — a private path on your machine, never a path in this repo.
  #
  # Unset by default, deliberately: an installer that silently seeded a
  # maintainer's own terms would ship those terms to everyone who ran it.
  DEFAULT="${PII_DENYLIST_DEFAULT:-}"
  if [ -n "$DEFAULT" ] && [ -f "$DEFAULT" ]; then
    cp "$DEFAULT" "$TOP/pii-denylist.local"
  else
    cp "$SRC/pii-denylist.local.template" "$TOP/pii-denylist.local"
  fi
fi

echo "PII gate installed into $TOP:"
echo "  .githooks/{pre-commit,pre-push,overwrite-ci-denylist,pre-push.test.sh,layer-parity.test.sh} + CI workflow + gitignore entries; core.hooksPath set."
echo "Next:"
echo "  1. Populate $TOP/${existing_denylist:-pii-denylist.local} (one term per line; '#' comments ok)."
echo "  2. Commit the gate files BEFORE adding a remote."
echo "  3. Once a GitHub remote exists, run .githooks/overwrite-ci-denylist yourself to set the PII_DENYLIST secret (typed confirmation; pre-push only warns on drift, it never writes the secret)."
echo "  4. Prove it can fail: add a throwaway term, commit a file containing it, watch the hook BLOCK. A gate that has never blocked anything is not evidence."
