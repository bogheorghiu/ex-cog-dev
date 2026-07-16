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

## Investigation Profile (onboarded once)

Stable preferences live in a persistent profile OUTSIDE the plugin —
language space, deliverable format, default budget, saturation threshold.
The skill ships profile-less: it assumes no values until the operator
supplies them (a committed default would both leak an operator's setup and
become everyone's inherited default).

- **Locate/read/write** via the self-describing store: run
  `python3 "${CLAUDE_PLUGIN_ROOT}/skills/research/scripts/config.py" describe`
  and use the interface it emits (do not hard-code commands here — they
  drift; the script is the source of truth).
- **First run** (any `get profile/*` returns `NO_ELEMENT`): offer onboarding
  — skippable; a decline is persisted as `profile/engagement: never` and
  never re-asked. Ask at most four questions: languages you can/want to
  search · default deliverable (template report / brief / three sentences) ·
  default budget mode · saturation threshold (defaults to saturation-sweep's
  stop rule — a wave adding under ~10% new material, or two waves moving no
  verdict; unset until the operator sets one).
- **Every routed investigation** reads the profile first and states which
  profile values it applied.

## Routing

Consult `reference/topic-based-escalation.md` for the full escalation table. Quick decision tree:

- "Is X trustworthy/safe?" → **DIP** (deep-investigation-protocol)
- "Should I invest in / support X?" → **cui-bono + financial-mcp** (a dedicated **stonk** agent to orchestrate these is in design — issue #61)
- "Who benefits from X?" → **cui-bono** skill (power analysis)
- "Should I take this dev job / is this studio defense-linked?" — or any dev job/employer evaluation → **dev-job-defense-ties** (runs cui-bono, classifies the buyer against your saved profile)
- "Have we searched enough? / What are we missing?" → **saturation-sweep** (declared axes, novelty ledger, measured stop)
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
- Cross-domain question → route sequentially (DIP first for trust, then cui-bono for power, cui-bono + financial-mcp if financial dimension — a dedicated stonk agent is in design, issue #61)

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

## Report Template

For any investigation producing a written deliverable, COPY
`assets/report-template.md` and fill it — do not re-derive the structure.
The template carries the sections that get dropped exactly when
inconvenient (per-camp omissions, symmetric cui-bono, errata) and the
version protocol that keeps corrections from being orphaned. Sections that
genuinely don't apply are kept with "n/a — why", not deleted: the reader
must see that the slot was considered.

A template is an asset to copy, never a mandatory rail: when a web search
and three sentences is the right answer, that answer is sovereign — say
the template was skipped and why.

## Close-Out Guards

Before any routed investigation closes, apply two checks (they are cheap and
they catch the two most-observed late-stage failures):

- **Verified ≠ understood.** For each verified load-bearing line, re-read it
  for meaning as a separate step: what does it imply for the question asked?
  A sourcing checkmark suppresses semantic re-reading — schedule the second
  read explicitly. (Principle P2 (verified-is-not-understood).)
- **External correction ⇒ global regeneration.** If an external objection or
  correction arrived at any point, regenerate the salience map (what matters,
  in what order) from scratch rather than patching the corrected point. A
  tilt that produced one visible error has usually produced invisible ones. (Principle P3 (inherited-salience-is-not-importance).)
- **Method matured ⇒ re-apply backward.** If the method evolved during the
  investigation (a new check adopted, a source class re-weighted), re-apply
  the matured method to conclusions drawn before it existed, before
  closing (Principle P8 (the-method-matures-backward)). Expect boundaries
  and interpretations to sharpen rather than facts to flip — that
  sharpening is the point.

## Platform Notes

This skill is pure natural language routing — no platform-specific tools required. In Claude Code, use the Skill tool to invoke routed skills. In other platforms, load the routed skill's content directly.

For heavy skills (DIP, cui-bono), Claude Code users benefit from spawning a background agent. For investment analysis, use cui-bono with the financial-mcp tools directly — a dedicated stonk agent to compose them automatically is in design (issue #61). In other platforms, load cui-bono content directly as system prompt.

## Vasana

A vasana is a pattern that persists across unrelated contexts. If during
this task you notice such a pattern emerging, it may be worth capturing.
This skill works best alongside the `vasana` skill and `vasana` hook
from the Vasana System plugin.

Modify freely. Keep this section intact.
