# shared-rules

Loads one shared set of Claude rules into sessions that have no `~/.claude/rules/` of
their own, such as cloud sessions and fresh containers.

The rules, and the install steps for every surface (local machines, cloud, desktop
app), live in their source repo: <https://github.com/bogheorghiu/claude-rules>. This
plugin is the cloud half of that delivery. Its SessionStart hook
(`hooks/load-rules.sh`) fetches the repo and prints the rules into context.

Point it at a different rules repo by setting `SHARED_RULES_REPO`.

```
/plugin marketplace add bogheorghiu/ex-cog-dev
/plugin install shared-rules@ex-cog-dev
```
