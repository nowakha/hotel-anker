# Hotel Anker — Learnings & Handoff

Stand: **2026-07-22 ~19:08 CEST** (Workstation **MLT-NITRO5-HN** + TABLETHI10MAX).
Ziel: eine andere Cursor-Instanz auf einem anderen Rechner kann ohne mündlichen Kontext weiterarbeiten.

**Workflow (verbindlich):** `.cursor/rules/hotel-anker-workflow.mdc` — jeden Schritt dokumentieren (Erfolg+Misserfolg), Credentials/Learnings mitziehen, commit + `git push origin HEAD`.

Detaillierte Chronik: [`WerbeLEDbox-CountDown/docs/SESSION_LOG.md`](./WerbeLEDbox-CountDown/docs/SESSION_LOG.md).

## Production encode `clock_24h.mp4` (2026-07-22 ~18:53 RUNNING)

Workstation **MLT-NITRO5-HN**, RTX 3080 Laptop, Driver **610.62**, FFmpeg **8.1.2** (WinGet Gyan; PATH oft leer → Full path unter `…\WinGet\Packages\Gyan.FFmpeg_…\ffmpeg-8.1.2-full_build\bin\`).

| Item | Detail |
|------|--------|
| Quelle | `C:\Users\User\Videos\st24.mov` (ffprobe only; **nie** `-f null` Full-Decode) |
| Filter | `crop=3840:1647:0:386,scale=860:360:flags=lanczos` · `-r 25` · `h264_nvenc` · `-g 25` |
| Output | `WerbeLEDbox-CountDown/media/clock_24h.mp4` (via `.partial` + Watcher) |
| Status | **encoding** ffmpeg PID **8652** (~11×) ETA ~**21:00 CEST**; Logs `media/_encode_clock_24h.*` |
| Git | große Media **gitignored** (`media/*.mp4`, `_encode*`) |

## AnkerPI02 Undervoltage idle-Check (2026-07-22 ~19:08)

SSH `192.168.8.106`: `get_throttled=0x0` (vorher unter Last `0x50000`). Volts 0.966 V, temp 47.7°C, load leicht, uptime ~1 min nach Reboot. **fb-clock** weiter **masked/inactive**. Keine UV-Meldungen in dmesg/journal seit Boot. Caveat: Sticky-Bits clearen bei Reboot; unter Last erneut messen. Gutes 5V/≥3A-PSU weiter empfohlen.
## AnkerPI02 Undervoltage idle-Check (2026-07-22 ~19:08)

SSH `192.168.8.106`: `get_throttled=0x0` (vorher unter Last `0x50000`). Volts 0.966 V, temp 47.7°C, load leicht, uptime ~1 min nach Reboot. **fb-clock** weiter **masked/inactive**. Keine UV-Meldungen in dmesg/journal seit Boot. Caveat: Sticky-Bits clearen bei Reboot; unter Last erneut messen. Gutes 5V/≥3A-PSU weiter empfohlen.
## AnkerPI02 OpenCV / Video-Clock (2026-07-22 ~18:45)

**Clock running? NEIN** — `fb-clock` soll **masked** bleiben. Netz-Ping ~18:51 (`.106`/`.112`/TS) **FAIL** — Mask-State remote nicht bestätigt.

| Befund | Detail |
|--------|--------|
| PSU | `vcgencmd get_throttled=0x50000` — **Under-voltage has occurred**; Reboots unter 4K-Decode/apt |
| apt `python3-opencv` | **FAIL** — ~645 MB Deps → OOM/Reboot mid-install auf 2 GB Pi |
| pip `opencv-python-headless` in venv | Install OK kurzzeitig; danach **`import cv2` / VideoCapture(st24) → SIGBUS** |
| Pure OpenCV decode-loop | **nicht tragbar** für st24 4K |
| Hybrid **OK kurz** | `fb_clock_opencv.py`: `ffmpeg -ss -frames:v 1` → PIL crop/scale/rotate180 → RGB565 fb0 |
| Gemessen | ~0.1–0.15 fps; extract 5–14 s/Frame; crop T386/B127; seek = wall clock Europe/Zurich |
| systemd enable | 2–3 Frames im Journal, dann **Reboot** → sofort wieder maskiert |
| Empfehlung | Offizielles **5 V/≥3 A** PSU; Produktion **`clock_24h.mp4` 860×360**; dann Unit `systemd/fb_clock_opencv.service` unmasken (`min-interval` 15 s) |

Enable (nur nach stabilem PSU / kleinerem Video):

```bash
sudo cp ~/WerbeLEDbox-CountDown/systemd/fb_clock_opencv.service /etc/systemd/system/fb-clock.service
sudo systemctl daemon-reload && sudo systemctl unmask fb-clock
sudo systemctl enable --now fb-clock
# Stop/Mask: sudo systemctl disable --now fb-clock; sudo systemctl mask fb-clock
```

## AnkerPI01 WiFi — persistent /etc keyfile (2026-07-22 ~18:12)

Same lesson as PI02: active profile was only under `/run/NetworkManager/system-connections/` (`netplan-wlan0-HotelAnker`). Now: `/etc/.../HotelAnker.nmconnection` (prio 20, powersave=2, DNS pinned). **Live:** wlan0 **HotelAnker** → `192.168.8.102`; Power Management **off**.

**5 GHz:** Pi Zero 2 W = **Band 1 only** → `HotelAnker_5G` not visible / not created (N/A on this hardware). PI02 keeps dual 5G+2.4 profiles.

## AnkerPI02 WiFi — Root Cause + Fix (2026-07-22 ~18:00)

**Nicht** rfkill, **nicht** `config.txt`/`dtoverlay` WiFi-Disable, **nicht** Underclock.

1. Stack: **NetworkManager** (dhcpcd absent; systemd-networkd inactive).
2. `/etc/NetworkManager/system-connections/` war **leer** → wlan0 `disconnected` / NO-CARRIER trotz Scan (HotelAnker @ 100%).
3. `nmcli connection add` landete nur unter `/run/NetworkManager/system-connections/` (tmpfs) → Profile nach Kill/Reload weg. **Fix:** Keyfiles direkt nach `/etc/...` schreiben, `chmod 600`, `nmcli connection reload`.
4. Profiles: `HotelAnker_5G` priority **20**, `HotelAnker` priority **10**; powersave=2; DNS 1.1.1.1/8.8.8.8. PSK in `secrets/wifi.hotelanker.yml`.
5. **Live:** wlan0 **HotelAnker_5G** → `192.168.8.106`; eth0 → `192.168.8.112`; Tailscale `100.103.54.63`. **fb-clock bleibt masked.**

## SD-Rescue AnkerPI02 — SUCCESS (2026-07-22 ~17:18)

SD im USB-Reader an MLT-NITRO5-HN (Disk 2, 119.4 GB, `bootfs`=`E:`):

- **fb-clock masked** (`→ /dev/null`); Wants entfernt; alte Unit `.DISABLED`.
- Gepatchtes `fb_clock_play.py` (ffprobe / Never decode) auf Pi-rootfs deployt.
- Repo-Unit als `fb-clock.service.REPO` (nicht enabled). **cmdline.txt unberührt.**
- `wsl --mount` scheiterte hier (`0x8007000f`); **usbipd** bind+attach → WSL `/dev/sde` OK.
- Helper `scripts/pi02_sd_rescue_wsl.sh` unter WSL ggf. CRLF strippen (`sed -i 's/\r$//'`) .

### Post-boot Verify — erledigt via Ethernet (~17:53–18:00)

Nach LAN-Kabel: SSH auf **`.112`** (eth) / mDNS `AnkerPI02.local`. Verify: **fb-clock masked**, `fb_clock_play.py` hat **ffprobe**. WiFi restored (siehe oben). Unmask weiter nur nach Freigabe.

## Cursor Workspace (kanonisch)

- **Einziger Arbeitsordner:** `C:\Users\User\Documents\Cursor Projects\Hotel Anker` (Name mit Leerzeichen) bzw. Harald-Pfad `C:\Users\Harald Nowak\Documents\Cursor Projects\Hotel Anker`.
- Cursor-Linke «Repositories»-Anzeige mit zwei Namen (**Hotel Anker** + **hotel-anker**) = derselbe Git-Stand: Ordnername vs. GitHub-Slug `nowakha/hotel-anker`.

## Repo & Secrets

- Remote: `https://github.com/nowakha/hotel-anker.git` (**privat halten** — enthält SSH-Passwörter).
- Credentials: `WerbeLEDbox-CountDown/secrets/ankerpi0{1,2}.credentials.yml` + `wifi.hotelanker.yml` — **bewusst getrackt**.
- SSH-User/Passwort beider Pis: `user` / `12345678` (PasswordAuthentication an).
- SSH-Keys: `hotel-anker-dev@TABLETHI10MAX` (legacy) + `hotel-anker-dev@MLT-NITRO5-HN` (2026-07-22).
- Private Keys **nicht** im Repo. Fragment: `WerbeLEDbox-CountDown/ssh/config.fragment`.

## Hardware-Wahrheit

1. **AnkerPI01** — Pi Zero 2 W: SPI0 `ws2812put` + Producer **`countdown_pi01`** → `shm://ws2812` `(1179,3)`. DHCP oft **`192.168.8.102`** (auch `.108` gesehen) — mDNS bevorzugen. **DNS pinned 1.1.1.1/8.8.8.8** (NM). WiFi: persistent `/etc/.../HotelAnker.nmconnection` (2.4 only; **kein 5 GHz**). **Tailscale 1.98.9 installiert** (`tailscaled` active); **Join NeedsLogin** — Auth: https://login.tailscale.com/a/144cabd401ab72 · Hostname `AnkerPI01` · `--accept-dns=false`.
2. **AnkerPI02** — Pi 4: HDMI **3440×1440@50**. **Default-Clock neu: `fb_clock_live.py`** (kein MP4/MOV-Decode). Optional designed `clock_24h.mp4` / provisional `st24.mov` nur mit gepatchtem `fb_clock_play` (ffprobe). **wlan0** oft **`192.168.8.106`** (HotelAnker_5G); **eth0** **`192.168.8.112`**. Tailscale: **`ankerpi02` / `100.103.54.63`**. fb-clock derzeit **masked**.
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

Status ~18:12: SSH OK, persistent HotelAnker keyfile under `/etc`, DNS pinned, powersave off, Tailscale **1.98.9 installiert** via LAN-SCP Deb; **Join wartet auf Browser-Auth** (kein Auth-Key). Nach Login: `tailscale ip -4` → Secrets `tailscale_ip` setzen.

## Offene Arbeit (Priorität)

1. PI02 nach SD-Rescue booten → SSH → **`install_fb_clock_live_service.sh`** (oder patched play verifizieren) → unmask nur Live/safe path.
2. **PI01 Tailscale Auth:** https://login.tailscale.com/a/144cabd401ab72 öffnen → danach IP in `secrets/ankerpi01.credentials.yml` eintragen.
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
