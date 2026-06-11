# WSL/Linux IOC checklist (Step 1)

> Loaded on demand by `windows-wsl-security-verification`. Each check carries its
> command and what a hit means, because a checklist line without its reading rule
> is where triage goes wrong. Run all of them — the vectors are independent.
>
> **Discriminator that governs every named-file check here:** a filename IOC is a
> *file*; test with `find -name` or hashes, never content-grep (your own notes and
> transcripts will contain the string once you've researched it — see SKILL.md
> Step 2).

## 1. Known-bad package versions

For the incident that triggered the triage, get the advisory's bad-version list,
then check what is actually installed — **in every environment, not just the
default one** (each venv, uv tool installs, global site-packages, nvm/node
versions):

```bash
# Python — list each environment you actually have:
pip list 2>/dev/null | grep -i <package>
~/.ai-py3venv/bin/pip list 2>/dev/null | grep -i <package>   # adjust per venv
uv tool list 2>/dev/null | grep -i <package>
# Node:
npm ls -g <package> 2>/dev/null; npm ls <package> 2>/dev/null
```

Reading: a version *outside* the bad window (older or fixed) is clean **on this
vector**; record the exact versions found. Worked class-example: the TeamPCP
campaign's LiteLLM compromise (CVE-2026-33634) had bad versions **1.82.7/1.82.8
only** — installs of 1.81.x / 1.83+ were clean, and the campaign's dropper left a
named `.pth` file, checked below by name.

## 2. Rootkit preload

```bash
cat /etc/ld.so.preload 2>/dev/null
```

Reading: this file is **absent on a normal system**. Any content = libraries
force-loaded into every process — a classic userland-rootkit hook. A hit here is
serious; treat the box as compromised and move to containment.

## 3. Persistence vectors

```bash
systemctl list-unit-files --type=service --state=enabled   # system services
systemctl --user list-units --all 2>/dev/null              # user units
systemctl list-timers --all                                # timers
ls -la /etc/cron* 2>/dev/null; crontab -l 2>/dev/null      # cron, user crontab
ls -la ~/.config/autostart 2>/dev/null                     # desktop autostart
```

Reading: you are matching against "things I installed on purpose" (ollama, distro
plumbing like resolve/timesync, snap services are typical legit residents). A
unit/timer/cron line you cannot attribute → pull its file and read what it
executes before judging.

## 4. Planted SSH key

```bash
cat ~/.ssh/authorized_keys 2>/dev/null
```

Reading: on a dev box that nobody SSHes *into*, this file should be absent or
empty. Any key you didn't put there = standing remote access for whoever holds
the private half. A hit is decisive.

## 5. Shell-rc injection

```bash
grep -nE 'curl[^|]*\|\s*(ba)?sh|wget[^|]*\|\s*(ba)?sh|base64\s+(-d|--decode)|/dev/tcp/' \
  ~/.bashrc ~/.profile ~/.bash_profile ~/.zshrc 2>/dev/null
```

Reading: droppers append a fetch-and-execute or an obfuscated payload to shell
startup so they re-run every session. A hit needs eyeballing — some legit
installers (version managers) also write rc lines; the tell is *fetching remote
content at shell start* vs. sourcing a local file.

## 6. Executable `.pth` files (Python autorun)

```bash
find / -name '*.pth' -path '*site-packages*' 2>/dev/null \
  -exec grep -l '^import' {} \;
```

Reading: `.pth` files normally contain only paths; a line starting with `import`
executes arbitrary code **at every Python interpreter start** — a known
supply-chain persistence trick. Legit uses exist (some packaging shims), so read
what the import does before verdicting. Also `find -name '<the named dropper>.pth'`
for the specific incident's artifact.

## 7. Network state (outside any sandbox)

```bash
sudo ss -tunp
```

Reading: run this in a **normal shell, not a sandboxed agent session** — sandboxes
can blind it. You're eyeballing outbound connections for processes that have no
business talking to the network. Snapshot-quality evidence only (an implant that
phones home hourly won't be mid-call), so a quiet listing is weak comfort; an
unexplained established connection is a strong lead.

## 8. Secrets-exposure inventory (what a thief would have gotten)

```bash
ls -la ~/.ssh ~/.aws ~/.config/gh ~/.netrc 2>/dev/null
env | grep -iE 'TOKEN|KEY|SECRET|PASS' | cut -d= -f1        # names only
find ~ -maxdepth 3 -name '.env' 2>/dev/null
cat ~/.npmrc 2>/dev/null   # plaintext auth tokens live here
```

Reading: this isn't an IOC check — it's the blast-radius measurement that decides
the *response* to any hit above. If a compromise window overlaps with long-lived
plaintext credentials being present, those credentials rotate **from a clean
device**, whatever the other checks say.

## Recording

Per vector: `HIT` (with the artifact), `clean`, or `not-checked` — never let an
unchecked vector default to clean (the iterative-verification rule: no
confirmation = UNVERIFIED, not DISCONFIRMED).
