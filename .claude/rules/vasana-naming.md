---
paths:
  - "vasana-system/**"
---

# Vasana naming — reserve the word, default to "pattern"

Use **"Vasana"** only in four reserved slots: the system name, the entry skill
(`vasana`), the hook (`vasana.sh`), and the `## Vasana` section every skill carries.
**Everywhere else the word is "pattern"** — `record-pattern`, `pattern-library`,
"capture a pattern," and so on.

## Why

"Vasana" is a mystical-sounding Sanskrit loanword, and `descriptions-and-discoverability`
calls for *over-grounding* such a name — concrete words, not more of the same vibe — so
the term keeps a meaning instead of dissolving into atmosphere. Spend the word on every
mechanism and the baggage spreads everywhere; the system reads as woo and the name stops
distinguishing anything. Spend it only where it names the system's *identity* — its
brand, its entry point, its propagation section — and the term stays load-bearing while
the plain word "pattern" carries the working vocabulary, which is where clarity matters
most. The reserved slots are exactly the identity-carrying ones; the rest is mechanism,
and mechanism reads clearer in plain English.

## Where this also lives

The shipped `vasana` skill states this rule in-band so consumers see it; this file is the
*development-time* copy that loads when you edit `vasana-system/` files. They must stay
consistent — if the reserved set ever changes, change both (the skill and this rule). The
rule itself is dev guidance and ships with no plugin, per `rule-design.md`.
