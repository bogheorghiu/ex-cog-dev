# No sensitive data in the repo — any branch, any history

`ex-cog-dev` is public. Treat **every branch and the full git history as public.**
Never commit personal or otherwise sensitive data — not to `main`, not to a feature
branch, not "just temporarily." Once it's in history it's effectively published, and
it survives a later delete.

(No `paths:` frontmatter on purpose — this is an always-relevant security convention,
so it loads every session, like `github-references.md`.)

## What counts as sensitive
- Personal data / PII; private profiles, preferences, political or values choices.
- Secrets: API keys, tokens, passwords, session cookies / auth state.
- Anything you wouldn't want a stranger reading — even mid-development.

## Where operator config goes instead: stay local
Operator-specific config is **model-generated → downloaded → kept local → never
committed.** Worked example: `dev-job-defense-ties` ships **profile-less** — the
operator's threshold and political filter choices live only on the local machine,
not in the repo, the reports, or the history. This **extends `shipped-skill-config.md`**
(config stays outside the *plugin*) to the stronger line: config stays outside the
*repo* entirely.

## Why this is load-bearing
It's the precondition that lets everything live in one public repo with no private
"insulation" mirror (#38): if nothing sensitive is ever committed, there's no
confidentiality reason to keep a stable copy private.

## When in doubt
Don't commit it. Put it in a gitignored local path and reference it *by location* —
the way the config-store pattern does. A leak you prevented costs nothing; one in
history is permanent.
