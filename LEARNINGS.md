# Hotel Anker — Learnings & Handoff

Stand: **2026-07-22 ~17:04 CEST** (Workstation **MLT-NITRO5-HN**).
Ziel: eine andere Cursor-Instanz auf einem anderen Rechner kann ohne mündlichen Kontext weiterarbeiten.

**Workflow (verbindlich):** `.cursor/rules/hotel-anker-workflow.mdc` — jeden Schritt dokumentieren (Erfolg+Misserfolg), Credentials/Learnings mitziehen, commit + `git push origin HEAD`.

Detaillierte Chronik: [`WerbeLEDbox-CountDown/docs/SESSION_LOG.md`](./WerbeLEDbox-CountDown/docs/SESSION_LOG.md).

## Cursor Workspace (kanonisch)

- **Einziger Arbeitsordner:** `C:\Users\User\Documents\Cursor Projects\Hotel Anker` (Name mit Leerzeichen).
- Auf Disk gibt es **kein** zweites Clone `hotel-anker` unter `Cursor Projects\` — geprüft 2026-07-22.
- Cursor-Linke «Repositories»-Anzeige mit zwei Namen (**Hotel Anker** + **hotel-anker**) = derselbe Git-Stand: Ordnername vs. GitHub-Slug `nowakha/hotel-anker`. Kein Multi-Root-`.code-workspace`, nur ein `workspaceStorage`-Eintrag auf den Hotel-Anker-Pfad.
- Agent-Root muss auf den Hotel-Anker-Pfad zeigen (`move_agent_to_root`). Ghost-Eintrag «hotel-anker» in der Projektliste ggf. schließen/entfernen — **nicht** von Disk löschen (existiert dort nicht).

## Repo & Secrets

- Remote: `https://github.com/nowakha/hotel-anker.git` (**privat halten** — enthält SSH-Passwörter).
- Credentials: `WerbeLEDbox-CountDown/secrets/ankerpi0{1,2}.credentials.yml` — **bewusst getrackt**.
- SSH-User/Passwort beider Pis: `user` / `12345678` (PasswordAuthentication an).
- SSH-Keys gesehen:
  - Historisch: `hotel-anker-dev@TABLETHI10MAX` (Pubkey in `docs/ANKERPI01.md`).
  - Neu 2026-07-22: `hotel-anker-dev@MLT-NITRO5-HN` auf beiden Pis in `authorized_keys`.
- Private Keys **nicht** im Repo. Fragment: `WerbeLEDbox-CountDown/ssh/config.fragment`.
- GitHub: `gh` eingeloggt als `nowakha`. Tailscale Desktop: `nowakha@googlemail.com`.

## Hardware-Wahrheit

1. **AnkerPI01** — Pi Zero 2 W: SPI0 LED putter. mDNS `AnkerPI01.local`. DHCP zuletzt oft **`192.168.8.102`** (Docs nannten auch `.108` — immer mDNS bevorzugen). Tailscale: **noch nicht** zuverlässig installiert.
2. **AnkerPI02** — Pi 4: HDMI **3440×1440@50**, `fb-clock.service`, Splash `media/boot_splash_3440x1440.*`. LAN **`192.168.8.106`**. Tailscale: **`ankerpi02` / `100.103.54.63`** (war gejoint; nach Hang/Reboot ggf. erneut prüfen).
3. **SD-Karte PI02 schwer entnehmbar** (Decke) → Boot-Schutz oberste Priorität; SD-Rescue nur wenn Ethernet unmöglich (`docs/PI02_SD_RESCUE.md`).
4. **Teensy** am PI02 USB: Live-Pfad für 8×512; Pico = Lab.
5. Provisorisches Clock-Video auf PI02: `media/st24.mov` (4K, 24h, t=0 = 00:00). Produktion bleibt `clock_24h.mp4` 860×360 `-g 25`.

## Kritische Falle (2026-07-22)

`fb_clock_play.probe_size()` mit `ffmpeg -i FILE -f null -` dekodiert **die gesamte Datei**. Bei 24h 4K → Pi tot.  
**Fix im Repo:** `ffprobe` / `ffmpeg -i` ohne Output. **Vor dem nächsten `fb-clock`-Start auf den Pi deployen.**  
Auch `fb_play.py` hatte denselben Bug → im Repo ebenfalls auf ffprobe umgestellt (Lab-Helper; Live-Service nutzt `fb_clock_play.py`).

### Failure mode (sehr hohe Sicherheit)

1. Boot → `fb-splash` malt Anker-Logo auf `/dev/fb0` → **Splash sichtbar**.
2. `fb-clock.service`: `ExecStartPre` wartet bis **120 s** auf NTP, startet **danach trotzdem**.
3. Alter Player → `probe_size()` Full-Decode `st24.mov` → Hang → Netz tot.
4. Repo-Fix **noch nicht** auf dem Pi.

### Rescue-Watcher FAIL trotz Power-Cycles (2026-07-22 ~16:50–16:55)

**Ursache:** PI02 auf **WiFi only**. Association/DHCP/SSH/Tailscale oft **erst nach** dem Hang → **kein SSH-Fenster** für den Watcher.  
Re-Check nach weiterem User-Power-Cycle (~16:43–16:55): Watcher PID **16964** alive; aggressiv ~7 min kein Ping/TCP22; ARP `.106` fehlt; TS offline ~50+ min; DHCP `.100–.115` ohne `.106`; Log ohne `SUCCESS`. SSH/fb-clock-Verify **BLOCKED**.  
Alter Watcher pollte nur `192.168.8.106` + Tailscale `100.103.54.63`.

| Option | Realistisch? | Bemerkung |
|--------|--------------|-----------|
| **Direkt-Ethernet PC↔Pi** | **Ja — Prefer** | Kein DHCP nötig; auto-MDIX; APIPA `169.254.*`; Link in Sekunden → NTP-Fenster; Doc `PI02_DIRECT_ETH_RESCUE.md` |
| Ethernet via Switch/Router | Ja | Bekannte `.106` wenn DHCP; Watcher pollt weiter `.106`+TS |
| Serial `serial0,115200` | Nur mit UART@GPIO | In cmdline dokumentiert; physisch oft schwerer als SD |
| Weitere WiFi-Power-Cycles | **Nein** | Timing gegen Watcher |
| **SD-Rescue** | **Ja wenn kein Eth-Fenster** | User bereit; `docs/PI02_SD_RESCUE.md` + `scripts/pi02_sd_rescue_wsl.sh` |

**Direct-Eth Grenzen:** Ohne DHCP beide `169.254.x.x` — SSH OK solange sshd noch läuft. Wenn ffmpeg Full-Decode die CPU schon friert, hilft kein Interface → Power-Cycle + frühes Fenster erneut. Static nur auf PC ohne Pi-Matching nutzlos; APIPA-Scan ist der praktische Weg.

**Lauf 2026-07-22 ~16:58–17:04:** Kabel gesteckt, PC Ethernet **Up 1 Gbps** + APIPA, `pi02_rescue_direct_eth.ps1` / Watcher `linklocal=True` alive — **kein** Pi-ARP, **kein** TCP/22, **kein** `SUCCESS`. → **rescued=no**; User muss **jetzt power-cyclen** (Kabel allein bei Hang nutzlos).

Tooling: `scripts/pi02_rescue_direct_eth.ps1` → `pi02_rescue_watch.ps1` (`.106` + Tailscale + mDNS + `Get-NetNeighbor`/`arp` für `169.254.*`).

**Nicht** `cmdline.txt` experimentieren. Recovery-Zeile: `media/cmdline.recovery.txt`.

## Encode / Transfer

- Quelle Workstation: `C:\Users\User\Videos\st24.mov` (auch USB-Kopie).
- Crop: Top 386, Bottom 127, Left/Right 0.
- USB→SD rsync: **~13 min @ ~17 MB/s**, Size OK.
- NVENC auf 3080: Driver ≥610 nötig für aktuelles FFmpeg 8.x; Encode-ETA ~6 h bei 860×360.

## Print / Bespannung

Unverändert: `Richnerstutz-Bespannung-Paket/`, Rahmen 2100 mm, Textil→LED 45 mm.

## Offene Arbeit (Priorität)

1. **PI02 Rescue:** **Direkt-Ethernet** PC↔Pi + `pi02_rescue_direct_eth.ps1` + Power-Cycle (Doc `PI02_DIRECT_ETH_RESCUE.md`). Wenn Port unerreichbar / kein SSH-Fenster → **SD-Rescue**. Danach Patch verifizieren, erst dann `fb-clock` unmask/enable.
2. DNS pin (1.1.1.1/8.8.8.8) + Tailscale auf PI01.
3. Produktion `clock_24h.mp4` NVENC encode + Upload.
4. Teensy flash/validate; Countdown-Producer PI01.

## Kontakt (Technik)

Harald Nowak · Modernlight · Harald.Nowak@modernlight.ch · +41 76 579 84 54 · Wangenstrasse 57, 3018 Bern  
Regel: `.cursor/rules/harald-nowak-modernlight.mdc`
