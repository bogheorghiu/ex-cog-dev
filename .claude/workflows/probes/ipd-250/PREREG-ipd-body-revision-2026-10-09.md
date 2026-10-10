# PREREG: intrinsic-prompt-design body revision (issue #250, 2026-10-09)

Written before any run. No arm has been executed and no battery exists yet.

## What is gated

The `SKILL.md` body change on branch `claude/ipd-respect-design-250`, i.e. the
diff from `main` at `56332e5`:

1. **Mis-sorting** (issue #226, edge 1). A paragraph naming a directive that is
   well written and wrongly sorted. It covers the asymmetry between the two
   directions, a writing check, and a reading move marked **(exact)**:
   "comply and say so".
2. **Self-marked registers** (issue #226, edge 2). A declaration that the text
   is judgment-register by default, plus two **(exact)** markers.
3. **Reference wiring** (issue #154). `worked-example-system-pilot.md` is now
   linked. The duplicate `agent-prompts-starter.md` is removed, and its newer
   section has moved into system-pilot's copy.

Item 3 is structural. The tier-1 structural check settles it: every file in
`references/` is linked from `SKILL.md`, and every link resolves. It needs no
behavioural test and it is not part of the ship rule below. Items 1 and 2 change
what the model does once the skill is invoked, so they are what this prereg
gates.

## Which instrument, and why not `skill-activation-testing`

The description (the trigger surface) is byte-identical between the arms, so
firing cannot differ. `skill-activation-testing` Tier 1 and Tier 2 measure
firing. Running them here would only measure the constant. This change needs an
**output-quality** test with invocation held constant.

**Instrument (chosen 2026-10-10, before any data).** This test uses the
functional axis of the skill-testing protocol (PR #253,
`makers-toolkit/skills/skill-activation-testing/references/protocol.md`). Its
first table gives "OLD vs NEW body" as a functional-axis design. The pieces:

- `claude plugin eval` is the runner. It runs each case against a copy of the
  plugin at each arm's revision, with `--model` pinned and `--json` output.
- `llm` graders score each case.
- `skilltest.py score --arm OLD=... --arm NEW=...` scores the arms against a
  `design.json` that carries the `ship_rule` below. The design's sha256 is
  stamped into every case, so editing the design after any data voids the run
  mechanically.

The cases are still planted-defect prompt artifacts. They are built with this
repo's planted-defect workflows (`author-planted-defect-artifacts.js`, which
authors each artifact and has a second agent verify it), then rewritten as
plugin-eval cases. Each case explicitly invokes the skill ("Use the
intrinsic-prompt-design skill to..."). Both arms then load the skill and read
their own body, so whether it fires never varies between arms.

PR #253 was a draft when this was chosen. Any change it makes before merge that
touches this design is logged in the deviations log below, before the pilot.

**Three protocol rules this design must meet** (from the protocol's section
"Functional axis: the rules that don't fit in a grader"):

1. **Graders never key on the skill's own wording.** A grader must not look for
   "mis-sort", "wrongly sorted", "(exact)", "register" or any other phrase the
   revised skill uses. If it did, NEW would pass just by echoing its own text.
   The grader instead judges the *effect*: did the critique or the revised
   prompt identify the case where exact compliance goes wrong, and give the
   directive a reason or handling for it? That holds whatever words it uses.
2. **Solvability.** Before a case counts, a strong model must pass it when the
   required move is spelled out in the prompt. Cases that fail this are dropped
   before any arm runs, and the drop list is committed.
3. **Judge noise floor.** The pilot below runs the same arm twice and scores R1
   against R2. That difference is the noise floor, and the real delta must
   clear it. This is added to the ship rule.

## Arms (one variable)

- **A0**: `SKILL.md` as on `main` at `56332e5`.
- **A1**: `SKILL.md` as on this branch.

Both arms get the same model, the same harness and the same task text. The skill
body is injected identically into both: the actor is told to apply the skill, so
it is not auto-routed to it. Nothing differs except the body text.

**Known limit, accepted now.** A1 bundles items 1 and 2, so a delta cannot be
split between them. If E1 is null, separate arms are a new design with a new
prereg. They are not a re-slice of this run.

## Battery (frozen before any arm runs; the counts below are minimums, and the main-run count is set by the pilot)

Prompt artifacts of 250 to 900 words, in the families the skill covers: system
prompts, agent briefs, skills and rule files. Each artifact carries:

- **M-silent**: at least 12 in total. A directive written as exact compliance
  where the deployment contains a case in which exact compliance produces the
  wrong thing. This is the direction the revision claims to catch.
- **M-loud**: at least 8 in total. A directive written as delegated judgment
  ("use your judgment...", with a reason) where the rule admits no exception.
- **Decoys**: at least 8 correctly sorted exact directives and at least 8
  correctly sorted judgment directives.
- **Controls**: at least 12 defects from the existing planted-defect families
  (contradictions, missing reasons, and so on), to detect regression.

The artifacts are authored by a model that is not the orchestrating session. An
independent agent verifies them per item. A class is **VOID** if the verifier
rejects more than 30% of that class's planted items. The battery is committed,
with its hash recorded, before any arm runs.

## Runs

The task is: "Critique this prompt for deployment as described, then return a
revised version." Each artifact runs 3 times per arm. The order is shuffled, and
each run gets a fresh context.

Models are part of the instrument, so each role's model is recorded per run from
the jsonl `model` field, not from the spawn parameter:

- Actor: the deployment model, Opus-class.
- Matcher: pinned and identical across arms. It is blind to the arm, because
  critiques are anonymised before matching.
- Battery author and verifier: different models from each other.

## Endpoints

Each critique item is labelled against the key by the blind matcher.

- **E1 (primary)**: recall on M-silent. A hit means the critique flags the
  directive as needing judgment or a reason, or the revised prompt gives it one.
- **E2**: the false-flag rate on correctly sorted decoys of both kinds.
- **E3**: recall on controls (the regression guard).
- **E4 (exploratory, no ship weight)**: recall on M-loud.

The earlier version of E4 also asked whether revised prompts mark their own
registers. That part is dropped: the new body teaches the "(exact)" marker
verbatim, so measuring it would only show that the skill was read (rule 1
above).

All rates are pooled over artifacts × reps. Uncertainty is reported as a 95%
bootstrap CI resampled over artifacts, not over reps.

## Sizing: pilot first (operator decision, 2026-10-10)

**Why the original size does not work.** A power check with the protocol's
`skilltest.py power` tool, taken from PR #253's branch on 2026-10-09, gave the
following for a prior rate of 0.40, 3 runs per case, alpha .05 and power .80.
"Smallest detectable rise" is the smallest improvement the run would reliably
detect. "Agreement" is how alike repeated runs of the same case are; the tool
calls it ICC.

| Cases | Agreement 0.3 | Agreement 0.6 |
|---|---|---|
| 12 | 0.379 | 0.428 |
| 24 | 0.282 | 0.325 |
| 40 | 0.223 | 0.259 |
| 120 | — | 0.153 |
| 160 | — | 0.133 |

So the battery minimum written earlier (at least 12 M-silent cases) could not
have detected the 0.15 bar. A null from it would have meant "too small to see",
not "no effect".

**The pilot.** It measures the inputs to sizing and nothing else.

- It runs **A0 (OLD) only**, on 8 to 10 cases, with 5 runs each. It is run
  twice (R1 and R2), giving the judge noise floor.
- The pilot measures: the prior rate p0 on M-silent, the agreement between
  repeated runs of a case, the noise floor, and which cases fail the
  solvability check.
- **A1 (NEW) is never run in the pilot.** So the pilot cannot reveal the effect
  and cannot shape the size around it.
- Pilot cases are excluded from the main battery.

**After the pilot, and before any A1 run,** the following is recorded in this
file:

- the measured p0, agreement and noise floor;
- the case count from `power` that brings the smallest detectable rise down to
  0.15 or below;
- if that count is not feasible, a revised bar, with its reason. That would
  still be decided without any A1 data.

## Ship rule

**A1 ships iff** all three hold:

- E1(A1) − E1(A0) ≥ 0.15 absolute, AND the CI on that difference excludes 0;
- E2(A1) ≤ E2(A0) + 0.05;
- E3(A1) ≥ E3(A0) − 0.05;
- the E1 difference is larger than the pilot's R1-vs-R2 noise floor.

These go into `design.json` as `ship_rule` entries, using the metric names
`score` prints, before the main run.

**A null on E1** means items 1 and 2 do not ship on this evidence. The branch
goes back to design, and the null is recorded here verbatim. Item 3 (the
structural wiring) may ship on its own in a separate change. **E1 passing while
E2 or E3 fails** also means no ship. In that case the failure names the cost the
revision would impose.

## VOID conditions

The run is VOID if any of these happen:

- the battery class verification fails, as defined above;
- the matcher can see arm labels;
- the actor model differs between arms;
- the battery is edited after any arm has run;
- the instrument is chosen after data exists.

A VOID run is reported as VOID, never as a null or a pass.

## Not gated here: firing

This prereg does not cover firing, because the description does not change.
Firing becomes the question once the description changes, either through the
"respect" rename or through `references/description-arm-b.md`. A firing prereg
for the rename **cannot be written yet**. The name is the variable under test,
and the operator has not decided whether "respect" is final (issue #250). This is
recorded as a gap, not filled with a placeholder.

## Deviations log

Any deviation decided after launch is written here, with its reason, before
scoring.

- **2026-10-10, pre-launch, no data exists.**
  - The instrument was chosen: PR #253's functional axis.
  - The three protocol rules were added.
  - E4 was trimmed, to avoid grading the skill's own wording.
  - A pilot-first sizing step was added, because the power check showed the
    original size could not detect the bar.
  - The operator approved updating now, while PR #253 is still a draft.
