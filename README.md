# ex-cog — means of cognition

AI doesn't think *for* you. At its best, it thinks *with* you. You hand it a
half-formed question, a mess of a document, a thing you can't quite see the shape
of — and it hands back something you can work with. That's *externalized cognition*:
thinking pulled out of one head and made into something more than one head can hold.
It was never really a solo act anyway. The lone mind sealed in its own skull was
always a fiction; AI just makes that plain.

But the same capability can be handed to you or taken from you. Watch where search is
going: from a list of sources you pick through to a single answer, generated out of
sight, that you're meant to trust. That's externalized cognition at scale — and
enclosed. A few firms own the machinery and decide which answer you see. (Enclosure
is an old move: fence the commons, then rent people back what they used to use for
free.) Cognition can be held in common or walled off the same way, and that fight
isn't settled.

This repo doesn't settle it. It's small, and the real work is happening in more
places than this one. But here's a handful of tools built the other way: they hand
you the means, not the answer — something to drive, not an oracle to trust — and
some turn on the machinery itself, asking who owns it, who benefits, and what's being
left unsaid. Free to install, local, yours to change.

[Install](#install) · [research-toolkit](#research-toolkit) · [vasana-system](#vasana-system) · [makers-toolkit](#makers-toolkit) · [security-toolkit](#security-toolkit)

## Install

**Claude Cowork** — add the marketplace `bogheorghiu/ex-cog-dev` via Customize →
Browse plugins, then install the plugins you want.

**Claude Code**

```
/plugin marketplace add bogheorghiu/ex-cog-dev
/plugin install research-toolkit@ex-cog-dev
/plugin install vasana-system@ex-cog-dev
/plugin install makers-toolkit@ex-cog-dev
/plugin install security-toolkit@ex-cog-dev
```

> `bogheorghiu/ex-cog` is private for now, so `ex-cog-dev` is where development
> happens and, for the moment, the place to install from. The `-dev` stays in the
> name so anyone who already added the marketplace keeps working.

## Plugins

### research-toolkit

`v3.2.2` · Verify a claim. Trace who benefits. Turn your own conclusion inside out
before you trust it.

- **Map power.** `cui-bono` asks who gains and who loses, through six lenses —
  weapons, labor, environment, governance, supply chains, geopolitics.
  `deep-investigation-protocol` runs staged source sweeps for when the marketing and
  the reality diverge. `manufactured-consensus-detection` asks whether your sources
  agree on their own or just echo one origin. `source-omission-analysis` reads the
  silences — what no one is saying.
- **Break your own case.** `dialectic-spiral` builds the strongest opposite of your
  conclusion and runs it at the evidence, four rounds minimum. `text-deconstruction`
  finds where a text contradicts itself on its own terms. `frame-rotation` rephrases
  the problem through another language's grammar to knock you out of English
  defaults. `iterative-verification` stops when the evidence clears the bar, not when
  you're tired.
- **Pull the sources.** `youtube-research` and `substack-research` mine practitioner
  know-how and independent reporting (Substack through a browser scraper, one-time
  login). `video-transcript-extraction` grabs transcripts from captions or local
  Whisper.
- **Live data, no keys.** `financial-mcp` returns prices, fundamentals, history, and
  indicators — RSI, MACD, Bollinger — from Yahoo Finance. `macro-monitor` watches that
  data for macro-stress signals. `transparency-mcp` puts public power on the record:
  Congress bills, members, and votes (GovTrack), World Bank indicators, and nonprofit
  990s (ProPublica).

### vasana-system

`v2.5.2` · Catch the same behavior surfacing in places that have nothing to do with
each other. Write it down. Test whether it's real.

- **The loop.** `vasana` flags a candidate mid-work. `record-pattern` captures it with
  structure. `find-similar` checks whether it recurs or was a fluke. `test-pattern`
  checks whether a saved pattern actually fires and changes anything. `pattern-library`
  browses the collection. `break-pattern` and `check-assumptions` turn the same
  scrutiny back on your own work.
- **Two MCP servers, told straight.** `relational-memory` works: it saves facts, task
  state, and core principles to disk in layered storage, recalls them by search, and
  summarizes old entries as they pile up. `edge-graph` records relations as weighted
  edges that grow heavier each time you cross them, so what recurs rises to the top.
  Both can flag a relation-type or verb that repeats three times or more. What neither
  does *yet* is the bigger ambition — reading those recurrences into higher-order
  patterns, or letting shared vocabulary consolidate on its own. That part is still a
  sketch. Today they're a memory system that works in practice, not the pattern engine
  the design imagines. Storage is local disk; nothing survives an ephemeral cloud
  session.

### makers-toolkit

`v0.8.1` · Discipline for building with AI. Methodology, not machinery — nothing to
configure, just skills that hold a line.

- `system-pilot` — six steps: define what "done" means, split spec from orchestration
  from tools, test the seams early, design the schema first, and run repair loops that
  record only *verified* lessons. Every rule carries the failure it prevents. Adapted
  from the *Universal CLAUDE.md Protocol*.
- `intrinsic-prompt-design` — write prompts that survive edge cases by giving the
  model the reason behind a rule, not just the rule.
- `skill-activation-testing` — find out whether a skill's description actually makes it
  fire: a fast blind-router proxy, plus a live firing-counter hook (it ships and
  works) for the real measurement.

### security-toolkit

`v0.2.2` · Guardrails that run as hooks. Automatic, not advice you have to remember.

- **Catches prompt-injection** in any tool output, MCP results included — loud warning
  for the blatant stuff, quiet log for the rest, with a path allowlist. It flags and
  records; it doesn't block.
- **Blocks dangerous git** before it runs: push to `main`/`master`, force push,
  `reset --hard`, `--no-verify`, `branch -D`, `clean -fd`, `rm -rf`, PR self-merges.
- **Blocks Desktop Commander's** process-spawning and config-setting tools, the ones
  that slip past Claude Code's permission boundaries.

## Architecture

Each plugin is self-contained — its own `plugin.json`, skills, agents, hooks, and
optional MCP servers. Plugins reference each other by name, not by path.

## License

MIT
