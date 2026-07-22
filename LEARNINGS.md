# Hotel Anker — Learnings & Handoff

Stand: **2026-07-22 ~17:34 CEST** (Workstation **MLT-NITRO5-HN** + TABLETHI10MAX).
Ziel: eine andere Cursor-Instanz auf einem anderen Rechner kann ohne mündlichen Kontext weiterarbeiten.

**Workflow (verbindlich):** `.cursor/rules/hotel-anker-workflow.mdc` — jeden Schritt dokumentieren (Erfolg+Misserfolg), Credentials/Learnings mitziehen, commit + `git push origin HEAD`.

Detaillierte Chronik: [`WerbeLEDbox-CountDown/docs/SESSION_LOG.md`](./WerbeLEDbox-CountDown/docs/SESSION_LOG.md).

## SD-Rescue AnkerPI02 — SUCCESS (2026-07-22 ~17:18)

SD im USB-Reader an MLT-NITRO5-HN (Disk 2, 119.4 GB, `bootfs`=`E:`):

- **fb-clock masked** (`→ /dev/null`); Wants entfernt; alte Unit `.DISABLED`.
- Gepatchtes `fb_clock_play.py` (ffprobe / Never decode) auf Pi-rootfs deployt.
- Repo-Unit als `fb-clock.service.REPO` (nicht enabled). **cmdline.txt unberührt.**
- `wsl --mount` scheiterte hier (`0x8007000f`); **usbipd** bind+attach → WSL `/dev/sde` OK.
- Helper `scripts/pi02_sd_rescue_wsl.sh` unter WSL ggf. CRLF strippen (`sed -i 's/\r$//'`) .

### Post-boot Verify (~17:34) — noch kein Netz

User meldete Boot nach SD-Rescue. Calm Check (~2 min, keine Spam-Polls): **kein** Ping/TCP22 auf `.106`, mDNS oder Tailscale (`ankerpi02` offline ~1h). ARP `.106` Incomplete. Remote-Verify von mask/Player **BLOCKED**.

**Nächster Schritt:** Netz am Pi (WiFi/Ethernet) herstellen → SSH → Verify mask + ffprobe → dann **`fb_clock_live`** enable (kein `st24.mov`-Decode) bzw. gepatchtes `fb_clock_play` nur mit sicherem Probe — Unmask nur nach Freigabe. Siehe `docs/NEXT_AGENT.md`.

## Cursor Workspace (kanonisch)

- **Einziger Arbeitsordner:** `C:\Users\User\Documents\Cursor Projects\Hotel Anker` (Name mit Leerzeichen) bzw. Harald-Pfad `C:\Users\Harald Nowak\Documents\Cursor Projects\Hotel Anker`.
- Cursor-Linke «Repositories»-Anzeige mit zwei Namen (**Hotel Anker** + **hotel-anker**) = derselbe Git-Stand: Ordnername vs. GitHub-Slug `nowakha/hotel-anker`.

## Repo & Secrets

- Remote: `https://github.com/nowakha/hotel-anker.git` (**privat halten** — enthält SSH-Passwörter).
- Credentials: `WerbeLEDbox-CountDown/secrets/ankerpi0{1,2}.credentials.yml` — **bewusst getrackt**.
- SSH-User/Passwort beider Pis: `user` / `12345678` (PasswordAuthentication an).
- SSH-Keys: `hotel-anker-dev@TABLETHI10MAX` (legacy) + `hotel-anker-dev@MLT-NITRO5-HN` (2026-07-22).
- Private Keys **nicht** im Repo. Fragment: `WerbeLEDbox-CountDown/ssh/config.fragment`.

## Hardware-Wahrheit

1. **AnkerPI01** — Pi Zero 2 W: SPI0 `ws2812put` + Producer **`countdown_pi01`** → `shm://ws2812` `(1179,3)`. DHCP oft **`192.168.8.102`** (auch `.108` gesehen) — mDNS bevorzugen.
2. **AnkerPI02** — Pi 4: HDMI **3440×1440@50**. **Default-Clock neu: `fb_clock_live.py`** (kein MP4/MOV-Decode). Optional designed `clock_24h.mp4` / provisional `st24.mov` nur mit gepatchtem `fb_clock_play` (ffprobe). LAN **`192.168.8.106`**. Tailscale: **`ankerpi02` / `100.103.54.63`**.
3. **SD-Karte PI02 schwer entnehmbar** → Boot-Schutz; SD-Rescue Docs: `docs/PI02_SD_RESCUE.md`.
4. **Teensy** am PI02 USB: Hex gebaut + offline validiert (`teensy/hex/`, `validate_teensy_build.py` PASS). Flash: `teensy/scripts/flash_from_pi02.ps1`. Pico = Lab.

## Kritische Falle (2026-07-22)

`fb_clock_play.probe_size()` mit `ffmpeg -i FILE -f null -` dekodierte **die gesamte Datei**. Bei 24h 4K → Pi tot.  
**Fix:** ffprobe / kein Full-Decode. **Noch besser für Betrieb:** Live-Clock ohne Video.

### Failure mode

1. Boot → Splash sichtbar.
2. `fb-clock` startet nach NTP-Wartezeit.
3. Alter Player → Full-Decode `st24.mov` → Hang → Netz tot.

### Rescue

Direkt-Ethernet + Watcher (`PI02_DIRECT_ETH_RESCUE.md`) oder SD-Rescue (SUCCESS ~17:18). Nicht `cmdline.txt` experimentieren.

## Print / Bespannung

- `Richnerstutz-Bespannung-Paket/`, Rahmen 2100 mm, Textil→LED 45 mm.
- Interim-Schemas `06-fotos-vom-rahmen/01-schema-*.png`. Original-JPGs: `import_rahmen_fotos.ps1`.

## Erledigt 2026-07-22 (Lücken geschlossen)

- Live-Clock + Install-Skript; optional `gen_clock_24h.py`.
- PI01 Countdown-Producer + systemd.
- Teensy hex tracked + validate script PASS.
- Richnerstutz Schema-Beilagen + Import-Skript.

## Offene Arbeit (Priorität)

1. PI02 nach SD-Rescue booten → SSH → **`install_fb_clock_live_service.sh`** (oder patched play verifizieren) → unmask nur Live/safe path.
2. PI01 online: `install_ws2812put_service.sh` + `install_countdown_pi01_service.sh`.
3. Teensy flash (Program-Taste) wenn PI02 USB ok.
4. Original-Rahmen-JPGs nachlegen; optional NVENC `clock_24h.mp4`.

## Kontakt (Technik)

Harald Nowak · Modernlight · Harald.Nowak@modernlight.ch · +41 76 579 84 54 · Wangenstrasse 57, 3018 Bern  
Regel: `.cursor/rules/harald-nowak-modernlight.mdc`
