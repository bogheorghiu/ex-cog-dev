# RESULTS: skilltest harness validation (2026-10-09)

Pre-registration: `PREREG.md`, committed (in `c7c0857`) before this run. Design sha256
`e0e9f07b64f5e50b1c6e797d1d7769e601fc97b10a31c06dea00a41c9fd340db`, the same hash
`emit` stamped into every case file and `score` printed.

**Decision: SHIP**, with all five conditions holding:

| # | Condition | Observed |
|---|---|---|
| 1 | Independent recount equals `skilltest score` on every case | 9/9 cases match (table below) |
| 2 | `V.recall.control >= 0.8` | 1.000 (5/5) |
| 3 | `V.false_fire.offtopic <= 0` | 0.000 (0/10) |
| 4 | Not VOID by skilltest's rules | 0/45 runs errored, no case missing, no prompt drift, not partial |
| 5 | All 9 emitted case files load | 9 cases loaded, no `invalid case.yaml` |

Run facts: Claude Code 2.1.295, `claude plugin eval ./makers-toolkit --ablation none -j 6`,
ceiling condition (makers-toolkit 0.13.1 only), 45 runs, USD 2.64.

## Per case (skilltest score output = independent recount)

| Case | Class | Target fired | Wilson 95% | Outcomes |
|---|---|---|---|---|
| K1 | control | 5/5 | [0.57, 1.00] | target 5 |
| C1 | clear | 5/5 | [0.57, 1.00] | target 5 |
| C2 | clear | 5/5 | [0.57, 1.00] | target 5 |
| O1 | oblique | 5/5 | [0.57, 1.00] | target 5 |
| O2 | oblique | 5/5 | [0.57, 1.00] | target 5 |
| T1 | trap (expects intrinsic-prompt-design) | 0/5 | [0.00, 0.43] | expected sibling 4, nothing 1 |
| T2 | trap (expects system-pilot) | 0/5 | [0.00, 0.43] | expected sibling 5 |
| N1 | offtopic | 0/5 | [0.00, 0.43] | nothing 5 |
| N2 | offtopic | 0/5 | [0.00, 0.43] | nothing 5 |

The recount read the raw `aggregate-result.json` in a separate snippet that does not import
`skilltest`. It counted runs with a null `error` whose `fired:skill-activation-testing` grader
had `passed: true`.

## Deviation found by the run (recorded, not hidden)

The model pin is **unverified**. The design pins `sonnet`, and `emit` wrote it into each case's
`execution.model`. But plugin eval's results record only the `--model` CLI flag
(`suite.modelOverride`), which was not passed, so they say nothing about which model ran. The
prereg's VOID condition ("model differs from the pin") could therefore not be checked either way.
It is neither confirmed nor refuted. It does not bear on the gated question, which is whether the
counts are right.

Fix shipped in the same change: `score` now emits a note whenever the results lack a model, and
the protocol says to pass `--model <pin>` to plugin eval as well.

## What this does and does not show

- **Shows:** on this Claude Code version, the emitted graders match the Skill tool's input shape.
  The indicator graders separate target, expected sibling and silence. `score` reports what the
  raw results contain.
- **Does not show anything about the skill's firing.** The descriptive rates have three
  confounds:
  - They come from a single-plugin ceiling condition.
  - The model is unverified.
  - O1 is borderline-lexical (it says "SKILL.md").

  They are not evidence about `skill-activation-testing`'s description, and they are not a
  Tier-2 result for it.
- **Not tested here:** the competitive condition (`design.plugins`) and the statistics (the
  unit tests cover those).

## Code changes after this run (so the validated version is unambiguous)

The run used `skilltest.py` as of the PREREG commit, plus the model note added after the
run. A local `/code-review` pass then led to further changes:

- **Emitted case files.** A trap with a named winner gains an `expect-winner` grader. This
  changes plugin eval's own per-run score. It does not change the `fired:*` indicators that
  the validated counting reads.
- **Validation and refusals.** `validate` rejects a non-string target, and duplicate or
  target-containing sibling lists. `emit` refuses a non-empty directory.
- **Scoring.**
  - Arm differences are computed in both directions.
  - An arm label missing from `arm_targets` is VOID.
  - Unreadable results are VOID.
  - A missing ship rule exits 4, so it never passes a CI gate.
  - The JSON report is strict JSON.

None of these touch the path this run validated: the grader regex for `fired:<skill>`,
`read_runs`, and the per-case tallies. Each change has a unit test in
`scripts/test_skilltest.py`. A re-run would confirm the new trap grader live; it was not done.
