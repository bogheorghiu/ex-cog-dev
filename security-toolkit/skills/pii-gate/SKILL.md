---
name: pii-gate
description: >-
  Installs a PII/secret gate into a git repo — pre-commit + pre-push hooks and a
  CI workflow that block personal names and secrets from reaching a remote. Fires
  BEFORE a repo can leak: on `git init`, "new repo", "set up a repo", "add a
  remote", "push this to GitHub", "publish this", "make this repo public", "first
  push", or "is it safe to push this?". Also fires on the retrofit case — an
  existing repo that already has a remote and needs the gate plus a full-history
  scan. Use when a repo will hold real names, client identifiers, addresses, or
  any personal context that must never enter git history. Covers denylist setup,
  the write-only `PII_DENYLIST` Actions secret, gitleaks secret scanning, and the
  armed-run proof that the gate actually blocks. Not for scanning a repo you are
  not about to push, and not a substitute for gitleaks alone.
---

# PII gate — install it before the first push

**Seed question:** *Once this repo has a remote, every name in its history is
permanent — so is the gate in place BEFORE that, or are we retrofitting after the
window already closed?*

## Why the ordering is the whole skill

Pushed history is effectively permanent. Deleting the file that carried a name
does not remove it from the commits that carried it, and a private repo is one
visibility toggle away from public. So the gate only makes "person-clean" durable
if it exists **before the first byte reaches the remote**. Retrofitting after a
push means the unprotected window already happened, and no amount of later
scanning closes it.

The installer is idempotent and takes seconds. There is no cost case for
deferring it.

## Install

```
bash "${CLAUDE_PLUGIN_ROOT}/pii-gate/install.sh" /path/to/repo
```

That copies the hooks into `.githooks/`, adds the CI workflow, appends the
gitignore entries, points `core.hooksPath` at `.githooks`, and — only if the repo
has no denylist under either accepted name — seeds an **empty**
`pii-denylist.local` at the repo root. A repo that already has one keeps it,
under whichever name it uses.

Re-running it updates the hooks and workflow in place and never touches an
existing denylist.

**It can refuse, and a refusal is information rather than a fault.** In every
case below it writes nothing at all and exits non-zero. There are three:

1. **The target is a linked worktree.** `core.hooksPath` is shared across
   worktrees while these files are not, so installing there would disable hooks
   in all the others. Run it against the main worktree instead; the message names
   the path.
2. **The repo runs hooks somewhere else that would go quiet** — a `.husky`
   directory, a machine-wide hooks dir, or the default `.git/hooks`. Pointing
   `core.hooksPath` at `.githooks` makes git stop looking there. Nothing is
   deleted, so the fix is to **copy those hooks into `.githooks/`** alongside the
   gate's, or re-run with `PII_GATE_REPLACE_HOOKSPATH=1` to accept that they stop
   running in this repo.
3. **`.githooks/` already holds hooks that are not this gate's.** Here the files
   would be **overwritten**, not merely silenced — so this is the one to slow
   down on. Move or rename them first. `PII_GATE_REPLACE_HOOKSPATH=1` also
   applies, but it means *replacing* those files: if they are untracked, nothing
   in the installer can give them back.

The one case it passes over quietly is a *global* hooks dir whose only hook is a
`pre-commit` — this gate chains that one, so nothing is lost. Re-running over an
installation of this gate is likewise silent: it tells its own hooks from
someone else's by content, not by filename.

## Then, in order

1. **The operator populates the denylist — never you.** One term per line; `#`
   comments and blanks ignored. Do not invent, guess, or type personal terms into
   it yourself, and do not read the finished file back into the conversation: the
   point of the gate is that those terms live in exactly one gitignored file and
   nowhere else. Ask them to fill it in and tell you when it's done.

   **Use the filename the installer printed**, which is `pii-denylist.local` on a
   fresh repo but `pii-denylist.txt` on a retrofit that already had one. Creating
   a `.local` beside an existing `.txt` is the shadowing trap described under the
   arming probe below: the hooks take the first name they find, so the operator's
   real list would go unread while the gate reported itself active on the new,
   nearly-empty file.
2. **Commit the gate files before adding a remote.**
3. **Once a GitHub remote exists**, the operator runs
   `.githooks/overwrite-ci-denylist` themselves to set the `PII_DENYLIST` Actions
   secret. It needs an authenticated `gh` and a typed `Yes`. Pushing only *warns*
   when the local file has drifted from the secret — it never writes it, because
   an Actions secret is write-only and an overwrite destroys a value nobody can
   read back.

## Prove it can fail — this step is not optional

An empty denylist leaves the denylist layers honestly **INACTIVE**, and they say
so. That means every green run before the first *armed* run is no evidence at
all: a gate that has never blocked anything looks identical to a gate with
nothing to find.

So once terms are in, arm it once on purpose:

```
cd /path/to/repo                                   # the probe file must be INSIDE the repo
DL=$([ -f pii-denylist.local ] && echo pii-denylist.local || echo pii-denylist.txt)
echo "throwaway-term" >> "$DL"
echo "throwaway-term" > probe.md && git add probe.md
git commit -m probe        # MUST be blocked
```

Watch it block, then `git rm --cached probe.md && rm probe.md` and remove the
throwaway term from `$DL`.

**Append to the denylist the repo actually uses — that is what `$DL` is for.**
The hooks accept two filenames and take the **first** one they find, checking
`pii-denylist.local` before `pii-denylist.txt`, with no union between them. So on
a repo retrofitted with a `pii-denylist.txt`, writing the probe term to
`pii-denylist.local` *creates* that file and shadows the real one: the probe
passes, having proved only itself, while every real term goes unread. Delete the
throwaway term afterwards and you are left with an empty `.local` that normalizes
to nothing — the gate reports INACTIVE with the operator's list sitting one
filename away. If you did create a `.local` this way, remove the **file**, not
just the line.

**The probe file has to be inside the working tree.** Writing it to `/tmp` and
staging it makes `git add` fail with *"is outside repository"*, so nothing is
staged and the hook has an empty diff to scan — it matches nothing and produces
no block.

What you actually see is a non-zero exit from `git commit`, because with an empty
index git refuses on its own ("nothing added to commit"). That is the trap: the
failed command looks like the gate doing its job, when the gate never ran on
anything. Read the output, not the exit code — a real block says
`pre-commit BLOCKED: a denylisted term is in the staged changes`. Anything else
means the probe never reached the hook, which is a false negative in the one step
that exists to rule false negatives out.

If it did *not* block with the probe staged inside the repo, the gate really is
not installed the way you think — check that `git config core.hooksPath` returns
`.githooks`.

The same applies to CI: the workflow's first *armed* run (secret set, terms
present) is its first real test. Read that run's log rather than inferring from a
green check.

## Retrofitting a repo that already has a remote

Install the gate first, then scan the **full history**, not just the tree — a
tree scan reports clean on a branch where a name was added and later removed,
because the tree genuinely is clean. The shipped workflow's `history` job does
this in CI. The local equivalent greps history against *your denylist*:

```
DL=$([ -f pii-denylist.local ] && echo pii-denylist.local || echo pii-denylist.txt)
git log -p -m --all --text --no-ext-diff --no-textconv --pretty=fuller \
  | grep -a -i -F -w -f <(grep -v -e '^[[:space:]]*$' -e '^[[:space:]]*#' "$DL")
```

Every flag there is load-bearing, and the gate passes each for a reason worth
knowing before you drop one. Each defeats a different way the scan can come back
clean about content it was never shown:

- `--no-ext-diff --no-textconv` stop a repo-local `.gitattributes` diff driver
  from rewriting or blanking content before grep is shown it.
- `--text` covers the neighbouring case: a path marked `-diff` in
  `.gitattributes` makes git emit "Binary files ... differ" instead of the diff,
  and the gate records this as measured — without `--text` the name is simply
  absent from the stream.
- `--pretty=fuller` prints the **Commit** (committer) identity, which the default
  format omits — it shows Author only. A commit whose *committer* identity
  carries the name is invisible without it, and amends and rebases are exactly
  where the two identities diverge.
- `-m` makes `git log -p` emit a diff for merge commits, so a name introduced
  only in a conflict resolution is still scanned.
- `grep -a` forces the stream to be treated as text. Its opposite, `-I`, declares
  the *whole* stream binary at the first NUL byte and abandons it — so a single
  generated blob anywhere in your history would hide a name in every other
  commit.

**Never hand the raw denylist to `grep -f`** — here or anywhere. Every layer of
the gate strips comments and blank lines before scanning, and a hand-run command
that skips that step is not the same scan. The shipped template is *entirely*
comments, eight of them a bare `#`; loaded as a pattern, `#` matches any line
containing one, so this command would drown a real hit in every comment in your
history. The `grep -v` is the normalization, not tidiness.

Reach for gitleaks for the other half — **secrets**, not names. It runs in the
workflow's separate `secrets` job with its own built-in rules and is never handed
the denylist, so it cannot find a personal name and will return clean while one
sits in your history. Two scans, two different questions; neither substitutes for
the other.

Say plainly that a retrofit does not undo an earlier exposure. If a real name is
already in pushed history, the honest options are history rewrite plus a force
push, or accepting the exposure — not a gate that starts from now.

## What the gate is and isn't

Three layers: pre-commit (staged diff), pre-push (every commit being pushed, plus
the ref name, commit message, author identity and tag message — each is a route a
name takes to the remote on its own), and CI (tree + full history + gitleaks).

**Everything fails closed.** An unreadable denylist, a failed `mktemp`, a `grep`
that errored rather than not-matched — each blocks instead of passing. "Could not
check" must never read the same as "checked, clean."

Matching is case-insensitive, fixed-string, and **whole-word everywhere it reads
content** — staged diffs, pushed history, and both CI content scans. No
wildcards, so list diacritic and ASCII spellings as separate terms. A matched
term is never echoed by any layer — not in hook output, not in CI logs.

**One deliberate exception: CI's scan of tracked file *paths* is a substring
match.** A filename concatenates where prose does not — `assets/<name>scan.png`
offers no word boundary — so whole-word matching there would miss exactly the
case that scan exists to catch. The consequence to know before it bites: with the
term `Ana`, a tracked file named `banana.png` fails CI. That job logs counts
only, never the offending path (a path can itself contain the term), so the
failure arrives without a filename. To find it, run the same substring match
locally:

```
DL=$([ -f pii-denylist.local ] && echo pii-denylist.local || echo pii-denylist.txt)
git ls-files \
  | grep -i -F -f <(grep -v -e '^[[:space:]]*$' -e '^[[:space:]]*#' "$DL")
```

Same normalization as the history command above, for an overlapping reason. Two
distinct ways the raw file misfires, both verified on GNU grep 3.11: a **blank**
line becomes an empty pattern that matches every line (this scan, which has no
`-w`, then returns your entire file list), and a **comment** line becomes a
literal pattern — a bare `#` matches anything containing one, which `-w` does not
prevent, since `#` is not a word character. Strip both, always.

The local hooks are armed **per clone** (`core.hooksPath`), so a fresh clone that
skipped that step has no local coverage while still being able to push. That is
exactly what the CI layer is the backstop for — don't treat the hooks alone as
coverage.

## Vasana

A vasana is a pattern that persists across unrelated contexts. If during this
task you notice such a pattern emerging, it may be worth capturing. This skill
works best alongside the `vasana` skill and `vasana` hook from the Vasana System
plugin.
