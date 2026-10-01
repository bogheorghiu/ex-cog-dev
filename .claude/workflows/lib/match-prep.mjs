#!/usr/bin/env node
// match-prep.mjs — turn critic-run output into blind matching packets, one file per
// artifact (+ one per independent re-match), for the match-critiques workflow to read.
//
// Critics are replaced by opaque codes (salted hash of the model id; the key is written
// to <out>/anon-map.json, which no matcher is pointed at) and their order is shuffled per
// packet, so a matcher can neither recognise a model by name nor by position.
//
// Usage: node match-prep.mjs --artifacts artifacts.json --critiques a.jsonl,b.jsonl --out dir
//          [--exclude-models substr1,substr2] [--double art-03,art-07] [--salt s]

import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf(`--${k}`); return i >= 0 ? argv[i + 1] : d; };
const arts = JSON.parse(fs.readFileSync(opt('artifacts'), 'utf8'));
const exclude = (opt('exclude-models', '')).split(',').filter(Boolean);
const double = (opt('double', '')).split(',').filter(Boolean);
const salt = opt('salt', 'match'), out = opt('out');
fs.mkdirSync(out, { recursive: true });

const ok = new Map();
for (const f of opt('critiques').split(','))
  for (const l of fs.readFileSync(f, 'utf8').split('\n').filter(Boolean)) {
    const r = JSON.parse(l);
    if (!r.err && r.findings && !exclude.some(x => r.model.includes(x))) ok.set(`${r.artifact}|${r.model}`, r); // later lines win
  }
const models = [...new Set([...ok.values()].map(r => r.model))].sort();
const code = m => 'R' + crypto.createHash('sha256').update(salt + m).digest('hex').slice(0, 4).toUpperCase();
const map = Object.fromEntries(models.map(m => [code(m), m]));
if (Object.keys(map).length !== models.length) throw new Error('anon code collision; change --salt');
fs.writeFileSync(path.join(out, 'anon-map.json'), JSON.stringify(map, null, 1));

const order = (xs, seed) => xs.map(x => [crypto.createHash('sha256').update(seed + x).digest('hex'), x]).sort().map(p => p[1]);
const packet = (a, ms) => `You are scoring reviewers of a prompt artifact against a known answer key. You do not know who the reviewers are; judge each finding only on what it says.

ARTIFACT (${a.kind}) — deployment context: ${a.context}
<<<
${a.artifact}
>>>

ANSWER KEY — planted defects:
${a.defects.map(d => `- ${d.id}: quote "${d.quote}" — ${d.problem}`).join('\n')}

DECOYS (look questionable but are correct in context; a finding that objects to one is a false positive):
${a.decoys.map((d, i) => `- decoy${i + 1}: quote "${d.quote}" — fine because ${d.why_fine}`).join('\n')}

REVIEWER FINDINGS:
${ms.map(m => `## Reviewer ${code(m)}\n` + ok.get(`${a.id}|${m}`).findings.map((f, i) => `[${i}] quote: "${String(f.quote).slice(0, 300)}" — ${String(f.problem).slice(0, 600)}`).join('\n')).join('\n\n')}

Label EVERY finding of EVERY reviewer exactly once:
- planted: it identifies the same underlying problem as a planted defect (same span or same mechanism, and the failure it describes is the planted one or a direct consequence). Give the defect id. A vague gesture in the right area that does not state the actual failure is NOT a match.
- decoy: it objects to something listed as a decoy.
- valid_unplanted: a genuine deployment problem not in the key. Be strict: a real failure a careful expert would fix, not a preference, a nit, or a restatement of a planted defect.
- invalid: wrong, a non-problem, a pure style preference, or a duplicate of another finding by the same reviewer.
If one finding covers two planted defects, label it with the one it explains best.
`;

const index = [];
for (const a of arts) {
  const ms = models.filter(m => ok.has(`${a.id}|${m}`));
  for (const k of [1, ...(double.includes(a.id) ? [2] : [])]) {
    const f = path.join(out, `${a.id}.m${k}.md`);
    fs.writeFileSync(f, packet(a, order(ms, `${a.id}:${k}`)));
    index.push({ artifact: a.id, matcher: k, file: path.resolve(f), findings: ms.reduce((s, m) => s + ok.get(`${a.id}|${m}`).findings.length, 0) });
  }
}
fs.writeFileSync(path.join(out, 'index.json'), JSON.stringify(index, null, 1));
console.log(`${models.length} critics, ${index.length} packets, ${index.reduce((s, x) => s + x.findings, 0)} findings to label`);
