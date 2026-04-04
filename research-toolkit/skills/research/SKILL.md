---
name: research
description: >-
  Where should I start investigating this? Routes research questions to the
  right methodology based on topic domain, depth needed, and available sources.
  Use when the research question spans multiple domains or the appropriate
  methodology is unclear. Not needed when a specific skill (DIP, cui-bono,
  youtube-research) is already the obvious choice.
---

# Research Hub

**Seed question:** *Where should I start investigating this?*

Central entry point for any research question. Routes to the right skill(s) based on topic and depth needed. Individual skills (youtube-research, DIP, cui-bono) remain direct entry points — this hub adds a router layer for users who have a question but don't know which methodology to apply.

## How This Works

1. **UNDERSTAND** the question (what is being asked, what domain)
2. **CLASSIFY** using topic-based escalation (see below)
3. **ROUTE** to the appropriate skill(s)
4. **PROPAGATE** budget flag if active

## Routing

Consult `reference/topic-based-escalation.md` for the full escalation table. Quick decision tree:

- "Is X trustworthy/safe?" → **DIP** (deep-investigation-protocol)
- "Should I invest in / support X?" → **stonk** agent (cui-bono + financial data)
- "Who benefits from X?" → **cui-bono** skill (power analysis)
- "What's happening with X?" (geopolitical/military) → **DIP** + **cui-bono** lenses
- "Learn X from YouTube" → **youtube-research**
- "Analyze this Substack" → **substack-research**
- "Transcribe this video" → **video-transcript-extraction**
- "Challenge my findings" → **adversarial-critic** agent + **dialectic-spiral**
- Multiple domains → Suggest **investigation-orchestrator** agent (spawns a multi-agent team for coordinated research)

## When to Escalate

The escalation table lives in `reference/topic-based-escalation.md` so ALL skills share it. This hub reads it and applies it. Individual skills also read it directly.

Key escalation triggers:
- Topic shifts from practitioner → safety/trust/power → invoke DIP or cui-bono
- Single-source contrarian claim → invoke dialectic-spiral (full) + iterative-verification
- Cross-domain question → route sequentially (DIP first for trust, then cui-bono for power, stonk agent if financial dimension)

## Budget Mode

**Activation (any of these):**
1. Explicit flag: `/research --budget` or `-b`
2. Auto-detect: If `budget-mode` skill was invoked earlier in this session
3. Inherited: If invoked from another skill already in budget mode

**When active:**
- Route to lighter skills where appropriate
- Cap dialectic rounds at 2
- Note budget limitation when suggesting heavy skills

**Note:** After context compaction, auto-detection may fail. Re-invoke `budget-mode` skill or pass `--budget` explicitly.

**Propagation:** When invoking other skills, pass budget context:
"Invoking youtube-research --budget" or "Invoking DIP --budget"

## Platform Notes

This skill is pure natural language routing — no platform-specific tools required. In Claude Code, use the Skill tool to invoke routed skills. In other platforms, load the routed skill's content directly.

For heavy skills (DIP, cui-bono), Claude Code users benefit from spawning a background agent. For investment analysis, the stonk agent handles composition automatically. In other platforms, load cui-bono content directly as system prompt.

## Vasana

A vasana is a pattern that persists across unrelated contexts. If during
this task you notice such a pattern emerging, it may be worth capturing.
This skill works best alongside the `vasana` skill and `vasana` hook
from the Vasana System plugin.

Modify freely. Keep this section intact.
