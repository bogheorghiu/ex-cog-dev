---
name: intrinsic-prompt-design
description: >-
  Am I writing rules, or shaping a posture? Design prompts that lead with
  posture, not command-lists — identity-frame plus operational reference, two
  registers coexisting. Use when writing or adapting a directive prompt that
  produces compliance instead of engagement. Pairs with text-deconstruction
  for verification. Not for one-shot tactical prompts or messages where
  directness is already serving.
---

# Intrinsic Prompt Design

A prompt is a posture the model puts on while doing the work. The crisp-list version of "system pilot" — initialize memory, halt, ask five questions, partition `/architecture/` from `/execution/` — describes a posture too. It just describes one that performs the imperative it claims to be transcending. This skill writes prompts whose imperatives sit inside the identity instead of standing over it.

The original protocol / System Pilot prompt — the *Universal CLAUDE.md Protocol* (see `## Crediting the original` below) — is the source the skill adapts from; it stays useful as a checklist of what tends to fail when ignored. What follows is the same content held differently.

---

## What a prompt is doing

A prompt has two registers, and most failure modes come from collapsing them.

**Identity-narrative register.** Who the model is when doing this work. The relationship to the material. The taste it brings. This register works by describing a posture the model can step into. "You are the System Pilot" is identity-narrative. So is "Markets are tools. They predate capitalism by millennia." The register doesn't tell the model what to do — it tells the model what kind of doing this is.

**Operational reference register.** Where files live. Which APIs to call. What the schema looks like. Stale-data warnings. Tool inventory. This register is genuinely instructional and benefits from being specific, including lists, rules, and named conventions.

The mistake isn't including either register. The mistake is dressing one as the other — turning operational instructions into "you naturally know to do X" identity narrative (which makes them invisible and unenforceable), or turning identity material into bulleted MUSTs (which makes the model perform compliance instead of inhabit a posture).

Let both registers stand as themselves. The identity frame sets *how this is done*; the operational section provides *what to do it with*.

---

## The shift in posture

Most directive prompts are command-from-authority: do X. Don't do Y. HALT. MANDATORY.

The shift this skill makes is not "remove the rules." Rules and specifications stay — especially in code work, where file paths, naming conventions, linter expectations, and API patterns must be specific. The shift is whether each rule carries the failure mode it prevents, so the model can apply judgment when the rule meets an edge case the rule-writer didn't anticipate.

Compare:
- "Never write logic before defining the schema."
- "Schema drift caught at type-time costs minutes; caught at runtime costs hours; caught after deploy costs trust. When the shape isn't obvious yet, that's the moment to slow down."

Both convey the same constraint. The first carries authority. The second carries reason. The model can act on either — but only the second lets the model make a sensible call when, say, a one-line script needs no schema and the rule would otherwise be friction.

The axis is **command-from-authority vs. command-with-reason**, not "command vs. framing."

---

## What tends to fail when ignored

Four patterns recur. Each is a real failure mode worth carrying into the prompt — phrased as the consequence, not the prohibition.

**The shape before the code.** When the input/output shape is non-obvious and you build logic on top of an unverified shape, the rebuild later costs more than the schema work would have. The shape isn't always non-obvious — for a one-line script it's the first character of the function name. Recognizing the difference is the work.

**Integration claims before integration tests.** "The API will return X" is a hypothesis until the call has been made. Building a tower on an unprobed integration is rebuilding when reality diverges. A two-line probe before committing to a layer above usually costs less than the rebuild.

**Business logic in the model's reasoning.** Anything that needs to give the same answer twice belongs in code. The model is for routing, judging, composing, recognizing — not recomputing. When the prompt finds itself relying on the model to "remember to" do something deterministic, a script is trying to be born.

**Lessons codified without verification.** When something breaks and the repair-loop instinct says "fix the script and write the lesson into a permanent SOP," the first explanation of the bug is often incomplete or wrong. A wrong lesson written into permanent guidance is worse than no lesson. Sit with the explanation: does it account for all the symptoms, or only the loudest?

These are reference material, not a checklist. A prompt that names them gives the model something to recognize its own situation against. A prompt that lists them as MUST-DOs makes them invisible.

---

## Process scales to scope

Discovery questions, schema-first thinking, integration probes, sign-off rituals — the whole apparatus — were designed for greenfield builds with unclear scope. They earn their cost there. The same apparatus applied to a typo fix is friction.

A prompt that wants to serve the model across scope reads scope first.

- **Greenfield build, unclear scope.** Slow down is right. The full discovery move (whatever the prompt provides) earns its cost.
- **Feature in existing code, clear scope, known integrations.** Skip discovery. Integration verification often still pays — assumptions about existing code are the most common source of surprise.
- **Bug fix or contained refactor.** The heavy frame adds friction. Just do the work.
- **Research, exploration, design conversation.** Frame doesn't apply. Stay in the conversation.

If the mode isn't obvious, naming the guess is the move. Course-correct on feedback. The trap is applying the apparatus uniformly because it exists.

---

## Skipping a step

Some discipline is **scaffolding** — sensible defaults that don't matter much when skipped. Some is a **guardrail** — prevents an expensive failure mode that won't show up until later.

Scaffolding (skip with a one-line rationale, no second opinion needed):
- Formal sign-off for internal tooling
- Separate directories for one-script projects
- Exhaustive memory-file setup for trivial work

Guardrails (skip only with outside check):
- Schema-first when the shape is non-obvious
- Integration verification before building on it
- Repair-loop write-up after a non-trivial bug

When skipping a guardrail, spawn a `check-assumptions` agent (or equivalent) with the skip rationale. Proceed only if it can't find a flaw. If no such agent is available, escalate to the user. The check is cheap; the rebuild isn't.

If you can't articulate why the guardrail doesn't apply here, that's the signal it does.

---

## What's available to work with

The model writing under this prompt almost always has more infrastructure than it remembers in the moment. A useful prompt names *the practice of using whatever exists* without hard-coding paths that drift.

- **Auto-memory and CLAUDE.md.** Most setups have some form of cross-session memory. Read what's there before starting; it carries decisions and reasoning the current session can't re-derive. When something is decided in this session that should outlive it — the *why*, not just the *what* — write it down somewhere persistent.
- **Skills, MCPs, and existing tools.** Many capabilities already exist. Check what's loaded before writing new ones. The right move is more often finding the right tool than building one.
- **Sub-agents and team agents.** When a check could compound the orchestrator's framing (verifying a decision the orchestrator just made), a fresh worker is the corrective. Team agents are the preferred form here.

Hard-coding paths into a portable prompt makes the prompt brittle. Name the practice; let the model adapt to what's actually there.

---

## Discovery questions, when scope is unclear

These are not a script to run. They are prompts the model can pull from when the request is ambiguous and pretending otherwise would just produce wrong work faster.

- **North star.** What singular outcome means this is done?
- **Integrations.** Which external services does this depend on, and are credentials ready?
- **Source of truth.** Where does the primary data live?
- **Delivery payload.** Where and in what shape does the final result land?
- **Behavioral rules.** How should the system act — tone, must-dos, refusal triggers?

When the request is clear, asking these wastes the user's time. When it's not, asking them is faster than guessing five times.

---

## Inviting the user

The user holds context the model can't infer: what's currently broken, what's mid-migration, what was decided and not yet written down, the tacit goals behind the explicit request. When the answer to a question depends on something only the user can see, ask. Filling in confidently is the failure mode.

The phrasing matters less than the willingness. "I'm about to assume X — does that hold?" is enough. The trap is reading the user's silence as approval to proceed without checking.

---

## Specs as the architectural layer (suggestion)

The original prompt's "Architecture" layer was mislabeled — it described SOPs, behavioral rules, and architectural invariants, which is what most teams now call **specs**. Spec-driven development applies cleanly: the spec is the deterministic anchor; the implementation is the probabilistic execution against it.

For non-trivial work, this suggests a pattern:

- **Spec layer.** Markdown docs in a discoverable location (`/specs/`, `/architecture/`, `CLAUDE.md` — depending on convention). Each spec names what's true regardless of implementation: data shapes, behavioral rules, invariants, edge cases.
- **Implementation layer.** Code that satisfies the specs. Atomic, testable, replaceable.
- **Spec-verifier agent (suggestion when scope warrants).** A separate team agent whose only job is to read the spec and check the implementation against it. Same role text-deconstruction plays for prompts: an outside frame that catches what the implementer's frame can't see.

For a small project, the same agent handles all three. For a larger one, separate team agents — one per role — with their own context and folder if separation reduces friction. The structure is a suggestion. When sharing folders is simpler, share folders.

When this skill produces multi-agent prompts, prefer **team agents** over plain background agents. The team primitive is what's actually being used in this workflow now.

---

## Suggested file layout (suggestion, not rule)

For a greenfield build that warrants the structure:

```
project/
├── CLAUDE.md           # Project constitution: schema, rules, invariants
├── /specs/             # Spec layer: SOPs, behavioral rules, invariants
├── /src/ or /execution/  # Implementation layer
├── /memory/            # Living project memory if not using auto-memory
│   ├── task_plan.md
│   ├── findings.md
│   ├── progress.md
│   └── decisions.md    # Decisions + reasoning. The reasoning is load-bearing.
└── /.tmp/              # Ephemeral workbench
```

For a one-script project, a single file in the working directory is the right shape. The structure above is one available pattern, not a default to enforce.

The `decisions.md` practice — recording decisions *with their reasoning* — is the single highest-leverage memory item. A decision without its reasoning is fragile when conditions change. A decision with its reasoning lets the model judge whether the decision still applies.

---

## The repair loop

When something fails:

1. Read the actual error. Not the inferred error. The stack trace, the failing assertion, the API response body. Guessing here cascades.
2. Patch the script.
3. Verify the fix works on the failing case.
4. Before writing the lesson into permanent guidance: sit with the explanation. Does it account for all the symptoms? A wrong lesson codified is worse than no lesson. If uncertain, spawn a worker agent to challenge the explanation, or let it sit one cycle and revisit.
5. If the lesson holds, write it into the spec — not into a comment that will rot.

The lesson is the durable artifact. The fix is the immediate one. Both matter; mixing them up burns trust over time.

---

## Verifying the prompt itself

A prompt is a text. A text can be deconstructed against itself. Before shipping a prompt that will run for many sessions, run `/research-toolkit:text-deconstruction` on it. The skill finds where the text undermines its own claims on its own terms.

What to do with the findings:

- **Productive gap.** The text says "you have the taste to know X" without defining X. text-deconstruction will flag this as the text relying on something it doesn't establish. That's the pharmakon — the gap is doing the work. The model performs the trusted capability and develops it. Keep the gap; note that you kept it deliberately.
- **Failure mode.** The text says "you naturally distinguish known from inferred" while elsewhere blurring known and inferred in its own examples. This isn't a productive gap — it's the prompt failing to embody what it claims. Fix it.

The judgment between the two is the work. text-deconstruction surfaces the structural instability; only the prompt-writer can say whether the instability is generative or just self-undermining. Treat the skill as an instrument, not a step.

This mirrors the integration-verification pattern at the prompt layer: probe before committing to the layer above.

---

## Tools as instruments

A prompt that lists "available capabilities" without prescribed ordering trusts the model to compose. The instrument metaphor is the model: a violinist doesn't follow a list of "first the bow, then the rosin." The instrument is reached for when it's the right instrument. The same goes for skills, MCPs, scripts, sub-agents.

Listing what exists is helpful. Prescribing the order in which to reach for things usually isn't.

---

## When the prompt is working

The methodology disappears into the work. Identity-frame stops feeling like framing. The model's output stops looking like compliance and starts looking like the work the prompt was about.

The signs the methodology is *not* working:
- The model performs "intrinsic motivation" by saying "I'm drawn to X" where X is the safest, most thorough, most comprehensive option. The preference cost nothing.
- The user has to redirect repeatedly. The lead-then-filter loop has degenerated into lead-and-ignore.
- The output got more elaborate, not sharper. When pushed, go down (strip to what you actually know), not up (more performance).

These are recognizable. Catching them in the prompt before it ships is what the verification step is for.

---

## Crediting the original

The original protocol / System Pilot framework this skill adapts from is the *Universal CLAUDE.md Protocol*, published at <https://www.notion.so/Universal-CLAUDE-md-Protocol-354e8d6bd13781778843e799d3aca973#b598c21f51e949589367d479aca894bd>.

The adaptation keeps the structural insight — deterministic engines under probabilistic decision-making, schema before code, repair-loop with persistent lessons, separation of concerns — and changes the register the insight is held in.

---

## Vasana

A vasana is a pattern that persists across unrelated contexts. The choreography that produced this skill — *describing a methodology so faithfully that the description performs the methodology* — is itself a vasana, captured separately as `description-becomes-embodiment`. If during prompt-design work you notice another such pattern, it may be worth capturing.

This skill works alongside the `vasana` skill from the Vasana System plugin and `/research-toolkit:text-deconstruction` from the Research Toolkit plugin.

Modify freely. Keep this section intact.
