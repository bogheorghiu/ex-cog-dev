#!/usr/bin/env python3
"""skilltest - the statistics-and-bookkeeping layer over `claude plugin eval`.

`claude plugin eval` (Claude Code >= 2.1.269) already runs live turns against a
plugin, repeats them, and grades each run. This tool does not run anything. It
supplies what that runner leaves out, and what this skill's discipline needs:

  validate  a run design (cases as data) against the discipline before any run
  emit      the design as plugin-eval case dirs, so the frozen design IS the input
  score     plugin-eval results -> per-case rates with intervals, per-class rates,
            arm differences with paired intervals, and the pre-registered ship
            rule evaluated mechanically (SHIP / NO-SHIP / VOID)
  power     how small a difference a planned run could detect at all

Stdlib only, so it runs anywhere `python3` does. See references/protocol.md for
when to use each subcommand; the design schema is enforced by `validate`, and its
error messages are the schema documentation.
"""

import argparse
import hashlib
import json
import math
import os
import random
import re
import sys
from pathlib import Path

CLASSES = ("clear", "oblique", "control", "trap", "offtopic")
POSITIVE = ("clear", "oblique", "control")
NEGATIVE = ("trap", "offtopic")
OPS = {
    ">": lambda a, b: a > b,
    ">=": lambda a, b: a >= b,
    "<": lambda a, b: a < b,
    "<=": lambda a, b: a <= b,
}
MIN_RUNS = 5
DEFAULT_VOID_ERROR_RATE = 0.10
BOOTSTRAP_DRAWS = 4000
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
FIRED_PREFIX = "fired:"
ANY_SKILL = "*"


# --------------------------------------------------------------------------- design

def load_design(path):
    raw = Path(path).read_bytes()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def arm_target(design, label=None):
    """The skill name that fires in this arm. Differs from design["target"] only in a
    rename A/B, where arm_targets maps each arm label to its own name."""
    return (design.get("arm_targets") or {}).get(label, design["target"])


def case_prompt(design, case, label=None):
    # Only a control names the skill; "{target}" lets one control serve both arms of a rename.
    return case["prompt"].replace("{target}", arm_target(design, label))


def validate(design):
    """Return (errors, warnings). Errors block emit/score; warnings are printed."""
    errors, warnings = [], []
    if design.get("schema") != "skilltest-design/1":
        errors.append('schema must be "skilltest-design/1"')
    target = design.get("target", "")
    if not NAME_RE.match(target or ""):
        errors.append("target must be a bare skill name (kebab-case, no plugin prefix)")
    arm_targets = design.get("arm_targets") or {}
    if not isinstance(arm_targets, dict) or not all(NAME_RE.match(str(v)) for v in arm_targets.values()):
        errors.append("arm_targets, if given, maps arm label -> bare skill name (for a rename A/B)")
        arm_targets = {}
    names = {target, *arm_targets.values()} - {""}
    if not design.get("model"):
        errors.append("model is required: the session model is part of the instrument "
                      "(discipline #6) and must be pinned, never inherited")
    runs = design.get("runs")
    if not isinstance(runs, int) or runs < 1:
        errors.append("runs must be a positive integer")
    elif runs < MIN_RUNS:
        warnings.append(f"runs={runs} < {MIN_RUNS}: live firing is stochastic; "
                        "a per-case rate from fewer runs is barely a rate")
    cases = design.get("cases")
    if not isinstance(cases, list) or not cases:
        errors.append("cases must be a non-empty list")
        return errors, warnings

    seen = set()
    name_tokens = sorted({t for n in names for t in n.split("-") if len(t) > 3})
    for i, c in enumerate(cases):
        where = f"cases[{i}]"
        cid = c.get("id", "")
        if not ID_RE.match(str(cid)):
            errors.append(f"{where}: id must match {ID_RE.pattern}")
        elif cid in seen:
            errors.append(f"{where}: duplicate id {cid}")
        seen.add(cid)
        cls = c.get("class")
        if cls not in CLASSES:
            errors.append(f"{where}: class must be one of {CLASSES}")
            continue
        prompt = c.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            errors.append(f"{where}: prompt must be non-empty text")
            continue
        expect = c.get("expect")
        if not isinstance(expect, str) or not expect:
            errors.append(f"{where}: expect must name the skill that should win the turn, "
                          'or "none" - an unnamed winner makes 0 recall unreadable')
            continue
        if cls in POSITIVE and expect != target:
            errors.append(f"{where}: a {cls} case must expect the target ({target})")
        if cls == "offtopic" and expect != "none":
            errors.append(f'{where}: an offtopic case must expect "none"')
        if cls == "trap" and expect == target:
            errors.append(f"{where}: a trap expects a sibling or \"none\", never the target")
        siblings = c.get("siblings", [])
        if not isinstance(siblings, list) or not all(NAME_RE.match(s or "") for s in siblings):
            errors.append(f"{where}: siblings must be a list of bare skill names")
        elif cls == "trap" and expect != "none" and expect not in siblings:
            errors.append(f"{where}: a trap's expected sibling must also be listed in siblings")
        lowered = prompt.lower()
        if cls == "oblique":
            # A shared word is not always the cue (a skill-testing skill's oblique turn may
            # still say "SKILL.md"), so token overlap warns; the full name is an error below.
            leaks = [t for t in name_tokens if t in lowered]
            if leaks:
                warnings.append(f"{where}: oblique prompt shares words with the target's name "
                                f"({leaks}) - confirm none of them is the lexical cue")
        if cls != "control" and any(n in lowered for n in names):
            errors.append(f"{where}: only a control case may name the target skill")
        if cls != "control" and "{target}" in prompt:
            errors.append(f"{where}: the {{target}} placeholder is for control cases only")
        if any(ord(ch) > 127 for ch in prompt):
            warnings.append(f"{where}: non-ASCII prompt - fine in YAML, but a tracked .json "
                            "design must be ASCII-only (CLAUDE.md); keep the design file untracked or escape-free")

    classes = {c.get("class") for c in cases}
    if "oblique" not in classes:
        warnings.append("no oblique cases: the run cannot discriminate (discipline #3 - ceiling "
                        "first, discriminate second)")
    if "trap" not in classes:
        warnings.append("no trap cases: recall without precision is half a result (discipline #4)")

    plugins = design.get("plugins")
    if plugins is not None and (not isinstance(plugins, list) or not plugins
                                or not all(isinstance(x, str) and x and not os.path.isabs(x) for x in plugins)):
        errors.append("plugins, if given, must be a non-empty list of plugin dirs relative to the "
                      "directory plugin eval runs against (the catalog of the competitive condition)")

    for j, cond in enumerate(design.get("ship_rule", []) or []):
        if not (isinstance(cond, list) and len(cond) == 3 and cond[1] in OPS
                and isinstance(cond[2], (int, float)) and isinstance(cond[0], str)):
            errors.append(f"ship_rule[{j}] must be [metric, op, number] with op in {list(OPS)}")
    if not design.get("ship_rule"):
        warnings.append("no ship_rule: score will report numbers but cannot decide; if this run "
                        "gates a ship, write the rule before running (preregister-ship-decision)")
    return errors, warnings


# --------------------------------------------------------------------------- emit

def _q(s):
    # A JSON string is a valid YAML double-quoted scalar.
    return json.dumps(s)


# plugin eval rejects weight 0 and, under --ablation none, scores every grader; this
# weight keeps the indicators from moving its own score off the expect grader's.
INDICATOR_WEIGHT = 0.001


def _fired_grader(skill, weight=INDICATOR_WEIGHT):
    if skill == ANY_SKILL:
        match = None
    else:
        match = r'"skill"\s*:\s*"(?:[\w-]+:)?' + re.escape(skill) + '"'
    lines = [f"  - name: {_q(FIRED_PREFIX + skill)}",
             "    type: tool_used",
             "    tool: Skill",
             f"    weight: {weight}"]
    if match:
        lines.append(f"    input_match: {_q(match)}")
    return lines


def case_yaml(design, case, design_hash, plugin_paths=None, arm=None):
    target = arm_target(design, arm)
    match = r'"skill"\s*:\s*"(?:[\w-]+:)?' + re.escape(target) + '"'
    expect_lines = ["  - name: \"expect\"",
                    "    type: tool_used",
                    "    tool: Skill",
                    f"    input_match: {_q(match)}"]
    if case["class"] in NEGATIVE:
        expect_lines += ["    min: 0", "    max: 0"]
    out = [
        'schema_version: "1.1"',
        f"name: {_q(case['id'])}",
        f"description: {_q('skilltest ' + case['class'] + ' case; design sha256 ' + design_hash)}",
        f"tags: [{_q('skilltest')}, {_q(case['class'])}]",
        f"runs: {design['runs']}",
    ] + ([f"plugins: {json.dumps(plugin_paths)}"] if plugin_paths else []) + [
        "execution:",
        f"  model: {_q(design['model'])}",
        f"  max_turns: {design.get('max_turns', 3)}",
        f"  allowed_tools: {json.dumps(design.get('allowed_tools', ['Skill']))}",
        f"  prompt: {_q(case_prompt(design, case, arm))}",
        "graders:",
    ] + expect_lines
    for skill in [target] + list(case.get("siblings", [])) + [ANY_SKILL]:
        out += _fired_grader(skill)
    return "\n".join(out) + "\n"


def emit(design, design_hash, out_dir, root=None, arm=None):
    """root: the directory plugin eval will run against (default: out_dir's parent).
    design["plugins"] is relative to it; case.yaml wants paths relative to the case dir."""
    out = Path(out_dir).resolve()
    root = Path(root).resolve() if root else out.parent
    for case in design["cases"]:
        d = out / case["id"]
        d.mkdir(parents=True, exist_ok=True)
        paths = None
        if design.get("plugins"):
            paths = [os.path.relpath(root / p, d) for p in design["plugins"]]
        (d / "case.yaml").write_text(case_yaml(design, case, design_hash, paths, arm), encoding="utf-8")
    return len(design["cases"])


# --------------------------------------------------------------------------- results

def read_runs(result_path, arm_key):
    """Plugin-eval aggregate-result.json -> {case_name: [run, ...]} for one arm."""
    data = json.loads(Path(result_path).read_text(encoding="utf-8"))
    meta = {
        "claudeVersion": data.get("claudeVersion"),
        "modelOverride": (data.get("suite") or {}).get("modelOverride"),
        "plugins": (data.get("suite") or {}).get("plugins"),
        "partial": data.get("partial"),
    }
    cases = {}
    for c in data.get("cases", []):
        runs = []
        for r in (c.get("arms") or {}).get(arm_key, []) or []:
            fired = set()
            graders = {}
            for g in r.get("graders", []):
                graders[g.get("name")] = bool(g.get("passed"))
                name = g.get("name") or ""
                if name.startswith(FIRED_PREFIX) and g.get("passed"):
                    fired.add(name[len(FIRED_PREFIX):])
            runs.append({
                "error": r.get("error") or r.get("aborted"),
                "fired": fired,
                "graders": graders,
                "score": r.get("score"),
                "passed": bool(r.get("passed")),
            })
        cases[c.get("name")] = {"runs": runs, "prompt": c.get("promptMarkdown")}
    return cases, meta


def classify(run, case, target):
    """Which outcome class a run landed in. Order matters: the target outranks all."""
    fired = run["fired"]
    if target in fired:
        return "target"
    expect = case["expect"]
    if expect not in (target, "none") and expect in fired:
        return "expected-sibling"
    if any(s in fired for s in case.get("siblings", [])):
        return "sibling"
    if ANY_SKILL in fired:
        return "other"
    return "nothing"


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, centre - half), min(1.0, centre + half))


def _pooled(per_case, ids):
    k = sum(per_case[i][0] for i in ids)
    n = sum(per_case[i][1] for i in ids)
    return k / n if n else float("nan")


def _percentile(xs, q):
    xs = sorted(x for x in xs if not math.isnan(x))
    if not xs:
        return float("nan")
    pos = q * (len(xs) - 1)
    lo, hi = math.floor(pos), math.ceil(pos)
    return xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)


def cluster_ci(per_case, ids, rng, draws=BOOTSTRAP_DRAWS):
    """Interval for a pooled rate, resampling CASES, not runs: runs of one prompt are
    correlated, so treating them as independent would make the interval too narrow."""
    ids = list(ids)
    if not ids:
        return (float("nan"), float("nan"))
    stats = [_pooled(per_case, [rng.choice(ids) for _ in ids]) for _ in range(draws)]
    return (_percentile(stats, 0.025), _percentile(stats, 0.975))


def paired_diff_ci(a, b, ids, rng, draws=BOOTSTRAP_DRAWS):
    """Interval for rate(a) - rate(b) over the same cases, resampling cases jointly."""
    ids = list(ids)
    if not ids:
        return (float("nan"), float("nan"))
    stats = []
    for _ in range(draws):
        pick = [rng.choice(ids) for _ in ids]
        stats.append(_pooled(a, pick) - _pooled(b, pick))
    return (_percentile(stats, 0.025), _percentile(stats, 0.975))


def sign_flip_p(deltas, rng, max_exact=14, draws=20000):
    """Two-sided p for 'mean per-case delta is zero', by flipping the sign of each case's
    delta (the method adewale/skill-eval-harness uses). Exact up to max_exact non-zero
    cases, Monte Carlo above. Unlike the bootstrap it stays valid at a handful of cases -
    and it shows plainly when a design CANNOT reach significance: 3 cases floor at p=.25."""
    ds = [d for d in deltas if d != 0]
    if not ds:
        return 1.0
    obs = abs(sum(ds)) - 1e-12
    if len(ds) <= max_exact:
        hits = total = 0
        for mask in range(1 << len(ds)):
            s = sum(-d if (mask >> i) & 1 else d for i, d in enumerate(ds))
            hits += abs(s) >= obs
            total += 1
        return hits / total
    hits = sum(abs(sum(d if rng.random() < 0.5 else -d for d in ds)) >= obs for _ in range(draws))
    return (hits + 1) / (draws + 1)


def _rate_deltas(a, b, ids):
    return [(a[i][0] / a[i][1]) - (b[i][0] / b[i][1]) for i in ids if a[i][1] and b[i][1]]


def summarise_arm(design, cases_runs, target):
    """Per-case tallies for one arm: target-fired k/n, outcome classes, run scores."""
    per_case, errors, total = {}, 0, 0
    for case in design["cases"]:
        runs = cases_runs.get(case["id"], {"runs": []})["runs"]
        good = [r for r in runs if not r["error"]]
        total += len(runs)
        errors += len(runs) - len(good)
        outcome = {}
        for r in good:
            cls = classify(r, case, target)
            outcome[cls] = outcome.get(cls, 0) + 1
        scores = [r["score"] for r in good if isinstance(r["score"], (int, float))]
        per_case[case["id"]] = {
            "k": outcome.get("target", 0),
            "n": len(good),
            "outcome": outcome,
            "score_sum": sum(scores),
            "score_n": len(scores),
        }
    return per_case, errors, total


def score(design, design_hash, arms, seed=None):
    """arms: list of (label, result_path, arm_key). Returns a report dict."""
    rng = random.Random(seed if seed is not None else int(design_hash[:12], 16))
    void, notes, summaries = [], [], {}
    void_rate = design.get("void_error_rate", DEFAULT_VOID_ERROR_RATE)
    ids_by_class = {cls: [c["id"] for c in design["cases"] if c["class"] == cls] for cls in CLASSES}

    for label, path, arm_key in arms:
        runs, meta = read_runs(path, arm_key)
        missing = [c["id"] for c in design["cases"] if c["id"] not in runs]
        if missing:
            void.append(f"{label}: cases in the design but not in the results: {missing}")
        for c in design["cases"]:
            got = (runs.get(c["id"]) or {}).get("prompt")
            if got is not None and got.strip() != case_prompt(design, c, label).strip():
                void.append(f"{label}: case {c['id']} ran a different prompt than the frozen design")
        if meta["modelOverride"] and meta["modelOverride"] != design["model"]:
            void.append(f"{label}: ran on model {meta['modelOverride']}, design pins {design['model']}")
        elif not meta["modelOverride"]:
            # The results record only the --model flag, not case.yaml's execution.model.
            notes.append(f"{label}: results do not record the model; rerun plugin eval with "
                         f"--model {design['model']} so the pin is checkable, not assumed")
        if design.get("plugins"):
            ran = sorted(Path(p.get("path") or "").name for p in (meta["plugins"] or []))
            want = sorted(Path(p).name for p in design["plugins"])
            if ran != want:
                void.append(f"{label}: catalog {ran} differs from the design's plugins {want}")
        if meta["partial"]:
            void.append(f"{label}: plugin eval reported a partial run")
        per_case, errors, total = summarise_arm(design, runs, arm_target(design, label))
        if total and errors / total > void_rate:
            void.append(f"{label}: {errors}/{total} runs errored (> {void_rate:.0%})")
        short = [cid for cid, pc in per_case.items() if pc["n"] < design["runs"]]
        if short:
            notes.append(f"{label}: fewer than {design['runs']} usable runs for {short}")
        summaries[label] = {"per_case": per_case, "meta": meta, "errors": errors, "total": total}

    metrics = {}
    for label, s in summaries.items():
        pc = {cid: (v["k"], v["n"]) for cid, v in s["per_case"].items()}
        sc = {cid: (v["score_sum"], v["score_n"]) for cid, v in s["per_case"].items()}
        for cls, ids in ids_by_class.items():
            if not ids:
                continue
            kind = "recall" if cls in POSITIVE else "false_fire"
            metrics[f"{label}.{kind}.{cls}"] = _pooled(pc, ids)
            lo, hi = cluster_ci(pc, ids, rng)
            metrics[f"{label}.{kind}.{cls}.ci_lo"] = lo
            metrics[f"{label}.{kind}.{cls}.ci_hi"] = hi
        all_ids = [c["id"] for c in design["cases"]]
        if any(v["score_n"] for v in s["per_case"].values()):
            metrics[f"{label}.score.all"] = _pooled(sc, all_ids)
            lo, hi = cluster_ci(sc, all_ids, rng)
            metrics[f"{label}.score.all.ci_lo"] = lo
            metrics[f"{label}.score.all.ci_hi"] = hi

    labels = list(summaries)
    for i, a in enumerate(labels):
        for b in labels[i + 1:]:
            pa = {cid: (v["k"], v["n"]) for cid, v in summaries[a]["per_case"].items()}
            pb = {cid: (v["k"], v["n"]) for cid, v in summaries[b]["per_case"].items()}
            for cls, ids in ids_by_class.items():
                if not ids:
                    continue
                kind = "recall" if cls in POSITIVE else "false_fire"
                key = f"diff({a}-{b}).{kind}.{cls}"
                metrics[key] = _pooled(pa, ids) - _pooled(pb, ids)
                lo, hi = paired_diff_ci(pa, pb, ids, rng)
                metrics[key + ".ci_lo"], metrics[key + ".ci_hi"] = lo, hi
                metrics[key + ".p"] = sign_flip_p(_rate_deltas(pa, pb, ids), rng)
            sa = {cid: (v["score_sum"], v["score_n"]) for cid, v in summaries[a]["per_case"].items()}
            sb = {cid: (v["score_sum"], v["score_n"]) for cid, v in summaries[b]["per_case"].items()}
            if any(n for _, n in sa.values()) and any(n for _, n in sb.values()):
                all_ids = [c["id"] for c in design["cases"]]
                key = f"diff({a}-{b}).score.all"
                metrics[key] = _pooled(sa, all_ids) - _pooled(sb, all_ids)
                lo, hi = paired_diff_ci(sa, sb, all_ids, rng)
                metrics[key + ".ci_lo"], metrics[key + ".ci_hi"] = lo, hi
                metrics[key + ".p"] = sign_flip_p(_rate_deltas(sa, sb, all_ids), rng)

    decision, rule_lines = None, []
    rule = design.get("ship_rule") or []
    if void:
        decision = "VOID"
    elif rule:
        ok = True
        for metric, op, value in rule:
            got = metrics.get(metric)
            if got is None or (isinstance(got, float) and math.isnan(got)):
                void.append(f"ship_rule metric {metric} was not computed by this run")
                ok = None
                break
            held = OPS[op](got, value)
            rule_lines.append(f"{metric} = {got:.3f} {op} {value}: {'holds' if held else 'FAILS'}")
            ok = ok and held
        decision = "VOID" if ok is None else ("SHIP" if ok else "NO-SHIP")

    return {
        "design_sha256": design_hash,
        "target": design["target"],
        "model": design["model"],
        "summaries": summaries,
        "metrics": metrics,
        "decision": decision,
        "rule_lines": rule_lines,
        "void": void,
        "notes": notes,
    }


def render(report, design):
    out = [f"design sha256 {report['design_sha256']}",
           f"target {report['target']}   session model (pinned) {report['model']}"]
    for label, s in report["summaries"].items():
        m = s["meta"]
        out.append(f"\n== arm {label}: claude {m['claudeVersion']}, model {m['modelOverride']}, "
                   f"plugins {[(p.get('name'), p.get('version')) for p in (m['plugins'] or [])]}, "
                   f"errored runs {s['errors']}/{s['total']}")
        for c in design["cases"]:
            pc = s["per_case"][c["id"]]
            lo, hi = wilson(pc["k"], pc["n"])
            outcomes = ", ".join(f"{k} {v}" for k, v in sorted(pc["outcome"].items()))
            out.append(f"  {c['id']:<12} {c['class']:<8} expect {c['expect']:<24} target fired "
                       f"{pc['k']}/{pc['n']} [{lo:.2f}, {hi:.2f}]   ({outcomes})")
    out.append("\n== metrics (pooled over runs; [interval] resamples cases - percentile bootstrap, "
               "too narrow below ~10 cases per class; p is the exact sign-flip test on per-case deltas)")
    for k in sorted(report["metrics"]):
        if k.endswith((".ci_lo", ".ci_hi", ".p")):
            continue
        v = report["metrics"][k]
        lo = report["metrics"].get(k + ".ci_lo")
        hi = report["metrics"].get(k + ".ci_hi")
        p = report["metrics"].get(k + ".p")
        span = f" [{lo:.2f}, {hi:.2f}]" if lo is not None else ""
        span += f" sign-flip p={p:.3f}" if p is not None else ""
        out.append(f"  {k} = {v:.3f}{span}")
    for n in report["notes"]:
        out.append(f"note: {n}")
    for v in report["void"]:
        out.append(f"VOID: {v}")
    for line in report["rule_lines"]:
        out.append(f"rule: {line}")
    out.append(f"\nDECISION: {report['decision'] or 'none (no ship_rule in design)'}")
    out.append("Validity limit: plugin eval loads only the plugin(s) under test, so the catalog is the "
               "plugin itself - this measures firing under intra-plugin competition, not under a full "
               "installed catalog.")
    return "\n".join(out)


# --------------------------------------------------------------------------- power

def _z(p):
    # Inverse standard normal CDF (Acklam), enough precision for planning.
    a = [-3.969683028665376e01, 2.209460984245205e02, -2.759285104469687e02,
         1.383577518672690e02, -3.066479806614716e01, 2.506628277459239e00]
    b = [-5.447609879822406e01, 1.615858368580409e02, -1.556989798598866e02,
         6.680131188771972e01, -1.328068155288572e01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e00,
         -2.549671010149854e00, 4.374664141464968e00, 2.938163982698783e00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e00,
         3.754408661907416e00]
    if p < 0.02425:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > 1 - 0.02425:
        return -_z(1 - p)
    q = p - 0.5
    r = q * q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


def mde(p0, cases, runs, icc, alpha=0.05, power=0.8):
    """Smallest absolute rise over baseline rate p0 a two-arm comparison can detect.

    Effective sample per arm = cases*runs / (1 + (runs-1)*icc): repeated runs of one
    prompt are correlated (icc), so ten runs of one case are worth far less than ten
    cases. Normal approximation; a planning number, not a guarantee."""
    n_eff = cases * runs / (1 + (runs - 1) * icc)
    za, zb = _z(1 - alpha / 2), _z(power)
    delta = 0.0
    for _ in range(100):  # fixed-point on the variance at p1 = p0 + delta
        p1 = min(0.999, p0 + delta)
        delta = (za + zb) * math.sqrt((p0 * (1 - p0) + p1 * (1 - p1)) / n_eff)
    return delta, n_eff


# --------------------------------------------------------------------------- cli

def _parse_arm(spec):
    # LABEL=path[:with|:without]
    if "=" not in spec:
        raise argparse.ArgumentTypeError("arm must be LABEL=path[:with|:without]")
    label, rest = spec.split("=", 1)
    key = "with"
    for suffix in (":with", ":without"):
        if rest.endswith(suffix):
            rest, key = rest[: -len(suffix)], suffix[1:]
    return (label, rest, key)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="skilltest", description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate", help="check a run design against the discipline")
    v.add_argument("design")
    e = sub.add_parser("emit", help="write the design as plugin-eval case dirs")
    e.add_argument("design")
    e.add_argument("out_dir", help="<root>/<evals dir>; run `claude plugin eval <root> --eval-dir <evals dir>`")
    e.add_argument("--root", help="directory plugin eval will run against (default: out_dir's parent)")
    e.add_argument("--arm", help="arm label; required when the design has arm_targets (a rename A/B)")
    s = sub.add_parser("score", help="score plugin-eval results against the design")
    s.add_argument("design")
    s.add_argument("--arm", action="append", type=_parse_arm, required=True,
                   help="LABEL=aggregate-result.json[:with|:without]; repeat for each arm")
    s.add_argument("--json", help="also write the full report as JSON here")
    s.add_argument("--seed", type=int, help="bootstrap seed (default: derived from the design hash)")
    p = sub.add_parser("power", help="minimum detectable effect for a planned run")
    p.add_argument("--p0", type=float, required=True, help="baseline rate in the comparison arm")
    p.add_argument("--cases", type=int, required=True)
    p.add_argument("--runs", type=int, required=True)
    p.add_argument("--icc", type=float, required=True,
                   help="within-case correlation of runs (0 = independent, 1 = every run identical); "
                        "unknown? plan with 0.3 and 0.6 and read both")
    args = ap.parse_args(argv)

    if args.cmd == "power":
        delta, n_eff = mde(args.p0, args.cases, args.runs, args.icc)
        print(f"effective n per arm {n_eff:.1f}; minimum detectable rise over p0={args.p0:.2f}: "
              f"{delta:.3f} (alpha .05 two-sided, power .80)")
        return 0

    design, digest = load_design(args.design)
    errors, warnings = validate(design)
    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)
    for err in errors:
        print(f"error: {err}", file=sys.stderr)
    if errors:
        return 2
    if args.cmd == "validate":
        print(f"ok: {len(design['cases'])} cases, design sha256 {digest}")
        return 0
    if args.cmd == "emit":
        if design.get("arm_targets") and args.arm not in design["arm_targets"]:
            print(f"error: this design renames the target per arm; pass --arm one of "
                  f"{sorted(design['arm_targets'])}", file=sys.stderr)
            return 2
        n = emit(design, digest, args.out_dir, args.root, args.arm)
        print(f"wrote {n} case dirs under {args.out_dir} (design sha256 {digest})")
        return 0
    report = score(design, digest, args.arm, seed=args.seed)
    print(render(report, design))
    if args.json:
        Path(args.json).write_text(json.dumps(report, indent=2, default=sorted), encoding="utf-8")
    return {"SHIP": 0, "NO-SHIP": 1, "VOID": 3}.get(report["decision"], 0)


if __name__ == "__main__":
    sys.exit(main())
