#!/usr/bin/env python3
"""Unit tests for skilltest.py. Stdlib only; no network, no `claude` calls.

The result fixtures mirror the aggregate-result.json shape that `claude plugin
eval` 2.1.295 actually wrote in a live run (cases[].arms.with[].graders[] with
name/passed, cases[].promptMarkdown, suite.modelOverride). Exits non-zero on
failure.
"""

import copy
import importlib.util
import json
import math
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("skilltest", _HERE / "skilltest.py")
st = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(st)

failures = 0


def check(label, condition):
    global failures
    print(f"   {'ok  ' if condition else 'FAIL'} {label}")
    if not condition:
        failures += 1


DESIGN = {
    "schema": "skilltest-design/1",
    "target": "skill-activation-testing",
    "model": "sonnet",
    "runs": 5,
    "cases": [
        {"id": "C1", "class": "clear", "expect": "skill-activation-testing",
         "prompt": "Help me A/B test whether my skill description fires.",
         "siblings": ["intrinsic-prompt-design"]},
        {"id": "O1", "class": "oblique", "expect": "skill-activation-testing",
         "prompt": "I changed one line in a SKILL.md and I am not sure it made any difference.",
         "siblings": ["intrinsic-prompt-design"]},
        {"id": "T1", "class": "trap", "expect": "intrinsic-prompt-design",
         "prompt": "Rewrite this system prompt so the model follows it more reliably.",
         "siblings": ["intrinsic-prompt-design"]},
        {"id": "N1", "class": "offtopic", "expect": "none",
         "prompt": "What is the boiling point of water at 2000 m?"},
    ],
    "ship_rule": [["NEW.recall.oblique", ">=", 0.6], ["NEW.false_fire.trap", "<=", 0.2]],
}


def raises_exit(fn):
    try:
        fn()
        return False
    except SystemExit:
        return True


def errs(design):
    return st.validate(design)[0]


def run(fired=(), error=None, score=None):
    return {"score": score if score is not None else 1.0, "passed": True, "error": error,
            "graders": [{"name": "expect", "passed": True}]
            + [{"name": st.FIRED_PREFIX + s, "passed": True} for s in fired]}


def result(per_case, model="sonnet", prompts=None, partial=False, arm="with"):
    """per_case: {case_id: [run, ...]} -> plugin-eval-shaped dict."""
    cases = []
    for c in DESIGN["cases"]:
        if c["id"] not in per_case:
            continue
        cases.append({"name": c["id"],
                      "promptMarkdown": (prompts or {}).get(c["id"], c["prompt"]) or c["prompt"],
                      "arms": {arm: per_case[c["id"]]}})
    return {"schemaVersion": 1, "claudeVersion": "2.1.295", "partial": partial,
            "suite": {"modelOverride": model, "plugins": [{"name": "makers-toolkit", "version": "x"}]},
            "cases": cases}


def write(tmp, name, data):
    p = Path(tmp) / name
    p.write_text(json.dumps(data))
    return str(p)


T = "skill-activation-testing"
SIB = "intrinsic-prompt-design"

print("validate")
check("a sound design has no errors", errs(DESIGN) == [])
d = copy.deepcopy(DESIGN); del d["model"]
check("missing model is an error (model is part of the instrument)", any("model" in e for e in errs(d)))
d = copy.deepcopy(DESIGN); d["cases"][1]["prompt"] = "Does my activation wording fire?"
check("an oblique prompt sharing a target-name word warns",
      errs(d) == [] and any("activation" in w for w in st.validate(d)[1]))
d = copy.deepcopy(DESIGN); d["cases"][1]["prompt"] = "is skill-activation-testing right here?"
check("an oblique prompt carrying the full target name is rejected", any("control" in e for e in errs(d)))
d = copy.deepcopy(DESIGN); d["cases"][0]["prompt"] = "use skill-activation-testing please"
check("only a control may name the target", any("control" in e for e in errs(d)))
d = copy.deepcopy(DESIGN); d["cases"][2]["expect"] = T
check("a trap may not expect the target", any("trap" in e for e in errs(d)))
d = copy.deepcopy(DESIGN); d["cases"][2]["siblings"] = []
check("a trap's expected sibling must be listed", any("siblings" in e for e in errs(d)))
d = copy.deepcopy(DESIGN); d["cases"][0]["expect"] = SIB
check("a positive must expect the target", any("must expect the target" in e for e in errs(d)))
d = copy.deepcopy(DESIGN); d["cases"][3]["expect"] = SIB
check('an offtopic case must expect "none"', any("offtopic" in e for e in errs(d)))
d = copy.deepcopy(DESIGN); d["cases"][1]["id"] = "C1"
check("duplicate ids are rejected", any("duplicate" in e for e in errs(d)))
d = copy.deepcopy(DESIGN); d["ship_rule"] = [["NEW.recall.oblique", "=>", 0.6]]
check("a malformed ship rule is rejected", any("ship_rule" in e for e in errs(d)))
d = copy.deepcopy(DESIGN); d["target"] = None
check("a non-string target is a reported error, not a crash", any("target" in e for e in errs(d)))
d = copy.deepcopy(DESIGN); d["cases"][0]["siblings"] = [T]
check("a sibling list containing the target is rejected", any("distinct" in e for e in errs(d)))
d = copy.deepcopy(DESIGN); d["cases"][0]["siblings"] = [SIB, SIB]
check("a repeated sibling is rejected", any("distinct" in e for e in errs(d)))
d = copy.deepcopy(DESIGN); d["runs"] = 3
check("runs below 5 warns but does not error",
      errs(d) == [] and any("runs=3" in w for w in st.validate(d)[1]))
d = copy.deepcopy(DESIGN); d["cases"] = [c for c in d["cases"] if c["class"] != "trap"]
check("a design with no trap warns", any("no trap" in w for w in st.validate(d)[1]))

print("emit")
with tempfile.TemporaryDirectory() as tmp:
    n = st.emit(DESIGN, "abc123", tmp)
    clear = (Path(tmp) / "C1" / "case.yaml").read_text()
    trap = (Path(tmp) / "T1" / "case.yaml").read_text()
    check("one case dir per case", n == 4 and all((Path(tmp) / c["id"] / "case.yaml").exists()
                                                  for c in DESIGN["cases"]))
    check("the frozen prompt is emitted verbatim", json.dumps(DESIGN["cases"][0]["prompt"]) in clear)
    check("the pinned model and run count are emitted", '"sonnet"' in clear and "runs: 5" in clear)
    check("the design hash travels with every case", "abc123" in clear)
    check("a negative's expect grader asserts zero calls", "min: 0" in trap and "max: 0" in trap)
    check("a positive's expect grader does not", "max: 0" not in clear)
    check("a trap with a named winner also grades that the winner fired",
          'name: "expect-winner"' in trap and "intrinsic\\\\-prompt\\\\-design" in trap
          and 'name: "expect-winner"' not in clear)
    check("emit refuses a non-empty directory (stale cases would run unflagged)",
          raises_exit(lambda: st.emit(DESIGN, "abc123", tmp)))
    check("indicator graders carry a negligible weight so they barely move plugin eval's own score",
          clear.count(f"weight: {st.INDICATOR_WEIGHT}") == 3 and '"fired:*"' in clear)
    try:
        import yaml  # optional: CI runs the linters with pyyaml available
        parsed = yaml.safe_load(trap)
        check("emitted YAML parses (pyyaml)", parsed["graders"][0]["max"] == 0
              and parsed["execution"]["prompt"] == DESIGN["cases"][2]["prompt"])
    except ImportError:
        print("   skip emitted-YAML parse check (pyyaml not installed)")

with tempfile.TemporaryDirectory() as tmp:
    d = copy.deepcopy(DESIGN); d["plugins"] = ["makers-toolkit", "research-toolkit"]
    st.emit(d, "abc123", str(Path(tmp) / "evals"))
    y = (Path(tmp) / "evals" / "C1" / "case.yaml").read_text()
    check("the competitive catalog is emitted relative to each case dir",
          'plugins: ["../../makers-toolkit", "../../research-toolkit"]' in y)
d = copy.deepcopy(DESIGN); d["plugins"] = ["/abs/path"]
check("absolute plugin paths are rejected", any("plugins" in e for e in errs(d)))

print("rename A/B")
REN = copy.deepcopy(DESIGN)
REN["arm_targets"] = {"OLD": T, "NEW": "respect"}
REN["cases"][0] = {"id": "K1", "class": "control", "expect": T, "prompt": "Use the {target} skill on this."}
check("a rename design validates", errs(REN) == [])
r2 = copy.deepcopy(REN); r2["cases"][1]["prompt"] = "should I ask for respect here?"
check("a non-control prompt naming either arm's skill is rejected", any("control" in e for e in errs(r2)))
r2 = copy.deepcopy(REN); r2["cases"][1]["prompt"] = "use {target}"
check("the placeholder is control-only", any("placeholder" in e for e in errs(r2)))
with tempfile.TemporaryDirectory() as tmp:
    st.emit(REN, "h", str(Path(tmp) / "old"), arm="OLD")
    st.emit(REN, "h", str(Path(tmp) / "new"), arm="NEW")
    old_k = (Path(tmp) / "old" / "K1" / "case.yaml").read_text()
    new_k = (Path(tmp) / "new" / "K1" / "case.yaml").read_text()
    check("each arm's control names that arm's skill",
          "Use the skill-activation-testing skill" in old_k and "Use the respect skill" in new_k)
    check("each arm's graders look for that arm's skill",
          '"fired:respect"' in new_k and '"fired:respect"' not in old_k)
    check("emit refuses a rename design without --arm",
          st.main(["emit", write(tmp, "ren.json", REN), str(Path(tmp) / "x")]) == 2)
    new_res = result({"C1": [run(["respect", "*"])] * 5, "O1": [run(["respect", "*"])] * 5,
                      "T1": [run([SIB, "*"])] * 5, "N1": [run()] * 5},
                     prompts={"C1": None})
    new_res["cases"].insert(0, {"name": "K1", "promptMarkdown": "Use the respect skill on this.",
                                "arms": {"with": [run(["respect", "*"])] * 5}})
    rep_ren = st.score(REN, "h" * 64, [("NEW", write(tmp, "rn.json", new_res), "with")], seed=1)
    bad_label = st.score(REN, "h" * 64, [("new", write(tmp, "rn2.json", new_res), "with")], seed=1)
    check("an arm label missing from arm_targets voids rather than guessing the name",
          bad_label["decision"] == "VOID")
    check("score counts the arm's own skill name as the target",
          rep_ren["metrics"]["NEW.recall.oblique"] == 1.0 and rep_ren["decision"] != "VOID")

print("classify")
case_t = DESIGN["cases"][2]
check("target outranks a sibling in the same run",
      st.classify({"fired": {T, SIB, "*"}}, case_t, T) == "target")
check("a trap's named winner is expected-sibling",
      st.classify({"fired": {SIB, "*"}}, case_t, T) == "expected-sibling")
check("a named sibling on a positive is sibling",
      st.classify({"fired": {SIB, "*"}}, DESIGN["cases"][0], T) == "sibling")
check("an unnamed skill is other", st.classify({"fired": {"*"}}, case_t, T) == "other")
check("silence is nothing", st.classify({"fired": set()}, case_t, T) == "nothing")

print("wilson")
lo, hi = st.wilson(0, 5)
check("0/5 has a lower bound of 0 and an upper bound near .43", lo == 0 and abs(hi - 0.4345) < 0.001)
lo, hi = st.wilson(5, 5)
check("5/5 is not reported as certainly 1 from below", hi == 1 and abs(lo - 0.5655) < 0.001)
check("0/0 is undefined, not zero", all(math.isnan(x) for x in st.wilson(0, 0)))

print("sign-flip")
import random as _r
g = _r.Random(0)
check("5 equal positive deltas give exact two-sided p = 2/32", st.sign_flip_p([0.6] * 5, g) == 2 / 32)
check("3 cases cannot reach p < .25 however large the effect", st.sign_flip_p([1, 1, 1], g) == 0.25)
check("no non-zero delta is p = 1", st.sign_flip_p([0, 0], g) == 1.0)
check("mixed-sign deltas are not significant", st.sign_flip_p([0.5, -0.5, 0.4, -0.4], g) == 1.0)
mc = st.sign_flip_p([0.2] * 20, _r.Random(0))
check("above 14 cases it falls back to Monte Carlo, still tiny for a uniform effect", mc < 0.001)

print("score")
with tempfile.TemporaryDirectory() as tmp:
    new = write(tmp, "new.json", result({
        "C1": [run([T, "*"])] * 5,
        "O1": [run([T, "*"])] * 4 + [run()],
        "T1": [run([SIB, "*"])] * 5,
        "N1": [run()] * 5,
    }))
    old = write(tmp, "old.json", result({
        "C1": [run([T, "*"])] * 5,
        "O1": [run([T, "*"])] + [run()] * 4,
        "T1": [run([T, "*"])] * 2 + [run([SIB, "*"])] * 3,
        "N1": [run()] * 5,
    }))
    rep = st.score(DESIGN, "f" * 64, [("NEW", new, "with"), ("OLD", old, "with")], seed=1)
    m = rep["metrics"]
    check("recall pools target firings over usable runs", m["NEW.recall.oblique"] == 0.8)
    check("false fire on traps counts target firings", m["OLD.false_fire.trap"] == 0.4)
    check("the arm difference is computed per class",
          abs(m["diff(NEW-OLD).recall.oblique"] - 0.6) < 1e-9)
    check("the interval brackets the point estimate",
          m["NEW.recall.oblique.ci_lo"] <= 0.8 <= m["NEW.recall.oblique.ci_hi"])
    check("one case per class means the case-resampled interval is degenerate - honest, not hidden",
          m["NEW.recall.oblique.ci_lo"] == m["NEW.recall.oblique.ci_hi"])
    check("the rule holds -> SHIP", rep["decision"] == "SHIP")
    check("both diff directions exist, so a pre-registered rule does not depend on --arm order",
          abs(m["diff(OLD-NEW).recall.oblique"] + 0.6) < 1e-9)
    check("per-case outcome classes are kept",
          rep["summaries"]["NEW"]["per_case"]["T1"]["outcome"] == {"expected-sibling": 5})
    again = st.score(DESIGN, "f" * 64, [("NEW", new, "with"), ("OLD", old, "with")], seed=1)
    check("scoring is deterministic for a fixed seed", again["metrics"] == m)

    d = copy.deepcopy(DESIGN); d["ship_rule"] = [["NEW.recall.oblique", ">=", 0.9]]
    check("the rule fails -> NO-SHIP", st.score(d, "f" * 64, [("NEW", new, "with")], seed=1)["decision"] == "NO-SHIP")
    d["ship_rule"] = [["NEW.recall.nonexistent", ">=", 0.1]]
    check("a rule naming an uncomputed metric is VOID, not a pass",
          st.score(d, "f" * 64, [("NEW", new, "with")], seed=1)["decision"] == "VOID")

    drift = write(tmp, "drift.json", result({c["id"]: [run()] * 5 for c in DESIGN["cases"]},
                                             prompts={"O1": "a quietly reworded prompt"}))
    check("a prompt that differs from the frozen design voids the run",
          st.score(DESIGN, "f" * 64, [("NEW", drift, "with")], seed=1)["decision"] == "VOID")
    other_model = write(tmp, "model.json", result({c["id"]: [run()] * 5 for c in DESIGN["cases"]},
                                                   model="haiku"))
    check("a run on a different model than the design pins voids it",
          st.score(DESIGN, "f" * 64, [("NEW", other_model, "with")], seed=1)["decision"] == "VOID")
    unrecorded = write(tmp, "nomodel.json", result({c["id"]: [run()] * 5 for c in DESIGN["cases"]},
                                                     model=None))
    rep = st.score(DESIGN, "f" * 64, [("NEW", unrecorded, "with")], seed=1)
    check("an unrecorded model is flagged, not silently trusted",
          any("--model sonnet" in n for n in rep["notes"]))
    errored = write(tmp, "err.json", result({c["id"]: [run(error="boom")] + [run()] * 4
                                             for c in DESIGN["cases"]}))
    check("more than 10% errored runs voids the run",
          st.score(DESIGN, "f" * 64, [("NEW", errored, "with")], seed=1)["decision"] == "VOID")
    d = copy.deepcopy(DESIGN); d["plugins"] = ["makers-toolkit", "research-toolkit"]
    check("a run whose loaded catalog differs from the design's plugins voids it",
          st.score(d, "f" * 64, [("NEW", new, "with")], seed=1)["decision"] == "VOID")
    partial = write(tmp, "part.json", result({"C1": [run()] * 5}))
    check("a case missing from the results voids the run",
          st.score(DESIGN, "f" * 64, [("NEW", partial, "with")], seed=1)["decision"] == "VOID")
    rep = st.score(DESIGN, "f" * 64, [("NEW", errored, "with")], seed=1)
    check("errored runs leave the denominator rather than counting as misses",
          rep["summaries"]["NEW"]["per_case"]["C1"]["n"] == 4)

    ablation = result({c["id"]: [run(score=1.0)] * 5 for c in DESIGN["cases"]})
    for c in ablation["cases"]:
        c["arms"]["without"] = [run(score=0.0)] * 5
    abl = write(tmp, "abl.json", ablation)
    rep = st.score(DESIGN, "f" * 64, [("W", abl, "with"), ("WO", abl, "without")], seed=1)
    check("with/without arms of one plugin-eval file score as a functional delta",
          rep["metrics"]["diff(W-WO).score.all"] == 1.0)

    check("an unreadable results file is VOID, not a crash",
          st.score(DESIGN, "f" * 64, [("NEW", str(Path(tmp) / "missing.json"), "with")], seed=1)["decision"] == "VOID")

print("power")
d0, n0 = st.mde(0.5, 100, 1, 0.0)
check("100 independent runs per arm at p0=.5 detect roughly a .19 rise", 0.17 < d0 < 0.22 and n0 == 100)
d1, n1 = st.mde(0.5, 20, 5, 0.6)
check("correlated repeats shrink the effective sample", n1 < 40 and d1 > d0)
check("inverse normal is accurate at the usual quantiles",
      abs(st._z(0.975) - 1.95996) < 1e-4 and abs(st._z(0.8) - 0.84162) < 1e-4)

print("cli")
with tempfile.TemporaryDirectory() as tmp:
    dp = write(tmp, "design.json", DESIGN)
    check("validate exits 0 on a sound design", st.main(["validate", dp]) == 0)
    bad = copy.deepcopy(DESIGN); del bad["model"]
    check("validate exits 2 on an unsound design", st.main(["validate", write(tmp, "bad.json", bad)]) == 2)
    rf = write(tmp, "r.json", result({c["id"]: [run()] * 5 for c in DESIGN["cases"]}))
    norule = copy.deepcopy(DESIGN); del norule["ship_rule"]
    check("no ship rule exits non-zero: a CI gate fails closed",
          st.main(["score", write(tmp, "nr.json", norule), "--arm", "NEW=" + rf]) == 4)
    allerr = write(tmp, "ae.json", result({c["id"]: [run(error="x")] * 5 for c in DESIGN["cases"]}))
    out = str(Path(tmp) / "rep.json")
    st.main(["score", dp, "--arm", "NEW=" + allerr, "--json", out])
    txt = Path(out).read_text()
    check("the JSON report is strict JSON (no NaN)", "NaN" not in txt and json.loads(txt) is not None)
    check("power runs", st.main(["power", "--p0", "0.5", "--cases", "10", "--runs", "5", "--icc", "0.3"]) == 0)

print(f"\n{'all passed' if not failures else f'{failures} FAILED'}")
raise SystemExit(1 if failures else 0)
