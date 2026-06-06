# ex-cog — means of cognition

AI doesn't make people obsolete. At its best it doesn't think *for* you — it thinks
*with* you: it takes thought out of one head and turns it into something you can see,
question, and build on. The name for that is *externalized cognition*, and it quietly
retires an old assumption — that thinking happens alone, inside one skull, the
Cartesian fiction. It never did; cognition was always relational. AI just makes it
legible.

That — externalized cognition — is the real capability, and most of the industry
points it at small, disposable tasks. Used differently, it's the difference between
*consuming* whatever you're handed and *producing* the alternatives — which, like
cognition itself, was never solo work. On its own, lone effort stays a hobby; at this
scale, what carries weight is people building in common, in the open.

The stakes aren't hypothetical. The most common way people reach information is
already shifting its default — from a list of sources you navigate to an interface
that answers for you, with agents doing the searching in the background. That's
externalized cognition too, arriving at scale — but centralized, and from there
enclosed: a few firms own the means and pass you the output. (Enclosure is the old
move — common land fenced into private property, the public left renting what it once
used freely.) A means of cognition can be held in common, or walled off the same
way — and which way it goes isn't settled yet.

These plugins don't build that — it's a far bigger job, and the serious parts are
underway elsewhere. What's here is smaller and more ordinary: a handful of tools made
in that spirit — for normal users as much as power users, on cloud models or local
ones where local is good enough. Useful on their own, and modest about what they are.

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
