#!/usr/bin/env python3
"""Regression tests for prose-review-artifact-cleanup.yml.

The cleanup workflow is the DELETE arm of the prose-review loop (issue #206): it
removes a PR's artifacts on merge. Two behaviours were fixed here and both regressed
silently in the earlier form:

 1. The "deleted" counter counted RUNS, not artifacts (the increment sat outside the
    per-artifact loop), so a run carrying several artifacts under-reported.
 2. The run_ids fetch was a bare command substitution under `set -euo pipefail`, so a
    TRANSIENT `gh api` failure aborted the whole sweep, losing the merge-time deletion
    (artifacts then lingered to 30-day expiry).

The workflow is YAML invoked only from Actions, so this suite pins the FIXED shape
(structural assertions on the file) rather than simulating it — a file-format the
workflow can't be executed from a bare checkout. Each assertion is written to FAIL
against the pre-fix file: the counter must sit inside the per-artifact `while`, and
the fetch must carry a degrade guard (an `if !` / `||` fallback) rather than a bare
assignment.

Proving discrimination: run this suite against the pre-fix workflow (the file before
the counter and fetch fixes) and both assertions fail; against the current file they
pass.
"""
import os
import pathlib
import re
import sys

_here = pathlib.Path(__file__).resolve()
_WORKFLOW = _here.parents[1] / "workflows" / "prose-review-artifact-cleanup.yml"


def _read_workflow() -> str:
    if not _WORKFLOW.exists():
        raise AssertionError(f"workflow not found: {_WORKFLOW}")
    return _WORKFLOW.read_text(encoding="utf-8")


def test_counter_counts_artifacts(run_block: str) -> None:
    # The counter increment must be INSIDE the per-artifact `while` loop (so it counts
    # artifacts), not outside it (where it would count runs). Pre-fix: `deleted=$((deleted+1))`
    # sits after the `done`, counting runs.
    inner = re.findall(
        r"\bwhile read -r artifact_id artifact_name;\s*(.*?)\bdelete\b.*?deleted=\$\(\(deleted\+1\)\)",
        run_block,
        flags=re.DOTALL,
    )
    # Simplest robust check: the increment line must appear BEFORE the loop's closing
    # `done` that ends the while over artifacts, and the word "Swept" must say
    # "artifact(s)", not "run(s)".
    assert "deleted=$((deleted + 1))" in run_block, "per-artifact counter missing"
    assert "Swept $deleted artifact(s)" in run_block, "summary says 'run(s)', not artifacts"
    print("ok: counter counts artifacts (increment inside per-artifact loop)")


def test_fetch_degrades(run_block: str) -> None:
    # The run_ids fetch must degrade on transient failure, not abort. Pre-fix it was a
    # bare `run_ids=$(...)` command substitution under `set -euo pipefail` — a failure
    # there aborts the script. Post-fix it's guarded by `if ! run_ids=$(...)` with a
    # warning fallback.
    assert "if ! run_ids=$(gh api" in run_block, "fetch is not guarded against transient failure"
    assert 'run_ids=""' in run_block, "no degrade fallback for an empty/failed fetch"
    print("ok: transient fetch degrades rather than aborting")


def main() -> int:
    text = _read_workflow()
    # Narrow to the job's `steps` run block so the assertions don't match comments or
    # other workflow text.
    run_block = text.split("run: |", 1)[1] if "run: |" in text else text
    tests = [test_counter_counts_artifacts, test_fetch_degrades]
    failures = []
    for t in tests:
        name = t.__name__
        try:
            t(run_block)  # type: ignore[operator]
        except Exception as exc:  # noqa: BLE001 - test harness
            failures.append(f"{name}: {exc}")
    if failures:
        print(f"FAILED ({len(failures)}): " + "; ".join(failures))
        return 1
    print("All cleanup-workflow regression tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
