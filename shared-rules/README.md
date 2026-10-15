# shared-rules

Loads one shared set of Claude rules into sessions that don't have them installed
locally, such as cloud sessions and fresh containers.

The rules, and how to install them on each surface (local machines, cloud, desktop
app), live in their source repo: <https://github.com/bogheorghiu/claude-rules>. This
plugin covers cloud sessions; `hooks/load-rules.sh` is its SessionStart hook.

```
/plugin marketplace add bogheorghiu/ex-cog-dev
/plugin install shared-rules@ex-cog-dev
```

## Settings

Claude Code asks for these when you enable the plugin:

- **Rules repository**: the git URL whose `rules/` folder is loaded. Point it at your
  own repo to use your own rules.
- **Rule updates**: `ask` (default) or `auto`. With `ask`, rules added or changed in
  the repo after you installed wait until you approve them: Claude tells you what
  changed at the start of a session and applies the update only if you say yes. With
  `auto`, they load as soon as they're published.

One limit: `ask` remembers your approvals in the plugin's data folder. A container
that starts empty every time, such as a fresh cloud session, has no record of past
approvals, so each such session loads whatever the repo holds at that moment.

## What it runs and fetches

At each session start the hook runs `git` to clone the rules repository you configured
(or update its saved copy) into the plugin's data folder, then prints the rule files
into the session's context. It sends nothing anywhere else and runs nothing from the
fetched repository: the rule files are read as text, never executed. The approve
command it offers runs `git reset` in that same saved copy, and only when you approve.
