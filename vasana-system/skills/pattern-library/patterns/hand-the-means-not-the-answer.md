---
name: hand-the-means-not-the-answer
status: formulation-in-progress (evidence settled; name & general statement are not — see Formulation status)
description: In any capability transfer — an instruction, a tool, a product, a delegation — what travels decides where agency sits afterward. Transfer only a terminal product (an answer, a bare directive, a verdict) and judgment stays at the source; the receiver complies or consumes and returns for every new case. Transfer the generator (the reason behind the rule, the means of producing answers, the machinery itself) and the receiver can handle cases the source never anticipated. NAME PROVISIONAL — formulation in progress. Other phrasings that should find this entry: "command = enclosure, reason = commons"; "justification travels with the directive"; generator vs output; means of cognition; rules that carry their why.
---

# Hand the Means, Not the Answer

## Vasana

A vasana is a pattern that persists across unrelated contexts. If during
this task you notice such a pattern emerging, it may be worth capturing.
This skill works best alongside the `vasana` skill and `vasana` hook
from the Vasana System plugin.

Modify freely. Keep this section intact.

---

## What This Pattern Is

When capability passes from one party to another, **what travels decides
where agency sits afterward.** Hand over only an *output* — a single
answer, a bare directive, a verdict — and the capacity to judge stays at
the source: the receiver can comply or consume, and must come back for
every case the output didn't cover. Hand over the *generator* — the reason
behind the rule, the means of producing answers, the machinery itself —
and the receiver can handle cases the source never anticipated. Agency
concentrates or distributes according to which one crossed the boundary.

**Origin:** Logged as "candidate vasana A" in the intrinsic-motivation
analysis (2026-06-06) under the too-narrow name *"whether the
justification travels with the directive decides where agency sits."*
Confirmed by the owner 2026-06-12 with a correction that is itself
instructive: the prompt-scale name hid the fact that the *economic* form
was a second occurrence all along — the recurrence bar was met before the
engineering case ever arrived. Generalized and recorded accordingly.

---

## Formulation status — IN PROGRESS (owner ruling, 2026-06-12)

**What is settled:** the vasana is real. Occurrences 1 and 2 stand in
unrelated domains; the recurrence bar is met. This is *not* a
lacking-examples draft.

**What is not settled: the formulation.** Both names tried so far borrow
one occurrence's native vocabulary and fail to cover the other:

- *"Justification travels with the directive"* (first try) — names only
  the prompt-scale form; hid occurrence 2 for six days.
- *"Hand the means, not the answer"* (current, provisional) — names only
  the economic-scale form. Defects, per the owner: (a) at title level it
  reads too much like `scaffold-vs-crutch` (empowering-vs-not aid),
  though the mechanisms differ; (b) **a command without its why isn't an
  "answer" at all** — it's a demand. In the economic case the receiver
  *wants* the terminal product; in the prompt case it's imposed. The
  means/answer dyad therefore doesn't generalize across the two
  occurrences that establish the pattern.

**What a finished formulation must do:** state the shared mechanism in
vocabulary native to *neither* occurrence; cover both the wanted-product
case (rented answer) and the imposed-product case (bare command) as the
same move (the reasoning/machinery stays at the source, only its terminal
product crosses); and be distinguishable from `scaffold-vs-crutch` in the
statement itself, not only in a kin note. Candidate direction left open,
not decided: something on the axis of *what stays behind* (the generator
retained at the source) rather than *what is given*. Per
emergence-over-enforcement: don't force the name; let further use
surface it.

---

## Recognizing When This Applies

**Conditions:**
- Writing rules, prompts, skills, CLAUDE.mds — does each directive carry
  its why, so the executor can judge the edge case the author didn't
  foresee? (The prompt-scale practice is `intrinsic-prompt-design`.)
- Designing tools and products — does this hand the user the means to
  re-derive and adapt, or rent them a verdict they must keep returning
  for?
- Evaluating institutions, platforms, services — one-answer search vs a
  list of sources you pick through is this fork at industrial scale.
- Delegating — does the delegate get the goal and its reasons, or only
  the steps?

**Not this pattern:**
- One-shot transfers with no ongoing relationship — answering a question
  is fine; the fork matters when cases are open-ended.
- Deliberate concentration — a safety interlock or a hard block can be
  *correctly* reason-free at the point of enforcement (the reason lives in
  the docs, not the gate). The pattern's demand is knowing you chose
  concentration, not never choosing it.

---

## Cross-Domain Verification

**Mechanism check:** genuine shared structure — a generator (a function)
can be evaluated at new inputs by whoever holds it; outputs are
evaluations at inputs already seen. Dependence, control, and adaptability
follow mathematically from which of the two crossed the boundary. Not a
vocabulary resemblance.

**Occurrences (the two that establish recurrence — unrelated domains):**
1. **Instruction design.** A rule carrying its reason lets the executor
   judge unanticipated cases; a bare command produces compliance that
   breaks at the first novel one. (intrinsic-prompt-design; the repo's
   "state the why" Rule 1.)
2. **Political economy of cognition.** Enclosure rents you the answer —
   one-answer search, machinery owned out of sight; commons hands you the
   means — tools you drive. The manifesto's "they hand you the means, not
   the answer" is this pattern as a design bar.

**Supporting, contested (recorded honestly, not load-bearing):**
3. wikipediai Phase 1 (SDD×TDD): a spec whose docstrings carried their
   *Why* let two context-isolated agents (tests leg, implementation leg)
   interlock 90/90 green on first integration. Weaker as evidence — still
   engineering, still AI, near occurrence 1 — and a rival reading exists
   (interface *precision* did the coordinating; the reasons were
   decorative). Discriminator on record: re-run with a Why-stripped spec;
   if the legs still interlock, the rival reading wins. **Unrun.**

**Planned measurement:** the command-register vs reason-register A/B
against the viral Karpathy CLAUDE.md (ex-cog-dev issue #123) is the
prompt-scale form put to an experiment, including the frontier-vs-floor
twist (do reasons close part of the capability gap?).

**Kin in this library:** `scaffold-vs-crutch` — same family, different
axis: that one tracks whether *internal capacity* is trained or atrophies
over time; this one tracks where *agency* sits structurally the moment the
transfer happens. They compose: an answer-only transfer, habitual, becomes
a crutch. Held distinct.

---

## What Makes It Work

1. **The generator is what generalizes** — reasons, means, machinery all
   share the property that the holder can produce new outputs; that
   property, not generosity, is what redistributes agency.
2. **Scale-invariance** — the same fork is visible in one sentence of a
   prompt and in the structure of a search market; checking at one scale
   trains the eye for the other.
3. **Honest accounting of exceptions** — enforcement points may stay
   reason-free by design; the pattern survives because it demands the
   choice be deliberate, not because it forbids concentration.

---

## Testing This Pattern

Before relying on this:
1. **Baseline:** Write a ruleset / hand off a task with bare directives.
2. **With pattern:** Write another where each directive carries its why.
3. **Compare:** At the first genuinely novel edge case, which executor
   did the right thing without coming back?
4. **Pressure:** Does it work when rushed?

**Honest note:** the controlled test exists as a design (issue #123's
~20-task battery with divergence cases) but is unrun — n=0 on measurement.
The wikipediai discriminator (Why-stripped re-run) is likewise unrun; the
entry's recurrence claim rests deliberately on occurrences 1 and 2, not
on the engineering case.
