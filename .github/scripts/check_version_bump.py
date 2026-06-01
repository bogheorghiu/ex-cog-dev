#!/usr/bin/env python3
"""Version-bump guard (handoff Appendix C).

Fails a PR when files under a plugin directory changed but that plugin's
`.claude-plugin/plugin.json` `version` did not increase. The plugin version is
what `claude plugin update` keys on; a code/doc change shipped without a bump is
silently skipped by installs (the regression this guard prevents).

Usage (CI):
    python3 .github/scripts/check_version_bump.py <base_ref> [<head_ref>]

The decision logic (`evaluate`) is pure and unit-tested in
`test_check_version_bump.py`; the git plumbing is a thin wrapper around it.
"""

import json
import subprocess
import sys

# Top-level plugin dirs in this marketplace and the prefix that "belongs" to
# each. A change to any tracked file under the prefix requires a version bump
# in that plugin's manifest.
PLUGIN_DIRS = {
    "vasana-system": "vasana-system/",
    "research-toolkit": "research-toolkit/",
    "makers-toolkit": "makers-toolkit/",
    "security-toolkit": "security-toolkit/",
}


def version_tuple(v):
    """Parse a dotted version into an int tuple. (0,) for unparseable/None.

    Avoids the string-ordering trap where "1.9" > "1.10" alphabetically.
    """
    try:
        return tuple(int(p) for p in str(v).split("."))
    except (ValueError, AttributeError):
        return (0,)


def evaluate(changed_files, base_versions, head_versions, plugin_dirs=PLUGIN_DIRS):
    """Pure guard decision. Returns a list of failure messages ([] == pass).

    - changed_files: paths changed in the PR, relative to repo root.
    - base_versions / head_versions: {plugin_name: version_str_or_None} at the
      base and head refs (None = manifest absent or unparseable).
    - plugin_dirs: {plugin_name: dir_prefix}.

    Rules per plugin whose files changed:
    - manifest missing/unparseable at head  -> fail.
    - new plugin (absent at base, present at head) -> pass (any version ok).
    - head version must be strictly greater than base version -> else fail.
    """
    failures = []
    for name, prefix in plugin_dirs.items():
        touched = [f for f in changed_files if f.startswith(prefix)]
        if not touched:
            continue
        head_v = head_versions.get(name)
        base_v = base_versions.get(name)
        if head_v is None:
            failures.append(
                f"{name}: {len(touched)} file(s) changed under {prefix} but its "
                f".claude-plugin/plugin.json version is missing or unparseable at HEAD."
            )
            continue
        if base_v is None:
            # New plugin introduced in this PR — any version is acceptable.
            continue
        if version_tuple(head_v) <= version_tuple(base_v):
            failures.append(
                f"{name}: {len(touched)} file(s) changed under {prefix} but version did "
                f"not increase ({base_v} -> {head_v}). Bump {prefix}.claude-plugin/plugin.json."
            )
    return failures


def _read_version(ref, prefix):
    """Read a plugin's manifest version at a git ref; None if absent/unparseable."""
    path = f"{prefix}.claude-plugin/plugin.json"
    proc = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return None  # manifest does not exist at this ref
    try:
        return json.loads(proc.stdout).get("version")
    except json.JSONDecodeError:
        return None


def _changed_files(base_ref, head_ref):
    """Files changed between the merge-base of base_ref..head_ref and head_ref."""
    out = subprocess.run(
        ["git", "diff", "--name-only", f"{base_ref}...{head_ref}"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [line for line in out.splitlines() if line.strip()]


def main(argv):
    if not (2 <= len(argv) <= 3):
        print("usage: check_version_bump.py <base_ref> [<head_ref>]", file=sys.stderr)
        return 2
    base_ref = argv[1]
    head_ref = argv[2] if len(argv) == 3 else "HEAD"

    changed = _changed_files(base_ref, head_ref)
    base_versions = {n: _read_version(base_ref, p) for n, p in PLUGIN_DIRS.items()}
    head_versions = {n: _read_version(head_ref, p) for n, p in PLUGIN_DIRS.items()}

    failures = evaluate(changed, base_versions, head_versions)
    if failures:
        print("❌ Version-bump guard FAILED:")
        for f in failures:
            print(f"   - {f}")
        print(
            "\nAny change to a plugin's files must bump that plugin's "
            ".claude-plugin/plugin.json version, so `claude plugin update` picks it up."
        )
        return 1
    print("✅ Version-bump guard passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
