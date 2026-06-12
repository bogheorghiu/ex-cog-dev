# Windows-side checklist (Steps 3 and 5)

> Loaded on demand by `windows-wsl-security-verification`. Most of these run on
> the Windows host — GUI tools or PowerShell — which an agent inside WSL usually
> cannot reach. Drive them as instructions to the user; record reported results.

## 1. Full AV scan

Start it **first** — it runs for a long time in the background while the rest of
the checklist proceeds.

**The active-engine rule:** when a third-party AV (Bitdefender, Kaspersky, ESET…)
is installed, *it* is the active real-time engine and **Windows Defender drops to
passive mode**. The third-party product's Full System Scan covers this item —
additionally running Defender's `Start-MpScan -ScanType FullScan` duplicates
hours of disk I/O for no added real-time coverage. One full scan by the active
engine; that's the item.

(Also expect third-party AVs to auto-run periodic full scans — a second scan
appearing on its own hours later is usually the scheduler, not a finding.)

## 2. Second-opinion scan

One **on-demand** scanner that installs no resident engine, so it can't conflict
with the active AV: Malwarebytes Free or ESET Online Scanner. Why: every AV has
blind spots; a second signature set over the same disk is cheap coverage. Run
once, read results through `interpreting-detections.md`.

## 3. Sysinternals Autoruns — the hub check

Autoruns enumerates *everything* that starts automatically: logon entries,
services, drivers, scheduled tasks, codecs, shell extensions. Procedure:

1. Run as administrator. **Options → Hide Microsoft Entries + Hide Windows
   Entries**, then **F5** to rescan — what remains is third-party autostart, the
   reviewable set.
2. **Options → Scan Options → check VirusTotal** (hash lookups).
3. Focus tabs in order: **Logon**, **Scheduled Tasks**, **Services**, **Drivers**.

**Reading legend (this is where reviews go wrong):**

- **Red row** = unverified/missing code signature. Suspicious-by-default for an
  *unknown* binary; many legit small tools are also unsigned. Signature status is
  a prior, not a verdict.
- **Yellow row** = the registered file no longer exists. Usually leftover cruft
  from uninstalls; also what a cleaned-but-not-deregistered implant looks like.
  Identify what registered it before deleting.
- **"Error" in the VirusTotal column ≠ a detection.** It's a failed lookup.
  Re-check the hash manually if the entry matters.
- **"File not found: C:\Program.exe"** on a task = an **unquoted-path** task
  (`C:\Program Files\...` registered without quotes, parsed at the first space).
  Diagnostic of a *malformed* legit task, not malware — though the unquoted path
  itself is a minor privilege-escalation shape; fix or delete the task.
- Large yellow blocks of Windows-internal entries (WoW64/Known-DLLs,
  UpdateOrchestrator notifications and similar) = benign OS cruft and Autoruns
  quirks. Do not "clean" them.

`Get-ScheduledTask | Where-Object State -ne 'Disabled'` is **subsumed** by the
Scheduled Tasks tab — no need to run both.

## 4. VS Code extensions

```powershell
code --list-extensions
```

**The trust signal is the verified publisher *namespace*** — e.g.
`ms-vscode-remote.*` is Microsoft because the `ms-vscode-remote` namespace is
verified, not because the name sounds official. Typosquats imitate *names*
(`ms-vscode-remot`, `prettier-vscod`); they cannot occupy a verified namespace.
For each extension: is the namespace a verified publisher you recognize, and is
the extension consistent with work you actually do?

## 5. Surface reduction (the Step-5 pass over the same inventory)

Re-walk the Autoruns/extensions list asking **"do I actually use this?"** — every
autostart, service, and driver is attack surface, persistence real-estate, and
patch liability regardless of intent. Special cases worth singling out:

- **BYOVD-class drivers** (Bring Your Own Vulnerable Driver): low-level hardware
  utility drivers — CPU-Z's `cpuz*`, Gigabyte's `gdrv`, MSI/ASUS tuning drivers —
  are kernel-privileged and *known by name* to attackers, who ship the legit
  signed driver themselves to get kernel access. Keep only monitors you actively
  use; **delete stale driver registrations** left by uninstalled tools.
- **Remote-access tools** (AnyDesk, TeamViewer, Parsec…): each is a standing
  inbound channel. Uninstall the ones not in active use, don't just disable.
- **Idle-compute rental / distributed-compute agents**: their *job* is running
  other people's workloads on your box — structurally anti-containment. Remove
  from a dev box that handles credentials.
- **Launcher/updater autostarts** (game stores, browser-bundled updater tasks):
  the app can stay installed; the autostart and its scheduled update tasks can go.

**Uninstall mechanics gotcha:** `Get-AppxPackage | Remove-AppxPackage` removes
**Store/UWP apps only**. Classic Win32 desktop apps don't appear there at all —
uninstall via Settings → Apps or the app's own uninstaller. (This is why
`Get-AppxPackage *<name>*` returning nothing does not mean the app is gone.)

## Recording

Per item: verdict + what was removed/disabled and why, into the SKILL.md output
block. Detections of any kind route through `interpreting-detections.md` first.
