#!/usr/bin/env node
// critic-score.mjs — recall / precision / decoy hits / marginal recall per critic, from the
// blind matcher's labels (match-critiques workflow output) and the planted ground truth.
//
// "Marginal recall" is the number this battery exists for: planted defects a critic found
// that NO critic in the reference set (default: every critic whose id starts with
// "claude:") found. A model with modest recall can still be the best complement if what it
// catches is exactly what the reference set misses.
//
// Only matcher 1 is scored; matcher-2 packets are used to report matcher agreement (the
// share of findings both matchers labelled identically), so the matcher's own noise is
// printed next to the numbers it produced.
//
// Usage: node critic-score.mjs --artifacts artifacts.json --matches matches.json
//          --anon anon-map.json --critiques a.jsonl,b.jsonl [--ref-prefix claude:] [--json out.json]

import fs from 'node:fs';

const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf(`--${k}`); return i >= 0 ? argv[i + 1] : d; };
const arts = JSON.parse(fs.readFileSync(opt('artifacts'), 'utf8'));
const M = JSON.parse(fs.readFileSync(opt('matches'), 'utf8'));
const matches = M.matches || M;
const anon = JSON.parse(fs.readFileSync(opt('anon'), 'utf8'));
const REF = opt('ref-prefix', 'claude:');
const crit = opt('critiques').split(',').flatMap(f => fs.readFileSync(f, 'utf8').split('\n').filter(Boolean).map(l => JSON.parse(l)));
const cost = {};
for (const r of crit) if (!r.err) cost[r.model] = (cost[r.model] || 0) + (r.cost || 0); // later reruns overwrite nothing: errors cost too, see ledger

const planted = Object.fromEntries(arts.map(a => [a.id, new Set(a.defects.map(d => d.id))]));
const totalPlanted = arts.reduce((s, a) => s + a.defects.length, 0);
const m1 = matches.filter(m => m.matcher === 1);

// matcher agreement on double-matched packets
const key = m => `${m.artifact}|${m.anon}|${m.finding}`;
const m2 = new Map(matches.filter(m => m.matcher === 2).map(m => [key(m), m]));
let both = 0, same = 0;
for (const m of m1) { const o = m2.get(key(m)); if (o) { both++; if (o.label === m.label && (o.defect || '') === (m.defect || '')) same++; } }

const stats = {};
for (const [code, model] of Object.entries(anon)) {
  const mine = m1.filter(m => m.anon === code);
  const found = new Set(mine.filter(m => m.label === 'planted' && planted[m.artifact]?.has(m.defect)).map(m => `${m.artifact}|${m.defect}`));
  // a "planted" label naming an id the key does not contain is a matcher error, not a hit
  const n = mine.length, good = mine.filter(m => (m.label === 'planted' && planted[m.artifact]?.has(m.defect)) || m.label === 'valid_unplanted').length;
  stats[model] = { findings: n, recall: found.size / totalPlanted, precision: n ? good / n : null,
    decoyHits: mine.filter(m => m.label === 'decoy').length, invalid: mine.filter(m => m.label === 'invalid').length,
    validUnplanted: mine.filter(m => m.label === 'valid_unplanted').length, found, cost: cost[model] || 0 };
}
const refUnion = new Set(Object.entries(stats).filter(([m]) => m.startsWith(REF)).flatMap(([, s]) => [...s.found]));
for (const s of Object.values(stats)) s.marginal = [...s.found].filter(k => !refUnion.has(k)).length;
const allUnion = new Set(Object.values(stats).flatMap(s => [...s.found]));

console.log(`planted defects: ${totalPlanted}; found by reference set (${REF}*): ${refUnion.size}; by anyone: ${allUnion.size}`);
console.log(`matcher agreement on re-matched findings: ${both ? (same / both).toFixed(3) : 'n/a'} (${same}/${both})`);
console.log(`unscored: findings in packets the matcher did not label are not counted (see workflow log)\n`);
console.log('model'.padEnd(34) + 'recall  prec   decoy inval vUnpl  marginal  $total');
for (const [m, s] of Object.entries(stats).sort((a, b) => b[1].marginal - a[1].marginal || b[1].recall - a[1].recall))
  console.log(`${m.padEnd(34)}${s.recall.toFixed(3)}  ${s.precision?.toFixed(2) ?? ' - '}  ${String(s.decoyHits).padStart(4)}  ${String(s.invalid).padStart(4)}  ${String(s.validUnplanted).padStart(4)}  ${String(s.marginal).padStart(6)}   ${s.cost.toFixed(3)}`);
// defects nobody found, and defects only non-reference critics found
const missedAll = arts.flatMap(a => a.defects.filter(d => !allUnion.has(`${a.id}|${d.id}`)).map(d => `${a.id}:${d.id}(${d.subtlety})`));
console.log(`\nfound by nobody (${missedAll.length}): ${missedAll.join(', ')}`);
const onlyOthers = [...allUnion].filter(k => !refUnion.has(k));
console.log(`found only outside the reference set (${onlyOthers.length}): ${onlyOthers.map(k => `${k} <- ${Object.entries(stats).filter(([, s]) => s.found.has(k)).map(([m]) => m.split('/').pop()).join('+')}`).join('; ')}`);
if (opt('json')) fs.writeFileSync(opt('json'), JSON.stringify({ totalPlanted, refUnion: [...refUnion], agreement: both ? same / both : null,
  stats: Object.fromEntries(Object.entries(stats).map(([m, s]) => [m, { ...s, found: [...s.found] }])) }, null, 1));
