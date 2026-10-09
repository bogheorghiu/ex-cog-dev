# PREREG: does the skilltest harness count firings correctly? (2026-10-09)

**FROZEN** at the commit that adds this file. `design.json` beside it is final;
any edit to it after this commit voids the run (`skilltest score` prints the
design's sha256, and the results file must carry the same hash).

Written and committed before any run of this design returned data.

## What is gated

Shipping `scripts/skilltest.py` as the harness that `skill-activation-testing`
points consumers to. Nothing about the skill's own wording is gated: it is the
**specimen**, not the subject. The clear, oblique and trap rates below are
reported descriptively and carry no ship weight.

## The question

When a design goes through `validate`, then `emit`, then `claude plugin eval`,
then `score`, does the score report the firings that actually happened?

## Arms and inputs

- One arm, labelled `V`. The condition is the **ceiling**: only `makers-toolkit`
  is loaded (plugin eval's default catalog). The instrument is Tier 2 (live).
- `design.json`: 9 cases (1 control, 2 clear, 2 oblique, 2 traps, 2 off-topic),
  5 runs each, so 45 runs.
- Session model: `sonnet`, pinned in the design. This is cheaper than the
  deployment model. That is acceptable here only because the skill's firing is
  not what is being measured. **Scoring:** `skilltest score`, deterministic, with
  no judge model. **Design and interpretation:** the session that wrote this file.
- O1 shares the word "skill" (as in "SKILL.md") with the target's name. It is
  borderline-lexical and is left in as-is. It carries no ship weight.

## Ship rule

The harness ships iff **all** of the following hold:

1. **Independent recount matches.** For every case, `skilltest score`'s
   target-fired count equals a recount taken straight from the raw
   `aggregate-result.json`. The recount counts runs with a null `error` whose
   grader named `fired:skill-activation-testing` has `passed: true`, using a
   separate snippet that does not import `skilltest`. Any mismatch is
   **NO-SHIP**.
2. `V.recall.control >= 0.8`. The instrument can see a firing that was asked
   for. (This is in `design.json`'s `ship_rule`.)
3. `V.false_fire.offtopic <= 0`. The instrument does not invent firings. (This
   is also in `ship_rule`.)
4. The run is not VOID by `skilltest`'s own rules: more than 10% of runs
   errored, a case is missing, the prompt drifted from the design, the model
   differs from the pin, or the run is partial.
5. plugin eval loads all 9 emitted case files without an `invalid case.yaml`
   error.

If 2 or 3 fails while 1 holds, the counter is right and the **wiring** is
wrong: for example, the grader regex does not match the Skill input shape.
Either way it does not ship on this evidence. It goes back to design, and a new
prereg is written.

## Known limits (stated now so a pass isn't oversold)

- A pass shows the bookkeeping is right on one Claude Code version (the one
  recorded in the results). The `aggregate-result.json` schema is versioned
  (`schemaVersion: 1`), but a field rename upstream would break `read_runs`.
- It does not validate the competitive condition, where several plugins are
  loaded via `design.plugins`. That path was checked once by hand on
  2026-10-09, with one run on haiku: plugin eval loaded both plugins when run
  from their common parent. That check is not part of this gate.
- It does not validate the statistics. Those are covered by the unit tests in
  `scripts/test_skilltest.py`.
