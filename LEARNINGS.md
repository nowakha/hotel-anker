# Hotel Anker — Learnings & Handoff

Stand: **2026-07-22 ~17:45 CEST** (Workstation **MLT-NITRO5-HN** + TABLETHI10MAX).
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

1. **AnkerPI01** — Pi Zero 2 W: SPI0 `ws2812put` + Producer **`countdown_pi01`** → `shm://ws2812` `(1179,3)`. DHCP oft **`192.168.8.102`** (auch `.108` gesehen) — mDNS bevorzugen. **DNS pinned 1.1.1.1/8.8.8.8** (NM). **Tailscale noch nicht installiert.** WiFi war flaky (powersave + CDN).
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

## AnkerPI01 Netz — Root Cause (2026-07-22 ~17:45)

**Nicht nur DNS.** Drei Schichten:

1. **WiFi-Link instabil (Pi Zero 2 W)** — intermittierend 100% Ping-Loss / SSH-Timeouts trotz ARP; Power-Management war `on` → Service `wlan-powersave-off` + NM `powersave=disable`; Runtime ggf. wieder `on` nach Reconnect → `/sbin/iwconfig wlan0 power off` erneut.
2. **DNS fragil** — nur Router `192.168.8.254` → **FIX:** NM `ipv4.dns=1.1.1.1 8.8.8.8`, `ignore-auto-dns=yes` (verifiziert in `/etc/resolv.conf`).
3. **Tailscale-Deb-Fetch** — Small HTTPS zu `pkgs.tailscale.com` OK; IPv6 CloudFront tot; große IPv4-Downloads (~34 MB) timeout / „No route to host“ / ~KB/s. **Workaround:** Deb per LAN-SCP von Workstation, `dpkg -i`; `apt` mit `Acquire::ForceIPv4 true`.

Status ~17:45: SSH OK, DNS pinned, powersave off (re-asserted), Tailscale **nicht** installiert/joined.

## Offene Arbeit (Priorität)

1. PI02 nach SD-Rescue booten → SSH → **`install_fb_clock_live_service.sh`** (oder patched play verifizieren) → unmask nur Live/safe path.
2. **PI01 Tailscale:** LAN-SCP `tailscale_*_arm64.deb` → `dpkg -i` → `tailscale up --hostname=AnkerPI01 --accept-dns=false`.
3. PI01: `install_ws2812put_service.sh` + `install_countdown_pi01_service.sh`.
4. Teensy flash (Program-Taste) wenn PI02 USB ok.
5. Original-Rahmen-JPGs nachlegen; optional NVENC `clock_24h.mp4`.

## Kontakt (Technik)

Harald Nowak · Modernlight · Harald.Nowak@modernlight.ch · +41 76 579 84 54 · Wangenstrasse 57, 3018 Bern  
Regel: `.cursor/rules/harald-nowak-modernlight.mdc`

## 2026-07-22 17:44 — AnkerPI02 calm LAN discovery (post-SD-rescue)

**Result: not on LAN** (no SSH target found)

| Check | Result |
|-------|--------|
| PC net | Wi-Fi 192.168.8.111/24 gw .254; Ethernet Media disconnected |
| 192.168.8.106 | ping unreachable |
| Common IPs (.100/.106-.110/.112/.120/.2/.10/.20/.50/.80/.90) | no ping |
| ARP live | .101 (TTL128/Win), .103-.105 (TTL64, no :22), .254 gw; stale .102 (2c-cf-67 Pi OUI, no ping) |
| AnkerPI02.local / ankerpi02.local | name not found |
| Tailscale ankerpi02 100.103.54.63 | offline, last seen ~1h; ping timeout |
| 169.254 | eth down; 169.254.0.1 Stale/no MAC; :22 no |

Likely causes: WiFi not up after rescue; different subnet; still booting; eth cable only to PC but PC eth unplugged; Tailscale not started.

Not done: fb-clock/ffprobe verify (unreachable). Do not unmask.
