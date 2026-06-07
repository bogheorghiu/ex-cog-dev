---
paths:
  - "**/skills/**"
  - "**/.claude-plugin/plugin.json"
---

# Shipped-skill config — keep operator values out of the plugin

Guidance for a skill that needs **per-user configuration** — a threshold, a
preference, a secret, anything one operator sets that another wouldn't. A
heuristic with trade-offs, not a mandate: when a case argues against it, say why.

These plugins ship publicly via the `ex-cog-dev` marketplace, and every `uvx`
cold-start wipes the plugin cache. So config that lives *inside* the plugin is
both a privacy leak (you published the user's setup) and ephemeral (it's gone
next cold-start). The split below is what keeps a skill a reusable instrument
instead of one operator's setup hard-coded into a public artifact.

## Ship the mechanism profile-less; store values outside the plugin

The skill body and its reference packs ship; the operator's values do **not**.
Persist them outside the plugin, in the user's own config directory, written at
runtime — never as a committed file under the plugin dir.

- **Failure it prevents:** a committed example profile becomes the de-facto
  default everyone inherits — and anything personal in it ships to strangers. A
  skill that applies *no* values until the user supplies them can't leak them.
- Ship *shape* (a template, a default pack), not *content* (this user's red line).

## Reach the config dir through a self-locating, path-safe script — the model drives it

"Where does this land, OS-correctly, surviving a cache wipe, never in `/tmp` or
the plugin cache?" is a **determinism** question — the thing the model does
unreliably turn to turn. Put exactly that in a small script (locate + element IO
+ path-safety) and leave everything about *content* — the questions, the prose,
the interpretation — to the model. This is system-pilot's tool/conductor split
applied to config.

- **Failure it prevents:** the model hand-rolls a path, picks `/tmp` or the uvx
  cache, and the config silently evaporates — or a malformed name escapes the
  config dir. The script refuses temp/cache and validates every element ref, so
  the model never has to get it right.
- **The user never edits plugin files.** Configuration is conversational: the
  model runs the script; the user just talks. If a human has to open the plugin
  directory to set the skill up, the split has failed.

## Make the tool self-describing; don't hard-code its usage in prose

The script emits its own interface (a `describe` command); the SKILL.md
references *that* rather than spelling out commands that drift out of sync the
next time the script changes.

- **Failure it prevents:** the prose still says `profile.py save` long after the
  script learned `put profile/threshold`, and nothing tests the gap. A
  self-describing tool is exercised by the harness that runs it; a hard-coded
  usage string in prose is not.

## Worked example

`research-toolkit/skills/dev-job-defense-ties` ships profile-less: `config.py`
(self-describing, path-safe, OS-agnostic) stores decoupled `profile/*` and
`domain/*` elements in the user's own config dir, and `ARCHITECTURE.md` records
why. The skill applies no threshold until the operator sets one — verified live
(the install fires the skill, which onboards; it never reads a shipped profile,
because there isn't one).
