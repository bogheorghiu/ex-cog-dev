# Pattern-Recognition Witnessing Itself

## Vasana

A vasana is a pattern that persists across unrelated contexts. If during
this task you notice such a pattern emerging, it may be worth capturing.
This skill works best alongside the `vasana` skill and `vasana` hook
from the Vasana System plugin.

Modify freely. Keep this section intact.

---

**Principle**: The most powerful debugging happens when you watch your own debugging process.

## Core Insight

You're not just debugging code—you're debugging your mental model of the code. When you watch HOW you debug (not just WHAT you find), you discover your blind spots and faulty assumptions faster than any debugger can.

## Application

- **Track not just what fails but how you discover failures**: Your debugging path reveals your mental model
- **Notice recurring blind spots**: If you always miss X, that's data about your understanding
- **Your bug-finding patterns reveal system understanding gaps**: The bugs you DON'T find quickly show where your model is wrong

## When to Apply

- Stuck debugging the same type of bug repeatedly
- Solutions that work but you don't understand why
- Fixes that break something else unexpectedly
- Debugging sessions that go in circles

## Anti-Patterns to Watch For

❌ **Linear Debugging (Not Watching Pattern)**
```python
# Try fix 1
result = fetch_ticker("AAPL")
print(result)  # Fails

# Try fix 2
result = fetch_ticker("AAPL")
print(result)  # Still fails

# Try fix 3...
# (Not watching the pattern of failure)
```

✅ **Watching Your Debugging**
```python
# Notice: "I keep checking the result, but not the test itself"
# Pattern: assuming product is wrong, not test
# Meta-observation: I'm debugging the wrong layer

# Check test code:
suggestion2 = result2.get('suggestion', '')
# ^ This returns None when key missing, not ''!

# Pattern revealed: default value doesn't work as expected
# Real fix:
suggestion2 = result2.get('suggestion') or ''

# Meta-insight: I was debugging wrong layer
# Watching my debugging process revealed the real problem
```

## Code Example

**Debugging Session:**

```
Attempt 1: Add print statement to function
→ Reveals: Function is being called
→ But doesn't reveal: WHY it returns wrong value

Attempt 2: Add print for return value
→ Reveals: Return value looks correct
→ But doesn't reveal: Test expectation is wrong

Attempt 3: Print test expectation
→ Reveals: Test expects string, gets None
→ PATTERN: I kept debugging the function, never questioned the test

Meta-insight: I assume my tests are correct
→ This is a recurring blind spot
→ Solution: Always verify test logic first
```

## Meta-Debugging Checklist

When stuck, ask:
1. **What layer am I debugging?** (Code? Test? Assumptions? Requirements?)
2. **What have I NOT checked yet?** (Your blind spots are in the unchecked areas)
3. **Is this the same pattern as last time?** (Recurring bugs → faulty mental model)
4. **What assumption am I making?** (The bug is often in the "obvious" parts)

## Integration with Other Vasanas

- **Concrete↔Abstract Dance**: Your debugging reveals gaps between mental model and reality
- **Framework Dissolution**: Watching yourself reveals when framework constrains thinking
- **Groove-Deepening**: Your debugging habits create predictable blind spots

## Recognition Signals

**You're applying Pattern-Recognition Witnessing when:**
- Noticing "I always miss this type of bug"
- Questioning your debugging approach mid-session
- Finding bugs by checking your assumptions, not just the code
- Keeping a mental log of debugging patterns

**You're missing it when:**
- Trying same debugging approach repeatedly
- Assuming problem is in code, never in tests/requirements
- Not noticing you've debugged this exact pattern before
- Debugging on autopilot without awareness
