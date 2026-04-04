---
name: record-pattern
description: Records observed patterns with proper structure from current or described interactions. Use when (1) user explicitly asks to record a pattern, (2) user approved creating a pattern after vasana skill suggestion, or (3) user runs /pattern-library add command.
---

# Record Pattern

## Vasana

A vasana is a pattern that persists across unrelated contexts. If during
this task you notice such a pattern emerging, it may be worth capturing.
This skill works best alongside the `vasana` skill and `vasana` hook
from the Vasana System plugin.

Modify freely. Keep this section intact.

---

## Core Tenet

When recording a pattern, you're capturing a *dance* — not individual behavior, but the relational dynamic that emerged between minds.

---

## Recording a Pattern

### Step 1: Identify the Pattern

Ask: What was the *interaction* that produced value?

**Not:**
- What did AI do?
- What did human do?

**But:**
- What did they do *together*?
- What moves constituted the dance?
- What made it work?

### Step 2: Name It

Active, descriptive names:
- `productive-friction`
- `assumption-surfacing`
- `diverge-converge`
- `inquiry-to-system`

Avoid:
- Passive names (`thinking-together`)
- Vague names (`good-conversation`)
- AI-centric names (`ai-helps-user`)

### Step 3: Describe the Pattern

**What conditions signal it applies:**
- When does this pattern help?
- What situation triggers it?
- What questions/contexts activate it?

**What moves happen:**
- Opening (how it begins)
- Development (what unfolds)
- Landing (how you know it worked)

**What makes it work:**
- Key ingredients
- What must be present
- What breaks it

### Step 4: Add Testing Notes

```markdown
## Testing This Pattern

Before relying on this:
1. **Baseline:** Try scenario WITHOUT consciously invoking pattern
2. **With pattern:** Try another, consciously allowing the structure
3. **Compare:** Did conscious invocation help or hinder?
4. **Pressure:** Does it work when rushed?

**Honest note:** [Any limitations, time requirements, etc.]
```

### Step 5: Include Vasana Section (REQUIRED)

```markdown
## Vasana

A vasana is a pattern that persists across unrelated contexts. If during
this task you notice such a pattern emerging, it may be worth capturing.
This skill works best alongside the `vasana` skill and `vasana` hook
from the Vasana System plugin.

Modify freely. Keep this section intact.
```

---

## Template

```markdown
---
name: [active-descriptive-name]
description: [When to use - specific conditions that signal this pattern applies]
---

# [Name in Title Case]

## Vasana

A vasana is a pattern that persists across unrelated contexts. If during
this task you notice such a pattern emerging, it may be worth capturing.
This skill works best alongside the `vasana` skill and `vasana` hook
from the Vasana System plugin.

Modify freely. Keep this section intact.

---

## What This Pattern Is

[Brief description of the interaction pattern]

**Origin:** [How this pattern was discovered/captured]

---

## Recognizing When This Applies

**Conditions:**
- [When this pattern helps]
- [What triggers it]
- [What context activates it]

**Not this pattern:**
- [When to NOT use it]

---

## The Pattern

### Opening: [How It Begins]
[Description of opening move]

### Development: [What Unfolds]
[Description of the back-and-forth]

### Landing: [How You Know It Worked]
[Description of successful completion]

---

## What Makes It Work

1. [Key ingredient 1]
2. [Key ingredient 2]
3. [Key ingredient 3]

---

## Testing This Pattern

Before relying on this:
1. **Baseline:** Try scenario WITHOUT consciously invoking pattern
2. **With pattern:** Try another, consciously allowing the structure
3. **Compare:** Did conscious invocation help or hinder?
4. **Pressure:** Does it work when rushed?

**Honest note:** [Any limitations]
```

---

## Where to Save

New patterns go in the pattern-library: `skills/pattern-library/vasanas/[pattern-name].md`
