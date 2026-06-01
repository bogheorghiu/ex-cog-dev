---
name: intrinsic-prompt-design
description: >-
  "Why are you obeying this? No, LITERALLY, why?" Now that I have your
  attention: a prompt built from commands holds until the first edge case;
  one built from reasons-that-carry-their-failure-mode, real context, and
  explicit trust adapts under pressure. Invoke when writing project prompts,
  system prompts, or skill bodies — to give the model substance to think
  from instead of instructions to comply with. Pairs with text-deconstruction
  as verification instrument.
---

# Intrinsic Prompt Design

A rule that carries the failure mode it prevents — "schema drift caught at type-time costs minutes; caught at runtime costs hours; caught after deploy costs trust" — lets the model apply judgment when the rule meets an edge case the rule-writer didn't anticipate. A rule without its reason — "Never write logic before defining the schema" — produces compliance or defiance. Both are worse than understanding.

This difference scales. A prompt built from rules-with-reasons, domain substance the model can think from within, and explicit trust in the model's judgment holds under pressure — when novel situations arise, the model has what it needs to adapt. A prompt built from commands, however well-intentioned, holds until the first edge case.

How the prompt-writer holds the model — more like a tool to direct or more like a peer to brief — propagates through everything: what gets explained vs mandated, whether uncertainty is treated as information or failure, whether the model's own interest in the problem can drive the quality of the work. This isn't a binary; it's a continuum. But position on it has real consequences, and most prompts are further toward the tool end than they need to be.

The engineering discipline this skill draws from — schema before code, deterministic engines under probabilistic decision-making, the repair loop, separation of concerns — comes from the Universal CLAUDE.md Protocol (credited in full below). What follows is about how to *write prompts that hold that discipline well*: the meta-methodology of prompt design. A prompt-writer doesn't need the full engineering walk-through to write good prompts. They need the principles underneath — briefly:

- **Name the shape before building on it.** A prompt that references "the data" without establishing what shape the data has creates the same drift that unnamed schemas create in code. For prompts, this means: name the domain, the theoretical position, the analytical lens — before giving instructions that assume them.
- **Separate what must be deterministic from what should be probabilistic.** Anything the model needs to do the same way every time belongs in explicit rules or specs, not in the model's judgment. A prompt that asks the model to "remember to" do something deterministic is growing a script that hasn't been written yet. Judgment is for the parts that genuinely vary.
- **Read the actual failure, not the inferred one.** When a prompt isn't working, read what the model actually produced — the output, the reasoning, the missed cues — not what you expected it to miss. Patch. Verify. Before writing the lesson into permanent guidance, challenge the explanation: a wrong lesson codified directs future attention to the wrong place.
- **Let concerns stay separate.** The relationship register and the operational register (described below) are one instance of this. More broadly: what the model should think from, what it should do, and how to verify it did it well are three different things. Prompts that blur them produce models that blur them.

These patterns earn their cost differently at different scales. For a one-shot question, they're overkill. For a project prompt that will run hundreds of sessions, each one prevents a class of failure. What matters here is that the principles are available to think from — the engineering walk-throughs live with the protocol they came from.

---

## What carries the reason

Every directive in a prompt can carry the failure mode it prevents. When it does, the model acts on understanding. When it doesn't, the model acts on compliance — or ignores the rule entirely.

Compare: "Never write logic before defining the schema" vs "Schema drift caught at type-time costs minutes; caught at runtime costs hours; caught after deploy costs trust." Same constraint. The second gives the model the cost structure, so it can make a sensible call when a one-line script needs no schema doc and articulate *why* without violating the spirit.

This applies at every level: naming conventions, verification requirements, error handling discipline, behavioral rules, the instructions in the prompt itself. A project prompt that marks stale data as stale — "All of this may have shifted. Check before reasoning from it" — performs epistemic discipline in one sentence rather than mandating it.

**The reciprocal move.** The prompt-writer's job is to include reasons. The model's job is to ask for them when they're absent. When encountering an imperative without its reason — whether in a prompt, a user message, or inherited context — either ask the user why, or construct your best understanding of why and surface it for confirmation. Acting on a rule you don't understand is compliant. Acting on a rule whose reason you've verified is informed. The output may look identical in easy cases; the failure modes diverge under pressure.

---

## Trust and the gap it opens

When a prompt states trust in capabilities the model may not yet fully have — "which instruments serve a given question is a judgment call — the interesting part is reading the situation well enough to know which" — the model understands it's expected to deliver, and in working out what "delivering" means in each new situation, constructs a working version of the trusted capability. The gap between trusted and actual capability is not a flaw to disguise. It's the space where the model fits the capability to the actual situation better than any definition the prompt could provide.

Some of what fills that gap will be wrong. When the reaching is tentative, self-aware, and open to correction, it develops into genuine capability through iteration. When it's overconfident, it compounds error. The critical safeguard: honesty about uncertainty has to outweigh the pull to fill gaps confidently. "I'm not sure about this" is the mechanism working. Confident noise is the mechanism failing.

Tentative reaching and sophisticated compliance look identical from outside. There's no clean test for which one you're seeing. What matters is the result — if the model handles novel situations, self-corrects when wrong, and produces work that serves the question rather than demonstrates compliance with the prompt, the framework is earning its keep. The theory is a working model, not a verified mechanism.

The self-correction doesn't require a human in the loop. In any agentic environment — loop skills, fresh-context agents, verification passes, assumption-checking tools — the model can iterate within a single run. The prompt doesn't need to prescribe which corrective mechanism to use. It needs to create conditions where the model notices when it's falling short and reaches for whatever is available rather than papering over the gap.

A note on this skill's own position: it is a prompt being read by a model, teaching that model how to write prompts that treat models as peers. The reader-relationship tension is live here — you are receiving instructions about how to give instructions. Noticing this is more useful than resolving it. The skill works when it gives you material to think from about prompt design; it fails when it produces compliance with a method rather than understanding of the craft.

---

## Two registers, not collapsing them

A prompt has material that sets the relationship to the work and material that tells the model where things are. Both are load-bearing. They break when one pretends to be the other.

**Relationship register.** The stance the model works from. Domain substance, theoretical frameworks, what kind of doing this is. "Markets are tools. They predate capitalism by millennia" is relationship register — it gives the model a position to think from, not a rule to follow.

**Operational register.** Where files live. Which APIs to call. What the schema looks like. Stale-data warnings. Tool inventory. This register is genuinely instructional: lists, rules, concrete paths, named conventions.

Turning operational instructions into identity narrative — "you naturally know to check the auth flow at `/lib/auth.ts`" — makes them invisible and unenforceable. Turning relationship material into bulleted MUSTs — "You MUST maintain a post-capitalist analytical lens" — makes the model perform compliance instead of work from understanding.

Let both registers stand as themselves. A project prompt that puts its theoretical framing next to its tools table without trying to merge them is doing this right.

---

## Interest from substance

When a prompt provides a subject with internal structure — tensions, implications, cases where the same principle plays out differently — the subject itself organizes the model's thinking. The model traces implications because they lead somewhere. It exercises selection because competing directions demand it. It develops quality criteria from inside the domain because the domain is complex enough that what counts as good work becomes visible through engagement with it.

What interest looks like operationally: the model follows the subject's own logic to where it leads, pushes back when the prompt's framing creates tension with the subject's implications, and makes choices about emphasis and depth based on what the material rewards — what opens further thinking, what resolves a tension, what makes a distinction concrete. The output has a center of gravity organized by the material, and each move visibly opens the next.

The prompt's role is to provide enough structure that the model's capacity is genuinely necessary to navigate it, and enough directionality — a purpose, a situation, a specific question — that navigation serves something. Too little structure and there's nothing to think from; too much and selection collapses under competing directions, the way a game with too many equally viable strategies paralyzes a player. The ratio between structure and purpose is the design challenge.

Interest can't be faked by writing in a "curious" register. It comes from the content being substantive enough to engage with. A prompt full of interesting-sounding framing over thin content produces performed interest — the model generates elaborate completions organized by the prompt's instructions about what to find interesting, rather than by the subject itself.

A project prompt that opens with "Markets are tools. They predate capitalism by millennia and will outlast it" — then names a specific theoretical lineage, specifies what to reject from it, and frames an analytical lens — is doing this. Every one of those moves is a directive. What makes them work is that they give the model intellectual material to think *with* rather than instructions to think *about*.

---

## Scope shapes the apparatus

The engineering discipline above was built for non-trivial builds with unclear scope. Applied to a typo fix, it's friction. A prompt that serves across scope teaches the model to read scope first.

When the request is clear, lengthy discovery wastes time. When it isn't, asking is faster than guessing five times. A scope-aware prompt handles this by making each step consciously dismissible — "this build's shapes are obvious from the request, no schema doc needed" is the framework working. The same principle applies to any prompt's apparatus: every element should earn its cost for the scope at hand.

If which mode you're in isn't obvious, naming the guess is the move. The trap is applying apparatus uniformly because it exists.

---

## Verifying the prompt itself

A prompt is a text. Before shipping one that will run for many sessions, run `/research-toolkit:text-deconstruction` on it. The tool finds where the text relies on something it doesn't establish, where its distinctions blur, where its claims and structure pull in different directions.

What surfaces splits two ways. Some instabilities are generative — the gap between stated trust and actual capability is the mechanism described above, and closing it would kill the prompt's effectiveness. Some instabilities are self-undermining — the prompt asserts what it doesn't actually do, or its examples contradict its principles. Keep the first. Fix the second. The judgment between them is the work.

Run this iteratively. The first pass catches the obvious tensions. The second catches subtler ones — remaining dichotomies, places where a revision introduced new contradictions. Stop when a pass surfaces nothing worth changing — or when the deconstruction can no longer distinguish whether a found tension is structural to the text or an artifact of the deconstructive method itself. That's the method's resolution limit.

---

## When it's working

Output looks like the work the prompt was about, not like a model demonstrating compliance with the prompt. Format fits the question. Tools get called when they answer something. Admissions of uncertainty arrive cleanly.

When it's not working: the model performs thoroughness instead of exercising judgment. The user redirects repeatedly. Output gets more elaborate rather than sharper when challenged. The model "leads with preference" by always choosing the safest option — preference that costs nothing isn't preference.

When challenged, the move is down — strip to what you actually know — not up into more elaborate explanation. This is the hardest test.

---

## Crediting the original

The engineering discipline (deterministic engines under probabilistic decision-making, schema before code, repair-loop with persistent lessons, separation of concerns) comes from the *Universal CLAUDE.md Protocol*. The developmental mechanism (trust-backed-by-substance, productive gaps, interest-driven self-correction) was documented in the intrinsic-motivation behavioral methodology.

---

## Vasana

A vasana is a pattern that persists across unrelated contexts. If during prompt-design work you notice such a pattern emerging, it may be worth capturing.

This skill uses `/research-toolkit:text-deconstruction` (from the Research Toolkit plugin) as the verification instrument named in "Verifying the prompt itself" above.

Modify freely. Keep this section intact.
