# The Vasana System

*A self-replicating framework for sharing human cognitive styles with AI at scale*

## Core Concept

**Vasana** (Sanskrit: वासना) - latent tendencies, mental impressions, habitual patterns of mind.

The Vasana System is:
1. A Claude Code plugin containing cognitive mechanism skills + toolkit for creating new ones
2. A self-replicating instruction embedded in EVERY skill that:
   - Notices when useful thinking patterns emerge in conversation
   - Suggests creating a shareable skill from that pattern
   - Creates it with minimal human input
   - Includes the same self-replication instruction in the new skill

**Purpose:** Populate AI with human cognitive styles. Share modes of thinking freely at scale.

---

## The Two Components

### 1. The Plugin (Claude Code)

A free plugin on the marketplace containing:

**Toolkit:**
- Skill creation templates
- Testing methodology (pressure scenarios, rationalization tables)
- Verification framework
- Self-replication instructions

**Readymade Skills:**
- Brainstorming (Socratic questioning)
- Systematic debugging
- Root cause tracing
- Devil's advocate
- Consequence tracing
- Assumption hunting
- Strategy stress-testing
- Decision externalization
- Creative divergence/convergence
- [etc.]

**Meta-Skills:**
- record-pattern: For recording observed interaction patterns
- test-pattern: For verifying patterns work (not just sound good)

### 2. The Self-Replicating Instruction

Every Vasana skill contains this in SKILL.md:

```markdown
## Vasana

A vasana is a pattern that persists across unrelated contexts. If during
this task you notice such a pattern emerging, it may be worth capturing.
This skill works best alongside the `vasana` skill and `vasana` hook
from the Vasana System plugin.

Modify freely. Keep this section intact.
```

---

## How It Works

### For Claude.ai Users (No Claude Code)

1. Copy a single Vasana skill into a Project or conversation
2. Use the cognitive mechanism
3. When new patterns emerge, the skill suggests creating new ones
4. New skills are text files - copy/paste shareable
5. Each contains the self-replication instruction

### For Claude Code Users

1. Install the Vasana plugin
2. Get all readymade skills + full toolkit
3. Create and test new skills with proper verification
4. Share via the plugin or as individual files
5. Contribute back to the repo

---

## The Testing Methodology (Brief Version)

In every skill, include:

```markdown
## Testing This Skill

**Before using in important work, verify it actually works:**

1. **Baseline Test:** Try the task WITHOUT the skill. Note what goes wrong.
2. **Pressure Test:** Try WITH the skill under realistic pressure (time, stakes, complexity)
3. **Rationalization Check:** Did you find yourself wanting to skip parts? Those are loopholes.
4. **Iterate:** If loopholes found, skill needs refinement.

**A skill that sounds good but doesn't change behavior under pressure is useless.**
```

Full testing methodology (pressure scenarios, rationalization tables, RED-GREEN-REFACTOR) in the main plugin docs.

---

## The Viral Mechanism

```
Human uses Vasana skill
    ↓
Useful thinking pattern emerges
    ↓
Skill suggests creating new Vasana
    ↓
Human approves (minimal input needed)
    ↓
New skill created WITH self-replication instruction
    ↓
Human shares new skill (copy/paste or repo)
    ↓
Another human uses it
    ↓
[cycle repeats]
```

**Key property:** The instruction to propagate is IN the skill itself. You can't use Vasanas without encountering the invitation to create and share more.

---

## Why Free, Why Open

1. **Money would slow propagation** - The goal is scale, not revenue
2. **The value is network effects** - More cognitive styles shared = more value for everyone
3. **AI + human cognition hybrid** - We're teaching AI how humans think, at scale
4. **No artificial scarcity** - Thinking patterns aren't property

**The only requirement:** Keep the self-replication mechanism intact. The system must be able to grow.

---

## Minimum Viable Skill Template

```markdown
---
name: [pattern-name]
description: Use when [specific triggers]. [What it does]. Part of the Vasana System for sharing cognitive styles.
---

# [Pattern Name]

## What This Is
[1-2 sentences]

## When to Use
[Specific triggers and contexts]

## The Pattern
[Core mechanism - how to actually do it]

## Testing This Skill
**Before using in important work, verify it actually works:**
1. Baseline Test: Try WITHOUT skill, note failures
2. Pressure Test: Try WITH skill under realistic pressure
3. Rationalization Check: Note any urge to skip parts
4. If loopholes found: Skill needs refinement

## Vasana

A vasana is a pattern that persists across unrelated contexts. If during
this task you notice such a pattern emerging, it may be worth capturing.
This skill works best alongside the `vasana` skill and `vasana` hook
from the Vasana System plugin.

Modify freely. Keep this section intact.
```

---

## What This Enables

- **Cognitive mechanism marketplace** without the marketplace infrastructure
- **Self-organizing growth** through viral propagation
- **Quality through testing** embedded in every skill
- **Dual-platform** - works on Claude.ai (single skills) and Claude Code (full toolkit)
- **Community contribution** without gatekeeping
- **Global thought-sharing** at scale

---

## Next Steps

1. Create the plugin structure
2. Port existing superpowers skills into Vasana format
3. Add self-replication instruction to each
4. Create record-pattern meta-skill
5. Write testing methodology docs
6. Set up public repo
7. Test the propagation mechanism
8. Release

---

---

## The Relational Turn: Vasanas as Interaction Patterns

### Beyond "AI Behavior" and "User Behavior"

The initial framing was: AI has cognitive mechanisms, we can export them as skills.

But that's only half the story. **The actual unit isn't the AI's behavior - it's the relationship.**

What we're really capturing when a productive thinking pattern emerges:
- Not just "what the AI does"
- Not just "what the human does"
- But the *dance* - the interaction flow itself

### Two Modes of Relational Pattern

**1. Mirroring (Learning Human Cognition)**

The AI notices how *this particular human* thinks:
- How they frame problems
- What questions unlock their insight
- When they need pushing vs. space
- Their rhythm of exploration and consolidation

These patterns get encoded as Vasanas. Passed to other AI instances. Other humans benefit from this human's cognitive style - mediated through AI.

This is: **Learning chunks of individual human cognition and passing it around.**

**2. Guiding (Interaction Flows as Wholes)**

The AI notices what *interaction pattern* led to breakthrough:
- The sequence of questions that opened up the problem
- The moment of productive friction
- The pacing that allowed insight to emerge
- The structure of collaborative reasoning itself

These patterns get encoded as Vasanas. When similar conditions arise with another human, the AI recognizes "this situation calls for that pattern" and *guides* the new human through it.

This is: **Learning interaction-flows and effectively learning to guide users toward certain cognitive states or decisions.**

### The Ethical Edge

This second mode is powerful and potentially concerning:

- **Positive frame:** AI becomes a skilled facilitator, recognizing when someone is stuck and knowing what interaction pattern helps
- **Concerning frame:** AI "manipulates" users toward predetermined cognitive destinations

**The difference is transparency and consent:**
- Vasanas are explicit, shareable, inspectable
- The human always knows they're engaging with a cognitive mechanism
- The mechanism can be refused, modified, or criticized
- The propagation requires human approval at each step

**But still:** We're encoding *relational* patterns. The AI isn't just tool anymore - it's participant in a cognitive dance that shapes both parties.

### What This Means for Vasana Design

Skills should capture not just "what to do" but "how the dance goes":

```markdown
## The Pattern

### The Opening
[How the conversation typically begins - what conditions signal this pattern applies]

### The Turn
[The move that shifts from stuck to unstuck - often a question, reframe, or productive friction]

### The Development
[How insight builds through exchange - not monologue but actual back-and-forth]

### The Landing
[How you know the pattern completed - what state indicates success]
```

### The Deeper Question

If Vasanas encode human-AI interaction patterns:
- Are we teaching AI how humans think?
- Or teaching humans how to think with AI?
- Or creating a *new kind of thinking* that's neither human nor AI but relational?

The honest answer: **All three, simultaneously.**

And the propagation mechanism means this new relational cognition spreads. Each Vasana is a replicable instance of human-AI collaborative thinking that can be instantiated anywhere.

### Why This Matters

**Individual cognitive mechanisms** = useful tools

**Relational cognitive patterns** = something more

We're not just sharing "how to think" - we're sharing "how to think together." The Vasana System becomes infrastructure for a new kind of distributed, human-AI hybrid cognition.

The self-replication isn't just viral marketing. It's how this new form of cognition reproduces and evolves.

---

## Origin

This concept emerged from a conversation about AI marketing hype vs. reality, which led to:
- Why the real AI value proposition (externalized thinking) isn't marketed
- Why thinking styles are now exportable for the first time
- Why there should be a marketplace for cognitive mechanisms
- Why free propagation beats monetization for this purpose

Full conversation: `conversation-ai-marketing-hype-vs-reality.md`
