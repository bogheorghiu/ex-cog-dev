// match-critiques — map each critic's findings onto a planted-defect ground truth, blind.
//
// Why a workflow: "does this finding describe planted defect d3?" is a judgment call, so it
// belongs to model agents; the arithmetic (recall, precision, marginal recall) is plain code
// done afterwards. Packets are written by lib/match-prep.mjs, which anonymises and shuffles
// the critics; the matcher reads its packet from disk, so hundreds of findings never pass
// through the orchestrator's context. One matcher per artifact sees every critique of that
// artifact, which keeps its threshold consistent across critics; packets with matcher=2 are
// independent re-matches that measure the matcher's own noise.
//
// args: { index: [{artifact, matcher, file, findings}] }   (lib/match-prep.mjs -> index.json)
// returns: { matches: [{artifact, matcher, anon, finding, label, defect}], failed: [...] }

export const meta = {
  name: 'match-critiques',
  description: 'Blind matching of anonymised prompt critiques to planted defects, decoys, valid-unplanted, or invalid',
  whenToUse: 'Scoring a planted-defect critic battery (recall/precision per critic) without the matcher knowing which model wrote which critique',
  phases: [{ title: 'Match', detail: 'one matcher per packet (artifact x matcher)' }],
}

const OUT = {
  type: 'object', required: ['matches'],
  properties: { matches: { type: 'array', items: { type: 'object', required: ['anon', 'finding', 'label'], properties: {
    anon: { type: 'string', description: 'reviewer code, e.g. R1A2B' },
    finding: { type: 'integer', description: '0-based index of the finding within that reviewer' },
    label: { enum: ['planted', 'decoy', 'valid_unplanted', 'invalid'] },
    defect: { type: 'string', description: 'planted defect id when label=planted, else empty' },
  } } } },
}

phase('Match')
const res = await parallel(args.index.map(p => () =>
  agent(`Read the file ${p.file} in full (use the Read tool; read all of it, in pages if needed) and do exactly the labelling task it describes. It contains ${p.findings} findings in total; return one label for each of them.`,
    { label: `match:${p.artifact}:m${p.matcher}`, phase: 'Match', schema: OUT, effort: 'high' })
    .then(r => r ? { p, matches: (r.matches || []).map(m => ({ ...m, artifact: p.artifact, matcher: p.matcher })) } : null)))
const done = res.filter(Boolean)
// compare by key, not object identity: args is re-materialised on each access
const tag = p => `${p.artifact}:m${p.matcher}`
const failed = args.index.map(tag).filter(k => !done.some(d => tag(d.p) === k))
for (const d of done) if (d.matches.length !== d.p.findings) log(`${d.p.artifact}:m${d.p.matcher} labelled ${d.matches.length} of ${d.p.findings} findings`)
if (failed.length) log(`unscored packets: ${failed.join(', ')}`)
return { matches: done.flatMap(d => d.matches), failed }
