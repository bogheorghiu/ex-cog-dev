// critic-run.test.mjs — the "claude:" path end to end with a fake `claude` on PATH (no network):
// critiques are parsed and stored, an unparseable reply is recorded as an error rather than as
// zero findings, the session-identity variables never reach the child, and a re-run retries
// only the failed unit. Run: node .claude/workflows/lib/critic-run.test.mjs
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const d = fs.mkdtempSync(path.join(os.tmpdir(), 'cr-'));
const bin = path.join(d, 'bin'); fs.mkdirSync(bin);
// fake claude: answers with findings for model "good", garbage for "bad" (until bad.fixed exists),
// and records whether a session id leaked into its environment
fs.writeFileSync(path.join(bin, 'claude'), `#!/usr/bin/env node
const a = process.argv.slice(2); const model = a[a.indexOf('--model') + 1];
require('fs').appendFileSync(${JSON.stringify(path.join(d, 'env.log'))}, (process.env.CLAUDE_CODE_SESSION_ID ? 'LEAK' : 'clean') + '\\n');
const fixed = require('fs').existsSync(${JSON.stringify(path.join(d, 'bad.fixed'))});
const text = model === 'good' || fixed ? '{"findings":[{"quote":"q","problem":"p"}]}' : 'not json at all';
process.stdout.write(JSON.stringify({ is_error: false, result: text, total_cost_usd: 0.01, modelUsage: { [model]: {} } }));
`, { mode: 0o755 });
fs.writeFileSync(path.join(d, 'arts.json'), JSON.stringify([{ id: 'a1', kind: 'k', context: 'c', artifact: 'A' }]));
const out = path.join(d, 'crit.jsonl');
const env = { ...process.env, PATH: `${bin}:${process.env.PATH}`, OR_LEDGER: path.join(d, 'ledger.jsonl'), CLAUDE_CODE_SESSION_ID: 'parent-session' };
const run = () => execFileSync('node', [path.join(here, 'critic-run.mjs'), '--artifacts', path.join(d, 'arts.json'),
  '--models', 'claude:good,claude:bad', '--out', out], { env, stdio: 'pipe' });
run();
let rows = fs.readFileSync(out, 'utf8').trim().split('\n').map(l => JSON.parse(l));
const good = rows.find(r => r.model === 'claude:good'), bad = rows.find(r => r.model === 'claude:bad');
assert.deepEqual(good.findings, [{ quote: 'q', problem: 'p' }]);
assert.equal(good.err, null);
assert.equal(bad.findings, null, 'an unparseable reply must not become "0 findings"');
assert.equal(bad.err, 'unparseable');
assert.ok(!fs.readFileSync(path.join(d, 'env.log'), 'utf8').includes('LEAK'), 'parent session id reached the child');
fs.writeFileSync(path.join(d, 'bad.fixed'), '');
run();
rows = fs.readFileSync(out, 'utf8').trim().split('\n').map(l => JSON.parse(l));
assert.equal(rows.length, 3, 'the re-run retries only the failed unit');
assert.equal(rows[2].model, 'claude:bad'); assert.equal(rows[2].err, null);
fs.rmSync(d, { recursive: true, force: true });
console.log('critic-run: all assertions passed');
