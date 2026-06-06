# ex-cog — means of cognition

AI doesn't think *for* you — at its best it thinks *with* you. You hand it a
half-formed question, a messy document, a thing you can't quite see the shape of,
and it hands back something you can work with: turned over, talked back to, built
on. The name for that is *externalized cognition* — thinking taken out of one head
and made into something more than one person can hold. It was never really a solo
act anyway; the lone thinker sealed in one skull was always a fiction. AI just makes
that obvious.

How the capability gets delivered is the open question. The most common way people
reach information is already changing its default — from a list of sources you pick
through to an interface that simply answers, with the searching done out of sight.
That's externalized cognition at scale, but centralized: a few firms own the
machinery and decide what counts as an answer. (Enclosure is the old move — common
land fenced into private property, the public left renting what it once used freely.)
A means of cognition can be held in common or walled off the same way, and it isn't
settled yet which.

This repo doesn't decide that — it's a small thing, and the real work is happening
in more places than this one. What's here is a handful of tools made in that spirit,
free to install and use.

## Install

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

### research-toolkit `3.2.2`

Tools for investigating — verifying claims, tracing power, and stress-testing your
own conclusions before you trust them.

- **Power-mapping & investigation.** `cui-bono` maps who gains and who loses from an
  action, with six domain lenses (weapons, labor, environment, governance, supply
  chains, geopolitics). `deep-investigation-protocol` runs staged source sweeps for
  cases where the marketing and the operational reality diverge.
  `manufactured-consensus-detection` traces whether sources agree independently or
  just echo a single origin; `source-omission-analysis` reads what sources leave out.
- **Stress-testing.** `dialectic-spiral` builds the strongest version of the opposite
  of your conclusion and tests it against the evidence (at least four rounds).
  `text-deconstruction` close-reads a text to find where it undermines itself on its
  own terms. `frame-rotation` re-expresses a problem through other languages'
  grammars to break English-default framing. `iterative-verification` keeps looping
  until evidence thresholds actually pass — not when you feel finished.
- **Source acquisition.** `youtube-research` and `substack-research` pull practitioner
  knowledge and independent journalism (Substack via a browser scraper that needs a
  one-time login); `video-transcript-extraction` gets transcripts from captions or
  local Whisper.
- **Live data (two MCP servers).** `financial-mcp` returns stock prices, fundamentals,
  history, and technical indicators (RSI, MACD, Bollinger) from Yahoo Finance.
  `transparency-mcp` pulls US Congress bills, members, and votes (GovTrack), World
  Bank indicators, and nonprofit 990 filings (ProPublica). Free public sources, no
  API keys. `macro-monitor` is a checklist over that data for watching macro-stress
  signals.

### vasana-system `2.5.2`

Notice when the same behavioral pattern turns up in places that have nothing to do
with each other, write it down, and test whether it actually holds.

- **The working loop.** `vasana` flags a candidate pattern mid-work; `record-pattern`
  captures it with structure; `find-similar` checks whether it recurs elsewhere or was
  a one-off; `test-pattern` checks whether a recorded pattern fires and changes
  anything; `pattern-library` browses the collection. Other skills (`break-pattern`,
  `check-assumptions`) apply the same noticing to your own work as you go.
- **Two MCP servers — and an honest account of them.** `relational-memory` is a
  cross-session memory store that works: it saves facts, task state, and core
  principles to local disk in layered storage, recalls them by search, and
  auto-summarizes old entries as they pile up. `edge-graph` records relations as
  weighted edges that get heavier each time you traverse them, so what recurs becomes
  visible. Both can surface relation-types or verbs that repeat three or more times.
  What they do *not* yet do is the larger thing they're designed toward — interpreting
  those recurrences into higher-order patterns, or consolidating vocabulary as it
  emerges. That part is still a sketch; today they are a memory system that works well
  in practice, not the pattern-discovery engine the design imagines. Storage is local
  disk only — memories don't survive ephemeral cloud sessions.

### makers-toolkit `0.8.1`

Discipline for building things with AI — methodology, not machinery. Nothing to
configure; the skills just hold a standard.

- `system-pilot` — a six-step build discipline: define what "done" means, separate
  spec from orchestration from tools, verify integrations early, think schema-first,
  and run repair loops that only write down *verified* lessons. Each rule carries the
  failure mode it prevents.
- `intrinsic-prompt-design` — how to write prompts that survive edge cases: give the
  model the reason behind each rule, not just the rule.
- `skill-activation-testing` — a two-tier way to find out whether a skill's
  description actually makes it fire: a quick blind-router proxy, and a live
  firing-counter hook (which ships and works) for the real test.

### security-toolkit `0.2.2`

Guardrails that run as hooks — automatic, not advice you have to remember.

- **Flags likely prompt-injection** in any tool output, MCP results included — tiered
  (a loud warning for blatant patterns, a silent log for weaker ones) with a path
  allowlist. It detects and records; it doesn't block.
- **Blocks dangerous git operations** before they run: push to `main`/`master`, force
  push, `reset --hard`, `--no-verify`, `branch -D`, `clean -fd`, `rm -rf`, and PR
  self-merges.
- **Blocks Desktop Commander's** process-spawning and config-setting tools, which
  sidestep Claude Code's own permission boundaries.

## Architecture

Each plugin is self-contained — its own `plugin.json`, skills, agents, hooks, and
optional MCP servers. Plugins reference each other by name, not by path.

## License

MIT
