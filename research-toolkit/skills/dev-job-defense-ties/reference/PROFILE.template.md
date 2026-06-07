# dev-job-defense-ties — profile template (decoupled elements)

> The skill ships with **no profile**. Yours lives OUTSIDE the plugin as small,
> independent elements managed by `scripts/config.py` (the model drives it; you
> never run it). Keep it private — it is never committed here. **Not all fields
> are required.** Decoupling each element into its own file is what makes
> amend-in-place safe: change engagement without touching your red line.

## `profile/threshold` — the red line
`config.py get|put profile/threshold`

Derive it with cui-bono's *Framework Clarification* (weighting · absolute-vs-graduated · which actors count · state-ownership) and stress-test it with **dialectic-spiral**. Fill any subset of the tiers; the screen states which line it applied.

```
hard-stop:        # absolute no — any end-use, including training
  - <buyers / nationalities / end-uses you will not work for>
default-out:      # out, but lower-intensity; note any escalation/caveats
  - <...>
investigate:      # genuine dual-use — never auto-clear; resolve the buyer first
  - <...>
```

## `profile/settings` — engagement & field
`config.py get|put profile/settings`

Edit this element alone to change *how* the skill fires, without touching the threshold.

```
engagement: ask        # ask | always | never
field: dev             # dev (default) | gamedev | …  → selects which domain overlays apply
domain: domain-dev     # default pack; installed overlays live in <config>/domain/
```

## Domain overlays — `domain/<name>`
`config.py get|put domain/<name>`

Extend or narrow what the screen scans for, independent of your politics. The shipped `reference/domain-gamedev.md` is an example overlay — install it with `config.py put domain/gamedev` (from that file) to add game-engine signal. Keep the section headings (`## Lexicon` / `## Added lexicon`, `## Buyer …`, `## End-use ladder`) so the mechanism and the efficiency test can read it.
