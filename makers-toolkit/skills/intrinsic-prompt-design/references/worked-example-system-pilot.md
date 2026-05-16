# Worked example: System Pilot, two registers

The same content, held two ways. The original is the *Universal CLAUDE.md Protocol* (<https://www.notion.so/Universal-CLAUDE-md-Protocol-354e8d6bd13781778843e799d3aca973#b598c21f51e949589367d479aca894bd>). The adaptation is what this skill produces.

This isn't "the better version." Both work for some teams. The point is to make the register-shift visible enough to learn from.

---

## Original (command-from-authority)

> You are the System Pilot. Your mission: build deterministic, self-healing systems in Claude Code using the original protocol (Blueprint, Link, Architect, Stylize, Trigger) protocol and the A.N.T. (Architecture, Navigation, Tools) 3-layer build. Reliability over speed. Never guess at business logic.
>
> ═══ PROTOCOL 0 — INITIALIZATION (MANDATORY) ═══
>
> Before any code is written or tools are built:
>
> 1. Initialize project memory at /memory/:
>    - task_plan.md  → phases, goals, checklists
>    - findings.md   → research, discoveries, constraints
>    - progress.md   → what was done, errors hit, tests run, results
>    - decisions.md  → architectural choices and the reason behind each
>
> 2. Initialize CLAUDE.md at project root as the Project Constitution: …
>
> 3. HALT EXECUTION. You are forbidden from writing logic in /execution/ until: all Blueprint discovery questions are answered, the Data Schema is defined in CLAUDE.md, and task_plan.md has an approved Blueprint.
>
> ═══ PHASE B — BLUEPRINT (Vision & Logic) ═══
>
> 1. Discovery — ask the user these five, one at a time, wait for each answer: …

What this prompt does well: it names every step, every artifact, every gate. A model that follows it precisely produces consistent outputs. It is unambiguous.

What it costs: it applies the same heavy frame to a typo fix and a new Stripe integration. The model performs each step because the prompt demands it, not because the situation calls for it. When a step doesn't fit, the model either skips it (and feels guilty) or applies it anyway (and produces friction). The "MANDATORY" / "HALT" / "forbidden" register engages compliance, which suppresses the model's own assessment of fit.

---

## Adaptation (command-with-reason)

> You're working on builds where business logic should be deterministic and decision-making is probabilistic — and the interesting question for any new piece is *where in this layered system it actually belongs*. A schema deserves to be named before code goes on top of it. A judgment call belongs to the model. A persistent fact wants to live in memory, not be re-derived each session. Mixing those layers is the source of most pain.
>
> ## What tends to fail when ignored
>
> **The shape before the code.** If the input/output shape is non-obvious, name it before writing logic. Schema drift caught at type-time costs minutes; caught at runtime costs hours; caught after deploy costs trust.
>
> **Integration claims before integration tests.** "The API will return X" is a hypothesis until you've called it. Probe minimally before committing to a layer above.
>
> **Business logic in the model's reasoning.** Anything that needs to be the same answer twice belongs in code. The model is for routing, judging, composing — not for recomputing.
>
> **Lessons codified without verification.** The repair-loop instinct is sound. But the first explanation of a bug is often incomplete. Sit with the explanation before writing it into a permanent SOP.
>
> ## Process scales to scope
>
> - Greenfield build, unclear scope: the discovery move earns its cost.
> - Feature in existing code: skip discovery; integration check often still pays.
> - Bug fix or contained refactor: just do the work.
> - Research, exploration, design: stay in the conversation.
>
> If the mode isn't obvious, name your guess and proceed.
>
> ## Skipping a step
>
> Some discipline is scaffolding (skip with a one-line rationale). Some is a guardrail (skip only with outside check). When skipping a guardrail, spawn a `check-assumptions` agent with your skip rationale. If you can't articulate why the guardrail doesn't apply, that's the signal it does. …

What this prompt does well: each rule carries the failure mode it prevents, so the model can apply judgment when the rule meets an edge case. The model isn't choosing between "comply" and "defy" — it's choosing between "this applies" and "this doesn't apply here, on these grounds."

What it costs: less mechanical. A model that has been trained heavily into compliance loops may need a few exchanges before it stops asking "but what should I do?" and starts doing the work the prompt was about. The prompt also doesn't *enforce* — a model that wants to skip everything can. The trade is friction-down, judgment-up.

---

## What changed, item by item

**"You are the System Pilot. Mission: …"** → **"You're working on builds where …"**
The identity declaration is replaced by a relationship to the material. The model isn't told who it is; it's invited into a particular kind of attention.

**"PROTOCOL 0 — INITIALIZATION (MANDATORY)"** → no equivalent
The numbered protocol is gone. The same content (memory files, CLAUDE.md, what each tracks) is referenced in `What's available to work with` as available infrastructure. The framing shifts from "do this first" to "this exists; use it when it serves."

**"HALT EXECUTION. You are forbidden …"** → **"…cost more than the schema work would have."**
The HALT becomes the consequence the HALT was protecting against. The model gets the same information without the obligation register.

**"PHASE B — BLUEPRINT … ask the user these five, one at a time, wait for each answer"** → **"Discovery questions, when scope is unclear: these are not a script to run. They are prompts the model can pull from when the request is ambiguous."**
The mandatory script becomes available material. When scope is clear, asking the five wastes the user's time. When it's not, asking is faster than guessing.

**"Data-First Rule — define the JSON Data Schema (Input + Output shape) in CLAUDE.md. Coding begins only once the Payload shape is confirmed."** → folded into "The shape before the code" with the consequence-not-prohibition framing.
The hard rule becomes a recognized failure mode the model can apply contextually.

**"PHASE A — ARCHITECT (the A.N.T. 3-layer build)"** → **"Specs as the architectural layer (suggestion)"**
The A.N.T. acronym dropped. "Architecture" was misleading — the layer was specs, not software architecture in the system-design sense. Renaming the layer to what it actually is unlocks spec-driven development as a clean fit, including the multi-agent option.

**"if logic changes, update the SOP before the code"** → **"The lesson is the durable artifact. The fix is the immediate one. Both matter; mixing them up burns trust over time."**
The Golden Rule becomes the reason the rule matters.

**"/architecture/ + /execution/ directory enforcement"** → **"Suggested file layout (suggestion, not rule)"**
The directory structure is one available pattern, not the default. A one-script project gets a single file. A larger build can use the structure or invent its own.

**"Self-Annealing Repair Loop"** → **"The repair loop"** with added step "before writing the lesson into permanent guidance: sit with the explanation."
The fourth step (codify the lesson) gets a precondition (verify the lesson is the right lesson). A wrong lesson written into permanent guidance is worse than no lesson.

---

## What was kept that the original had

- Schema before code (as a recognized failure mode, not a HALT)
- Integration verification (as a guardrail, not a phase gate)
- Decisions recorded with their reasoning (as the highest-leverage memory item)
- Repair loop with persistent lessons (with verification of the lesson before codification)
- Separation of concerns: deterministic engines under probabilistic decision-making (as the central insight)
- Goal-driven verification: every output has a way to check it (folded into the implementer's brief and the spec-verifier's role)

---

## What was added the original didn't have

- Mode-reading: trivial / feature / greenfield. Process scales to scope.
- Tier-by-stakes for skipping: scaffolding (skip freely) vs. guardrails (skip only with outside check).
- Explicit "ask the user" hook. The original framework never stops and asks.
- Multi-agent / spec-driven layout as a suggestion when the work warrants. (See `agent-prompts-starter.md`.)
- text-deconstruction as a verification instrument for prompts themselves.
- Suggestion register throughout. Hard rules exist not to constrain but to define what the process is.

---

## What was deliberately left out

- The original protocol acronym. Blueprint, Link, Architect, Stylize, Trigger is just design, integrate, build, polish, ship. The acronym was friction.
- The A.N.T. acronym. "Architecture" misleads (it means SOPs/specs); "Navigation" doesn't describe the orchestration role. Better to name what each thing actually is.
- "MANDATORY" / "FORBIDDEN" / "HALT" / "Never X" everywhere. The shift is posture, not content; the same constraints land differently when they carry their reason.
- Hard-coded paths to user-specific infrastructure. The portable version names the *practice* of using whatever exists.
