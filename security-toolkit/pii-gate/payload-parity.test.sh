#!/usr/bin/env bash
# payload-parity.test.sh — fails when the SHIPPED gate drifts from the RUNNING gate.
#
# WHY THIS FILE EXISTS. This repo now does two things with one gate: it runs it (`.githooks/` +
# `.github/workflows/pii-denylist-guard.yml`) and it ships it (`security-toolkit/pii-gate/`, the
# plugin payload consumers install). Those are two copies of the same code, and two copies of
# anything drift the moment one is edited and the other is not — which is the entire subject of
# the sibling check, layer-parity.test.sh, and the reason it exists.
#
# The drift here is worse than ordinary duplication, because it is ASYMMETRIC. The running copy
# is exercised on every push: a mistake in it gets caught. The shipped copy is exercised by
# nobody in this repo — it is data until a consumer installs it — so a shipped copy that lost a
# job, or lost a `-w`, or lost the gitleaks step, looks exactly like a working one from in here.
# It fails first for the consumer, in their repo, on their history. That is the failure this
# file exists to make impossible: the copy people receive is checked against the copy we trust.
#
# The file list is DERIVED from install.sh's copy line rather than restated. Restating it would
# make this a third list that drifts like the first two; deriving it means adding a sixth hook to
# the installer automatically obliges that hook to match, with nobody editing this file.
#
# Run: bash security-toolkit/pii-gate/payload-parity.test.sh   (also runs in CI; see unit-tests.yml)
set -uo pipefail
cd "$(dirname "$0")/../.." || { echo "cannot reach the repo root"; exit 1; }

G=0
GREEN=$'\033[0;32m'; RED=$'\033[0;31m'; YEL=$'\033[0;33m'; NC=$'\033[0m'
chk() { # description, status
  if [ "$2" -eq 0 ]; then printf '  %sPASS%s  %s\n' "$GREEN" "$NC" "$1"
  else printf '  %sFAIL%s  %s\n' "$RED" "$NC" "$1"; G=1; fi
}

PAY=security-toolkit/pii-gate
RUN_WF=.github/workflows/pii-denylist-guard.yml
PAY_WF="$PAY/workflows/pii-denylist-guard.yml"
INSTALL="$PAY/install.sh"
TEMPLATE="$PAY/pii-denylist.local.template"

for f in "$INSTALL" "$PAY_WF" "$TEMPLATE" "$RUN_WF"; do
  [ -f "$f" ] || { echo "missing $f — the payload is incomplete, not merely drifted"; exit 1; }
done

echo "${YEL}--- The shipped hooks must BE the hooks this repo runs ---${NC}"

# Read the hook filenames out of the installer's cp line, so the installer stays the one place
# that says which files make up the gate.
HOOKS="$(grep -o '\$SRC/githooks/[A-Za-z0-9._-]*' "$INSTALL" | sed 's|.*/||' | sort -u)"
[ -n "$HOOKS" ] || { echo "could not read the hook list out of $INSTALL — has its cp line changed shape?"; exit 1; }

COUNT=0
for h in $HOOKS; do
  COUNT=$((COUNT + 1))
  if [ ! -f ".githooks/$h" ]; then
    chk "$h exists in .githooks/ (the installer ships a file this repo does not run)" 1
    continue
  fi
  cmp -s "$PAY/githooks/$h" ".githooks/$h"
  chk "$h is byte-identical: shipped copy == running copy" $?
done
[ "$COUNT" -ge 5 ]
chk "derived at least the 5 known gate files from the installer (got $COUNT)" $?

# Executability survives git: a payload hook that arrives without +x is copied without +x, and a
# hook git cannot execute does not run AND does not error. It is the silent-inactive failure.
for h in $HOOKS; do
  [ -x "$PAY/githooks/$h" ]
  chk "$h is executable in the payload (git preserves the mode; a non-exec hook silently never runs)" $?
done
[ -x "$INSTALL" ]
chk "install.sh is executable" $?

echo ""
echo "${YEL}--- The shipped workflow must carry every job, not just the denylist one ---${NC}"

# The lesson this encodes was learned the expensive way: a copy of this workflow that dropped the
# gitleaks job still validated, still ran, and still reported a green "denylist" result — so the
# check looked identical to a passing one while scanning for no secrets at all. Compare the JOB
# LIST, not merely the hooks.
RUN_JOBS="$(sed -n 's/^  \([a-z][a-z0-9_-]*\):$/\1/p' "$RUN_WF" | sort)"
PAY_JOBS="$(sed -n 's/^  \([a-z][a-z0-9_-]*\):$/\1/p' "$PAY_WF" | sort)"
[ -n "$RUN_JOBS" ] && [ "$RUN_JOBS" = "$PAY_JOBS" ]
chk "shipped workflow declares the same jobs as the running one" $?
if [ "$RUN_JOBS" != "$PAY_JOBS" ]; then
  echo "      running: $(echo "$RUN_JOBS" | tr '\n' ' ')"
  echo "      shipped: $(echo "$PAY_JOBS" | tr '\n' ' ')"
fi

grep -q 'gitleaks' "$PAY_WF"
chk "shipped workflow still installs gitleaks (secret scanning is not implied by the denylist job)" $?
grep -q 'sha256sum -c' "$PAY_WF"
chk "shipped workflow still verifies the gitleaks download against a pinned hash" $?

# KNOWN, DELIBERATE DIVERGENCE — recorded rather than hidden by omission. The two workflow files
# differ in their leading WHY comment: the running one names this repo's own reason for the gate,
# the shipped one states the general reason a consumer needs. Everything from the `on:` trigger
# down is the part that must agree, so that is what gets compared.
RUN_BODY="$(sed -n '/^on:/,$p' "$RUN_WF")"
PAY_BODY="$(sed -n '/^on:/,$p' "$PAY_WF")"
[ -n "$RUN_BODY" ] && [ "$RUN_BODY" = "$PAY_BODY" ]
chk "shipped and running workflows are identical from 'on:' down (headers may differ; see comment)" $?

echo ""
echo "${YEL}--- The shipped denylist template must be EMPTY of terms ---${NC}"

# The whole gate exists to keep personal terms out of a repo. A template that shipped with the
# maintainer's own terms would put those terms into every consumer's clone — this repo publishing
# exactly the thing it tells everyone never to publish. Comments and blank lines only.
TERMS="$(grep -cvE '^[[:space:]]*(#|$)' "$TEMPLATE")"
[ "$TERMS" -eq 0 ]
chk "template carries 0 denylist terms (found $TERMS)" $?

# Same failure by a different route: an installer that defaults to seeding from a maintainer's
# private file would ship the maintainer's terms to whoever ran it. The seed path must come from
# the environment and be empty unless the operator sets it.
# Matched as an ASSIGNMENT, not as a mention. The name also appears in the comment above that
# line, so a bare `grep PII_DENYLIST_DEFAULT` passes even after the code is changed to seed from
# a hard-coded path — verified by sabotage: replacing the assignment left this check green while
# the installer had already regained the defect. Same trap layer-parity.test.sh records for the
# secret-overwrite tool: a name on a comment line is documentation, not behaviour.
grep -qE '^[[:space:]]*[A-Z_]+="\$\{PII_DENYLIST_DEFAULT' "$INSTALL"
chk "installer ASSIGNS its optional seed path from PII_DENYLIST_DEFAULT (not merely mentions it)" $?
! grep -qE 'DEFAULT="\$(HOME|\{HOME)' "$INSTALL"
chk "installer does not hard-code a seed path under \$HOME" $?

echo ""
echo "${YEL}--- The payload must not leak the shipping repo's own paths ---${NC}"

# A consumer reads these files in their own repo. A path from the machine that built them is
# noise at best and an environment leak at worst.
#
# This file is excluded from its own scan: the patterns below ARE the check, so including it
# means the check fails whenever it is working. Self-triggering is the standard hazard of any
# scanner that names what it looks for (the prompt-injection hook carries an allowlist for the
# same reason) — and the honest fix is to exclude the detector, not to soften the pattern, which
# would blind it to the real thing.
! grep -rqE --exclude="$(basename "$0")" '(/home/[a-z]|ClaudeCodeHub|personal-vault)' "$PAY"
chk "no absolute home paths or private-folder names anywhere in the payload" $?

echo ""
echo "====================================="
if [ "$G" -eq 0 ]; then
  printf '%sThe shipped gate matches the running gate.%s\n' "$GREEN" "$NC"
else
  printf '%sPAYLOAD DRIFT — what we ship is not what we run.%s\n' "$RED" "$NC"
  echo "Re-sync security-toolkit/pii-gate/ from .githooks/ + $RUN_WF, or if the"
  echo "divergence is intentional, record it above as a named exception so the next reader"
  echo "learns it was chosen rather than forgotten."
fi
exit "$G"
