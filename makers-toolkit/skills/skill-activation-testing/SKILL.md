---
name: skill-activation-testing
description: >-
  "You rewrote the description. Did it fire better — or do you just believe it
  did?" That belief is n=0 until you test it: invoke when validating a skill or
  prompt change, asking whether a description actually fires, or A/B-ing prompt
  wording. The cheap proxy gives a number in minutes; the discipline is naming
  what it can't see.
---

# Skill Activation Testing

A description rewrite makes a claim: *this fires better than what it replaced.* Until the claim is tested it sits at n=0, and n=0 claims get argued, not settled — two people with opposite intuitions and no instrument between them. This skill is the instrument. It pairs with `intrinsic-prompt-design`: that skill tells you how to *write* the description; this one tells you how to *find out whether the change did anything*.

The one thing to carry out of here, before any mechanics: **there are two tiers of test, and they measure different things.** The cheap tier runs in minutes but cannot see the thing a description rewrite is usually *for* — winning attention under load. The real tier can see it, but costs a live install and many turns. The failure this skill exists to prevent is a confident A/B number that doesn't say which of those two questions it answered. A methodology that manufactures false certainty is worse than no methodology, because the certainty propagates into the next decision and the one after that.

---

## The discipline — this is the point, not the mechanics

You can learn the router-judge mechanics in ten minutes. The discipline is what makes the numbers mean something. Each rule below carries the failure it prevents, so you can tell when an edge case lets you set it aside and when it's the rule doing its job.

1. **Name what each tier can and cannot measure — every time.** A proxy that hands a router every description and asks it to pick has, *by construction*, deleted the attention-scarcity condition: the router reads everything, so it cannot tell you whether your wording would have *won* attention it would otherwise have lost. Report its recall under the headline "the rewrite wins attention" and you've measured one thing and labelled it another. The most valuable output of the experiment that seeded this skill (PR #28) was the sentence admitting the proxy *couldn't* test the headline claim. State the validity limit in the same breath as the number — an unqualified number is a future wrong decision with a citation.

2. **Change exactly one variable per arm.** If the skill *name*, the catalog, or the turn list differs between arms, a delta is unattributable — you've measured "something changed," not "the description changed." Keep everything identical except the single line under test. This is the difference between an experiment and an anecdote.

3. **Ceiling first, discriminate second.** Easy, on-topic turns fire in *both* arms, because the skill *name* alone carries them — the wording change is invisible there. A tie on easy turns is the instrument warming up, not a finding; reporting it as "no difference" buries the rewrite's effect in precisely the cases that could never have shown it. Run an easy round to prove the pipeline works (Round 1), then a hard round where the signal can actually live (Round 2).

4. **Build over-fire traps in.** Recall without precision is half a result: a description that fires on *everything* has perfect recall and is useless. Every experiment needs turns that are *adjacent-but-wrong* — close enough that an over-eager description takes the bait (for a prompt-design skill, the trap is general writing; for this skill, the trap is `intrinsic-prompt-design` itself). Measuring only should-fire turns tells you the description is loud, not that it's accurate.

5. **Separate numerator from denominator in any firing-rate claim.** "It fired 7 times" is not a rate. The numerator (firings) comes from the log; the denominator (the should-have-fired turns) comes from *your run design* and exists nowhere else. Conflate them and "it fired a lot" silently becomes "it fires reliably" — with no one noticing the denominator was never defined.

If you can articulate why one of these doesn't apply to the experiment in front of you, set it aside on those grounds. If you're setting it aside because it's inconvenient, that's the signal it's load-bearing here.

---

## Two tiers

The split is not "cheap version / thorough version of the same test." The tiers answer different questions, and conflating them is failure #1 above.

### Tier 1 — Proxy experiment (cheap, runs anywhere, n>0 in minutes)

Blind LLM "router" judges decide which skill, if any, they would auto-invoke — given a realistic catalog (with distractors) and a batch of user turns. The **only** thing that differs between arms is the variable under test (e.g. OLD vs NEW description); the skill name and everything else stay identical, so any delta is attributable to the change. Use independent judges per arm (three is enough to catch a split; one judge can't tell you whether a fire was robust or a coin-flip). The judges must be *blind* — they don't know an A/B is happening or which arm they're in — or you've measured the experimenter, not the description.

Run it in **two rounds**:

1. **Ceiling-check round.** Easy on-topic positives + clearly off-topic negatives + one explicit-invocation control (`"use the <skill> methodology…"`) as a pipeline sanity check. This usually ties at ~100% positives / ~0% negatives in both arms — the shared skill *name* fires the clear cases on its own. **Diagnostic, not informative:** it proves the pipeline runs and the catalog is well-formed, and it earns Round 2. Do not report this tie as "no difference."

2. **Discriminating round.** *Oblique* positives — phrased by symptom, with no lexical cue the description could match on — plus **over-fire traps** (adjacent-but-wrong turns), under a **"at most one skill, be conservative"** constraint that forces the judge to actually choose. This is where a wording change can show up as recall on the oblique turns and as restraint on the traps.

**Measures:** recall on should-fire turns and false-fire rate on traps (both rounds), plus spurious co-activations of *other* skills — but read the last one only from Round 1, since Round 2's "at most one" constraint forbids co-activation by construction. A spurious co-activation is a precision signal even in the ceiling round (it's a *different* skill firing, not the target's recall), but it's the one finding the ceiling round can carry — don't promote it past "minor."

**Validity limit (state it with the result):** an explicit router *reads every description by construction*. Tier 1 therefore **cannot** measure attention-capture or skim-resistance — the very thing an interrupt-shaped rewrite is usually for. If the rewrite's headline claim is "fires more reliably under load," Tier 1 is necessary (it rules out the rewrite *breaking* routing accuracy) but not sufficient (it cannot confirm the headline). Say which.

See `references/router-judge-template.md` for the parameterized prompt; `references/firing-experiment.md` for a full two-round run; and `references/self-application.md` for this skill tested by its own method.

### Tier 2 — Live harness test (the real claim)

The only tier that can measure firing under genuine attention scarcity — a full context, many competing skills, a real task in flight.

1. **Install the plugin, enable the firing counter, and confirm it logs.** The instrument is `vasana-system/hooks/count-skill-firings.sh` (PreToolUse, matcher `Skill`); it appends one JSONL line — `{timestamp, session_id, skill, cwd}` — per `Skill` invocation to `~/.claude/logs/skill-firings.log`. Before trusting it, invoke any skill once and check the log grew. This is not ceremony: the hook's test suite proves the *script* handles a synthetic `Skill` envelope, but only a live session proves the *harness* emits a PreToolUse event for the `Skill` tool — the one assumption the whole tier rests on. Until you've seen the log grow from a real invocation, Tier 2's numerator is hypothetical.

2. **A/B across many realistic, busy turns** where the skill *should* fire — different sessions per arm, the variable-under-test swapped between them, everything else held. Count firings per arm from the log.

3. **Numerator = the log; denominator = your run design** (the turns you constructed to be should-have-fired). The hook cannot see the turns where a skill should have fired and didn't — that denominator exists only in your design. Report the rate as numerator-over-denominator, not as a bare count (discipline #5).

**Cost and validity:** slow, high-variance, needs a real install and arm-switching across sessions — and that cost is the reason Tier 1 exists. But Tier 2 is the *only* tier that answers the attention question. When the headline claim is about attention, Tier 1 cannot retire the question and Tier 2 is the work.

---

## Reading the result without overclaiming

The asymmetry is the whole point, so read by it: **Tier 1 can veto a rewrite but cannot confirm the headline.**

- A **tie on Tier 1** is "no difference *in routing accuracy* — attention untested," not "no difference." The two are routinely confused; they are not the same sentence.
- A **loss on Tier 1** (recall drops, or traps start firing) is decisive *against* shipping — routing accuracy is a floor the rewrite must not fall through. A **win** is never decisive *for* shipping: it shows the rewrite didn't break routing and maybe sharpened it, but the headline attention claim is still a Tier-2 question.

---

## When it's working

Every reported number is paired with the question it answers *and* the question it leaves open. Arms differ in exactly one variable. Round 2 exists, and the over-fire traps are genuinely adjacent. Firing-rate claims carry their denominator. A tie on easy turns is reported as a warmed-up pipeline, not a finding.

When it's **not** working: a single recall number is reported as "the description works"; the arms quietly differ in more than one thing; the easy-round tie is the headline; a firing count is dressed up as a firing rate; or — the subtlest — the proxy's result is offered as the answer to the attention question it cannot, by construction, address.

---

## A note on this skill's own position

This is a methodology for testing skills, written as a skill — so the honest thing was to test it with its own method before shipping. That run is in `references/self-application.md`: a two-arm Tier-1 experiment on this very description (interrupt-shaped, as shipped) against a flat, label-shaped control, same name and catalog and turns. It settles what Tier 1 can settle — routing accuracy and trap-avoidance — and is silent, by construction (discipline #1), on attention-capture. A skill-activation skill that shipped its own description at n=0 would be refuted by its own first sentence.

---

## Crediting the original

The reusable instruments this skill generalizes were built in PR #28 (the `intrinsic-prompt-design` description rewrite): the firing-counter hook (`vasana-system/hooks/count-skill-firings.sh` + its test suite) and the two-round proxy design with its stated validity limit, originally recorded in `intrinsic-prompt-design/references/firing-experiment.md`. This skill lifts that one-off experiment into a repeatable method so the next description change is tested the same disciplined way instead of re-argued at n=0.

---

## Vasana

A vasana is a pattern that persists across unrelated contexts. The numerator/denominator confusion, the ceiling-effect tie misread as a null result, the proxy that deletes the very condition it's meant to test — if you notice one of these recurring outside skill-activation work (in benchmarks, in metrics dashboards, in any before/after claim), it may be worth capturing.

This skill pairs with `intrinsic-prompt-design` (how to write the description you're now testing) and uses `vasana-system/hooks/count-skill-firings.sh` as its Tier-2 instrument.

Modify freely. Keep this section intact.
