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

**The instrument is pending.** A sibling session is building the skill-testing
methodology and will post its entry point on issue #250. Until then the
candidate instrument is this repo's planted-defect critic battery:
`.claude/workflows/author-planted-defect-artifacts.js`, then
`match-critiques.js`, then `lib/critic-score.mjs`. It was first used in
`probes/prompt-skill-critics/`. The choice between the two is recorded in this
file, with its reason, **before** any arm runs. A choice made after seeing data
voids the run.

## Arms (one variable)

- **A0**: `SKILL.md` as on `main` at `56332e5`.
- **A1**: `SKILL.md` as on this branch.

Both arms get the same model, the same harness and the same task text. The skill
body is injected identically into both: the actor is told to apply the skill, so
it is not auto-routed to it. Nothing differs except the body text.

**Known limit, accepted now.** A1 bundles items 1 and 2, so a delta cannot be
split between them. If E1 is null, separate arms are a new design with a new
prereg. They are not a re-slice of this run.

## Battery (frozen before any arm runs)

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
- **E4 (exploratory, no ship weight)**: recall on M-loud, and whether the revised
  prompts mark their own registers.

All rates are pooled over artifacts × reps. Uncertainty is reported as a 95%
bootstrap CI resampled over artifacts, not over reps.

## Ship rule

**A1 ships iff** all three hold:

- E1(A1) − E1(A0) ≥ 0.15 absolute, AND the CI on that difference excludes 0;
- E2(A1) ≤ E2(A0) + 0.05;
- E3(A1) ≥ E3(A0) − 0.05.

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

(None yet. Any deviation decided after launch is written here, with its reason,
before scoring.)
