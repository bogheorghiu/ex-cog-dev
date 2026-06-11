# Interpreting detections (Step 4)

> Loaded on demand by `windows-wsl-security-verification`. Raw detections are
> ambiguous by design — AV vendors over-flag to be safe, aggregate labels
> compress away the substance, and web filters fire on things that never ran.
> These discriminators decide what a detection *is* before it becomes a verdict.
> Misreading costs in both directions: panic (credential rotation, rebuilds, lost
> days over grayware) or false comfort (a real trojan dismissed as "probably a
> false positive").

## 1. VirusTotal: grayware vs. a trojan wearing the app's name

The question a VT score must answer: **is the app itself junk (PUA/grayware), or
is this a distinct malware family masquerading as the app?** Different verdicts,
different responses — grayware you uninstall and move on; a masquerading trojan
means the box was compromised and credentials rotate.

**Do not read the aggregate** ("popular threat label: trojan.X", "14/70"). Read
the engine rows:

- **Named-family verdicts carry the signal.** Engines that name a specific
  family (ESET, Ikarus, Malwarebytes, Fortinet, CrowdStrike Falcon…): if they
  say `PUA`, `PUP`, `Riskware`, `grayware` **and the family is the app itself**
  (`family: <appname>`), the substance is "this app is classified as junkware."
- **Generic ML/heuristic rows escalate the *label*, not the evidence.** Engines
  like `Artemis!...`, `Static AI - Suspicious PE`, DeepInstinct fire on
  *features* — `upx` packing, `persistence` (autostart), `detect-debug` — which
  junkware and malware share. When the "trojan" rows are all of this kind and
  every named-family row says PUA-of-the-app, the aggregate "trojan" label is an
  artifact of averaging.
- **The flip side:** if *named-family* engines name a family that is **not** the
  app (`family: xmrig` on a "torrent client", a known stealer family on
  anything), that IS the masquerade case — treat as a hit.

Worked case: a torrent client at 14/70, aggregate "trojan.<appname>". Every
named-family verdict: uTorrent-PUA/Riskware, family = the app. Every "trojan"
row: generic ML on upx+persistence tags. Substance: real app, classified
grayware → uninstall as junk (surface reduction), not incident response.

## 2. Web-filter blocks: destination reputation ≠ infection

An AV's web-protection popup ("we blocked access to <site>") is a statement
about the **destination's** reputation/category — not a malware finding on your
box. Triage:

1. **What made the request?** A browser process is consistent with benign — and
   browsers make requests *without clicks*: a new-tab page's "top sites" tile
   re-requests stored historical URLs (favicon, preconnect) every time the tab
   opens. A non-browser process re-requesting a flagged destination is the
   actually-alarming shape. **Caveat:** not every popup exposes the originating
   process (page-load blocks often don't) — check what the popup actually shows
   before promising this field; when absent, triage on the URL and context
   instead.
2. **What kind of block?** Wording like "not recommended to continue *browsing*
   this website" = a page-load/category block in a browsing context. An
   exfiltration or C2 block reads differently and deserves escalation.
3. **Is the URL explainable from history?** A URL you recognize from past
   legitimate use, resurfacing via a new-tab tile, closes the loop. Privacy
   follow-up (clear the history entry, remove the tile — stored URLs can carry
   account identifiers in plaintext), not incident response.

## 3. False-positive priors worth knowing

- Single-engine hits (1/76) on a signed binary from a known vendor are almost
  always FP — verify the signature, check the vendor's known-FP notes.
- Detection names containing `Heur`, `Gen`, `Artemis`, `Static AI`, `ML` are
  heuristic guesses, weighted accordingly.
- A *known incident* FP class exists too: real campaigns trigger vendors to ship
  over-broad signatures that then flag adjacent legit software (this happened in
  the campaign-class incidents this skill grew from). When an advisory says "X
  was a false positive," believe the advisory over the local detection.

## The asymmetry, restated

A detection that *survives* these discriminators escalates calmly: contain,
rotate credentials from a clean device, plan a rebuild. A detection that
*doesn't* survive them gets closed **with its reason written down** — the next
scan will re-flag the same thing, and the written reason is what prevents
re-triaging it from scratch.
