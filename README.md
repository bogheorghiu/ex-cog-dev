# ex-cog — externalized cognition

Mostly skills — with a few MCP servers and hooks — for Claude Cowork and Claude
Code: investigation and verification for genuine zero-trust inquiry; discipline
for prompting and co-authoring with AI, built on reasons, not bare orders; a
proof-of-concept system for noticing patterns that recur, across unrelated topics
and in your own work with the AI; and guardrails that block dangerous commands.
Built for knowledge work — most of it needs no code at all — and honest about
what each tool does and doesn't do.

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

## At a glance

- **[research-toolkit](#research-toolkit)** — *Loaded topics. No thumb on the
  scale — especially yours.* Verify a claim, trace who benefits, and turn your
  own conclusion inside out before you trust it.
- **[makers-toolkit](#makers-toolkit)** — Discipline for prompting and
  co-authoring with AI — built on reasons, not bare orders. Nothing to
  configure — just skills you invoke.
- **[vasana-system](#vasana-system)** — *Proof of concept.* Notice the same
  regularity in unrelated topics — and, more usefully, in how you and the AI
  actually work together. Real, modest benefits today; not yet the
  self-organizing learner it's built toward.
- **[security-toolkit](#security-toolkit)** — Useful friction against obvious
  mistakes: hooks that block dangerous commands and flag prompt-injection. A
  basic draft, not a security product.

[Install ↓](#install)

## Install

**Claude Cowork** — no terminal needed: add the marketplace `bogheorghiu/ex-cog-dev`
via Customize → Browse plugins, then install the plugins you want.

**Claude Code**

```
/plugin marketplace add bogheorghiu/ex-cog-dev
/plugin install research-toolkit@ex-cog-dev
/plugin install makers-toolkit@ex-cog-dev
/plugin install vasana-system@ex-cog-dev
/plugin install security-toolkit@ex-cog-dev
```

> `bogheorghiu/ex-cog` is private for now, so `ex-cog-dev` is where development
> happens and, for the moment, the place to install from. The `-dev` stays in the
> name so anyone who already added the marketplace keeps working.

## Plugins

### research-toolkit

*Loaded topics. No thumb on the scale — especially yours.*

Interrogate what you're sold, and what you'd rather believe: verify a claim,
trace who benefits, and turn your own conclusion inside out before you trust it.

- **Not sure where to begin?** `research` routes the question for you — by domain,
  by how deep you need to go, by what sources exist — so you don't have to know
  the method names to use the methods.
- **Map power.** `cui-bono` asks who gains and who loses, through six lenses —
  weapons, labor, environment, governance, supply chains, geopolitics.
  `deep-investigation-protocol` runs staged source sweeps for when the marketing and
  the reality diverge. `manufactured-consensus-detection` asks whether your sources
  agree on their own or just echo one origin. `source-omission-analysis` reads the
  silences — what no one is saying. `dev-job-defense-ties` runs that same
  buyer-chain logic on a job offer — screen a studio or employer for hidden
  military or defense ties against a red line you set (kept on your machine,
  never committed).
- **Break your own case.** `dialectic-spiral` builds the strongest opposite of your
  conclusion and runs it at the evidence, four rounds minimum — with a bench of
  adversarial agents (a falsifier, a critic, a spiral that holds contradictions
  open instead of resolving them) to do the arguing. `text-deconstruction`
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

### makers-toolkit

Discipline for prompting and co-authoring with AI — built on reasons, not bare
orders. Nothing to configure, just skills that hold a line.

- `intrinsic-prompt-design` — give the model the *reason* behind a rule, not just
  the rule. In practice the reasons part clearly helps, even paired with plain
  imperatives — anecdotally so far; rigorous testing would be worth doing. Its bolder idea — deliberately leaving space for the model's own
  agency to fill — is the core experimental proposition.
- `system-pilot` — engineering discipline for deterministic systems: define what
  "done" means, split spec from orchestration from tools, test the seams early,
  schema first, repair loops that record only *verified* lessons. Adapted from the
  *Universal CLAUDE.md Protocol*.
- `skill-activation-testing` — find out whether a skill's description actually makes
  it fire: a fast blind-router proxy, plus a live firing-counter hook (it ships and
  works) for the real measurement.

### vasana-system

**A proof of concept — an early step toward a real ambition.** The idea: the
same regularity can turn up in places that have nothing to do with each other; an
AI not boxed into one field's categories can notice it, and check whether it's a
real shared mechanism or just a surface rhyme. Today that's a growing, hand-kept
list of specific observations — and they do resurface when the same shape shows
up again, which is genuinely useful: catching recurrences across unrelated
topics, and (often the bigger win) in the work itself, where you and the AI keep
making the same moves or settling into a groove. Each one also accumulates a
count of the times it has recurred, and that weight *seems* to matter in
practice — an impression, not yet a measured result. Where it's headed — a system
that recognizes and learns these patterns more on its own — is the genuine
intention, not a misreading of the name; that fuller version just isn't built
yet. Some skills are rougher than others and the bundled agent may be more than
it needs — but as an honest first step that already helps, it earns its place.

- **The loop.** `vasana` flags a candidate mid-work. `record-pattern` captures it with
  structure. `find-similar` checks whether it recurs or was a fluke. `test-pattern`
  checks whether a saved pattern actually fires and changes anything. `pattern-library`
  browses the collection. `break-pattern` and `check-assumptions` turn the same
  scrutiny back on your own work.
- **Beyond the loop.** `iterative-loop-engine` asks "am I *actually* done, or did I
  just stop?" and keeps work cycling until the completion criteria — not fatigue —
  say done. `self-improving-investigation` runs research through blind worker agents
  and dialectic synthesis when the risk of confirming your own bias is high.
  `inquiry-to-system` notices when a casual question is building toward something
  larger and turns the conversation into structured output. `temporal-shaping` designs
  the time-shape of a process — phases, pacing, why something feels off.
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

### security-toolkit

A basic draft, not a security product — plain bash hooks that pattern-match
on commands and tool output, plus one guided-verification skill. No external tools, no
sandbox; anything that doesn't match a pattern sails through. Useful friction against
obvious mistakes, not something to rely on for real security.

- **Catches prompt-injection** in any tool output, MCP results included — loud warning
  for the blatant stuff, quiet log for the rest, with a path allowlist. It flags and
  records; it doesn't block.
- **Blocks dangerous git** before it runs: push to `main`/`master`, force push,
  `reset --hard`, `--no-verify`, `branch -D`, `clean -fd`, `rm -rf`. Blocking
  `gh pr merge` is **off by default** (merge already passes through branch
  protection); turn it on interactively with the `/pr-merge-guard` command — which
  takes effect immediately — or declaratively with `EXCOG_BLOCK_PR_MERGE=1`. The
  `pr-merge-guard` skill explains it and flips it when you ask ("stop auto-merging,"
  "lock down main").
- **Blocks Desktop Commander's** process-spawning and config-setting tools, the ones
  that slip past Claude Code's permission boundaries.
- **Answers "am I compromised?"** after a supply-chain scare — a poisoned npm or PyPI
  package, a trojaned extension — with a guided check of a Windows + WSL2 machine
  (`windows-wsl-security-verification`): known-bad package versions, persistence,
  planted SSH keys, shell-rc injection, the Windows AV pass. It verifies, it doesn't
  harden — and a clean result raises confidence, never proves you're clean.

## Architecture

Each plugin is self-contained — its own `plugin.json`, skills, agents, hooks, and
optional MCP servers. Plugins reference each other by name, not by path.

## Credits

The ideas and direction are [Bogdan Gheorghiu](https://github.com/bogheorghiu)'s;
the words are mostly Claude's (Anthropic). A person choosing what's worth saying and
an AI finding the words for it is the externalized cognition this repo is about — so
we'd rather sign it than pretend otherwise.

## License

MIT
