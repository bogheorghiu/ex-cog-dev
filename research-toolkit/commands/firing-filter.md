---
description: "Control the deterministic firing layer: status | on | off (per session)"
argument-hint: "[status|on|off]"
---

Run the firing-filter control CLI and relay its output verbatim:

```
python3 "${CLAUDE_PLUGIN_ROOT}/hooks/firing-filter/firing_filter.py" cmd ${1:-status} ${CLAUDE_SESSION_ID:-manual}
```

Then, depending on the action:

- **status** — after relaying the output, add one sentence saying what the
  filter is (deterministic, zero model calls: words arm, situations inject
  one guidance each, blocks happen only on claim-vs-record facts, once per
  unit) and where its README lives
  (`hooks/firing-filter/README.md` in this plugin).
- **off** — relay the CLI's warning faithfully: disabling removes the
  toolkit's only layer that fires without anyone noticing anything (every
  recorded failure was caught by a human, none by self-review); the filter
  will NOT re-arm itself this session; `on` re-arms it.
- **on** — confirm ARMED and note it stays armed for the session.

If the session id is not available in `${CLAUDE_SESSION_ID}`, pass `manual` —
the state file is per-session, and `manual` scopes the command to hand-run
use without touching live session state.
