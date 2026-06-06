# ex-cog — means of cognition

AI doesn't make people obsolete. It makes obsolete the idea that thinking happens
alone, inside one skull — the Cartesian fiction. Cognition was always relational;
AI just makes that legible, by *externalizing* it: taking thought out of one head
and turning it into something visible, inspectable, that others can build on.

That — externalized cognition — is the real capability, and most of the industry
points it at small, disposable tasks. Used differently, it's the difference between
*consuming* whatever you're handed and *producing* your own alternatives.

The stakes aren't hypothetical. The most common way people reach information is
already shifting its default — from a list of sources you navigate to an interface
that answers for you, with agents doing the searching in the background. That's
externalized cognition too, arriving at scale — but enclosed: you get the output,
someone else keeps the means. The means of cognition can be held in common or fenced
off. These plugins are built for the first, and the window to build that way is open
now, not later.

A marketplace of plugins for Claude Code: investigation, verification, pattern
recognition, build discipline, and guardrails.

> The public marketplace `bogheorghiu/ex-cog` is private for now. `ex-cog-dev` is
> where development happens and, for the moment, the place to install from — the
> `-dev` stays in the name so anyone who already added the marketplace keeps working.

## Install

```
/plugin marketplace add bogheorghiu/ex-cog-dev
/plugin install research-toolkit@ex-cog-dev
/plugin install vasana-system@ex-cog-dev
/plugin install makers-toolkit@ex-cog-dev
/plugin install security-toolkit@ex-cog-dev
```

## Plugins

| Plugin | Version | What it does |
|---|---|---|
| **research-toolkit** | 3.2.2 | Verify claims, stress-test conclusions, spot manufactured consensus, trace who benefits. Investigation protocols (deep-investigation-protocol, cui-bono), dialectic spiral, frame rotation, source-omission analysis, macro/financial monitoring, video & substack research. Ships `financial-mcp` + `transparency-mcp`. |
| **vasana-system** | 2.5.2 | Notice when a behavioral pattern recurs across unrelated domains, record it, test whether it holds, and browse what you've found. Ships `relational-memory` + `edge-graph` MCPs for pattern persistence. |
| **makers-toolkit** | 0.8.1 | Engineering discipline for deterministic systems (system-pilot), the prompt-design methodology that sustains it (intrinsic-prompt-design), and a test method for whether a skill actually fires (skill-activation-testing). |
| **security-toolkit** | 0.2.2 | Guardrails as hooks, not advice: tiered prompt-injection detection (covering MCP output) and blocks on dangerous git / Desktop Commander actions. |

## Architecture

Each plugin is self-contained — its own `plugin.json`, skills, agents, hooks, and
optional MCP servers. Plugins reference each other by name, not by path.

## License

MIT
