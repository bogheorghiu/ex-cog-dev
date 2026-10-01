// or-call.mjs — one OpenRouter chat call with a hard, on-disk spending cap.
//
// Why a ledger file rather than an in-memory counter: batteries run as many separate
// processes (and get resumed after interruptions), so only a file sees the whole spend.
// The cap is checked BEFORE each call against what the ledger already holds, so a run can
// overshoot by at most one call's cost per concurrent worker — size the cap with that slack.
// Costs are the provider-reported `usage.cost` (OpenRouter's own record), never estimated.
//
// Env: OR_LEDGER (ledger path, required), OR_CAP_USD (default 8), OPENROUTER_API_KEY
// (optional: in environments where a proxy injects credentials, leave it unset).
// Behind an HTTPS proxy, Node's built-in fetch ignores HTTPS_PROXY unless the process runs
// with NODE_USE_ENV_PROXY=1 (Node >= 22.21); without it the call fails with a 401 that looks
// like a credential problem.

import fs from 'node:fs';

const LEDGER = process.env.OR_LEDGER;
const CAP = +(process.env.OR_CAP_USD ?? 8);

export function spent() {
  if (!LEDGER || !fs.existsSync(LEDGER)) return 0;
  return fs.readFileSync(LEDGER, 'utf8').split('\n').filter(Boolean)
    .reduce((s, l) => s + (JSON.parse(l).cost || 0), 0);
}

export async function chat({ model, messages, max_tokens = 4000, temperature, reasoning, tag = '' }) {
  if (!LEDGER) throw new Error('OR_LEDGER not set: refusing to spend without a ledger');
  const before = spent();
  if (before >= CAP) throw new Error(`budget cap reached: $${before.toFixed(4)} >= $${CAP}`);
  const body = { model, messages, max_tokens, usage: { include: true } };
  if (temperature !== undefined) body.temperature = temperature;
  if (reasoning) body.reasoning = reasoning;
  const headers = { 'content-type': 'application/json' };
  if (process.env.OPENROUTER_API_KEY) headers.authorization = `Bearer ${process.env.OPENROUTER_API_KEY}`;
  let res, j, lastErr;
  for (let attempt = 0; attempt < 4; attempt++) {
    try {
      res = await fetch('https://openrouter.ai/api/v1/chat/completions', { method: 'POST', headers, body: JSON.stringify(body) });
      j = await res.json();
      if (res.ok && j.choices) break;
      lastErr = JSON.stringify(j).slice(0, 300);
      if (res.status === 402 || res.status === 403) break; // credit/limit: retrying cannot help
    } catch (e) { lastErr = String(e); }
    await new Promise(r => setTimeout(r, 2000 * 2 ** attempt));
  }
  const cost = j?.usage?.cost ?? 0;
  fs.appendFileSync(LEDGER, JSON.stringify({ ts: new Date().toISOString(), tag, model, served: j?.model, cost,
    in: j?.usage?.prompt_tokens, out: j?.usage?.completion_tokens, ok: !!j?.choices, err: j?.choices ? undefined : lastErr }) + '\n');
  if (!j?.choices) throw new Error(`OpenRouter call failed for ${model}: ${lastErr}`);
  return { text: j.choices[0].message?.content ?? '', model: j.model, cost, usage: j.usage };
}
