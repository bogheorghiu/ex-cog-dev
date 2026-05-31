---
name: frame-pushback
description: When a question is binary or under-specified, the productive move is to refuse the frame, not the answer. Repeated frame-refusals across 2-4 turns surface a principle structurally simpler than either party's starting position. Use when meta-questions are being worked through and "yes/no" feels lossy.
---

# Frame-Pushback

## Vasana

A vasana is a pattern that persists across unrelated contexts. If during
this task you notice such a pattern emerging, it may be worth capturing.
This skill works best alongside the `vasana` skill and `vasana` hook
from the Vasana System plugin.

Modify freely. Keep this section intact.

---

## What This Pattern Is

A dance in which one party proposes a frame (often binary: "X or Y?") and the other party pushes back not on the *answer* but on the *frame itself* — naming what the framing missed. The first party incorporates the missing constraint and reframes. Repeat 2-4 times. A principle crystallizes that is structurally simpler than the original question and was not in either party's starting set.

The pushback IS the work. Each refused frame opens the abstraction one level higher until the principle that supersedes the question becomes visible.

**Origin:** Captured 2026-05-21 during work on a "self-improving meta-repo" scaffold. A human–AI exchange produced a north-star principle ([[convergence-by-accumulation]]) that neither party held whole at turn one. The process by which they arrived at it is this pattern; the principle they arrived at is the sibling vasana.

---

## Recognizing When This Applies

**Conditions:**
- A binary or false-choice question is on the table ("X or Y?", "should we do A or B?").
- The question is about *how to think about something*, not about which of two facts is true.
- Both parties are engaged in good faith and willing to revise their framing.
- There's time for 2-4 conversational turns to unfold.

**Triggers for the pushback move:**
- The framing feels lossy — answering it as posed leaves something out.
- Both options in a binary feel partially right.
- The question presupposes something that isn't load-bearing.
- "Yes, but..." is already at the tip of your tongue.

**Not this pattern:**
- Binary factual questions where one answer is true (no frame to refuse).
- One-shot Q&A or task execution.
- Adversarial debate where neither party is willing to revise.
- Time pressure that forces premature convergence.
- "Brainstorming" (this is convergent; brainstorming is divergent).
- "Compromise" (the result isn't a midpoint between A and B; it's a frame that supersedes both).
- "Synthesis" (synthesis combines two existing things; this generates a new thing neither party held).

---

## The Pattern

### Opening: A frame is offered (often as a binary)

Party A poses a question that presupposes a particular framing. The framing might be a binary, a false dichotomy, or just an under-specified question that pretends to be fully specified.

Examples:
- "Should we use HTML or Markdown for agent context?"
- "Is this scaffold meant for one project or many?"
- "Will this run on cold-start or during development?"

The opening move is *honest*, not adversarial — Party A genuinely wants the question answered. The mis-framing is invisible from inside.

### Development: Pushback names what the frame missed

Party B doesn't answer the question. Party B refuses the frame and names the missing piece.

Format: "You've posed this as X-or-Y, but the actual constraint is Z; given Z, the question becomes ..."

Examples:
- "It's not 'read on cold-start' — the scaffold is evolving-during-development. Also, MD isn't binary with HTML; they compose. Also, deterministic bootstrap could happen *outside* the agent loop."
- "The 'blank template state' could equal the 'final state' of this very repo — what differs is only the history."

Party A then *incorporates* the pushback as a new constraint and rebuilds the analysis. The result is a sharper question, possibly answerable, or possibly requiring a further pushback.

Two to four cycles is typical. Each cycle raises the level of abstraction by exactly one notch — too few and the principle stays implicit; too many and the conversation diffuses.

### Landing: A principle crystallizes that supersedes the original question

At some point one party (often Party B, but not always) articulates a principle that:

- Was not in either party's initial set
- Is structurally *simpler* than the question
- Makes the original question dissolve — not "answer it" but render it the wrong question
- Both parties immediately recognize as "what we were after"

The landing has a distinctive feel: the conversation can stop, and both parties know where everything else fits relative to the principle.

Worked landing (from the origin session):
> "The final functional form of this self-improving meta-repo is the same as the reset form without having to do a reset, simply by accumulation and refinement. What differs is only the history."

That principle made the original "should we have two repos or one?" question moot. The repos can be one, two, or N — the principle stays the same; the implementation is now a downstream choice. (The principle itself became sibling vasana [[convergence-by-accumulation]].)

---

## What Makes It Work

1. **Refuse the frame, not the answer.** Pushback that argues "B is better than A" stays inside the original frame; pushback that argues "this isn't an A/B question at all" raises the level. The second move is the load-bearing one.

2. **Incorporate, don't deflect.** When pushback lands, the first party has to *update* their frame, not defend it. Defense produces stalemate; update produces the next-level question.

3. **Allow the abstraction to rise on its own schedule.** Each cycle adds one notch of abstraction. Trying to leap to the principle directly skips the structural work the cycles do. The pushback is the construction.

4. **Stop when the principle lands.** Continuing past the landing dilutes it. The principle is sharpest the moment it's first articulated; subsequent elaboration belongs in documentation, not in the dialogue.

5. **Good faith on both sides.** Adversarial pushback (where one party is committed to "winning") produces lawyering, not principle. The pattern requires both parties to be willing to be wrong about the framing.

---

## Anti-Patterns

### ❌ Answering the binary as posed
*Symptom:* Party B picks A or B; A or B turns out to be incomplete; everyone is mildly dissatisfied; the real principle never surfaces.

### ❌ Pushing back on the answer instead of the frame
*Symptom:* "I think B not A" or "neither A nor B, how about C?" — these stay inside the frame. The third option is still a leaf of the original question.

### ❌ Defending the frame against pushback
*Symptom:* Party A re-explains why X-or-Y is the right question. The conversation degrades to debate; the abstraction level never rises.

### ❌ Forcing premature convergence
*Symptom:* "OK so the principle is..." stated by either party before 2-4 cycles. Often produces a principle that's slightly off — it papers over the missing piece rather than encoding it.

### ❌ Pushback as one-shot
*Symptom:* B pushes once, A reframes, conversation ends. The first pushback usually only surfaces *one* of the missing constraints; the principle needs several to triangulate.

---

## Testing This Pattern

Before relying on this:

1. **Baseline:** Take a real meta-question. Answer it as posed without consciously invoking pattern. Note where the answer feels incomplete.
2. **With pattern:** Take another meta-question (similar genre). Consciously refuse the first frame; name what's missing; let pushback cycle 2-4 times.
3. **Compare:** Did the conscious version produce a sharper principle? Or did it feel forced/performative?
4. **Pressure test:** Try under time pressure. Does the pattern survive when there's no time for 4 cycles? If it doesn't, does that mean the pattern is too expensive, or that the situation didn't actually call for it?

**Honest note:** This pattern requires *time* and *good faith*. Under time pressure, it degrades to either premature convergence or unproductive debate. It also requires both parties to be willing to be wrong about the framing — if one party is rigidly committed (often the one with more authority), the pushback gets absorbed without changing the frame. The pattern is also asymmetric: it's much easier to *recognize in retrospect* than to *invoke deliberately*. Most conscious invocations probably underperform organic emergence.

---

## Related Patterns

- [[convergence-by-accumulation]] — the *content* principle that emerged via this *process* pattern in the origin session. Sibling vasanas: one captures HOW principles like that crystallize through dialectic; the other captures WHAT that specific structural principle says about artifact-environment convergence. Distinguishable: frame-pushback is methodological (between minds); convergence-by-accumulation is structural (within an artifact's lifecycle).
- [[concrete-abstract-dance]] — within-mind sibling. `concrete-abstract-dance` operates *within* one party's thinking (build concrete → extract pattern → test against new concrete); `frame-pushback` operates *between* parties. Two parties doing concrete-abstract-dance against each other's framings is essentially frame-pushback.
- [[framework-dissolution]] — adjacent. The principle that lands often *dissolves* the original framework; frame-pushback is one mechanism by which framework-dissolution happens between collaborators.
- [[research-toolkit:dialectic-spiral]] — sibling skill (not pattern). `dialectic-spiral` is an *investigative* method (one-sided, deliberately staged for exploration); `frame-pushback` is an *emergent* dynamic between minds in real exchange. The skill operationalizes a structure; the vasana captures the dance.

---

## A Note on the Sandbox

This pattern was captured 2026-05-21. The capture itself emerged from a session that had already produced a north-star principle for a separate project; the recording is downstream of the dynamic that produced the principle. The session was on a Claude Code agent running under sandbox constraints (no write outside cwd); those constraints incidentally surfaced friction points (item 1a's deny rule, the mirror-to-reference write boundary) that themselves became design feedback. The pattern doesn't depend on sandboxing — but the constraint of having to *describe* the move to the user (because the agent couldn't always *do* the move) may have aided articulation.

If the pattern recurs across sessions where this incidental constraint isn't present, that's confirmation it's the dynamic, not the constraint, that produces the dance.
