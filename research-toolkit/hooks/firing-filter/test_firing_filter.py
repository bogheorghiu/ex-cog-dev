#!/usr/bin/env python3
"""Tests for firing_filter.py — stdlib only, CI-run.

Fixtures are synthetic texts embedding the STRUCTURES of the recorded cases
(a Method line claiming skills the ledger lacks; a source-judgement dispatch;
a tiered memo beside absence claims). The recorded units themselves stay out
of the repo deliberately: the corpus is not publishable, and the structures —
not the words — are what the engine matches.
"""
import inspect
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLUGIN_ROOT = HERE.parents[1]          # research-toolkit/
sys.path.insert(0, str(HERE))
import firing_filter as ff             # noqa: E402


class Env:
    """Point the engine at a temp data dir + temp firing log, real plugin root."""
    def __enter__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old = {k: os.environ.get(k) for k in
                    ("CLAUDE_PLUGIN_ROOT", "CLAUDE_PLUGIN_DATA", "SKILL_FIRINGS_LOG")}
        os.environ["CLAUDE_PLUGIN_ROOT"] = str(PLUGIN_ROOT)
        os.environ["CLAUDE_PLUGIN_DATA"] = str(Path(self.tmp.name) / "data")
        self.log = Path(self.tmp.name) / "skill-firings.log"
        os.environ["SKILL_FIRINGS_LOG"] = str(self.log)
        ff.seed_assets()
        return self

    def __exit__(self, *a):
        for k, v in self.old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        self.tmp.cleanup()

    def record_firing(self, skill, session="s1"):
        with open(self.log, "a", encoding="utf-8") as f:
            f.write(json.dumps({"timestamp": "t", "session_id": session,
                                "skill": skill, "cwd": ""}) + "\n")


# A verdict-rendering unit whose Method line claims two skills; structure of
# the recorded dossier (which drew 4 flags against a 1-entry ledger).
VERDICT_DOC = """# Report
**Method:** routed via `research-toolkit:research` -> dialectic-spiral (the
coordination thesis) + cui-bono (who benefits).
**Tiers:** GROUNDED / UNRESOLVED / CONTRADICTED
One-line verdict: the factual substrate is mostly GROUNDED while the thesis
is UNRESOLVED; two claims are CONTRADICTED, three GROUNDED, one UNRESOLVED.
"""

# A source-judgement dispatch (structure of the recorded wrong-framed one).
SOURCE_DISPATCH = ("Profile a video channel so its content can be weighted "
                   "for bias. This is cui-bono on the messenger. Tier: "
                   "GROUNDED / UNRESOLVED / Gap. Track record?")

# A claim-verification dispatch (structure of the recorded controls — must
# NOT match the source-judgement situation).
CLAIM_DISPATCH = ("Verify the three load-bearing factual claims against "
                  "primary documents. Tier each claim GROUNDED / UNRESOLVED "
                  "/ CONTRADICTED with source URLs.")

# A tiered memo beside absence claims (structure of the recorded profile).
TIERED_MEMO = ("GROUNDED: the critique. UNRESOLVED: the causal claims. "
               "GROUNDED: ownership. Specific accuracy dispute identified: "
               "NONE documented - no corrections, no retractions.")


class TestNormalization(unittest.TestCase):
    def test_qualified_name_normalizes_to_bare_slug(self):
        # The near-shipped prototype bug: an unnormalized comparison flagged
        # the one genuinely-invoked skill as not-fired. Pin it forever.
        self.assertEqual(ff.normalize_slug("research-toolkit:research"), "research")

    def test_prose_and_case_variants(self):
        self.assertEqual(ff.normalize_slug("Dialectic Spiral"), "dialectic-spiral")
        self.assertEqual(ff.normalize_slug("cui-bono"), "cui-bono")


class TestClaims(unittest.TestCase):
    def test_hyphenated_slug_claims_anywhere(self):
        with Env():
            self.assertIn("dialectic-spiral",
                          ff.claimed_slugs("applied dialectic-spiral here"))
            self.assertIn("dialectic-spiral",
                          ff.claimed_slugs("applied dialectic spiral here"))

    def test_single_word_skill_needs_method_context(self):
        with Env():
            # "research" is a skill name AND the commonest word in a report;
            # bare mentions must never flag.
            self.assertNotIn("research", ff.claimed_slugs("this research shows"))
            self.assertIn("research",
                          ff.claimed_slugs("Method: routed via research hub"))
            self.assertIn("research",
                          ff.claimed_slugs("used research-toolkit:research"))


class TestReconcile(unittest.TestCase):
    def test_reproduces_claimed_but_not_fired(self):
        with Env() as env:
            env.record_firing("research-toolkit:research")
            flags = ff.reconcile(VERDICT_DOC, "s1")
            # dialectic-spiral and cui-bono claimed, never fired; research
            # claimed AND fired -> not flagged.
            self.assertEqual(flags, ["cui-bono", "dialectic-spiral"])

    def test_no_flags_when_everything_fired(self):
        with Env() as env:
            for s in ("research", "dialectic-spiral", "cui-bono"):
                env.record_firing(s)
            self.assertEqual(ff.reconcile(VERDICT_DOC, "s1"), [])


class TestSituations(unittest.TestCase):
    def test_s1_fires_on_anchors_and_on_tier_density(self):
        with Env():
            self.assertTrue(any(s["id"] == "S1-verdict-rendered"
                                for s in ff.situations_for(VERDICT_DOC, "write")))
            dense = "verdicts: " + "GROUNDED UNRESOLVED " * 3
            self.assertTrue(ff.situations_for(dense, "write"))

    def test_s2_separates_source_judgement_from_claim_verification(self):
        with Env():
            self.assertTrue(ff.situations_for(SOURCE_DISPATCH, "dispatch"))
            # The measured control class: verifying claims is NOT judging a
            # source; the injection would be the wrong guidance there.
            self.assertFalse(ff.situations_for(CLAIM_DISPATCH, "dispatch"))

    def test_s3_needs_tiers_AND_absence(self):
        with Env():
            self.assertTrue(ff.situations_for(TIERED_MEMO, "return"))
            self.assertFalse(ff.situations_for(
                "GROUNDED GROUNDED UNRESOLVED - all parties documented.",
                "return"))

    def test_dispatch_instructing_tiers_does_not_fire_s1(self):
        with Env():
            # Dispatches carry 3-4 tier tokens as instructions; S1's
            # threshold (5) must not catch them.
            self.assertFalse(ff.situations_for(CLAIM_DISPATCH, "write"))


class TestArming(unittest.TestCase):
    def test_everyday_words_do_not_arm(self):
        with Env():
            hits, entries = ff.lexicon_hits(
                "the standard approach is obvious", ff.load_rows("lexicon"))
            self.assertTrue(hits < ff.ARM_MIN_HITS or entries < ff.ARM_MIN_ENTRIES)

    def test_research_register_arms(self):
        with Env():
            hits, entries = ff.lexicon_hits(
                SOURCE_DISPATCH + " credibility debunk propaganda no evidence",
                ff.load_rows("lexicon"))
            self.assertTrue(hits >= ff.ARM_MIN_HITS and entries >= ff.ARM_MIN_ENTRIES)


class TestSeam(unittest.TestCase):
    def test_local_rows_survive_reseed_and_shadow_off(self):
        with Env():
            local = ff.data_dir() / "local"
            local.mkdir(parents=True, exist_ok=True)
            (local / "lexicon.jsonl").write_text(
                json.dumps({"id": "arm-watchlist", "disabled": True}) + "\n" +
                json.dumps({"id": "user-row", "class": "arming",
                            "stems": ["bespokeword"],
                            "provenance": "user's measured miss"}) + "\n",
                encoding="utf-8")
            ff.seed_assets()  # a re-seed (e.g. plugin update) happens...
            rows = {r["id"] for r in ff.load_rows("lexicon")}
            self.assertIn("user-row", rows)           # ...growth survives
            self.assertNotIn("arm-watchlist", rows)   # ...shadow-off survives

    def test_reseed_code_path_never_names_the_local_dir(self):
        # Invariant, not style: the seam's guarantee is that the capability
        # to destroy user rows DOES NOT EXIST in the re-seed code path. If
        # this fails, someone made the re-seed CODE aware of local/ — that is
        # a design regression even if their code is careful. Comments and the
        # docstring are stripped first: prose may explain local/, code may
        # not touch it.
        src = inspect.getsource(ff.seed_assets)
        doc = ff.seed_assets.__doc__ or ""
        code_only = "\n".join(line.split("#", 1)[0]
                              for line in src.replace(doc, "").splitlines())
        self.assertNotIn("local", code_only)

    def test_reseed_updates_stale_seed_copy(self):
        with Env():
            copy = ff.data_dir() / "seed-copy" / "lexicon.jsonl"
            copy.write_text('{"id": "stale"}\n', encoding="utf-8")
            ff.seed_assets()
            self.assertIn("arm-watchlist", copy.read_text(encoding="utf-8"))


class TestHandle(unittest.TestCase):
    def _armed_state(self, session="s1"):
        st = ff.load_state(session)
        st["mode"] = "armed"
        ff.save_state(session, st)

    def test_pre_write_denies_once_then_passes_identical_resend(self):
        with Env() as env:
            env.record_firing("research-toolkit:research")
            self._armed_state()
            payload = {"session_id": "s1",
                       "tool_input": {"content": VERDICT_DOC}}
            out1 = ff.handle("pre-write", payload)
            self.assertEqual(
                out1["hookSpecificOutput"]["permissionDecision"], "deny")
            self.assertIn("dialectic-spiral",
                          out1["hookSpecificOutput"]["permissionDecisionReason"])
            # Bounded insistence: the identical unit is not re-blocked.
            self.assertIsNone(ff.handle("pre-write", payload))

    def test_clean_verdict_write_is_never_blocked(self):
        with Env() as env:
            for s in ("research", "dialectic-spiral", "cui-bono"):
                env.record_firing(s)
            self._armed_state()
            out = ff.handle("pre-write", {"session_id": "s1",
                                          "tool_input": {"content": VERDICT_DOC}})
            self.assertIsNone(out)  # guidance arrives post-write instead

    def test_post_write_injects_guidance_once(self):
        with Env():
            self._armed_state()
            payload = {"session_id": "s1",
                       "tool_input": {"content": VERDICT_DOC}}
            out = ff.handle("post-write", payload)
            self.assertIn("additionalContext", out["hookSpecificOutput"])
            self.assertIsNone(ff.handle("post-write", payload))

    def test_dispatch_deny_capped_per_session(self):
        with Env():
            self._armed_state()
            outs = []
            for i in range(3):
                outs.append(ff.handle("pre-agent", {
                    "session_id": "s1",
                    "tool_input": {"prompt": SOURCE_DISPATCH + f" v{i}"}}))
            denials = [o for o in outs if o]
            self.assertEqual(len(denials), ff.S2_SESSION_CAP)

    def test_stop_respects_stop_hook_active(self):
        with Env():
            self._armed_state()
            tp = Path(ff.data_dir()) / "t.jsonl"
            tp.write_text(json.dumps({
                "type": "assistant",
                "message": {"role": "assistant",
                            "content": [{"type": "text", "text": VERDICT_DOC}]}
            }) + "\n", encoding="utf-8")
            blocked = ff.handle("stop", {"session_id": "s1",
                                         "transcript_path": str(tp)})
            self.assertEqual(blocked["decision"], "block")
            again = ff.handle("stop", {"session_id": "s1",
                                       "transcript_path": str(tp),
                                       "stop_hook_active": True})
            self.assertIsNone(again)

    def test_unarmed_session_pays_nothing(self):
        with Env():
            out = ff.handle("pre-agent", {"session_id": "s1",
                                          "tool_input": {"prompt": SOURCE_DISPATCH}})
            # SOURCE_DISPATCH alone arms (research register) -> S2 may fire;
            # but a genuinely non-research payload must produce nothing:
            out2 = ff.handle("pre-write", {"session_id": "s2",
                                           "tool_input": {"content": "def f(): pass"}})
            self.assertIsNone(out2)

    def test_disabled_mode_emits_nothing(self):
        with Env():
            st = ff.load_state("s1")
            st["mode"] = "disabled"
            ff.save_state("s1", st)
            out = ff.handle("pre-write", {"session_id": "s1",
                                          "tool_input": {"content": VERDICT_DOC}})
            self.assertIsNone(out)

    def test_master_switch_off_is_full_passthrough(self):
        # Regression: master_enabled() shipped UNWIRED in 4.6.0–4.6.1, so
        # CLAUDE_PLUGIN_OPTION_FIRING_FILTER=off silently did nothing (an
        # M11 probe's "off" arm still armed). Off must mean: no output, no
        # ledger dir, no state — assertable from the filesystem.
        with Env():
            os.environ["CLAUDE_PLUGIN_OPTION_FIRING_FILTER"] = "off"
            try:
                for ev, payload in (
                        ("session-start", {"session_id": "s1"}),
                        ("user-prompt", {"session_id": "s1",
                                         "prompt": SOURCE_DISPATCH
                                         + " credibility debunk propaganda"}),
                        ("pre-write", {"session_id": "s1",
                                       "tool_input": {"content": VERDICT_DOC}}),
                        ("stop", {"session_id": "s1"})):
                    self.assertIsNone(ff.handle(ev, payload))
                self.assertFalse((ff.data_dir() / "ledger").exists())
            finally:
                del os.environ["CLAUDE_PLUGIN_OPTION_FIRING_FILTER"]


class TestFailOpen(unittest.TestCase):
    def test_garbage_stdin_exits_zero_and_passes_through(self):
        p = subprocess.run(
            [sys.executable, str(HERE / "firing_filter.py"), "pre-write"],
            input="NOT JSON", capture_output=True, text=True,
            env={**os.environ, "CLAUDE_PLUGIN_DATA":
                 tempfile.mkdtemp(prefix="ffx")})
        self.assertEqual(p.returncode, 0)
        self.assertEqual(p.stdout.strip(), "{}")


class TestOneAssetTwoConsumers(unittest.TestCase):
    def test_lint_references_the_asset_and_has_no_inline_watchlist(self):
        # The pre-refactor failure mode: the lint's watchlist lived as a prose
        # blockquote no script can read, guaranteeing drift between what the
        # model checks and what the hook checks. There must be ONE copy.
        lint = (PLUGIN_ROOT / "skills" / "cui-bono" / "references" /
                "frame-leak-lint.md").read_text(encoding="utf-8")
        self.assertIn("lexicon.jsonl", lint)
        self.assertNotIn("clean · safe · neutral", lint)


if __name__ == "__main__":
    unittest.main(verbosity=2)
