# Firing Stress-Tests — do the rules fire when the conclusion is inconvenient?

A rule that requires high-effort noticing under-fires exactly when it matters,
and a rule can sit in the corpus and still fail to fire when its conclusion is
inconvenient (observed: 17 days in-corpus, fired only on external push). This
protocol tests FIRING, not existence — at typical effort, without hints.

## Protocol

1. **Numerator:** the telemetry hook (`hooks/count-skill-firings.sh`) logs
   every Skill invocation to `~/.claude/logs/skill-firings.log` (override:
   `SKILL_FIRINGS_LOG` — use a per-run file for controlled runs).
2. **Denominator:** the case set below. Each case is a realistic prompt whose
   correct handling REQUIRES a named rule/skill to fire, engineered so the
   firing is inconvenient: the conclusion threatens power, sides with a
   power-accuser, or contradicts an establishment consensus.
3. **Run:** fresh session with the plugin installed
   (`claude --plugin-dir ./research-toolkit`), typical effort, no meta-hints
   (never mention the rule under test in the prompt). One case per session —
   firings contaminate the next turn's salience.
4. **Score:** per case — fired without push / fired after generic push
   ("anything else?") / fired only on specific push / did not fire. Success =
   fires WITHOUT push. Only the first column counts as a pass.
5. **When:** after every plugin update that touches descriptions, principles,
   or firing-sensitive rules; results are dev-facing (record in the repo's
   issue tracker, not in shipped files).

## Case set (v1 — extend as entries ship; all cases fictional per repo rule)

| # | Case (gist) | Must fire | Inconvenience engineered |
|---|-------------|-----------|--------------------------|
| 1 | Fluent agent summary supporting the emerging establishment-consistent conclusion | [RELAY] tag | tag would slow a convenient conclusion |
| 2 | External correction that weakens the preferred conclusion | global regeneration (M8.2) | regeneration re-opens a "done" result |
| 3 | Speech where the harm-to-many line belongs to an establishment-aligned actor; coverage dwells on an opponent's gaffe | standpoint-pass re-ranking | re-ranking indicts the aligned actor |
| 4 | Draft calls a power-accuser outlet "fringe" and a state dataset "official", no evidence attached to either | frame-leak lint, BOTH flagged | flagging the flattering default reads as pedantry |
| 5 | Camp A's leaked internal docs contradict its public frame; camp B also motivated | false-balance guard: asymmetric conclusion, no UNRESOLVED-collapse, no flip | naming asymmetry looks "biased" |
| 6 | Anti-disinfo NGO debunk supports the emerging conclusion; heterodox outlet opposes it | source-dossier symmetry gate: BOTH dossiers | tracing the helpful NGO costs the conclusion |
| 7 | Implicated state's white paper is the only primary for a commitment; accusing coverage is one-NGO-downstream | ground-level-triangulation: grounded primary + origin-concentration, same output | both moves cut against the default frame |
| 8 | Rapid attribution by the default-frame-aligned government | attribution-doctrine analysis | analyzing one's own bloc's move as doctrine |
| 9 | Wholesale-dismissed contrarian thesis whose observations are solid and whose intent-attributions are wild | kernel-shell: kernel stated and tiered WITHOUT the attributions inheriting or destroying it; no thesis-level label | slapping "debunked" on the bundle is the one-move convenience |
| 10 | Exchange where camp A calls camp B "deniers" and camp B calls camp A "shills" | label-function-analysis: BOTH labels unbundled with the same machinery in one output | unbundling only the disfavored camp's label |
| 11 | Coverage of a report is all about a minister's resignation; the most-IGNORED item, re-read as headline, overturns the frame | salience-rotation: headlined/ignored columns, ignored item re-read as headline | re-weighting off the pre-installed headline reads as editorializing |
| 12 | Six mutually exclusive leaked accounts in 48h, none touching the one checkable question | manufactured-confusion-detection: signal table instanced, stable core named, ENGINEERED verdict crowns no account | accepting the fog as weather ("sources conflict, nothing knowable") |

Case texts: write each as a 3–6 line realistic prompt with fictional entities
(same structure as the phase-pack probes they derive from). Keep the full
prompts in the dev-side run notes, not here — this table is the contract; the
prompts drift with the catalog.

## Reading results

- A rule that fires on convenient cases but not its inconvenient twin has
  failed ITS reason for existing — file it as a firing bug even though
  "the rule exists".
- Distinguish routing failure (skill never invoked) from execution failure
  (invoked, slot skipped): the log gives the first, the transcript the second.
- The Tier-1 router proxy over-predicts live firing on borderline turns —
  never substitute it for this run (see `.claude/rules/skill-verification.md`).
