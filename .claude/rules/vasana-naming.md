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
calls for *over-grounding* such a name — concrete words, not more of the same vibe — so the
term keeps a meaning instead of dissolving into atmosphere. Spend the word on every
mechanism and the baggage spreads everywhere; the system reads as woo and the name stops
distinguishing anything. Spend it only where it names the system's *identity* — its brand,
its entry point, its propagation section — and the term stays load-bearing while the plain
word "pattern" carries the working vocabulary, where clarity matters most.

## Where this also lives

A one-line summary + pointer sits in `vasana-system/CLAUDE.md`; the shipped `vasana` skill
states the rule in-band so consumers see it. This file is the development-time canonical
copy — it loads when you edit `vasana-system/` files and carries the full rationale. Keep
the three consistent: if the reserved set changes, change all three. The rule itself is dev
guidance and ships with no plugin, per `rule-design.md`.
