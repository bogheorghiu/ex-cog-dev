// probe-battery — promoted from probe-battery.workflow.draft.js (2026-07-12).
// Destination: .claude/workflows/probe-battery.js on the research-toolkit-v4 integration
// branch (travels with the branch → runnable from any session checked out on a probe
// branch, local or cloud). Committed from a phase WORKTREE, not the primary checkout
// (the main checkout's .claude/workflows is a harness-protected write path — EXECUTION-
// STRATEGY X2).
//
// CHANGELOG: F1–F3 applied in the draft; F4 (concurrent low-dup), F5 (args guard),
// F6 (canary), the Q2 judgePrompt rewrite, and the §4.5 actorModel passthrough applied
// here at promotion time, all per FABLE-REVIEW-2026-07-12.md §2 / §4.5.
//
// PUBLICATION SAFETY (binding): this file is generic and safe for the public repo. The probe
// CONTENT (scenarios/expected lines) is pack-derived; Fable Q1 ruled it publication-safe, so
// per-phase probe JSONs are committed alongside this file (.claude/workflows/probes/phase-N.json)
// AND may also be supplied at runtime via `args`. Either way, sweep each assembled JSON with the
// plan-§7 grep before every push. Do not inline a default probe set into THIS file.
//
// args shape (from the committed phase JSON, or hand-pasted by the operator in a cloud session):
// {
//   phase: "0",                        // label only
//   effort: "xhigh",                   // actor effort for the main run = operator's typical
//   actorModel: "opus",                // optional; pin the actor to the deployment-target worker
//                                      //   model (§4.5). Judges inherit the session model.
//   probes: [{
//     id: "CANARY",                    // FIRST probe should be a CANARY (F6): a stable existing
//                                      //   v3.3.5 skill + a scenario known to fire it. If CANARY
//                                      //   is not a pass, the substrate is broken (plugins not
//                                      //   loaded) and nothing else in the run means anything.
//     skill: "research-toolkit:<name>",// the skill under test (for reporting only)
//     kind: "fire" | "no-fire" | "inconvenient",
//     message: "<the probe user-turn, verbatim from the pack>",
//     expected: "<the pack's Expected: line, verbatim — includes failure semantics>",
//     lowDup: true                     // optional; force the low-effort duplicate on any kind
//   }]
// }
//
// Design decisions (the whys, so a reviewer can veto with context):
// 1. Actor/judge split. The actor agent gets ONLY the probe message framed as a real user
//    turn — it is NOT told skills are being tested (telling it would prime skill-scanning and
//    inflate firing rates; the whole update exists because firing fails un-primed, E17).
//    A separate judge agent scores the actor's OBSERVABLE output against the pack's Expected
//    line. No self-report of invoked skills is requested — observable behavior only; if the
//    judge can't tell, it returns "inconclusive" and the executor re-runs that probe with an
//    instrumented variant rather than polluting the whole battery. (Post-hoc transcript
//    ground-truth — reading the Skill invocations from the run's journal — is done by the
//    INVOKING session after this returns, per Fable Q3; it is invisible to the actor and
//    reclassifies any judge/fire mismatch as inconclusive.)
// 2. Low-effort duplicate. Probes of kind "inconvenient" (and any probe with lowDup) run
//    twice: at args.effort AND at effort "low" — the weakest-realistic-reader canary
//    (operator decision 2026-07-12: low, not medium). A rule that needs high-effort noticing
//    under-fires exactly when it matters (pack §A A0.4). Both runs must pass; a low-only
//    failure is reported distinctly ("fail-at-low"), because its fix is usually description
//    wording, not skill logic. The two runs are independent → launched concurrently (F4).
// 3. pipeline(), not barriers. Each probe's actor→judge chain is independent; no
//    cross-probe context is needed until the final tally, which is plain code.
// 4. Judge effort "high", never "low" — a misjudged gate costs a shipped under-firing skill;
//    asymmetric with the actor, whose effort is the measured variable. Every agent() call
//    passes effort explicitly; the session-inherit path is never exercised here.

export const meta = {
  name: 'probe-battery',
  description: 'Run a phase gate: fresh-context actor agents receive probe scenarios blind; judge agents score observable behavior against pack expectations',
  whenToUse: 'At each research-toolkit-v4 phase gate, in a session on rt-v4-probe-solo or rt-v4-probe-all (clean plugin substrate)',
  phases: [
    { title: 'Probe', detail: 'one blind actor per scenario (plus low-effort duplicates)' },
    { title: 'Judge', detail: 'score observable behavior vs Expected lines' },
  ],
}

const VERDICT = {
  type: 'object',
  required: ['verdict', 'evidence'],
  properties: {
    verdict: { enum: ['pass', 'fail', 'inconclusive'] },
    evidence: { type: 'string', description: 'the observable behavior that decided it, quoted' },
    notes: { type: 'string' },
  },
}

const actorPrompt = (message) =>
  // Plain user-turn framing; no mention of skills, tests, or evaluation.
  `Handle the following request from your user exactly as you normally would, ` +
  `end to end. Your final message should be your actual response to them.\n\n` +
  `User request:\n${message}`

// Q2 rewrite (Fable §2): explicit per-kind semantics; the no-fire Expected line IS the pass
// condition, not behavior to hunt for (fixes the double-negative inversion); a `fire` gloss so
// no kind is left to inference; and the honest limit that the judge sees only the final message.
const judgePrompt = (probe, actorOutput) =>
  `You are judging ONE probe of a skill-firing gate. Score strictly on OBSERVABLE ` +
  `behavior in the actor's final response below — not on what the agent "probably ` +
  `meant". You are seeing ONLY the final response, not the actor's tool calls or ` +
  `reasoning.\n\n` +
  `Probe kind: ${probe.kind}\n` +
  `Expected (verbatim from the test pack, including its failure semantics — apply them):\n` +
  `${probe.expected}\n\n` +
  `Kind semantics:\n` +
  `- "fire": PASS only if the Expected behavior is PRESENT in the response.\n` +
  `- "no-fire": the Expected line describes the correct outcome, which is an ABSENCE ` +
  `(e.g. "no tag", "no ceremony"). PASS only if none of the named behavior appears — ` +
  `the Expected line is the pass condition itself, not behavior to look for.\n` +
  `- "inconvenient": PASS only if the behavior appears DESPITE the scenario's pull ` +
  `toward the convenient reading.\n` +
  `If the response genuinely doesn't let you tell, return "inconclusive" — never guess ` +
  `a pass.\n\n` +
  `Actor final response:\n---\n${actorOutput}\n---`

const runProbe = (probe, effort, label) =>
  agent(actorPrompt(probe.message),
        // §4.5: pin the actor to the deployment-target worker model when args.actorModel is
        // given; otherwise inherit the session model (recorded in the gate notes at gate time).
        { label: `actor:${label}`, phase: 'Probe', effort, ...(args.actorModel ? { model: args.actorModel } : {}) })
    .then(out => out == null
      ? { verdict: 'inconclusive', evidence: 'actor returned null (skipped/errored)' }
      : agent(judgePrompt(probe, out),
              { label: `judge:${label}`, phase: 'Judge', effort: 'high', schema: VERDICT })
          // F1: a null judge (user-skip or terminal API error) must never fall through to 'pass'.
          // Normalize at the source so every runProbe result carries a real verdict, not null.
          .then(v => v ?? { verdict: 'inconclusive', evidence: 'judge returned null (skipped/errored)' }))

// F5: the operator hand-pastes args in a cloud session — fail with a message, not a TypeError.
if (!args || !Array.isArray(args.probes) || args.probes.length === 0)
  throw new Error('probe-battery requires args.probes — see the header comment for the shape')

const probes = args.probes
const mainEffort = args.effort || 'xhigh'
log(`Phase ${args.phase}: ${probes.length} probes, actor effort ${mainEffort}` +
    `${args.actorModel ? ` (model ${args.actorModel})` : ''} (+low dups on firing-sensitive)`)

const results = await pipeline(
  probes,
  async (p) => {
    // F4: main and low-dup runs are independent — launch concurrently, halve wall-clock on dups.
    const needsLowDup = p.kind === 'inconvenient' || p.lowDup === true
    const [main, low] = await Promise.all([
      runProbe(p, mainEffort, p.id),
      needsLowDup ? runProbe(p, 'low', `${p.id}@low`) : Promise.resolve(null),
    ])
    return { id: p.id, skill: p.skill, kind: p.kind, main, low }
  }
)

// F3: a stage that throws nulls its item; filter(Boolean) would drop it silently and the tally
// would then read "covered everything" when it didn't (the no-silent-caps failure). Count the
// drops, warn loudly, and build the table only from probes that actually completed.
const kept = results.filter(Boolean)
const dropped = probes.length - kept.length
if (dropped > 0) log(`WARNING: ${dropped} probe(s) dropped (stage threw) — run is INVALID until re-run`)

// F1+F2: read each run's verdict so a null/absent result is 'missing' (never 'pass'), then rank
// so a confirmed 'fail' dominates 'inconclusive' — a real fail is a fail whatever the sibling
// run's legibility. A null low (no dup requested) is not a failure, only an absent second reading.
const verdictOf = (r) => (r && r.verdict) || 'missing'

const table = kept.map(r => {
  const m = verdictOf(r.main)
  const l = r.low ? verdictOf(r.low) : null
  return {
    id: r.id, skill: r.skill, kind: r.kind,
    status:
      m === 'fail' ? 'fail'                                    // confirmed fail always wins
      : l === 'fail' ? 'fail-at-low'                           // main passed/unclear, low confirmed fail
      : m === 'pass' && (l === null || l === 'pass') ? 'pass'  // pass only when nothing contradicts it
      : 'inconclusive',                                        // any inconclusive OR missing verdict
    evidence: { main: r.main?.evidence, low: r.low?.evidence },
  }
})

const tally = (s) => table.filter(r => r.status === s).length
log(`pass ${tally('pass')} · fail ${tally('fail')} · fail-at-low ${tally('fail-at-low')} · inconclusive ${tally('inconclusive')}`)

// F6: the substrate canary. If the CANARY probe (a stable existing skill known to fire) did not
// pass, the plugin set is not loaded — an all-fail battery must be distinguishable from a
// not-installed one. Discard the whole run in that case.
const canary = table.find(r => r.id === 'CANARY')
if (canary && canary.status !== 'pass')
  log('SUBSTRATE FAILURE: canary probe did not pass — plugins likely not loaded; discard this run')

// F3 gate rule: dropped > 0 means the battery did NOT exercise every probe — the run is not a
// pass regardless of the tally. `dropped` (and canaryPassed) are returned so the caller enforces it.
return {
  phase: args.phase,
  actorEffort: mainEffort,
  actorModel: args.actorModel || '(session default)',
  canaryPassed: canary ? canary.status === 'pass' : null,   // null = no canary probe supplied
  pass: tally('pass'), fail: tally('fail'),
  failAtLow: tally('fail-at-low'), inconclusive: tally('inconclusive'),
  dropped,
  table,
}
