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
