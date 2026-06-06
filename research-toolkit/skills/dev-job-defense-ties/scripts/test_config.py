#!/usr/bin/env python3
"""Unit tests for config.py — the deterministic config store.

Written test-first (TDD): this file is the behavioral spec for the tool. No
network, no touching the real home dir (redirected via env to a scratch dir
created under the repo — NOT /tmp, which the store refuses). Exits non-zero on
failure.
"""

import importlib.util
import io
import os
import shutil
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("config_mod", _HERE / "config.py")
mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mod)

failures = 0


def check(label, condition):
    global failures
    print(f"   {'✓' if condition else '✗ FAILED:'} {label}")
    if not condition:
        failures += 1


def raises(fn, *a):
    try:
        fn(*a)
        return False
    except Exception:
        return True


def capture(*argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        mod.main(["config.py", *argv])
    return buf.getvalue()


SAFE_ROOT = Path(tempfile.mkdtemp(dir=os.getcwd(), prefix=".test_config_"))
for var in (mod.ENV_OVERRIDE, "XDG_CONFIG_HOME", "APPDATA"):
    os.environ.pop(var, None)

try:
    print("\n1. element-ref validation (no path traversal / dots / caps)...")
    store = mod.ConfigStore()
    p = store.element_path("profile/threshold")
    check("valid ref -> <cat>/<name>.md", p.parts[-2:] == ("profile", "threshold.md"))
    for bad in ["..", "profile", "a/b/c", "profile/../x", "Profile/x", "profile/thr.md", "", "profile/", "/etc/x"]:
        check(f"rejects {bad!r}", raises(store.element_path, bad))
    for good in ["profile/threshold", "profile/settings", "domain/gamedev", "domain/bio-tech-2"]:
        check(f"accepts {good!r}", not raises(store.element_path, good))

    print("\n2. describe() self-documents the interface (for the model)...")
    desc = capture("describe")
    check("describe lists the core verbs", all(v in desc for v in ("describe", "locate", "list", "get", "put", "remove")))
    check("describe shows element addressing", "category/name" in desc or "<cat/name>" in desc)

    print("\n3. locate honors $%s and creates the dir..." % mod.ENV_OVERRIDE)
    os.environ[mod.ENV_OVERRIDE] = str(SAFE_ROOT / "cfg")
    store = mod.ConfigStore()
    check("location() == override", store.location() == SAFE_ROOT / "cfg")
    capture("locate")
    check("locate created the dir", (SAFE_ROOT / "cfg").is_dir())

    print("\n4. put/get round-trip...")
    store.put("profile/threshold", "RED LINE v1\n")
    check("element file written under category dir", (SAFE_ROOT / "cfg" / "profile" / "threshold.md").exists())
    check("get returns what was put", store.get("profile/threshold") == "RED LINE v1\n")
    check("get missing -> None", store.get("domain/nope") is None)
    check("CLI get missing -> NO_ELEMENT", capture("get", "domain/nope").strip() == mod.NO_ELEMENT)

    print("\n5. decoupled edit — writing one element never touches a sibling...")
    store.put("profile/settings", "engagement: ask\n")
    store.put("profile/threshold", "RED LINE v2\n")  # amend one element
    check("sibling settings untouched after editing threshold", store.get("profile/settings") == "engagement: ask\n")
    check("threshold reflects the amend", store.get("profile/threshold") == "RED LINE v2\n")

    print("\n6. list reflects stored elements across categories...")
    store.put("domain/gamedev", "lexicon...\n")
    listed = set(store.list_elements())
    check("list shows all three elements", {"profile/threshold", "profile/settings", "domain/gamedev"} <= listed)

    print("\n7. remove deletes just that element...")
    store.remove("profile/settings")
    check("removed element gone from list", "profile/settings" not in set(store.list_elements()))
    check("removed element get -> None", store.get("profile/settings") is None)
    check("siblings survive removal", store.get("profile/threshold") == "RED LINE v2\n")

    print("\n8. path safety — set-location refuses temp/cache...")
    check("set-location /tmp/evil refused (rc != 0)", mod.main(["config.py", "set-location", "/tmp/evil"]) != 0)
    os.environ.pop(mod.ENV_OVERRIDE, None)

    print("\n9. OS-agnostic base + custom location round-trip...")
    if os.name == "nt":
        os.environ["APPDATA"] = str(SAFE_ROOT / "roaming")
        check("Windows base under %APPDATA%", mod.ConfigStore().canonical_base() == SAFE_ROOT / "roaming" / mod.APP)
    else:
        os.environ["XDG_CONFIG_HOME"] = str(SAFE_ROOT / "xdg")
        check("POSIX base under $XDG_CONFIG_HOME", mod.ConfigStore().canonical_base() == SAFE_ROOT / "xdg" / mod.APP)
    custom = SAFE_ROOT / "custom"
    check("set-location (safe) succeeds", mod.main(["config.py", "set-location", str(custom)]) == 0)
    s2 = mod.ConfigStore()
    check("location() follows the pointer", s2.location() == custom)
    s2.put("domain/gamedev", "X\n")
    check("round-trip in custom location", s2.get("domain/gamedev") == "X\n")
    capture("clear-location")
    check("clear-location reverts to base", mod.ConfigStore().location() == mod.ConfigStore().canonical_base())

    if failures == 0:
        print("\n✅ All config.py tests passed!")
    else:
        print(f"\n❌ {failures} check(s) failed.")
finally:
    shutil.rmtree(SAFE_ROOT, ignore_errors=True)

raise SystemExit(1 if failures else 0)
