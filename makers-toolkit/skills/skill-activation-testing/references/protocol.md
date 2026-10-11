# Protocol: testing a skill change end to end

**This is the entry point.** If you were sent here to test a skill change, start at step 1.
SKILL.md holds the *why* (the six disciplines). This file holds the *order of operations*.
`scripts/skilltest.py` does the bookkeeping, and `claude plugin eval` runs the live sessions.
Why plugin eval and not another tool: see `landscape-2026-10-09.md`.

Commands below assume the repo root as working directory. `ST` stands for
`python3 makers-toolkit/skills/skill-activation-testing/scripts/skilltest.py`.

## 1. Name the claim, and pick the axis that can test it

| The change claims... | Axis | Arms |
|---|---|---|
| the description fires more / more accurately | **activation** | OLD vs NEW copy of the plugin |
| a rename keeps (or improves) firing | **activation** | OLD vs NEW, with `arm_targets` |
| the body makes the output better once fired | **functional** | with vs without plugin, or OLD vs NEW body |

A description change needs the activation axis. A body change needs the functional axis.
A rename changes the trigger surface, so decide on it **before** you pre-register anything.

## 2. Check the run can answer the question at all

```bash
$ST power --p0 0.6 --cases 8 --runs 5 --icc 0.3   # and again with --icc 0.6
```

`power` prints the smallest difference the planned run could detect, and two settings move it:

- **`--p0`** is the comparison arm's expected rate. Use your best prior, such as a previous
  run's rate.
- **`--icc`** is how alike the repeated runs of one prompt are. It is unknown until measured;
  read both values and plan for the worse.

If the effect you expect is smaller than the printed number, add **cases**. More runs per case
help much less, because repeats of one prompt are correlated.

What a run that is too small does: issue #160's firing test returned "no measured lift".
That result cannot tell "no effect" apart from "too small to see one".

## 3. Write the design: cases as data

Write a `design.json`. `ST validate design.json` is the schema: its error messages name every
field. It enforces three things:

- each case's class;
- each case's **expected winner**: a positive expects the target, a trap names the sibling
  that should win, an off-topic case expects `"none"`;
- that only a control names the skill.

Two warnings from `validate` mean the run cannot discriminate: no oblique cases, or no traps.

Rules `validate` cannot check:

- **Oblique prompts carry the symptom, not the vocabulary.** If a skill's description says
  "A/B", an oblique turn that says "A/B" is a clear turn wearing a label.
- **Each turn is self-contained.** If a turn needs input the skill would first ask for, the
  model asks for it instead of firing, and the case measures nothing. Plugin eval runs each
  case in a fresh sandbox directory, so there is no repo context or deictic leak.
- **Condition is a design choice; name it.**
  - The **ceiling** condition loads only the plugin under test. This is plugin eval's default.
  - The **competitive** condition sets `"plugins": [...]` to the catalog's plugin dirs and runs
    plugin eval from their common parent.
  - Run the ceiling first. If it fails, stop and redesign; the competitive run would mean
    nothing (issue #72).
- **Rename A/B.** Set `"arm_targets": {"OLD": "intrinsic-prompt-design", "NEW": "respect"}`.
  Keep `"target"` as the logical name the `expect` fields use. Write controls as
  `"Use the {target} skill..."`.

## 4. Pre-register: the ship rule goes on disk before any data

Put the decision in the design as `"ship_rule": [[metric, op, number], ...]`. Metric names
are the ones `score` prints. For example:

- `NEW.recall.oblique`
- `NEW.false_fire.trap`
- `diff(NEW-OLD).recall.oblique.ci_lo`
- `diff(W-WO).score.all`

Then write `PREREG-<change>-<date>.md` beside the design. Model it on
`harness-validation/PREREG.md`. It should hold:

- the question;
- what is gated;
- the arms and the model behind every role;
- the conditions that make the run VOID;
- the known limits.

**Commit both before running.** The design's sha256 is stamped into every emitted case and
printed by `score`, so a design edited after the data no longer matches. That mismatch is the
point. This is `.claude/rules/preregister-ship-decision.md`, made mechanical.

## 5. Run it

One run directory per arm. Each holds a copy of the plugin at that arm's revision. Use
`git worktree add <dir> <base-ref>` for OLD, then copy the plugin dir out of it.

```bash
# ceiling: cases live under the plugin, and plugin eval targets the plugin
$ST emit design.json runs/NEW/<plugin>/evals [--arm NEW]    # --arm only with arm_targets
claude plugin eval runs/NEW/<plugin> ...
# competitive: cases live beside the plugins, and plugin eval targets their parent
$ST emit design.json runs/NEW/evals [--arm NEW]
claude plugin eval runs/NEW ...
```

Flags, every time:

- **`--model <the design's model>`.** Without it the results do not record which model ran
  (found in `harness-validation/RESULTS.md`).
- **`--ablation none`** for activation runs. Firing graders count only in that mode, and the
  no-plugin baseline cannot fire the skill anyway.
- **`--json <arm>.json --no-publish --trust-plugin`.**

For a functional run, write the cases directly in plugin eval's own format (`llm` and `regex`
graders) and keep the default `--ablation with-without`. Then score the two arms of that one
file, as in step 6.

## 6. Score

```bash
$ST score design.json --arm OLD=old.json --arm NEW=new.json          # activation A/B
$ST score design.json --arm W=f.json:with --arm WO=f.json:without    # functional, one file
```

The output, by level:

- **Per case:** target-fired k/n with a Wilson interval, and the outcome classes (target,
  expected sibling, other named sibling, other skill, nothing).
- **Per class:** pooled rates, with intervals that resample **cases**.
- **Per arm pair:** the difference and a sign-flip p-value.
- **The verdict:** SHIP, NO-SHIP or VOID.

The exit code is 0, 1 or 3, so CI can gate on it.

**Before reporting any silence as a miss**, re-run a sample of the silent should-fire cases
with `--keep-temp` and read the traces. Silence has three readings: a routing choice, a
session error, or the model asking for input. Only the first is a miss.

## 7. Report: every number with the question it leaves open

Copy the limits the tool prints. Add the condition (ceiling or competitive), the model per
role, and the Claude Code version. Then read the result by the asymmetry in SKILL.md:

- A Tier-1 win can veto nothing and confirm nothing about attention.
- A loss at any tier vetoes.
- A null on the pre-registered rule ships as a null. Don't re-derive it as a weaker success
  from the same runs.

## Functional axis: the rules that don't fit in a grader

The functional axis has no sibling skill yet (issue #74). Until it does, three rules apply
here:

- **Don't assert on anything the skill scripts verbatim.** If the skill says "emit a
  `[RELAY]` tag" and the grader greps for `[RELAY]`, adding the skill guarantees the pass. The
  A/B then measures whether the skill was read, not whether it helped. Grade what the skill
  *causes* (issue #205).
- **Solvability first.** Before a case counts, confirm a strong model passes it when the
  required move is spelled out in the prompt. A case nobody can pass measures nothing. This is
  SkillsBench's oracle, scaled down.
- **Know your judge's noise.** An `llm` grader votes 2 of 3 on one model. Before trusting a
  delta, run the same cases twice, unchanged, and score `R1` against `R2`. The difference
  between two identical arms is your noise floor. A real delta must clear it. Neither plugin
  eval nor any surveyed tool does this for you.

## Lifting this into its own plugin (not done yet)

Everything this methodology needs sits inside this skill directory:

- `SKILL.md`;
- `references/`, including this protocol, the landscape survey and the validation record;
- `scripts/skilltest.py` and its test.

The external dependencies are `python3` and Claude Code >= 2.1.269 for `plugin eval`.
Moving it to its own plugin takes:

1. A new top-level plugin dir with its own `.claude-plugin/plugin.json`, a marketplace entry,
   and version bumps on both plugins.
2. Moving this directory under it, and updating the test path in
   `.github/workflows/unit-tests.yml`.
3. Splitting the functional axis into its own skill, per issue #74's carving. Activation and
   functional testing are two skills that co-fire. At that point the six disciplines move into
   a shared reference both cite, which is the "extract at the second consumer" rule.
4. A firing test of the new plugin's skill descriptions, by this protocol, because a moved
   skill fires in a different catalog.
5. Updating the pointers in `.claude/rules/skill-verification.md` and
   `.claude/rules/skill-design.md`, which name this skill.
