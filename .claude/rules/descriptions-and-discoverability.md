---
paths:
  - "**/.claude-plugin/plugin.json"
  - "**/.claude-plugin/marketplace.json"
  - "**/skills/**/SKILL.md"
  - "**/README.md"
---

# Descriptions & discoverability — writing text meant to be found

Guidance for any text whose job includes being *discovered*: plugin and
marketplace `description`s, a `SKILL.md` `description`, a README or repo "About"
line. A heuristic with trade-offs, not a mandate — when a case argues otherwise,
say why. Composes with `skill-design.md` (a skill's scope/triggering) and
`skill-verification.md` (testing that a description change actually fires).

## Two layers: a findable surface over the deeper text

Lead with a plain, keyword-first surface a searcher (or an indexer) matches on;
keep the manifesto / philosophy / motto as the *deeper* layer beneath it. Never
lead with the manifesto or with jargon — discoverability is a findable surface
*over* the depth, not a dumbing-down of it.

## Say what's distinctive, in recognized terms

- **Name the value, not the commodity mechanism.** A *commodity* mechanism is one
  so common it distinguishes nothing — "pattern recognition," "memory," "AI."
  Naming it sells nothing (everyone has it). Name what's distinctive instead:
  "memory for *forms, not facts*," not "a memory MCP."
- **Use the real, recognized term** for what a thing is — accurate, searchable,
  *and* credible to those who know it ("usage-weighted knowledge graph," not a
  coined label; name a concept's lineage where one exists, e.g. POSIWID / Beer).

## Findable *and* fires: synonyms, idioms, related phrases

Carry the synonyms, idioms, and related phrases a person would actually type — not
just the canonical term. "cui bono" should also surface (and, for a skill, *fire*)
on "follow the money" / "who profits." For skills these double as oblique-positive
trigger phrases (no lexical match on the skill name).

## Write to the discerning reader: rigor, then honesty

The highest-value audience already wants this and has the lowest tolerance for
inflation. Win them; the rest self-sorts.

- **Signal the rigor that inoculates against your genre's failure mode.** Keep the
  *rigor* edge, drop the *stance/woo* edge: a critical-analysis tool says
  "symmetric, assumes no villain" (not coded-contrarian); a pattern tool says
  "tests for real shared mechanism, not surface resemblance" (not apophenia/woo).
- **Claim the practice, not the credential.** "field-built for *personal*
  investigative work," not "professional." Right-size verbs — real researchers
  clock inflated "research" instantly; prefer precise ones (investigation,
  verification, source-checking) in the value pitch.
- **Be honest about state.** Flag experimental / WIP parts. Discoverability is not
  overclaiming — an honest "WIP" keeps the discerning reader's trust; overselling
  loses it.
- **Let resonance stay latent.** A pun (ex-cog / excogitate), an academic lineage
  (externalized → *extended cognition*, Clark & Chalmers), an etymology — reward
  whoever catches it; never explain it or cite it as borrowed authority.
- **Explain the concept, not the etymology.** Define a term *through its value*
  (what a vasana is *good for*), not its origin.

## Names: make the register offset the name's first impression

- An **opaque** name needs a meaning glued on (ex-cog → "externalized cognition").
- A name with **baggage** needs prose that counteracts it: a mystical-sounding name
  (Sanskrit "vasana") needs *over-grounding* — concrete words, an everyday example,
  the rigor signal — not abstraction that compounds the vibe.
- The name is a **recall / brand** lever (matters *post*-traction, word-of-mouth);
  the **description** is the *discovery* lever (matters *pre*-traction, where people
  search what it *does*, not a name they've never heard). Cold-start visibility is
  solo promo, not the name.

## Mechanics

- **Length by artifact.** A `SKILL.md` `description` is hard-capped (≤ 1024 chars)
  **and loads into context every session** — brevity there is firing-critical.
  Plugin / marketplace blurbs are *uncapped and not context-loaded* → optimize for
  scannability + keyword signal-to-noise (~2–3 sentences), not a limit.
- **Delimiters for plain-text surfaces.** The GitHub "About" field renders no
  markdown — delimit with name-first + periods, not bold (which vanishes there).
- **Match register to surface / audience tier.** Keep the connoisseur register on
  discovery surfaces (aggregators, repo) where the narrow true audience self-selects.
  A larger *latent* audience (already uses Claude, can't find/install plugins) needs
  a *separate*, plain-language onramp — a different artifact, not the same blurb
  diluted. (The lower-barrier path to them is a standalone skill, not "a
  marketplace.")

## When it's working

A searcher's words match the surface; a skeptic reads rigor, not posturing; an
unfamiliar name carries a meaning; nothing is overclaimed; the deep text is still
there underneath for whoever digs. When it's **not**: the blurb leads with the
manifesto; "research" / "memory" do the talking; a pun or pedigree gets explained;
or one description tries to serve both the connoisseur and the newcomer and serves
neither.
