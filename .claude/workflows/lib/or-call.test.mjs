// or-call.test.mjs — the spending cap refuses BEFORE any network call, and spending without a
// ledger is refused outright. No network is used. Run: node .claude/workflows/lib/or-call.test.mjs
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const d = fs.mkdtempSync(path.join(os.tmpdir(), 'oc-'));
const ledger = path.join(d, 'ledger.jsonl');
fs.writeFileSync(ledger, [{ cost: 0.6 }, { cost: 0.5 }].map(x => JSON.stringify(x)).join('\n') + '\n');
process.env.OR_LEDGER = ledger;
process.env.OR_CAP_USD = '1';
// fetch must never be reached once the cap is hit; make any attempt loud
globalThis.fetch = async () => { throw new Error('network attempted'); };
const { chat, spent } = await import(path.join(here, 'or-call.mjs'));
assert.ok(Math.abs(spent() - 1.1) < 1e-9, 'spent() sums the ledger');
await assert.rejects(() => chat({ model: 'm', messages: [] }), /budget cap reached/);
assert.equal(fs.readFileSync(ledger, 'utf8').trim().split('\n').length, 2, 'a refused call writes nothing');
delete process.env.OR_LEDGER;
const fresh = await import(path.join(here, 'or-call.mjs') + '?noledger');
await assert.rejects(() => fresh.chat({ model: 'm', messages: [] }), /OR_LEDGER not set/);
fs.rmSync(d, { recursive: true, force: true });
console.log('or-call: all assertions passed');
