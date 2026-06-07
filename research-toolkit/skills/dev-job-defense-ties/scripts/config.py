#!/usr/bin/env python3
"""Config store for the dev-job-defense-ties skill.

The deterministic layer (system-pilot's "tools"): it owns *only* where config
lives and how each element is read/written — never what the config means. The
skill ships with no profile; a user's profile and domain overlays are stored
here, OUTSIDE the plugin, so they survive reinstalls and are never committed.

Elements are addressed generically as `<category>/<name>` (e.g. `profile/threshold`,
`domain/gamedev`) and stored one-per-file, so editing one never disturbs another.
New categories need no code change (open/closed). `describe` emits this interface
for the model, so the SKILL.md doesn't hard-code usage that could drift.

Stdlib only. Run `python3 config.py describe` to see the live interface.
"""

import os
import re
import sys
import tempfile
from pathlib import Path

APP = "dev-job-defense-ties"
ENV_OVERRIDE = "DEV_JOB_DEFENSE_CONFIG_DIR"
POINTER_FILE = "location"          # lives in the canonical base; contents = custom dir
NO_ELEMENT = "NO_ELEMENT"
# category and name each: lowercase, start alnum, then alnum/dash. No dots or
# slashes → an element ref can never escape the config dir (path-traversal safe).
REF_PART = re.compile(r"^[a-z0-9][a-z0-9-]*$")
# Ephemeral / cache-like locations a persisted config must never land in.
_UNSAFE_PARTS = (".cache", "uvx", "uv-cache", "site-packages", "__pycache__", "node_modules")

# (command, args, one-line doc) — the single source of truth for `describe`.
COMMANDS = [
    ("describe", "", "print this interface + current location + stored elements"),
    ("locate", "", "print (and create) the config directory"),
    ("set-location", "<dir>", "remember a custom config directory (refuses temp/cache)"),
    ("clear-location", "", "forget the custom directory (revert to default)"),
    ("list", "", "list stored elements as category/name"),
    ("get", "<cat/name>", "print an element, or NO_ELEMENT"),
    ("put", "<cat/name>", "write stdin to an element"),
    ("remove", "<cat/name>", "delete an element"),
]


def _is_unsafe(path):
    """True if `path` is a temp dir or a cache-like location we must refuse."""
    p = Path(path).expanduser()
    if not p.is_absolute():
        return True
    try:
        resolved = p.resolve()
    except OSError:
        resolved = p
    s = str(resolved)
    tmp = str(Path(tempfile.gettempdir()).resolve())
    if s == tmp or s.startswith(tmp + os.sep):
        return True
    parts = resolved.parts
    if "tmp" in parts:  # /tmp, /var/tmp, /private/tmp — temp roots vary by OS/TMPDIR
        return True
    return any(bad in parts or bad in s.split(os.sep) for bad in _UNSAFE_PARTS)


class ConfigStore:
    """Locate the config dir and read/write elements. The only stateful surface."""

    def canonical_base(self):
        """OS-agnostic default directory, ignoring any override/pointer."""
        if os.name == "nt":
            root = os.environ.get("APPDATA") or (Path.home() / "AppData" / "Roaming")
        else:
            root = os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config")
        return Path(root).expanduser() / APP

    def location(self):
        """Resolve the active config dir: env override > pointer > default base."""
        override = os.environ.get(ENV_OVERRIDE)
        if override:
            return Path(override).expanduser()
        pointer = self.canonical_base() / POINTER_FILE
        if pointer.exists():
            custom = pointer.read_text(encoding="utf-8").strip()
            if custom:
                return Path(custom).expanduser()
        return self.canonical_base()

    def element_path(self, ref):
        """Map `<category>/<name>` to a file path, rejecting anything unsafe."""
        parts = ref.split("/")
        if len(parts) != 2 or not all(REF_PART.match(p) for p in parts):
            raise ValueError(f"invalid element ref {ref!r}: expected <category>/<name> (lowercase, [a-z0-9-])")
        category, name = parts
        return self.location() / category / f"{name}.md"

    def get(self, ref):
        f = self.element_path(ref)
        return f.read_text(encoding="utf-8") if f.exists() else None

    def put(self, ref, data):
        f = self.element_path(ref)
        if _is_unsafe(f.parent.parent):
            raise ValueError(f"refusing to write into unsafe location: {self.location()}")
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(data, encoding="utf-8")
        return f

    def remove(self, ref):
        f = self.element_path(ref)
        if f.exists():
            f.unlink()
            return True
        return False

    def list_elements(self):
        loc = self.location()
        if not loc.is_dir():
            return []
        out = []
        for cat_dir in sorted(p for p in loc.iterdir() if p.is_dir()):
            for el in sorted(cat_dir.glob("*.md")):
                out.append(f"{cat_dir.name}/{el.stem}")
        return out

    def set_location(self, dest):
        dest = Path(dest).expanduser()
        if _is_unsafe(dest):
            raise ValueError(f"refusing unsafe location: {dest} (temp/cache paths are rejected)")
        base = self.canonical_base()
        base.mkdir(parents=True, exist_ok=True)
        (base / POINTER_FILE).write_text(str(dest), encoding="utf-8")
        dest.mkdir(parents=True, exist_ok=True)
        return dest

    def clear_location(self):
        pointer = self.canonical_base() / POINTER_FILE
        if pointer.exists():
            pointer.unlink()
        return self.canonical_base()


def describe(store):
    lines = [
        "dev-job-defense-ties config store — interface (for the model; the user never runs this).",
        "",
        "Addressing: elements are category/name (lowercase, [a-z0-9-]); stored one per file.",
        "Known categories: profile (threshold, settings), domain (one file per overlay).",
        "",
        "Commands:",
    ]
    for name, args, doc in COMMANDS:
        lines.append(f"  {name} {args}".ljust(26) + f"— {doc}")
    lines += ["", f"Location: {store.location()}", "Stored elements: " + (", ".join(store.list_elements()) or "(none)")]
    return "\n".join(lines)


def main(argv):
    cmd = argv[1] if len(argv) > 1 else ""
    ref = argv[2] if len(argv) > 2 else None
    store = ConfigStore()
    try:
        if cmd == "describe":
            print(describe(store))
            return 0
        if cmd == "locate":
            loc = store.location()
            if _is_unsafe(loc):
                sys.stderr.write(f"refusing unsafe config dir: {loc}\n")
                return 2
            loc.mkdir(parents=True, exist_ok=True)
            print(loc)
            return 0
        if cmd == "set-location" and ref:
            print(store.set_location(ref))
            return 0
        if cmd == "clear-location":
            print(store.clear_location())
            return 0
        if cmd == "list":
            print("\n".join(store.list_elements()))
            return 0
        if cmd == "get" and ref:
            val = store.get(ref)
            sys.stdout.write(val if val is not None else NO_ELEMENT + "\n")
            return 0
        if cmd == "put" and ref:
            print(store.put(ref, sys.stdin.read()))
            return 0
        if cmd == "remove" and ref:
            print("removed" if store.remove(ref) else NO_ELEMENT)
            return 0
    except ValueError as e:
        sys.stderr.write(f"{e}\n")
        return 2
    sys.stderr.write(describe(store) + "\n")
    return 64


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
