#!/usr/bin/env python3
"""firing-filter — deterministic firing layer for research-toolkit (M16).

THE PROBLEM THIS SOLVES. The toolkit's recorded failure mode is rules that are
correct and do not fire: in the canonical recorded session the model wrote the
governing principle into its own task list, named it in its own output, and
violated it minutes later — caught only by a human. Every recorded correction
was externally forced; none was spontaneous. So nothing here relies on the
analyst noticing anything. This layer is a scheduled external challenge:
zero model calls, zero judgment, pure string/log mechanics (doctrine A0.4:
a rule that requires high-effort noticing under-fires exactly when it matters).

THE DESIGN, in one sentence: situation-shaped triggers gate fact-shaped
checks — words only ever ARM; situations LOCATE points of application and
inject one bound guidance each; only facts (a written claim contradicted by
the session's own machine record) get teeth.

Why that split (each half measured against the recorded session's real bytes):
 * Word-matching carries NO enforcement signal: the recorded failure and its
   own correction produce identical lexicon hit-counts (10 vs 10), and on the
   correction the hits land on the corrective sentences themselves. A string
   cannot tell use from mention. So lexicon hits are ONLY an arming tripwire —
   over-firing there is free and correct.
 * Per-span payloads are theater at scale: bound questions attached to word
   spans yield 72 forced annotations on one 16k document (85% on the toolkit's
   own tier vocabulary used correctly) — no analyst answers 72 with care, and
   the ledger would then certify the failure as reviewed. So payloads attach
   to SITUATIONS (one per unit), never to spans.
 * Claim-vs-record reconciliation discriminates: the recorded dossier's Method
   line named four methodologies the session log shows were never invoked —
   flagged 4/4, zero model, zero false positives on the same session's six
   control units. "Named but not invoked" is a fact; it cannot be said
   ironically, quoted, or guarded against. Facts get the one blocking verb.

WHAT IT NEVER DOES (each prohibition is load-bearing; see README.md):
 * never asks any model anything (no judgment in a sensor — a sensor asked
   "is this warranted?" hands the bias its frame back);
 * never blocks on a word-hit or a situation-hit (blocks are for fact-flags
   only, and even those are once per unit content, then downgrade to ledger —
   an unbreakable block is a denial-of-service that gets the plugin disabled,
   which is total coverage loss);
 * never edits or curates its own lists (the watched layer choosing its own
   sensors is the fox auditing the henhouse; additions come from the human
   learn loop, each derived from a measured miss);
 * never gates on a Skill matcher (the failure IS "no skill fired"; a hook
   gated on skill invocation inherits the failure it exists to fix);
 * never fails closed (any internal error → allow + a SCAN-FAILED ledger
   line; a filter that halts work when broken gets uninstalled).

Surfaces (one engine, one extractor per event; adding a surface later is one
hooks.json stanza + one extractor branch):
   SessionStart          re-seed assets (seed-copy only), init state
   UserPromptSubmit      arming scan of the user prompt; armed announcement
   PreToolUse Task|Agent S2 dispatch-hygiene (deny once per unit, capped/session)
   PostToolUse Task|Agent S3 returned-verdict guidance (inject once per unit)
   PreToolUse Write|Edit S1 gate -> reconciliation (deny once per unit on flags)
   PostToolUse Write|Edit S1 verdict-hygiene guidance (inject once per unit)
   Stop                  S1 gate -> reconciliation on the final message
                         (block once; never when stop_hook_active)

Assets & state live behind the three-directory seed/local seam — see
seed_assets(): the re-seed code path never names the local directory, so
clobbering user growth is structurally impossible, not carefully avoided.
"""
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------- environment

def plugin_root() -> Path:
    # CLAUDE_PLUGIN_ROOT is exported to hook processes (verified platform
    # fact). Falling back to this file's grandparent keeps the CLI usable
    # when invoked by hand outside a hook.
    return Path(os.environ.get("CLAUDE_PLUGIN_ROOT",
                               Path(__file__).resolve().parents[2]))

def data_dir() -> Path:
    # CLAUDE_PLUGIN_DATA persists across plugin updates and dies on uninstall
    # (unless --keep-data): the right lifecycle for user-grown rows and
    # session state. Fallback keeps hand-runs working.
    base = os.environ.get("CLAUDE_PLUGIN_DATA")
    if not base:
        base = os.path.expanduser("~/.claude/plugins/data/research-toolkit-ex-cog-dev")
    d = Path(base) / "firing-filter"
    return d

def master_enabled() -> bool:
    # userConfig master switch reaches hooks as an env var. Absent means the
    # host never prompted (older CLI, headless) — default ON, because a
    # silently-disabled safety layer is this project's founding failure mode.
    for key in ("CLAUDE_PLUGIN_OPTION_FIRING_FILTER",
                "CLAUDE_PLUGIN_OPTION_FIRING-FILTER",
                "CLAUDE_PLUGIN_OPTION_firing_filter"):
        v = os.environ.get(key)
        if v is not None:
            return str(v).strip().lower() not in ("false", "0", "off", "no")
    return True

# ------------------------------------------------------------------ constants

TIER_TOKEN = re.compile(r"\b(GROUNDED|UNRESOLVED|CONTRADICTED)\b")
S1_TIER_MIN = 5   # a unit using tier verdicts 5+ times is rendering verdicts;
                  # dispatches that merely *instruct* tiering carry 3-4.
S3_TIER_MIN = 3   # a returned memo: fewer tokens suffice because the
S3_ABS_MIN = 1    # co-presence of an absence-phrase is the second condition.
ARM_MIN_HITS = 4      # arming: >=4 lexicon hits from >=2 entry families in one
ARM_MIN_ENTRIES = 2   # unit. Everyday words ("standard") alone must not arm a
                      # coding session; the recorded research units all clear
                      # this easily (10/3 on the sparsest failure unit).
S2_SESSION_CAP = 2    # dispatch denials per session: insistence, not DoS.

# ------------------------------------------------------------------- storage

def _read_jsonl(path: Path):
    rows = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
    except FileNotFoundError:
        pass
    return rows

def load_rows(kind: str):
    """Merged view: seed-copy ∪ local, with local shadow-off.

    A local row {"id": X, "disabled": true} silences a shipped row without
    editing shipped files (which the next update would revert) — e.g. a user
    whose investigation subject is literally named with a watchlist word.
    """
    d = data_dir()
    rows = {r["id"]: r for r in _read_jsonl(d / "seed-copy" / f"{kind}.jsonl")}
    for r in _read_jsonl(d / "local" / f"{kind}.jsonl"):
        rows[r["id"]] = r
    return [r for r in rows.values() if not r.get("disabled")]

def seed_assets():
    """Docs-canonical diff-reseed, adapted: compare each bundled seed file to
    its copy under seed-copy/ and overwrite ON DIFFERENCE — covering first run
    and updates. THE ONLY WRITE TARGET IS seed-copy/. This function does not
    reference the user's growth directory at all; the capability to destroy
    user rows does not exist in this code path (structural, not careful).
    """
    src = plugin_root() / "hooks" / "firing-filter" / "seed"
    dst = data_dir() / "seed-copy"
    dst.mkdir(parents=True, exist_ok=True)
    for f in sorted(src.glob("*.jsonl")):
        target = dst / f.name
        new = f.read_bytes()
        if not target.exists() or target.read_bytes() != new:
            target.write_bytes(new)
    # user growth lives at data_dir()/"local"; created on demand by the learn
    # loop / the user, never here.

def state_path(session_id: str) -> Path:
    p = data_dir() / "state"
    p.mkdir(parents=True, exist_ok=True)
    return p / f"{session_id or 'unknown'}.json"

def load_state(session_id: str) -> dict:
    try:
        return json.loads(state_path(session_id).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {"mode": "passive", "seen": [], "s2_denials": 0}

def save_state(session_id: str, st: dict):
    state_path(session_id).write_text(json.dumps(st), encoding="utf-8")

def ledger_append(session_id: str, entry: dict):
    p = data_dir() / "ledger"
    p.mkdir(parents=True, exist_ok=True)
    entry = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **entry}
    with open(p / f"{session_id or 'unknown'}.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def unit_hash(text: str) -> str:
    # Content-addressed insistence: a *revised* unit is re-scanned fresh; a
    # verbatim re-send of a flagged unit is not re-blocked (bounded
    # insistence — the record demands insistence, not deadlock).
    return hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()[:16]

# ----------------------------------------------------------------- detection

def lexicon_hits(text: str, rows):
    """Arming scan. Over-application here is a FEATURE: both the recorded
    failure and its correction should arm — firing costs nothing when the
    payload is 'wake the next layer'."""
    low = text.lower()
    hits, entries = 0, set()
    for r in rows:
        if r.get("class") != "arming":
            continue
        n = 0
        for stem in r.get("stems", []):
            n += low.count(stem.lower())
        for ph in r.get("phrases", []):
            n += low.count(ph.lower())
        if n:
            hits += n
            entries.add(r["id"])
    return hits, len(entries)

def match_situation(text: str, row: dict) -> bool:
    """Presence-only, unit-local, zero model. Each detector kind states a
    fact about what the unit IS, never whether it is justified."""
    low = text.lower()
    det = row.get("detect", {})
    if det.get("anchors"):
        if any(a.lower() in low for a in det["anchors"]):
            return True
    if det.get("tier_min"):
        tiers = len(TIER_TOKEN.findall(text))
        absents = sum(low.count(p.lower()) for p in det.get("absence_phrases", []))
        if tiers >= det["tier_min"] and absents >= det.get("absence_min", 0):
            return True
    fams = det.get("families")
    if fams:
        for phrases in fams.values():
            if any(p.lower() in low for p in phrases):
                return True
    return False

def situations_for(text: str, surface: str):
    return [r for r in load_rows("situations")
            if surface in r.get("surfaces", []) and match_situation(text, r)]

# ----------------------------------------------- claim-vs-record reconciliation

def skill_roster():
    """The roster IS the filesystem — `ls skills/` — so it cannot rot the way
    a hand-kept list would (a stale roster silently stops flagging new
    skills)."""
    d = plugin_root() / "skills"
    try:
        return sorted(p.name for p in d.iterdir() if p.is_dir())
    except OSError:
        return []

def fired_slugs(session_id: str):
    """Skills actually invoked this session, from the shipped telemetry hook's
    log (count-skill-firings.sh). Reading the signal is fine; *gating* on it
    would inherit the firing failure — this only ever supplies the record
    side of a reconciliation and an arming trigger."""
    log = os.environ.get("SKILL_FIRINGS_LOG",
                         os.path.expanduser("~/.claude/logs/skill-firings.log"))
    fired = set()
    try:
        with open(log, encoding="utf-8") as f:
            # tail-bounded: the log is append-only across all sessions.
            for line in f.readlines()[-4000:]:
                try:
                    e = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if e.get("session_id") == session_id:
                    fired.add(normalize_slug(e.get("skill", "")))
    except OSError:
        pass
    return fired

def normalize_slug(name: str) -> str:
    """Bare-slug normalization. The one near-shipped bug in this check's
    prototype was comparing a prose name to a tool-call name unnormalized —
    it flagged the single genuinely-invoked skill as not-fired. This is the
    check's entire risk surface; test_firing_filter.py pins it."""
    s = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")
    for prefix in ("research-toolkit-",):
        if s.startswith(prefix):
            s = s[len(prefix):]
    return s

def claimed_slugs(text: str):
    """A skill counts as CLAIMED only in forms that state 'this methodology
    was applied', not in casual prose:
      * hyphenated slug anywhere ('dialectic-spiral'), or its spaced twin —
        multi-word names are unambiguous;
      * plugin-qualified form ('research-toolkit:research') anywhere;
      * single-word names ('research') additionally on a line containing
        'method' or 'routed via' — 'this research shows' must never flag.
    """
    low = text.lower()
    lines = low.splitlines()
    method_lines = [ln for ln in lines if "method" in ln or "routed via" in ln]
    claimed = set()
    for slug in skill_roster():
        s = slug.lower()
        qualified = f"research-toolkit:{s}"
        if qualified in low:
            claimed.add(s)
            continue
        if "-" in s:
            if s in low or s.replace("-", " ") in low:
                claimed.add(s)
        else:
            if any(s in ln for ln in method_lines):
                claimed.add(s)
    return claimed

def reconcile(text: str, session_id: str):
    fired = fired_slugs(session_id)
    return sorted(c for c in claimed_slugs(text) if c not in fired)

# ------------------------------------------------------------------ payloads

def rec_reason(flags, guidance: str) -> str:
    names = ", ".join(flags)
    return (
        "firing-filter [claim-vs-record]: this unit names methodologies the "
        f"session's own skill ledger shows were never invoked: {names}. "
        "For each, either invoke the skill now, or state in the Method line "
        "that it was applied as prose discipline rather than invoked — "
        "non-invocation is a fact about mechanism, not a verdict on quality. "
        "Then re-send; a content-identical re-send will not be blocked again."
        + ("\n" + guidance if guidance else "")
    )

def announce_line() -> str:
    return ("research-toolkit firing-filter: ARMED (deterministic — zero model "
            "calls; word-hits only arm, situations inject one guidance each, "
            "blocks happen only on claim-vs-record facts, once per unit). "
            "Disable for this session: /research-toolkit:firing-filter off "
            "(disabling removes the toolkit's only layer that fires without "
            "anyone noticing anything).")

# --------------------------------------------------------------------- events

def emit(obj):
    sys.stdout.write(json.dumps(obj) if obj else "{}")

def extract_text(event: str, payload: dict) -> str:
    """One extractor per surface — the only surface-specific code, so a new
    surface is one hooks.json stanza plus one branch here."""
    ti = payload.get("tool_input") or {}
    if event in ("pre-agent",):
        return str(ti.get("prompt", "") or "")
    if event in ("pre-write",):
        # Write carries content; Edit carries new_string (scan what will land
        # on disk, not what is being removed).
        return str(ti.get("content", "") or ti.get("new_string", "") or "")
    if event == "post-agent":
        tr = payload.get("tool_response")
        return _flatten(tr)
    if event == "post-write":
        return str(ti.get("content", "") or ti.get("new_string", "") or "")
    if event == "user-prompt":
        return str(payload.get("prompt", "") or "")
    if event == "stop":
        return last_assistant_text(payload.get("transcript_path", ""))
    return ""

def _flatten(x) -> str:
    if x is None:
        return ""
    if isinstance(x, str):
        return x
    if isinstance(x, list):
        return "\n".join(_flatten(i) for i in x)
    if isinstance(x, dict):
        if isinstance(x.get("text"), str):
            return x["text"]
        return "\n".join(_flatten(v) for v in x.values())
    return str(x)

def last_assistant_text(transcript_path: str) -> str:
    """Final assistant message from the transcript JSONL. Defensive: format
    drift here must degrade to 'no unit' (allow), never to a crash."""
    try:
        lines = Path(transcript_path).read_text(encoding="utf-8").splitlines()
    except OSError:
        return ""
    for line in reversed(lines):
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        msg = e.get("message") or {}
        if (e.get("type") == "assistant" or msg.get("role") == "assistant"):
            content = msg.get("content")
            if isinstance(content, list):
                texts = [b.get("text", "") for b in content
                         if isinstance(b, dict) and b.get("type") == "text"]
                if texts:
                    return "\n".join(texts)
            elif isinstance(content, str) and content:
                return content
    return ""

def maybe_arm(st: dict, text: str, session_id: str, source: str) -> bool:
    """Arming trigger 1: lexicon density on any scanned unit. Trigger 2: a
    research-toolkit skill fired this session. Trigger 3 is the command.
    Once armed, stays armed (per session); DISABLED never self-re-arms —
    a filter that re-arms after being dismissed has overridden the one
    authority the record validates (the human)."""
    if st["mode"] in ("armed", "disabled"):
        return st["mode"] == "armed"
    hits, entries = lexicon_hits(text, load_rows("lexicon")) if text else (0, 0)
    if hits >= ARM_MIN_HITS and entries >= ARM_MIN_ENTRIES:
        st["mode"] = "armed"
        ledger_append(session_id, {"event": "armed", "by": f"lexicon:{source}",
                                   "hits": hits, "entries": entries})
        return True
    if fired_slugs(session_id):
        st["mode"] = "armed"
        ledger_append(session_id, {"event": "armed", "by": "skill-fire"})
        return True
    return False

def handle(event: str, payload: dict) -> dict | None:
    session_id = str(payload.get("session_id", "") or "")
    if event == "session-start":
        seed_assets()
        return None

    st = load_state(session_id)
    if st["mode"] == "disabled":
        # Silent tier-0 ledgering only: zero cost, zero interruption, keeps
        # the learn loop supplied. (Operator may read "off" as "stop even
        # logging" — if so, delete this block; nothing else depends on it.)
        text = extract_text(event, payload)
        if text:
            hits, entries = lexicon_hits(text, load_rows("lexicon"))
            if hits:
                ledger_append(session_id, {"event": "hit-while-disabled",
                                           "surface": event, "hits": hits})
        return None

    text = extract_text(event, payload)
    armed = maybe_arm(st, text, session_id, event)

    out = None
    if event == "user-prompt":
        if armed:
            out = {"hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": announce_line()}}

    elif event == "pre-agent" and armed and text:
        h = unit_hash(text)
        sits = situations_for(text, "dispatch")
        if sits and h not in st["seen"] and st["s2_denials"] < S2_SESSION_CAP:
            st["seen"].append(h)
            st["s2_denials"] += 1
            guidance = "\n".join(s["guidance"] for s in sits)
            ledger_append(session_id, {"event": "flag", "surface": "pre-agent",
                                       "unit": h,
                                       "situations": [s["id"] for s in sits],
                                       "action": "deny-once"})
            out = {"hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason":
                    "firing-filter [situation — fires once per dispatch]:\n"
                    + guidance
                    + "\nRevise if warranted, then re-send; a re-send is not "
                      "blocked again this session."}}

    elif event == "post-agent" and armed and text:
        h = unit_hash(text)
        sits = situations_for(text, "return")
        if sits and h not in st["seen"]:
            st["seen"].append(h)
            ledger_append(session_id, {"event": "flag", "surface": "post-agent",
                                       "unit": h,
                                       "situations": [s["id"] for s in sits],
                                       "action": "inject"})
            out = {"hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext":
                    "firing-filter [situation]:\n" +
                    "\n".join(s["guidance"] for s in sits)}}

    elif event == "pre-write" and armed and text:
        h = unit_hash(text)
        sits = situations_for(text, "write")
        if sits and h not in st["seen"]:
            flags = reconcile(text, session_id)
            if flags:
                st["seen"].append(h)
                guidance = "\n".join(s["guidance"] for s in sits)
                ledger_append(session_id, {"event": "flag", "surface": "pre-write",
                                           "unit": h, "rec_flags": flags,
                                           "action": "deny-once"})
                out = {"hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": rec_reason(flags, guidance)}}
            # No fact-flags: the situation guidance arrives via post-write
            # injection instead — a clean verdict write is never blocked.

    elif event == "post-write" and armed and text:
        h = unit_hash("post:" + text)
        sits = situations_for(text, "write")
        if sits and h not in st["seen"]:
            st["seen"].append(h)
            ledger_append(session_id, {"event": "flag", "surface": "post-write",
                                       "unit": h,
                                       "situations": [s["id"] for s in sits],
                                       "action": "inject"})
            out = {"hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext":
                    "firing-filter [situation]:\n" +
                    "\n".join(s["guidance"] for s in sits)}}

    elif event == "stop" and armed and text:
        h = unit_hash(text)
        sits = situations_for(text, "stop")
        if sits and h not in st["seen"] and not payload.get("stop_hook_active"):
            flags = reconcile(text, session_id)
            if flags:
                st["seen"].append(h)
                ledger_append(session_id, {"event": "flag", "surface": "stop",
                                           "unit": h, "rec_flags": flags,
                                           "action": "block-once"})
                out = {"decision": "block",
                       "reason": rec_reason(
                           flags, "\n".join(s["guidance"] for s in sits))}
            else:
                ledger_append(session_id, {"event": "flag", "surface": "stop",
                                           "unit": h,
                                           "situations": [s["id"] for s in sits],
                                           "action": "ledger"})

    save_state(session_id, st)
    return out

# ------------------------------------------------------------------ CLI mode

def cli(args):
    """`firing_filter.py cmd status|on|off <session_id>` — backs the
    /research-toolkit:firing-filter command. State is per-session; `off` does
    not self-re-arm (the human's dismissal is the one authority on record)."""
    action = args[0] if args else "status"
    session_id = args[1] if len(args) > 1 else "manual"
    st = load_state(session_id)
    if action == "on":
        st["mode"] = "armed"
        save_state(session_id, st)
        ledger_append(session_id, {"event": "armed", "by": "command"})
        print("firing-filter: ARMED (by command).")
    elif action == "off":
        st["mode"] = "disabled"
        save_state(session_id, st)
        ledger_append(session_id, {"event": "disabled", "by": "command"})
        print("firing-filter: DISABLED for this session (will not re-arm "
              "itself; re-enable with `on`). Note: disabling removes the "
              "toolkit's only layer that fires without anyone noticing "
              "anything; tier-0 hits are still ledgered silently.")
    else:
        local_rows = sum(len(_read_jsonl(p))
                         for p in (data_dir() / "local").glob("*.jsonl"))
        ledgers = list((data_dir() / "ledger").glob("*.jsonl"))
        print(f"firing-filter status: mode={st['mode']} "
              f"(session {session_id})\n"
              f"  local rows: {local_rows} — these die with plugin uninstall "
              f"unless you pass --keep-data; PR them upstream to make them "
              f"permanent (each carries its provenance).\n"
              f"  ledgers: {len(ledgers)} session file(s) under "
              f"{data_dir() / 'ledger'}")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "cmd":
        cli(sys.argv[2:])
        return
    event = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        payload = {}
    try:
        out = handle(event, payload)
    except Exception as e:  # fail OPEN, loudly in the ledger, never block work
        try:
            ledger_append(str(payload.get("session_id", "")),
                          {"event": "SCAN-FAILED", "surface": event,
                           "error": f"{type(e).__name__}: {e}"})
        except Exception:
            pass
        out = None
    emit(out)
    sys.exit(0)

if __name__ == "__main__":
    main()
