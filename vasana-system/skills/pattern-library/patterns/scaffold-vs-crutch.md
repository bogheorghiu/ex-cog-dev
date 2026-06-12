---
name: scaffold-vs-crutch
description: Use when designing or evaluating any external aid — a tool, a skill, an AI workflow, a teaching method — to ask which fork it takes: does it build the user's internal capacity (scaffold) or substitute for it and let it decay (crutch)? Triggers on design reviews ("does this leave the user more capable?"), on "AI makes people dumber" debates, and whenever a tool's help could be doing the user's thinking instead of training it.
---

# Scaffold vs Crutch

## Vasana

A vasana is a pattern that persists across unrelated contexts. If during
this task you notice such a pattern emerging, it may be worth capturing.
This skill works best alongside the `vasana` skill and `vasana` hook
from the Vasana System plugin.

Modify freely. Keep this section intact.

---

## What This Pattern Is

The same external aid has *opposite* developmental effects depending on use:
it either **builds** internal capacity (scaffold — temporary, removable,
leaves you more able) or **substitutes** for it (crutch — creates dependence,
leaves you less able). The tool is not the variable; the fork is whether the
internal process is *trained* or *bypassed*.

**Origin:** Staged publicly as ex-cog-dev issue #93 (Jun 7, 2026; snapshot in
the excogitations archive) with status "reconcile with local library" —
reconciled into this library 2026-06-12 after a fresh design occurrence
(see below). Unlike most library patterns this is a *criterion* pattern
(like `mechanism-not-metaphor`), not an interaction dance: its use is as a
design/eval question, not a choreography.

---

## Recognizing When This Applies

**Conditions:**
- Designing or reviewing a tool, skill, prompt, or workflow whose job is to
  help someone do something they could (or should) learn to do.
- Evaluating an AI-assisted practice: is this "thinks *with* you" (capacity
  exercised) or "thinks *for* you" (capacity bypassed)?
- Answering the "AI makes people dumber" critique honestly: yes — used as a
  crutch; the design aim is scaffold.
- A tool "helps" but the user is less able without it each month — crutch
  signature.

**Not this pattern:**
- Aids for functions nobody needs to internalize (a dishwasher is not a
  crutch — there's no capacity worth training).
- Permanent compensations for permanent losses (an actual prosthetic used as
  designed); the pattern is about *avoidable* atrophy of *trainable* capacity.

---

## Cross-Domain Verification

**Mechanism check:** shared causal structure, not metaphor — offloading a
function either *exercises-then-returns* it (capacity grows) or
*replaces-and-lets-it-decay* (capacity shrinks). Use-dependent capacity
change under offloading is the single mechanism in every domain below.

**Domains verified:**
- Education — scaffolding (Vygotsky/Wood-Bruner-Ross sense) vs spoon-feeding.
- Navigation — GPS dependence measurably degrades spatial memory
  (cognitive-offloading research).
- Arithmetic — calculators vs mental arithmetic practice.
- Prosthetics / exoskeletons — assistance vs disuse atrophy (the literal
  source of "crutch").
- AI tools — "thinks with you" vs "thinks for you"; the ex-cog manifesto's
  "something to drive, not an oracle to trust" is this criterion applied to
  search.
- Tool/skill design (fresh occurrence, 2026-06-12) — the `action-bias` skill
  re-aim (ex-cog-dev issue #65): re-targeted at the *user's* deferral
  tendency, surfacing the pattern and offering the next concrete action
  (scaffold), instead of overriding the model's act-vs-plan judgment
  (a louder command — the enclosure-shaped sibling of a crutch).

**Lineage:** Sterelny (the scaffolded mind); cognitive-offloading research
(Risko & Gilbert and successors). Named lineage, not borrowed authority —
the mechanism stands on the evidence above.

---

## The Pattern (as a design move)

### Opening: Ask the fork question
At design or review time: *does using this leave the user more capable, or
more dependent?* Concretely: if the aid vanished after three months of use,
would the user perform the task better or worse than before they had it?

### Development: Locate the trained-vs-bypassed seam
Find where the internal process runs. A scaffold makes the user execute the
process with support (and the support is removable by design); a crutch
executes the process *for* them. Many tools can be either — the seam is in
the interaction design, not the feature list.

### Landing: A removability test you can state
You know it's a scaffold when you can say what the user will have
internalized and roughly when the support could be withdrawn — or why
permanent support is genuinely appropriate. If neither can be stated, it's
drifting crutch-ward.

---

## What Makes It Work

1. **The fork is in use, not in the tool** — the same artifact scaffolds one
   user and cripples another; evaluate the practice, not the product label.
2. **Mechanism over moralizing** — "does this train or bypass the internal
   process?" is checkable; "is this making people lazy?" is not.
3. **Removability as the operational test** — scaffolds are designed to be
   taken away; crutches are designed to be renewed.

---

## Testing This Pattern

Before relying on this:
1. **Baseline:** Review a tool design WITHOUT consciously invoking the pattern.
2. **With pattern:** Review another, consciously asking the fork question.
3. **Compare:** Did the criterion surface design changes the plain review missed?
4. **Pressure:** Does it work when rushed?

**Honest note:** The library's A/B protocol above has not been run on this
pattern (n=0 in-session); cross-domain verification rests on the external
cognitive-offloading literature and two documented design occurrences (the
ex-cog manifesto framing; the action-bias re-aim). An open question staged
with the original issue: whether the capability-floor parity test
(wikipediai Rule 3) and a scaffold/crutch eval are the *same instrument* —
both measure "does the tool leave the weaker party more capable?" If that
holds under scrutiny, this pattern generalizes further; it has not been
checked.
