// match-prep.test.mjs — blind packets: no model id leaks into a packet, codes are stable,
// failed critiques and excluded models are left out, a later re-run replaces an earlier line,
// and re-match packets get their own order. Run: node .claude/workflows/lib/match-prep.test.mjs
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const d = fs.mkdtempSync(path.join(os.tmpdir(), 'mp-'));
const out = path.join(d, 'out');
fs.writeFileSync(path.join(d, 'arts.json'), JSON.stringify([{ id: 'a1', kind: 'grader', context: 'ctx', artifact: 'TEXT',
  defects: [{ id: 'd1', quote: 'q1', problem: 'p1' }], decoys: [{ quote: 'dq', why_fine: 'ok' }] }]));
const rec = (model, findings, err = null) => JSON.stringify({ artifact: 'a1', model, rep: 1, findings, err });
fs.writeFileSync(path.join(d, 'c.jsonl'), [
  rec('vendor/alpha-model', [{ quote: 'old', problem: 'superseded' }]),
  rec('vendor/alpha-model', [{ quote: 'x', problem: 'finding from alpha' }]),     // later line wins
  rec('vendor/beta-model', [{ quote: 'y', problem: 'finding from beta' }]),
  rec('vendor/broken-model', null, 'unparseable'),                                // failed: skipped
  rec('vendor/excluded-model', [{ quote: 'z', problem: 'should not appear' }]),   // excluded by flag
].join('\n'));
const run = () => execFileSync('node', [path.join(here, 'match-prep.mjs'), '--artifacts', path.join(d, 'arts.json'),
  '--critiques', path.join(d, 'c.jsonl'), '--out', out, '--exclude-models', 'excluded', '--double', 'a1'], { stdio: 'pipe' });
run();
const map = JSON.parse(fs.readFileSync(path.join(out, 'anon-map.json'), 'utf8'));
assert.deepEqual(Object.values(map).sort(), ['vendor/alpha-model', 'vendor/beta-model']);
const idx = JSON.parse(fs.readFileSync(path.join(out, 'index.json'), 'utf8'));
assert.equal(idx.length, 2, 'one packet plus one re-match packet');
assert.equal(idx[0].findings, 2);
for (const p of idx) {
  const t = fs.readFileSync(p.file, 'utf8');
  for (const m of ['alpha-model', 'beta-model', 'broken-model', 'excluded-model', 'vendor/']) assert.ok(!t.includes(m), `packet leaks "${m}"`);
  assert.ok(t.includes('finding from alpha') && !t.includes('superseded'), 'the later critique line must replace the earlier one');
  assert.ok(!t.includes('should not appear'));
  // the scorer maps codes back through anon-map.json, so every code a matcher sees must be in it
  const codes = [...t.matchAll(/^## Reviewer (\S+)$/gm)].map(m => m[1]);
  assert.deepEqual(codes.sort(), Object.keys(map).sort(), 'packet codes must be exactly the anon-map keys');
}
const first = JSON.stringify(map);
run();
assert.equal(JSON.stringify(JSON.parse(fs.readFileSync(path.join(out, 'anon-map.json'), 'utf8'))), first, 'codes must be stable across runs');
fs.rmSync(d, { recursive: true, force: true });
console.log('match-prep: all assertions passed');
