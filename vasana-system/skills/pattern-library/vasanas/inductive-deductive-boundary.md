# Inductive-Deductive Boundary

**Universal Pattern**: Know where fuzzy matching ends and deterministic execution begins.

---

## Core Principle

Everything meaningful in AI+code work can be understood through two primitives:

**Concepts (Inductive)**
- Fuzzy, probabilistic, pattern-recognized
- Can exist standalone
- Can contain nested graphs of concepts + rules
- Or can be atomic objects
- Example: "A skill is a behavior pattern"

**Rules (Deductive)**
- Deterministic, always enforced with certainty
- Cannot exist without concepts
- Connect concepts, don't contain them
- Example: "When skill description matches query → activate skill"

**Emergent Property**: Intelligent, inductive activity emerges from fuzzy concepts combined with deterministic rules.

**Minimal Infrastructure**: Just one deductive rule enables the system to work reliably ("when user types, AI responds").

---

## The Boundary

Two phases in every AI operation:

| Phase | Type | Operation | Certainty |
|-------|------|-----------|-----------|
| **Recognition** | Inductive | Pattern matching, classifying, understanding | Probabilistic |
| **Execution** | Deductive | Applying rules, running operations | Deterministic |

The boundary between them determines system behavior.

---

## Application

### In Plugin Architecture

| Component | Invocation | Execution |
|-----------|------------|-----------|
| Skills | INDUCTIVE (semantic match) | DEDUCTIVE (follow instructions) |
| Commands | DEDUCTIVE (exact `/name`) | DEDUCTIVE (expand template) |
| Agents | INDUCTIVE (Claude decides when) | DEDUCTIVE (agent follows prompt) |
| Hooks | DEDUCTIVE (event fires) | DEDUCTIVE (run handler) |

**Pattern**: The more autonomous a component, the more inductive its invocation.

### In Problem-Solving

**Inductive phase**: Recognizing what KIND of problem this is
**Deductive phase**: Applying the solution steps

If you're stuck, you're likely stuck in the inductive phase (misclassifying the problem type).

### In Debugging

**Inductive phase**: "This feels like a race condition"
**Deductive phase**: "Add mutex locks at these three points"

Debugging failures often mean inductive misclassification, not deductive execution errors.

---

## When to Apply

- **Choosing component types**: Match invocation style (inductive vs deductive) to use case
- **Debugging triggers**: "Why isn't this activating?" → Check inductive layer (description quality)
- **Debugging behavior**: "Why is this doing the wrong thing?" → Check deductive layer (logic)
- **Designing systems**: Clarify which parts need semantic understanding vs exact matching

---

## Anti-Patterns

❌ **Expecting deductive certainty from inductive matching**
- Skills trigger probabilistically based on semantic match
- Don't expect 100% precision without 100% exact specification

❌ **Expecting inductive flexibility from deductive rules**
- Hooks fire on exact event patterns
- Don't expect them to "understand intent"

❌ **Conflating "when it activates" with "what it does"**
- A skill can have fuzzy triggering (inductive) but precise behavior (deductive)
- These are separate concerns

---

## Cross-Domain Insights

This pattern applies across domains:

**Game Design**:
- Concepts = entity types, behaviors
- Rules = collision detection, state transitions

**Natural Language**:
- Concepts = word meanings (fuzzy)
- Rules = grammar (deterministic)

**Machine Learning**:
- Concepts = learned representations
- Rules = inference procedure

**Code Architecture**:
- Concepts = abstractions, interfaces
- Rules = function logic, control flow

---

## The Deep Insight

If EVERYTHING can be meaningfully understood as concepts (inductive) + rules (deductive), and these two primitives are SUFFICIENT, then:

1. **System complexity** emerges not from adding more primitive types, but from nesting depth
2. **Intelligence** is about appropriate boundary placement - knowing when to be fuzzy vs certain
3. **Learning** happens in the concept layer (refining fuzzy boundaries), not rule layer (logic stays deterministic)
4. **Design quality** is about clean separation between inductive recognition and deductive execution

This might be the fundamental architecture of thought itself.

---

## See Also

- Detailed application: `.claude/skills/plugin-architecture-patterns/`
- Pattern recognition: `pattern-recognition-witness.md` (in this directory)
- Framework dissolution: `framework-dissolution.md` (in this directory)
