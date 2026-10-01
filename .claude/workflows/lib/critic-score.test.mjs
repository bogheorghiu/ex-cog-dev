// critic-score.test.mjs — recall, precision, decoy hits, marginal recall and matcher agreement
// from a hand-computed fixture. Run: node .claude/workflows/lib/critic-score.test.mjs
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const d = fs.mkdtempSync(path.join(os.tmpdir(), 'cs-'));
const w = (f, x) => fs.writeFileSync(path.join(d, f), typeof x === 'string' ? x : JSON.stringify(x));
w('arts.json', [{ id: 'a1', defects: [{ id: 'd1' }, { id: 'd2' }, { id: 'd3' }], decoys: [{ quote: 'q' }] }]);
w('anon.json', { RA: 'claude:ref', RB: 'vendor/other' });
w('crit.jsonl', [{ model: 'claude:ref', cost: 0 }, { model: 'vendor/other', cost: 0.5 }].map(x => JSON.stringify({ ...x, err: null })).join('\n'));
w('matches.json', { matches: [
  // ref finds d1, d2; flags the decoy once; one invalid
  { artifact: 'a1', matcher: 1, anon: 'RA', finding: 0, label: 'planted', defect: 'd1' },
  { artifact: 'a1', matcher: 1, anon: 'RA', finding: 1, label: 'planted', defect: 'd2' },
  { artifact: 'a1', matcher: 1, anon: 'RA', finding: 2, label: 'decoy' },
  { artifact: 'a1', matcher: 1, anon: 'RA', finding: 3, label: 'invalid' },
  // other finds d2 and d3 (d3 is its marginal catch) plus one valid unplanted
  { artifact: 'a1', matcher: 1, anon: 'RB', finding: 0, label: 'planted', defect: 'd2' },
  { artifact: 'a1', matcher: 1, anon: 'RB', finding: 1, label: 'planted', defect: 'd3' },
  { artifact: 'a1', matcher: 1, anon: 'RB', finding: 2, label: 'valid_unplanted' },
  // an id the key does not contain must not count as found
  { artifact: 'a1', matcher: 1, anon: 'RB', finding: 3, label: 'planted', defect: 'd9' },
  // matcher 2 re-labels two of RA's findings: one agrees, one differs
  { artifact: 'a1', matcher: 2, anon: 'RA', finding: 0, label: 'planted', defect: 'd1' },
  { artifact: 'a1', matcher: 2, anon: 'RA', finding: 1, label: 'invalid' },
] });
execFileSync('node', [path.join(here, 'critic-score.mjs'), '--artifacts', path.join(d, 'arts.json'), '--matches', path.join(d, 'matches.json'),
  '--anon', path.join(d, 'anon.json'), '--critiques', path.join(d, 'crit.jsonl'), '--json', path.join(d, 'out.json')], { stdio: 'pipe' });
const o = JSON.parse(fs.readFileSync(path.join(d, 'out.json'), 'utf8'));
const ref = o.stats['claude:ref'], oth = o.stats['vendor/other'];
assert.equal(o.totalPlanted, 3);
assert.equal(ref.recall, 2 / 3);
assert.equal(ref.precision, 2 / 4, 'ref: 2 planted of 4 findings');
assert.equal(ref.decoyHits, 1);
assert.equal(ref.marginal, 0, 'the reference set has no marginal catches over itself');
assert.equal(oth.recall, 2 / 3, 'd9 is not in the key and must not count');
assert.equal(oth.precision, 3 / 4, '2 planted + 1 valid-unplanted of 4');
assert.equal(oth.marginal, 1, 'd3 is the one defect the reference set missed');
assert.equal(o.agreement, 0.5, 'one of two re-matched findings labelled identically');
fs.rmSync(d, { recursive: true, force: true });
console.log('critic-score: all assertions passed');
