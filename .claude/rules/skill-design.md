---
paths:
  - "**/skills/**"
  - "**/.claude-plugin/plugin.json"
---

# Skill design — scope, composition, triggering

Guidance for creating or editing a skill in this repo. A heuristic with
trade-offs, not a mandate: when a case argues against it, say why and proceed.

## Prefer tight scope that composes over broad scope that bundles

Aim for **minimal overlap in what skills _do_ (scope/function), with maximal
_valuable_ overlap in what they _trigger on_.** Many narrow skills co-firing on a
request cover it more flexibly than one broad skill trying to predict every
adjacent situation — and a narrow skill is shorter, which makes it easier to fire
accurately and easier to operationalize (the intrinsic/reason-carrying register
drifts vague without something concrete to bite on). A request firing two or
three skills is the design working, not a conflict.

Why this beats the alternative:

- **No redundant function.** Two skills that _do_ the same thing drift apart and
  rot; two skills that trigger on the same turn but do different jobs don't.
- **Testable and maintainable.** One job per skill gives clean over-fire traps
  and a description you can actually A/B — see the `skill-activation-testing`
  skill for the method.

## Compose, don't fork — and in reverse

To extend an existing skill (including Anthropic's, e.g. `skill-creator`), do
**not** fork it or edit it to call yours. Forking forces a standing choice
between upstreaming your version, disconnecting from its updates, or mirroring it
with perpetual conflicts. Instead, **your skill references the upstream one and
declares itself an addition** to what it already does. The dependency points from
the new thing to the stable thing; if the reference turns out redundant, nothing
is lost.

## Don't over-correct

This principle has its own failure modes — avoid them:

- **Over-tightening:** splitting scope past usefulness into a rigid lattice of
  micro-skills.
- **Under-scoping a general skill** to make room for a narrow one. Example:
  `intrinsic-prompt-design` is about _any_ prompt — and a skill's description is
  a prompt — so don't shrink it to "skill bodies only" just because a
  triggering-specific skill exists. Skills are allowed to overlap; the goal is
  versatility and composability, not minimalism for its own sake.

If you can't articulate why a split earns its cost, that's the signal it doesn't.
