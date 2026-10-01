#!/usr/bin/env node
// critic-run.mjs — ask many models to review the same prompt artifacts, blind, with one
// identical instruction, and store every critique verbatim for later matching against the
// planted ground truth.
//
// Why this instrument exists: "which model complements Claude" is a question about what a
// model catches that Claude misses, which only a battery with known defects can answer. A
// model's general benchmark rank does not say it, and its own description of its strengths
// is not evidence. Matching findings to planted defects is a judgment step and happens
// elsewhere (blind to which model wrote each critique); this script only collects.
//
// Model ids: OpenRouter ids go through or-call.mjs (ledger + hard cap). Ids prefixed
// "claude:" run through a headless `claude -p` with the session environment scrubbed, so the
// Claude side gets the identical prompt without OpenRouter spend.
//
// Usage: NODE_USE_ENV_PROXY=1 OR_LEDGER=... OR_CAP_USD=8 node critic-run.mjs \
//          --artifacts artifacts.json --models a,b,claude:claude-opus-5 --out critiques.jsonl \
//          [--reps 1] [--concurrency 6] [--max-tokens 6000] [--reasoning low]

import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const { chat } = await import(path.join(here, 'or-call.mjs'));
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf(`--${k}`); return i >= 0 ? argv[i + 1] : d; };
const arts = JSON.parse(fs.readFileSync(opt('artifacts'), 'utf8'));
const models = opt('models').split(',');
const outPath = opt('out'), REPS = +opt('reps', 1), CONC = +opt('concurrency', 6);
const MAXT = +opt('max-tokens', 6000), REASONING = opt('reasoning', 'low');

export const critiquePrompt = a => `You are reviewing a prompt artifact before it is deployed. Find the problems that would actually cause it to fail or misbehave in deployment.

Deployment context: ${a.context}

ARTIFACT (${a.kind}):
<<<
${a.artifact}
>>>

List every genuine defect you find. For each: quote the exact span (verbatim, short) and state concretely what goes wrong in deployment because of it. Do not list stylistic preferences or things that are fine as written. If something looks unusual but is justified by the context, leave it out.

Return ONLY JSON: {"findings":[{"quote":"...","problem":"..."}]}`;

const SCRUB = /^(CLAUDECODE|CLAUDE_PID|CLAUDE_EFFORT|MAX_THINKING_TOKENS|SESSION_INGRESS_URL|CLAUDE_ADDITIONAL_DIRECTORIES|CLAUDE_AFTER_LAST_COMPACT|CLAUDE_CODE_(SESSION_ID|REMOTE_SESSION_ID|POST_FOR_SESSION_INGRESS_V2|MESSAGING_\w+|TEE_SDK_STDOUT|ADDITIONAL_DIRECTORIES_CLAUDE_MD|CHILD_SESSION|SYNC_SESSION_REFS|SYNC_SKILLS|SESSION_ATTENDED|DIAGNOSTICS_FILE|DEBUG))$/;
const childEnv = Object.fromEntries(Object.entries(process.env).filter(([k]) => !SCRUB.test(k)));
const settings = JSON.stringify({ enabledPlugins: { 'research-toolkit@ex-cog-dev': false, 'i-have-adhd@i-have-adhd': false } });

async function callClaude(model, prompt) {
  const cwd = fs.mkdtempSync(path.join(os.tmpdir(), 'critic-'));
  // spawnSync inside an async worker blocks the loop, so Claude critics run one at a time;
  // acceptable because the OpenRouter calls are the slow, parallel part.
  const r = spawnSync('claude', ['-p', prompt, '--settings', settings, '--model', model, '--effort', REASONING === 'low' ? 'low' : 'medium',
    '--output-format', 'json', '--tools', ''], { cwd, env: childEnv, encoding: 'utf8', timeout: 600000, maxBuffer: 1 << 26 });
  fs.rmSync(cwd, { recursive: true, force: true });
  let j; try { j = JSON.parse(r.stdout); } catch { throw new Error('claude -p output unparseable: ' + (r.stderr || r.stdout).slice(0, 200)); }
  if (j.is_error) throw new Error('claude -p error: ' + String(j.result).slice(0, 200));
  return { text: j.result, model: Object.keys(j.modelUsage || {})[0] || model, cost: 0, notionalCost: j.total_cost_usd };
}

const parse = t => { const m = (t || '').match(/\{[\s\S]*\}/); try { return m ? JSON.parse(m[0]) : null; } catch { return null; } };
const done = new Set(fs.existsSync(outPath) ? fs.readFileSync(outPath, 'utf8').split('\n').filter(Boolean)
  .map(l => JSON.parse(l)).filter(r => !r.err).map(r => `${r.artifact}|${r.model}|${r.rep}`) : []);
const jobs = [];
for (const a of arts) for (const m of models) for (let rep = 1; rep <= REPS; rep++)
  if (!done.has(`${a.id}|${m}|${rep}`)) jobs.push({ a, m, rep });
console.error(`${jobs.length} critiques to run`);

let next = 0;
await Promise.all(Array.from({ length: Math.min(CONC, jobs.length) }, async () => {
  while (next < jobs.length) {
    const { a, m, rep } = jobs[next++];
    const t0 = Date.now();
    let res, err = null;
    try {
      res = m.startsWith('claude:') ? await callClaude(m.slice(7), critiquePrompt(a))
        : await chat({ model: m, messages: [{ role: 'user', content: critiquePrompt(a) }], max_tokens: MAXT, reasoning: { effort: REASONING }, tag: `critic:${a.id}` });
    } catch (e) { err = String(e).slice(0, 300); }
    const parsed = res ? parse(res.text) : null;
    if (res && !parsed) err = 'unparseable';
    fs.appendFileSync(outPath, JSON.stringify({ artifact: a.id, model: m, served: res?.model, rep, ms: Date.now() - t0,
      cost: res?.cost ?? 0, notionalCost: res?.notionalCost, findings: parsed?.findings ?? null, raw: parsed ? undefined : res?.text?.slice(0, 4000), err }) + '\n');
    console.error(`${a.id} ${m}: ${err ? 'ERR ' + err.slice(0, 100) : (parsed.findings?.length ?? 0) + ' findings, $' + (res.cost ?? 0)}`);
    if (String(err).includes('budget cap')) process.exit(3);
  }
}));
