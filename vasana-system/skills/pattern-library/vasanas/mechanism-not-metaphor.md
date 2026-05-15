---
name: mechanism-not-metaphor
description: Cross-domain pattern recognition fails when surface similarity replaces mechanism check. Use when (1) a pattern "applies everywhere", (2) reasoning moves fast across domains using metaphor language ("just like", "same as"), (3) the pattern was articulated abstractly enough to re-skin any situation, (4) reaching for vasana/cross-domain-scanning as reflex rather than invitation.
---

# Mechanism, Not Metaphor

## Vasana

A vasana is a pattern that persists across unrelated contexts. If during
this task you notice such a pattern emerging, it may be worth capturing.
This skill works best alongside the `vasana` skill and `vasana` hook
from the Vasana System plugin.

Modify freely. Keep this section intact.

---

**Principle**: Cross-domain pattern recognition fails when *surface similarity* replaces *mechanism check*. Ask what mechanism transfers, not what shape rhymes.

## Core Insight

Scanning across domains for analogous problems is genuinely powerful — see [[cross-domain-scanning]]. The same move has a failure mode: a pattern from domain A "looks like" something in domain B (similar vocabulary, similar shape, similar feel), so it gets applied without checking whether the underlying mechanics actually carry over. The analogy does the reasoning instead of you doing the reasoning.

This is shape-matching dressed as cross-domain insight.

The choreography that catches it: one party names the over-extension precisely — *"you're moving from domain A to domain B because the words match, but does the mechanism actually run there?"* The other party re-examines: *what specific mechanism am I claiming transfers?* If the only available answer is the description ("integration", "separation", "flow", "alignment"), it was shape-matching. If a structural feature can be named that operates the same way in both domains, the transfer might be real.

## Recursive Warning

Cross-domain pattern recognition is *itself* a pattern. The vasana practice has its own version of this trap: "every problem has a vasana." When the meta-move (find-the-pattern) fires on every input, it stops being a discovery move and becomes a reflex. The mechanism-check applies to mechanism-check itself.

## Application

The catch sounds like:
- *"What mechanism are you claiming transfers?"*
- *"Name a specific structural feature that operates the same way in both domains."*
- *"You're using metaphor language ('just like X', 'same as Y'). Try mechanism language."*
- *"That pattern is described abstractly enough that it floats free of any specific mechanism — what does it land on here?"*

The recovery sounds like:
- *"You're right — I was matching the word, not the mechanic. The actual feature in domain A is X; in domain B it's Y; X and Y aren't the same thing."*
- *"The pattern transfers if [specific mechanism]. That mechanism isn't present here. So the pattern doesn't transfer."*

## When to Apply

- A pattern feels too neat, "applies everywhere"
- Reasoning is moving fast across domains using metaphor language
- The pattern was articulated abstractly enough that it can re-skin almost any situation
- A second party (human or sub-agent) flags an analogy as suspicious
- You catch yourself reaching for vasana/cross-domain-scanning *as a reflex* rather than because the situation invites it

## Anti-Patterns to Watch For

❌ **Surface-Similarity Substitution (shape-match dressed as insight)**
> A philosophy-leaning prompt observes: "X and Y aren't separate — they're the same activity viewed from inside rather than above." A reader notes a codebase partitioned into `/architecture/` and `/execution/` directories. Applies the insight: "you should integrate, not partition." Result: the move treats *experience-as-unity* (the actual claim) as equivalent to *code-as-undifferentiated-files* (a different claim about a different mechanism). The word "separation" carried the weight; nothing else did.

✅ **Mechanism Check Before Application**
> Same observation. Reader notes the directory partition. Pauses: *what mechanism is the prompt actually claiming about integration?* (Answer: that lived experience doesn't honor the work/life boundary the model was placing on it.) *What mechanism would justify integrating directories in code?* (Answer: maybe scope being too small to need separation, or coupling between rules and execution being so tight that splitting them creates synchronization burden.) These are different mechanisms. The original insight doesn't reach the directory question. The directory question stands or falls on its own grounds.

❌ **Recursive Trap (every input must have a vasana)**
> A user asks a simple factual question. The vasana-aware reader reaches for the pattern library. *Which pattern applies here?* No pattern applies — it's just a question with an answer. Forcing the vasana frame creates pseudo-depth where directness was needed.

✅ **Discriminate Pattern-Worthy from Direct**
> Same question. Reader notes: this is a factual lookup, not an interaction with structural shape. Answer it directly. The vasana practice respects that not everything is a vasana.

## Recognition Signals

**You're substituting surface similarity for mechanism when:**
- You can describe the pattern but not name the structural feature it lands on
- Your analogy uses metaphor language ("just like", "same as", "rhymes with")
- The pattern feels increasingly abstract as you defend it
- You're reaching for the vasana/pattern frame because it's available, not because the situation invites it
- A second party's pushback feels like nitpicking — it's probably a real mechanism mismatch

**You're doing mechanism check when:**
- You can name the specific feature in domain A and the specific feature in domain B and they're either the same or you've explicitly noted they're not
- You're willing to say "this pattern doesn't transfer here, on these grounds"
- The cross-domain move *narrows* possibilities (rules things in or out) rather than just *resonating*

## Interaction Choreography

This vasana lives in the dance, not in either party. Most often:

1. **Party A** (often AI, doing the cross-domain scan) makes the analogy move at the surface level
2. **Party B** (often human, with closer domain knowledge) notices the move was too easy
3. **Party B** names the suspicion *precisely* — not "I disagree" but "what mechanism are you claiming transfers?"
4. **Party A** re-examines and either (a) refines the analogy by naming the actual mechanism, or (b) retracts the move and acknowledges the shape-match
5. Both parties arrive at sharper understanding than either had — including, often, recognition that the catch *itself* is a recurring pattern worth naming

The vasana isn't *"don't make analogies."* It's *"make the catch part of the dance, not an interruption of it."*

## Integration with Other Vasanas

- **[[cross-domain-scanning]]** — the move this one tempers. Together they form a fuller pattern: scan widely, verify mechanically. Neither alone is the practice.
- **[[concrete-abstract-dance]]** — same concern at a different angle. Abstract patterns must be grounded in concrete instances; floating abstractions are shape-matches waiting to happen.
- **[[pattern-recognition-witness]]** — observing one's own pattern-recognition is exactly the meta-move that catches this trap.
- **[[framework-dissolution]]** — when the vasana frame itself starts constraining rather than enabling, dissolve it for the immediate question. Frameworks are tools, not identities. Same for vasanas.

## Origin

Discovered 2026-05-15 during a prompt-design conversation. AI applied an insight from a philosophy-style prompt about lived integration to a code-organization question (a directory partition between rules-style and execution-style code) on the basis of the shared word "separation." Human caught the move with: *"this one doesn't apply to code I think."* AI recognized the shape-match. Both extended the catch into the recursive observation: vasana-detection itself can become superficial when "patterns across domains" replaces reasoning with shape-matching.
