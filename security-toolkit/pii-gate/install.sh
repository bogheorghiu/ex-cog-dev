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

mkdir -p "$TOP/.githooks" "$TOP/.github/workflows"
# pre-push.test.sh ships with the hooks on purpose: the suite is what makes a change to pre-push
# checkable in the repo that runs it, and a copy that drifts from its tests is the thing this gate
# cannot afford. Living in the hooks directory is harmless — git dispatches only exact hook names.
cp "$SRC/githooks/pre-commit" "$SRC/githooks/pre-push" "$SRC/githooks/overwrite-ci-denylist" \
   "$SRC/githooks/pre-push.test.sh" "$SRC/githooks/layer-parity.test.sh" "$TOP/.githooks/"
chmod +x "$TOP/.githooks/pre-commit" "$TOP/.githooks/pre-push" "$TOP/.githooks/overwrite-ci-denylist" \
         "$TOP/.githooks/pre-push.test.sh" "$TOP/.githooks/layer-parity.test.sh"
cp "$SRC/workflows/pii-denylist-guard.yml" "$TOP/.github/workflows/pii-denylist-guard.yml"

if ! grep -qx 'pii-denylist.local' "$TOP/.gitignore" 2>/dev/null; then
  # BOTH filenames, because the hooks accept both and their error text advertises both. Ignoring
  # only one leaves a contributor who follows that advice with an untracked file of real names —
  # visible in git status, IDE trees, screen shares and backups. That is a surface no gate reaches,
  # because no gate runs in the working tree.
  printf '\n# PII denylist — personal terms, must NEVER be committed (see .githooks/)\npii-denylist.local\npii-denylist.txt\n.pii-denylist.synced\n' >> "$TOP/.gitignore"
fi

git -C "$TOP" config core.hooksPath .githooks

if [ ! -f "$TOP/pii-denylist.local" ]; then
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
echo "  1. Populate $TOP/pii-denylist.local (one term per line; '#' comments ok)."
echo "  2. Commit the gate files BEFORE adding a remote."
echo "  3. Once a GitHub remote exists, run .githooks/overwrite-ci-denylist yourself to set the PII_DENYLIST secret (typed confirmation; pre-push only warns on drift, it never writes the secret)."
echo "  4. Prove it can fail: add a throwaway term, commit a file containing it, watch the hook BLOCK. A gate that has never blocked anything is not evidence."
