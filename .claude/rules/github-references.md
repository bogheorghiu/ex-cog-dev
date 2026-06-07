# Referring to issues and PRs

When you mention an issue or a pull request **in prose** — a chat reply, a
comment body sentence, a doc — write `issue #N` or `PR #N`, never a bare `#N`.

Issues and PRs share one number space on GitHub, so `#44` alone is ambiguous:
the reader can't tell which kind it is without clicking. In rendered GitHub
surfaces a bare `#44` at least gets an icon and hover preview that disambiguates
it; in a chat transcript there's no icon, so the bare number is just a number.
Naming the kind costs three characters and removes the guess.

This is a prose convention, not a syntax rule:

- **Chat / prose / docs:** `issue #N`, `PR #N`. Always name the kind.
- **Commit messages and issue/PR bodies:** the bare `#N` is fine — GitHub
  auto-links it there, and `Fixes #N` / `Closes #N` keywords require the bare
  form to work. Don't break those.
