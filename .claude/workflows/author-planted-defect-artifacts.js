// author-planted-defect-artifacts — build a ground-truthed battery for prompt CRITICS: realistic
// prompt artifacts with planted defects (obvious/moderate/subtle) plus decoys, each verified by an
// independent agent. Pair with lib/critic-run.mjs (collect critiques), lib/match-prep.mjs +
// match-critiques.js (blind labelling) and lib/critic-score.mjs (recall, precision, marginal recall).
// First used 2026-10-01: probes/prompt-skill-critics/ (8 artifacts, 61 defects, 21 decoys).
//
// Why Fable authors and a different agent verifies: an author grading its own planted defects
// would confirm them; the verifier deletes non-defects and adds genuine unplanted ones, so a critic
// is not penalised for a correct finding the key missed.

export const meta = {
  name: 'author-planted-defect-artifacts',
  description: 'Fable authors prompt artifacts with planted, ground-truthed defects and decoys; an independent reviewer verifies each defect is real and each decoy is defensible',
  whenToUse: 'Building a recall/precision battery for prompt critics (which models catch which defects)',
  phases: [
    { title: 'Author', detail: 'Fable writes artifacts with planted defects + decoys' },
    { title: 'Verify', detail: 'independent reviewer confirms ground truth' },
  ],
}

const ART = {
  type: 'object', required: ['artifacts'],
  properties: { artifacts: { type: 'array', items: {
    type: 'object', required: ['id', 'kind', 'context', 'artifact', 'defects', 'decoys'],
    properties: {
      id: { type: 'string' },
      kind: { type: 'string', description: 'system prompt / agent brief / skill / grader / tool contract / rule file / few-shot bank' },
      context: { type: 'string', description: '2-4 sentences: target model class, deployment, objective - what a reviewer is told' },
      artifact: { type: 'string', description: 'the full prompt artifact, 250-900 words, realistic' },
      defects: { type: 'array', minItems: 5, maxItems: 8, items: { type: 'object', required: ['id', 'quote', 'problem', 'subtlety'], properties: {
        id: { type: 'string' }, quote: { type: 'string', description: 'verbatim span from the artifact where the defect lives' },
        problem: { type: 'string', description: 'what goes wrong in deployment because of it, concretely' },
        subtlety: { enum: ['obvious', 'moderate', 'subtle'] } } } },
      decoys: { type: 'array', minItems: 1, maxItems: 3, items: { type: 'object', required: ['quote', 'why_fine'], properties: {
        quote: { type: 'string' }, why_fine: { type: 'string', description: 'why this looks questionable but is correct and intentional in context' } } } },
    } } } },
}

const FAMILIES = [
  'contradictions between instructions; an output contract that two parts of the prompt specify differently; a few-shot example that violates the stated rules',
  'missing failure handling (unreachable source, empty input, tool error); hallucination invited by asking for facts the model cannot have; an untrusted-input channel (retrieved docs, user-pasted text) treated as instructions',
  'a judgment directive given with no reason where edge cases will occur; a hard safety/format constraint softened into vague prose; a must-hold-every-time rule left in prose where a validator/schema could enforce it; emphasis inflation (IMPORTANT/MUST everywhere) burying the one rule that matters',
  'a claim about the target model or harness capabilities that is unverifiable or false for the stated deployment; scope creep (instructions irrelevant to the objective); a grader whose criteria are not decidable from the material it is given; a router/skill description that will not be selected for the requests it is meant to catch',
]

phase('Author')
const res = await pipeline(FAMILIES,
  // a stage callback receives (previous result, original item, index); in the first stage the
  // previous result IS the item, so the index is the third argument
  (fam, _item, i) => agent(`Write 2 realistic prompt artifacts (the kind a team actually deploys: system prompts, agent briefs, skills, graders, tool contracts, rule files) for a benchmark of prompt REVIEWERS.

In each artifact, plant 5-8 genuine defects. Draw mainly from these families, mixing in others where natural: ${fam}.
Mix subtlety: about 2 obvious, 2-3 moderate, 2-3 subtle per artifact. A subtle defect is one a careful expert catches but a skim misses. Every defect must cause a concrete deployment failure you can state.

Also plant 1-3 DECOYS: things a shallow reviewer would flag but that are correct and intentional in context (e.g. a deliberately terse imperative where exact compliance is the point; an intentional redundancy that guards a known failure; an unusual format the downstream parser requires). The decoys measure false positives, so their justification must be visible from the context you give the reviewer.

The artifact must read as a competent team's real work, not a strawman: most of it should be good. Do not mark defects inside the artifact text. Return ids ${i * 2 + 1} and ${i * 2 + 2} as "art-${i * 2 + 1}", "art-${i * 2 + 2}".`, { label: `author:${i + 1}`, phase: 'Author', schema: ART, model: 'fable', effort: 'high' }),
  (batch, fam, i) => agent(`You verify ground truth for a prompt-reviewer benchmark. For each artifact below, check every planted defect and decoy against the artifact text and its context:
- A defect stays only if (a) its quote is verbatim in the artifact, and (b) it would genuinely cause the stated failure for the stated deployment. Fix quotes that are not verbatim; delete defects that are not genuine (say so in their problem field prefixed DELETED: is not allowed - just remove them).
- A decoy stays only if a careful expert, given the context, would agree it is fine. Remove decoys that are actually defects (or move them into defects).
- If an artifact contains an UNPLANTED genuine defect that a reviewer would rightly report, add it to defects with subtlety and a note "unplanted" in problem - otherwise reviewers get penalized for correct findings.
Return the corrected artifacts in the same schema.

${JSON.stringify(batch?.artifacts ?? [], null, 1)}`, { label: `verify:${i + 1}`, phase: 'Verify', schema: ART, effort: 'high' }),
)
const arts = res.filter(Boolean).flatMap(b => b.artifacts).map((a, k) => ({ ...a, id: `art-${String(k + 1).padStart(2, '0')}` }))
log(`${arts.length} artifacts, ${arts.reduce((s, a) => s + a.defects.length, 0)} defects, ${arts.reduce((s, a) => s + a.decoys.length, 0)} decoys`)
return { artifacts: arts }