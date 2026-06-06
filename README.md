# ex-cog — means of cognition

AI doesn't think *for* you — it thinks *with* you: it takes thought out of one
head and turns it into something you can see, question, and build on. The name for
that is *externalized cognition*, and it retires an old assumption — that thinking
happens alone, inside one skull. It never did; AI just makes it visible.

The most common way people reach information is already shifting its default: from
a list of sources you navigate to an interface that answers for you, with agents
searching in the background. That's externalized cognition arriving at scale, but
centralized — a few firms decide what counts as an answer and hand you the result.
(Enclosure is the old move: common land fenced into private property, the public
left renting what it used freely.) A means of cognition can be held in common or
walled off the same way, and which way it goes isn't settled yet.

These plugins don't settle it. What's here is a handful of tools made in that
spirit, for anyone to use.

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

Trace who benefits, verify claims, stress-test conclusions, spot manufactured
consensus. The investigation protocols (deep-investigation-protocol, cui-bono) map
power structures and funding flows. Dialectic-spiral and frame-rotation stress-test
your findings from angles you weren't using. Source-omission analysis catches what's
*missing* from the conversation rather than what's in it.

Includes video and Substack research, macro/financial monitoring, and two MCP
servers (`financial-mcp`, `transparency-mcp`) for structured access to market data
and public-interest records.

### vasana-system `2.5.2`

Notice when a behavioral pattern shows up across contexts that have nothing in
common, record it, test whether it holds, and browse what you've found. A vasana is
not a personal habit — it's a pattern that persists across domains, scales, and
(potentially) people. The system doesn't judge patterns as good or bad;
groove-deepening is also mastery. Ships `relational-memory` and `edge-graph` MCPs
for cross-session pattern persistence.

### makers-toolkit `0.8.1`

Engineering discipline for deterministic systems (system-pilot), the prompt-design
methodology that sustains it (intrinsic-prompt-design), and a test method for
whether a skill actually fires when it should and stays quiet when it shouldn't
(skill-activation-testing).

### security-toolkit `0.2.2`

Guardrails as hooks, not advice: tiered prompt-injection detection covering MCP
output, and blocks on dangerous git and Desktop Commander actions. Runs
automatically — you don't invoke it, it watches.

## Architecture

Each plugin is self-contained — its own `plugin.json`, skills, agents, hooks, and
optional MCP servers. Plugins reference each other by name, not by path.

## License

MIT
