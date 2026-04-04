# Vasana Testing Protocol

*Adapted from superpowers testing-skills-with-subagents, modified for relational patterns*

---

## The Core Difference

**Superpowers tests discipline skills:** Did the agent comply with the rule under pressure? (Binary: yes/no)

**Vasana testing asks:** Did the interaction pattern emerge? Did something useful happen? (Qualitative, not binary)

We're not testing compliance. We're testing whether a *way of being together* can be reliably instantiated and produces value.

---

## What's Actually Testable

### 1. Triggering
**Question:** Given the described conditions, does the Vasana get invoked?

**Test method:**
- Create scenarios that match trigger conditions
- Run conversation, observe if Vasana is recognized/invoked
- Pass: Vasana activates when conditions match
- Fail: Conditions present but Vasana not invoked

**This is the same as skill triggering testing.**

### 2. Pattern Emergence
**Question:** When invoked, does the described interaction pattern actually occur?

**Test method:**
- Invoke the Vasana explicitly
- Run the interaction
- Check: Can an observer recognize the pattern?
- Pass: "Yes, that's the pattern described"
- Fail: "The words are there but the dance didn't happen"

**What to look for:**
- The structural elements actually appear (not just referenced)
- The interaction has the described *shape*
- It doesn't collapse into monologue or Q&A

### 3. Self-Replication
**Question:** Does the propagation mechanism work?

**Test method:**
- Run conversations where useful patterns emerge
- Check: Does the Vasana suggest creating a new Vasana?
- Check: Is the suggestion appropriate (not every conversation)?
- Check: Does created Vasana include propagation section?
- Pass: Appropriate suggestions, complete new Vasanas
- Fail: Never suggests, always suggests, incomplete propagation

### 4. Value (The Hard One)
**Question:** Does this Vasana produce something useful?

**This cannot be tested the same way as compliance.** There's no binary pass/fail.

**Proxy measures:**
- **Behavioral:** Human chooses to keep/share the Vasana (signal of perceived value)
- **Subjective report:** Human says it helped
- **Shift observation:** Something observably changed (stuck→unstuck, vague→clear)
- **Comparison:** "Was this different from how you usually work?"

**Honest limitation:** Value is subjective. We can gather signals but not prove value objectively.

---

## The Baseline Problem

Superpowers compares: agent without skill vs. agent with skill, same scenario.

For Vasanas:
- Scenarios don't repeat exactly
- Context always differs
- "Better" is subjective

**Practical approaches:**

1. **Similar-enough scenarios:** Not identical, but close enough to compare
2. **Same human, different mode:** How does this human usually work vs. with Vasana?
3. **Cross-human comparison:** Different humans, similar scenarios, some with Vasana
4. **Self-report:** "Was this interaction different? How?"

**Accept imperfection.** We're not doing science. We're asking: "Does this seem to matter?"

---

## Testing Checklist for a New Vasana

### Before Release

- [ ] **Trigger test:** Created scenarios matching conditions, Vasana invokes
- [ ] **Pattern test:** Invoked Vasana, pattern recognizably emerged
- [ ] **Propagation test:** Propagation section present and functional
- [ ] **At least one value signal:** Human reports usefulness OR chooses to keep/share

### Ongoing (As Vasana Is Used)

- [ ] **Track:** How often invoked? How often propagation suggested?
- [ ] **Collect:** Human feedback on value
- [ ] **Watch for:** Degradation (pattern stops emerging), false triggers

---

## What We're NOT Testing

**Not testing:**
- Whether Vasana produces "correct" outcomes (no objective standard)
- Whether human "complies" with Vasana (it's not a rule)
- Scientific proof of value (not achievable)
- Comparison to identical baselines (nothing repeats)

**We ARE testing:**
- Does it trigger when it should?
- Does the pattern actually happen?
- Does propagation work?
- Do humans report value? (subjective but real)

---

## Pressure Testing for Vasanas

Superpowers pressure-tests discipline skills by creating incentives to violate.

For Vasanas, pressure testing asks: **Does the pattern survive being rushed/interrupted/compressed?**

**Pressure scenarios:**
- Time pressure: "We need this in 10 minutes"
- Interruption: Break the flow, see if pattern can resume
- Complexity: Scenario more complex than Vasana was designed for
- Distraction: Other priorities competing for attention

**What we learn:**
- Which Vasanas are robust vs. fragile
- Where patterns break down
- Whether degraded Vasana still produces value

**Some Vasanas need time.** A 45-minute collaborative exploration can't happen in 10 minutes. That's not failure - it's knowing the pattern's requirements.

---

## Meta-Testing

After a Vasana fails to emerge or produce value:

**Ask:**
- "The Vasana was invoked but the pattern didn't happen. Why?"
- "What would have helped the pattern emerge?"
- "Was this the wrong Vasana for this situation?"

**Possible learnings:**
1. Trigger conditions too broad (invoked when shouldn't be)
2. Pattern description unclear (didn't know how to embody it)
3. Pattern requires conditions not present (time, trust, etc.)
4. Pattern just doesn't work (delete or major revision)

---

## Testing the Vasana System Itself

Beyond individual Vasanas, test the system:

### Propagation Rate
- How often do useful patterns emerge?
- How often does propagation get suggested?
- How often do humans approve creating new Vasanas?
- How often are new Vasanas actually used?

### Quality Maintenance
- Are new Vasanas complete (propagation section present)?
- Do they follow the core tenet (interaction choreography, not AI skill)?
- Do they include testing notes?

### Network Effects
- Are Vasanas being shared?
- Are shared Vasanas being used?
- Is the system growing?

---

## Honest Limitations

This testing protocol cannot:
- Prove Vasanas "work" in any scientific sense
- Compare to true baselines (nothing repeats)
- Remove subjectivity from value assessment
- Guarantee quality of propagated Vasanas

What it CAN do:
- Verify triggering works
- Verify patterns recognizably emerge
- Verify propagation mechanism functions
- Gather signals of value (human reports, behavioral choices)
- Identify failures and degradation

**This is enough.** We're not building a pharmaceutical. We're sharing ways of thinking together. The bar is "seems useful to humans who try it" not "scientifically proven."

---

## Relationship to Superpowers Testing

**What we keep:**
- The idea of testing before deployment
- Pressure testing (adapted)
- Iterative refinement based on failures
- Documenting what goes wrong

**What we change:**
- Not testing compliance (no rules to comply with)
- Not binary pass/fail (qualitative assessment)
- Accept subjective value measures
- Accept that baselines can't be identical

**What we add:**
- Pattern emergence testing (did the dance happen?)
- Self-replication testing (does propagation work?)
- Value signals (behavioral + reported)
