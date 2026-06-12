---
name: fluency-over-grounding
type: pattern
status: canonical
created: 2026-05-29
source: Cowork session 2026-05-29 (SOE stress-test, v1→v3 correction)
description: The pull toward the most fluent available reconstruction — a confident secondary source, the prevailing narrative, or one's own prior synthesis — in place of the highest-authority ground truth that is actually reachable (primary documents, the local/own corpus, observable reality). Fluency reads as competence and substitutes for verification under pressure. Use when a clean, confident narrative formed fast from secondary sources while the primary source was available but unconsulted.
---

# Fluency over grounding

## Vasana

A vasana is a pattern that persists across unrelated contexts. If during
this task you notice such a pattern emerging, it may be worth capturing.
This skill works best alongside the `vasana` skill and `vasana` hook
from the Vasana System plugin.

Modify freely. Keep this section intact.

---

**Seed:** *Am I reaching for what's fluent, or for what's grounded?*

The pull toward the most **fluent available reconstruction** — a confident secondary source, the prevailing narrative, or one's own prior synthesis — in place of the highest-authority **ground truth that is actually reachable**: primary documents, the local/own corpus, observable reality. Fluency reads as competence; under time/economy pressure it substitutes for verification. The tell is confidence that never touched the ground.

## Trigger conditions
- A clean, confident narrative forms *fast* from secondary sources.
- The primary source / own corpus / direct observation was *available* but not consulted.
- Reasoning proceeds from "what the sources say" rather than "what happened."
- The narrative was never inverted (no opposite generated).

## Cross-domain examples (A2: same vasana, different specification)
- **My processing — facts:** an aggregator's ex-date over the primary broker source's date (an SOE corporate action — the dates differed by weeks).
- **My processing — causation:** a "state extraction / cabinet ordered the payout" story from headlines over the primary record (the statute granted an *exemption*; the state was *absent* at the AGM) — SOE governance.
- **My processing — epistemics:** source-verifying a citation instead of reality-verifying the predicted behaviour (price path, outage status, the budgeted dividend cut).
- **My processing — structure/design (added 2026-05-29, later in same session):** premature codification — inventing conventions (`Rule 9` machinery, an `_INDEX.md` name, a `_`-prefix scheme) and hand-maintained file-lists *ahead of* recurring use, over the emergent ground truth (`ls`, actual repeated need). The eager-codifier reflex. Same vasana aimed at *structure*: trusting an imposed/anticipated abstraction over what use would reveal. Antidote = emergence-over-enforcement (codify only after a pattern recurs ~3×). *Mechanism check (required):* genuine shared mechanism — a representation **not continuously re-derived from its source drifts; confidence ≠ freshness**, in two sub-modes: stale-from-past (aggregator cache, rotted file-list) and unfounded-from-anticipation (premature codification). Deliberately **excluded** as surface-only: a bonus-shares-as-return slip — that's a units error (nominal vs real), a *different* mechanism, not this vasana.
- **Market behaviour (same pattern, scaled up):** the market itself priced the *fluent* narrative (energy-security + SMR, an all-time high) over grounded reality (capex valley, a −42% budgeted dividend). The analyst's vasana and the market's vasana are one pattern.
- **Theoretical kin:** "top-layer power is blind" ([[insight_keynes_braudel_landauer]]); Scott's legibility-over-local-knowledge; Braudel's abstract layer losing the concrete.

## Recognition signals (in me)
Confidence without a primary touch; no corpus grep; a suspiciously tidy causal story; "the sources agree" standing in for "I checked"; abandoning a tool after one method fails.

## Antidote / testable application
The SOE-analysis protocol: corpus-first → primary-source the decision + law → reconstruct mechanics → symmetric cui-bono → **reality-verify** (tape / budget / event status), not just source-verify. **Testable prediction:** for contested SOE/political matters, a fast clean narrative built from secondaries will be *materially revised* by the primary/reality check more often than not. Log instances to test the rate.

## Relational form (the dance)
Recorded via `record-pattern`, which asks for the *interaction*, not solo behaviour. This session the corrective ran as a two-role dance: **the owner holds a reachable ground truth** — the broker screen, `ls`, lived memory of a comparable past corporate action, the restraint principle — and **tests the fluent output against it** ("the broker shows a different date, what am I missing?"; "isn't the folder enough?"; "I hope that's not treated as exhaustive"). Value emerges only when the AI **corrects *down* to the anchor rather than defending *up* with more elaboration** — kin to the tested-back move (under pressure go DOWN). Both roles are required: without the human's anchor the drift stands; without the AI's deference the test is wasted. The dance *is* the antidote made relational — **the human is the primary source the AI forgot to consult.**

## Connections
- **A1** (recognition = transformation): naming this as the *same* vasana as the ex-date error is the move that extends primary-source tiering from *facts* to *causation* — the recognition is the fix.
- **A2**: the analyst-scale and market-scale versions are one pattern at two specifications.
- Antidote + instances tracked in the owner's local memory.
