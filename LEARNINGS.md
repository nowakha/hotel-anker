# Hotel Anker â€” Learnings & Handoff

Stand: **2026-07-29** — PI01+PI02 auf Administration; PI02 `fb-clock` mit echter `out_time`-Sync.
Ziel: eine andere Cursor-Instanz auf einem anderen Rechner kann ohne mündlichen Kontext weiterarbeiten.

## Clock geht nach (2026-07-29 ~03:15)

- **Symptom:** Uhrvideo auf PI02 sichtbar hinter Wanduhr; alter Drift-Gate meldete nichts.
- **Ursache 1:** Drift wurde als `seek + monotonic` geschätzt — bei ffmpeg-Lag (Throttle) bleibt Drift≈0, obwohl Bild nachgeht.
- **Ursache 2:** Pi unter Last `temp≈82–85°C`, `throttled=0xe0008` (soft temp) — Scale 860→3440 RGB565 @25 fps hält `-re` nicht.
- **Ursache 3:** Pipeline-Latenz v4l2m2m→fbdev ≈ **1.4 s**; ohne Seek-Lead thrashte echter `out_time`-Check (Resync-Schleife).
- **Fix LIVE:** `fb_clock_play.py` liest ffmpeg `-progress out_time`; `--seek-lead 1.4`; `--max-fps 12` vor Upscale; `--max-drift 0.5` / check 2 s. Unit deployed.
- **Hardware:** Kühlung/PSU weiter beobachten — sonst Drift wächst langsam und resynct gelegentlich (sichtbarer Hitch).

**Workflow (verbindlich):** `.cursor/rules/hotel-anker-workflow.mdc` — jeden Schritt dokumentieren (Erfolg+Misserfolg), Credentials/Learnings mitziehen, commit + `git push origin HEAD`.

**Agent-Handoff (eine Datei):** [`AGENTS.md`](./AGENTS.md) — Status, Next, Session-Chronik (ersetzt `NEXT_AGENT.md` + Roh-Transkripte).  
Detaillierte Chronik: [`WerbeLEDbox-CountDown/docs/SESSION_LOG.md`](./WerbeLEDbox-CountDown/docs/SESSION_LOG.md).

## Agent-Docs konsolidiert (2026-07-29)

- `AGENTS.md` = kanonisch (Orientierung + LIVE-Status + alle Top-Level-Agent-Sessions).
- `WerbeLEDbox-CountDown/docs/NEXT_AGENT.md` entfernt; Verweise → `AGENTS.md`.
- Guest-Portal-Quellen wieder auf dem aktiven Branch; Export CSV unter `guest-email-portal/exports/`.

## WPA3 / AnkerPI01 Zero 2 W (2026-07-29)

- **Administration** live: `wpa3_transition=true`, `pmf_mode=optional` → Scan `WPA2 WPA3` (nicht mehr WPA3-only).
- Pi Zero 2 W (CYW43436): **kein zuverlässiges WPA3-SAE**; NM immer `key-mgmt=wpa-psk`. WPA3-only + PMF required → Association fail / „Secrets were required“.
- Vor Migrate immer UniFi `wlanconf` + Client-Scan SECURITY prüfen — nicht Docs-Annahme „WPA2“ blind glauben.
- Siehe `WerbeLEDbox-CountDown/docs/NETWORK_UNIFI.md` § WPA3.

## AnkerPI01 SD WiFi rescue (2026-07-29)

- **Never** set `HotelAnker` `autoconnect=no` until Administration is associated **and** wlan0 has `192.168.1.x` for several seconds. Doing that when Admin fails → **zero WiFi** (PI01 bricked offline).
- Soll runtime: SSID **Administration** primary (prio 100, powersave=2, PSK `HeimatSchutz`, **wpa-psk**). HotelAnker low-prio fallback until proven.
- SD offline fix path (TabletHi10Max): usbipd busid **6-2** Mass Storage → WSL mount bootfs/rootfs → `scripts/pi01_sd_wifi_rescue.sh --auto` → sync/umount → `usbipd detach` → SD back into Pi + power on.
- Always **umount before** `usbipd detach`; yank-while-mounted caused EXT4 journal I/O errors (recoverable via `e2fsck -fy`).

## Hauptprojekt & Netz (2026-07-28)

- **Ein Repo:** `Hotel Anker/` = Remote `hotel-anker`. Module sind Ordner, keine zweiten Roots.
- **SSIDs:** `Administration` (`.1.x`, Pis+Staff) · `HotelAnker` (Bar `.2.x`) · `HotelAnkerGuest` (Portal `.3.x`).
- **PSK Staff:** `HeimatSchutz` (`secrets/wifi.hotelanker.yml`) — gilt für Administration **und** HotelAnker.
- **Pis umziehen:** `scripts/migrate_pis_to_administration_wifi.py` (SSH-Jump über UDM; Windows routed VLAN2 nicht).
- **2026-07-28 Versuch:** PI01 teilweise umgestellt, danach offline — **Power-Cycle**, dann Skript erneut. PI02 war schon ohne SSH.
- **~19:00 Recheck:** beide Tailscale offline; UniFi zeigt keine Pi-Clients; DHCP noch Bar-Leases (PI02 `.2.222`). **Ja Strom-Reset**, **kein** Factory/SD-Wipe (SD schwer erreichbar). Nach Boot oft wieder HotelAnker → Skript.

## Domains Hotel Anker Rorschach (2026-07-28)

- **Belegt:** `hotelanker.ch` / `hotel-anker.ch` / `anker-hotel.ch` (Hostpoint, keine Website); `hotelanker.com` Aftermarket; `hotelanker.de` + `.eu`.
- **Sofort kaufen:** `ankerhotel.ch` + `hotelankerrorschach.ch` + `hotel-anker-rorschach.ch` + `hotelanker.swiss` ≈ **CHF 105** Jahr 1 (Hostpoint).
- **Empfohlen dazu:** `hotelankerrorschach.com`, `hotelanker.net`, `anker-rorschach.ch`.
- **Warum Geo:** sonst Verwechslung mit Luzern (`hotel-restaurant-anker.ch`).
- **.swiss:** OFCOM-Validierung; Verlängerung Markt ca. CHF 100–170.
- Canvas-Detail: Cursor `canvases/hotel-anker-domains.canvas.tsx`.

## Production clock LIVE (2026-07-23)

- Video: `media/clock_24h.mp4` 860×360 H.264 25fps 86400s auf PI02
- Service: `fb-clock.service` → `fb_clock_play.py` (continuous + resync 120s, HW decode, rotate 180)
- Boot: **enabled**; NTP wait in ExecStartPre
- FPS: live fbdev **~25 fps @ 1.02×** (vs ~0.1 fps mit 4K st24 extract)
- `throttled=0x0` nach Start

## Clock smooth patch (2026-07-24; Sync-Nachzug 2026-07-29)

User: gelegentliches Ruckeln / Uhr geht nach. Ursachen:
1. **Harter ffmpeg-Kill alle 120s** → sichtbarer Hitch (behoben: kein periodischer Resync)
2. **`rotate=PI` nach Upscale** → Flip vor Scale
3. **Mono-Drift-Gate** sah ffmpeg-Lag nicht → 2026-07-29: echte `out_time` + seek-lead + max-fps 12
4. SD read-ahead / Scheduling / Soft-Temp

## Production `clock_24h.mp4` encode (2026-07-23)

- Datei: `WerbeLEDbox-CountDown/media/clock_24h.mp4` (~11.4 GiB) — **860×360** H.264 25 fps `-g 25`, duration **86400.08 s**
- Encode: NVENC auf MLT-NITRO5-HN; altes MP4-Partial ohne moov unbrauchbar → Re-Encode als MKV → Remux
- Deploy-Watcher: `scripts/deploy_clock_24h_when_ready.ps1` (stop 4K, SCP via Tailscale, FPS-Messung, `fb-clock` enable)
- **Blocker:** AnkerPI02 Tailscale offline (~6h) — vermutlich Hang von 4K-Uhr; Power-Cycle am Hotel nötig, dann Deploy automatisch

## Abfahrt 2026-07-22 ~19:41 — Encode pause + Clock live

- **NVENC pause:** ffmpeg PID 8652 gestoppt; Partial `WerbeLEDbox-CountDown/media/_encode_clock_24h.partial.mp4` behalten @ **~37.6%** (`out_time=09:01:50` / 24h). Nicht löschen.
- **Clock dauerhaft:** AnkerPI02 `fb-clock.service` = `fb_clock_opencv.py` **vf860 + drm**, `min-interval 0`, `Restart=always`/`RestartSec=30`, Video `st24.mov`, TZ Europe/Zurich. Verify: frames on fb0, `throttled=0x0`, NRestarts=0.
- Resume encode später auf MLT-NITRO5-HN; danach `clock_24h.mp4` auf Pi.

## Research Pi Clock Playback (2026-07-22 ~19:22)

VollstÃ¤ndig: [`WerbeLEDbox-CountDown/docs/RESEARCH_PI_CLOCK_PLAYBACK.md`](./WerbeLEDbox-CountDown/docs/RESEARCH_PI_CLOCK_PLAYBACK.md).

| Finding | Implication |
|---------|-------------|
| Pi 4 H.264 HW **max ~1080p**; 4K nur HEVC | `st24.mov` 4K H.264 = **immer Soft-Decode**; `v4l2m2m` FAIL erwartet |
| Seek-jedes-Frame ist Anti-Pattern | Continuous play + periodischer Wall-Clock-Resync |
| Signage-Best-Practice | Pre-transcode (unser `860Ã—360`) vor dem Pi |
| fb0 RGB565 ohne X | GStreamer `v4l2convert`â†’`fbdevsink` (Anthias) oder mpv `--vo=drm` |
| PSU | 5.1â€¯V / â‰¥3â€¯A offiziell; `0x50000` = UV history |

**NÃ¤chstes Experiment:** `clock_24h.mp4` auf PI02 â†’ continuous mpv/gstreamer mit `--start=HH:MM:SS` (Europe/Zurich), nicht ffmpeg-Einzelbild.

## AnkerPI02 Pipeline-Bench + Max-FPS (2026-07-22 ~19:28)

**Frage:** Unterscheidet sich 860Ã—360 vs 3440Ã—1440? Was ist schneller?

**Antwort (gemessen, 3 Runs, `st24.mov` 4K, crop T386/B127):** Bottleneck ist **ffmpeg Seek+Decode** (~12â€“13â€¯s), nicht Resize. 860 vs 3440 Host-Resize spart nur ~0.2â€¯s. OpenCV **fehlt** (`cv2` nicht installiert / zuvor SIGBUS).

| Pipeline | MEAN total | ~fps | Bemerkung |
|----------|------------|------|-----------|
| A legacy PNG+PIL 3440 | **13905â€¯ms** | 0.07 | Baseline |
| B1/B2 Host 860 (+blit/NN-up) | ~136â€“13700â€¯ms | 0.07 | kaum besser |
| C1 vfâ†’3440 raw | 12341â€¯ms | 0.08 | ffmpeg crop/scale |
| **C2 vfâ†’860 + NN-up** | **12155â€¯ms** | **0.08** | volles Bild, Gewinner UX/Speed |
| C3 vfâ†’860 center-blit | 12119â€¯ms | 0.08 | winzig auf 3440 â€” nicht brauchbar |
| D `-hwaccel drm` +860 | **12081â€¯ms** | 0.08 | knapp schnellster; v4l2m2m **FAIL** |
| Stages (C2) | extractâ‰ˆ12045 / resizeâ‰ˆ33 / rgb565â‰ˆ72 / fbâ‰ˆ4â€¯ms | | |

**Live max-fps** (`--pipeline vf860 --hwaccel drm --min-interval 0`, 150â€¯s): **15 Frames** auf fb0, `eff_fpsâ‰ˆ0.10â€“0.13`, extract 3.7â€“15â€¯s, **`throttled=0x0` durchgÃ¤ngig**. drm fiel 1Ã— aus â†’ Soft-Fallback. **fb-clock bleibt masked**, `fb_clock_opencv` disabled.

**Default im Player:** `--pipeline vf860` (ffmpeg `crop+scale=860:360+hflip/vflip` â†’ raw â†’ NEARESTâ†’3440 â†’ RGB565). FÃ¼r Autostart weiter `min-interval 15` in Unit.

## Production encode `clock_24h.mp4` (2026-07-22 ~18:53 RUNNING)

Workstation **MLT-NITRO5-HN**, RTX 3080 Laptop, Driver **610.62**, FFmpeg **8.1.2** (WinGet Gyan; PATH oft leer â†’ Full path unter `â€¦\WinGet\Packages\Gyan.FFmpeg_â€¦\ffmpeg-8.1.2-full_build\bin\`).

| Item | Detail |
|------|--------|
| Quelle | `C:\Users\User\Videos\st24.mov` (ffprobe only; **nie** `-f null` Full-Decode) |
| Filter | `crop=3840:1647:0:386,scale=860:360:flags=lanczos` Â· `-r 25` Â· `h264_nvenc` Â· `-g 25` |
| Output | `WerbeLEDbox-CountDown/media/clock_24h.mp4` (via `.partial` + Watcher) |
| Status | **encoding** ffmpeg PID **8652** (~11Ã—) ETA ~**21:00 CEST**; Logs `media/_encode_clock_24h.*` |
| Git | groÃŸe Media **gitignored** (`media/*.mp4`, `_encode*`) |

## AnkerPI02 Undervoltage idle-Check (2026-07-22 ~19:08)

SSH `192.168.8.106`: `get_throttled=0x0` (vorher unter Last `0x50000`). Volts 0.966 V, temp 47.7Â°C, load leicht, uptime ~1 min nach Reboot. **fb-clock** weiter **masked/inactive**. Keine UV-Meldungen in dmesg/journal seit Boot. Caveat: Sticky-Bits clearen bei Reboot; unter Last erneut messen. Gutes 5V/â‰¥3A-PSU weiter empfohlen.
## AnkerPI02 Undervoltage idle-Check (2026-07-22 ~19:08)

SSH `192.168.8.106`: `get_throttled=0x0` (vorher unter Last `0x50000`). Volts 0.966 V, temp 47.7Â°C, load leicht, uptime ~1 min nach Reboot. **fb-clock** weiter **masked/inactive**. Keine UV-Meldungen in dmesg/journal seit Boot. Caveat: Sticky-Bits clearen bei Reboot; unter Last erneut messen. Gutes 5V/â‰¥3A-PSU weiter empfohlen.
## AnkerPI02 OpenCV / Video-Clock (2026-07-22 ~18:45)

**Clock running? NEIN** â€” `fb-clock` soll **masked** bleiben. Netz-Ping ~18:51 (`.106`/`.112`/TS) **FAIL** â€” Mask-State remote nicht bestÃ¤tigt.

| Befund | Detail |
|--------|--------|
| PSU | `vcgencmd get_throttled=0x50000` â€” **Under-voltage has occurred**; Reboots unter 4K-Decode/apt |
| apt `python3-opencv` | **FAIL** â€” ~645â€¯MB Deps â†’ OOM/Reboot mid-install auf 2â€¯GB Pi |
| pip `opencv-python-headless` in venv | Install OK kurzzeitig; danach **`import cv2` / VideoCapture(st24) â†’ SIGBUS** |
| Pure OpenCV decode-loop | **nicht tragbar** fÃ¼r st24 4K |
| Hybrid **OK kurz** | `fb_clock_opencv.py`: `ffmpeg -ss -frames:v 1` â†’ PIL crop/scale/rotate180 â†’ RGB565 fb0 |
| Gemessen | ~0.1â€“0.15â€¯fps; extract 5â€“14â€¯s/Frame; crop T386/B127; seek = wall clock Europe/Zurich |
| systemd enable | 2â€“3 Frames im Journal, dann **Reboot** â†’ sofort wieder maskiert |
| Empfehlung | Offizielles **5â€¯V/â‰¥3â€¯A** PSU; Produktion **`clock_24h.mp4` 860Ã—360**; dann Unit `systemd/fb_clock_opencv.service` unmasken (`min-interval` 15â€¯s) |

Enable (nur nach stabilem PSU / kleinerem Video):

```bash
sudo cp ~/WerbeLEDbox-CountDown/systemd/fb_clock_opencv.service /etc/systemd/system/fb-clock.service
sudo systemctl daemon-reload && sudo systemctl unmask fb-clock
sudo systemctl enable --now fb-clock
# Stop/Mask: sudo systemctl disable --now fb-clock; sudo systemctl mask fb-clock
```

## AnkerPI01 WiFi â€” persistent /etc keyfile (2026-07-22 ~18:12)

Same lesson as PI02: active profile was only under `/run/NetworkManager/system-connections/` (`netplan-wlan0-HotelAnker`). Now: `/etc/.../HotelAnker.nmconnection` (prio 20, powersave=2, DNS pinned). **Live:** wlan0 **HotelAnker** â†’ `192.168.8.102`; Power Management **off**.

**5 GHz:** Pi Zero 2 W = **Band 1 only** â†’ `HotelAnker_5G` not visible / not created (N/A on this hardware). PI02 keeps dual 5G+2.4 profiles.

## AnkerPI02 WiFi â€” Root Cause + Fix (2026-07-22 ~18:00)

**Nicht** rfkill, **nicht** `config.txt`/`dtoverlay` WiFi-Disable, **nicht** Underclock.

1. Stack: **NetworkManager** (dhcpcd absent; systemd-networkd inactive).
2. `/etc/NetworkManager/system-connections/` war **leer** â†’ wlan0 `disconnected` / NO-CARRIER trotz Scan (HotelAnker @ 100%).
3. `nmcli connection add` landete nur unter `/run/NetworkManager/system-connections/` (tmpfs) â†’ Profile nach Kill/Reload weg. **Fix:** Keyfiles direkt nach `/etc/...` schreiben, `chmod 600`, `nmcli connection reload`.
4. Profiles: `HotelAnker_5G` priority **20**, `HotelAnker` priority **10**; powersave=2; DNS 1.1.1.1/8.8.8.8. PSK in `secrets/wifi.hotelanker.yml`.
5. **Live:** wlan0 **HotelAnker_5G** â†’ `192.168.8.106`; eth0 â†’ `192.168.8.112`; Tailscale `100.103.54.63`. **fb-clock bleibt masked.**

## SD-Rescue AnkerPI02 â€” SUCCESS (2026-07-22 ~17:18)

SD im USB-Reader an MLT-NITRO5-HN (Disk 2, 119.4 GB, `bootfs`=`E:`):

- **fb-clock masked** (`â†’ /dev/null`); Wants entfernt; alte Unit `.DISABLED`.
- Gepatchtes `fb_clock_play.py` (ffprobe / Never decode) auf Pi-rootfs deployt.
- Repo-Unit als `fb-clock.service.REPO` (nicht enabled). **cmdline.txt unberÃ¼hrt.**
- `wsl --mount` scheiterte hier (`0x8007000f`); **usbipd** bind+attach â†’ WSL `/dev/sde` OK.
- Helper `scripts/pi02_sd_rescue_wsl.sh` unter WSL ggf. CRLF strippen (`sed -i 's/\r$//'`) .

### Post-boot Verify â€” erledigt via Ethernet (~17:53â€“18:00)

Nach LAN-Kabel: SSH auf **`.112`** (eth) / mDNS `AnkerPI02.local`. Verify: **fb-clock masked**, `fb_clock_play.py` hat **ffprobe**. WiFi restored (siehe oben). Unmask weiter nur nach Freigabe.

## Cursor Workspace (kanonisch)

- **Arbeitsordner (Harald / DESKTOP-UJ8NNE9):** `C:\Users\Harald Nowak\Documents\Cursor Projects\Hotel Anker` — Clone 2026-07-24 von `nowakha/hotel-anker` (leer → `git clone … .`).
- **Andere Maschine (MLT-NITRO5-HN):** `C:\Users\User\Documents\Cursor Projects\Hotel Anker`.
- Cursor-Anzeige mit zwei Namen (**Hotel Anker** + **hotel-anker**) = derselbe Git-Stand: Ordnername vs. GitHub-Slug `nowakha/hotel-anker`.
- Auf DESKTOP-UJ8NNE9: `git` installiert unter `C:\Program Files\Git\cmd\` (PATH oft leer → Session mit Full-PATH); `gh` fehlt noch.

## Repo & Secrets

- Remote: `https://github.com/nowakha/hotel-anker.git` (**privat halten** â€” enthÃ¤lt SSH-PasswÃ¶rter).
- Credentials: `WerbeLEDbox-CountDown/secrets/ankerpi0{1,2}.credentials.yml` + `wifi.hotelanker.yml` â€” **bewusst getrackt**.
- SSH-User/Passwort beider Pis: `user` / `12345678` (PasswordAuthentication an).
- SSH-Keys: `hotel-anker-dev@TABLETHI10MAX` (legacy) + `hotel-anker-dev@MLT-NITRO5-HN` (2026-07-22).
- Private Keys **nicht** im Repo. Fragment: `WerbeLEDbox-CountDown/ssh/config.fragment`.

## Hardware-Wahrheit

1. **AnkerPI01** â€” Pi Zero 2 W: SPI0 `ws2812put` + Producer **`countdown_pi01`** â†’ `shm://ws2812` `(1179,3)`. DHCP oft **`192.168.8.102`** (auch `.108` gesehen) â€” mDNS bevorzugen. **DNS pinned 1.1.1.1/8.8.8.8** (NM). WiFi: persistent `/etc/.../HotelAnker.nmconnection` (2.4 only; **kein 5 GHz**). **Tailscale 1.98.9 installiert** (`tailscaled` active); **Join NeedsLogin** â€” Auth: https://login.tailscale.com/a/144cabd401ab72 Â· Hostname `AnkerPI01` Â· `--accept-dns=false`.
2. **AnkerPI02** â€” Pi 4: HDMI **3440Ã—1440@50**. **Default-Clock neu: `fb_clock_live.py`** (kein MP4/MOV-Decode). Optional designed `clock_24h.mp4` / provisional `st24.mov` nur mit gepatchtem `fb_clock_play` (ffprobe). **wlan0** oft **`192.168.8.106`** (HotelAnker_5G); **eth0** **`192.168.8.112`**. Tailscale: **`ankerpi02` / `100.103.54.63`**. fb-clock derzeit **masked**.
3. **SD-Karte PI02 schwer entnehmbar** â†’ Boot-Schutz; SD-Rescue Docs: `docs/PI02_SD_RESCUE.md`.
4. **Teensy** am PI02 USB: Hex gebaut + offline validiert (`teensy/hex/`, `validate_teensy_build.py` PASS). Flash: `teensy/scripts/flash_from_pi02.ps1`. Pico = Lab.

## Kritische Falle (2026-07-22)

`fb_clock_play.probe_size()` mit `ffmpeg -i FILE -f null -` dekodierte **die gesamte Datei**. Bei 24h 4K â†’ Pi tot.  
**Fix:** ffprobe / kein Full-Decode. **Noch besser fÃ¼r Betrieb:** Live-Clock ohne Video.

### Failure mode

1. Boot â†’ Splash sichtbar.
2. `fb-clock` startet nach NTP-Wartezeit.
3. Alter Player â†’ Full-Decode `st24.mov` â†’ Hang â†’ Netz tot.

### Rescue

Direkt-Ethernet + Watcher (`PI02_DIRECT_ETH_RESCUE.md`) oder SD-Rescue (SUCCESS ~17:18). Nicht `cmdline.txt` experimentieren.

## Print / Bespannung

- `Richnerstutz-Bespannung-Paket/`, Rahmen 2100 mm, Textilâ†’LED 45 mm.
- Interim-Schemas `06-fotos-vom-rahmen/01-schema-*.png`. Original-JPGs: `import_rahmen_fotos.ps1`.

## Erledigt 2026-07-22 (LÃ¼cken geschlossen)

- Live-Clock + Install-Skript; optional `gen_clock_24h.py`.
- PI01 Countdown-Producer + systemd.
- Teensy hex tracked + validate script PASS.
- Richnerstutz Schema-Beilagen + Import-Skript.

## AnkerPI01 Netz â€” Root Cause (2026-07-22 ~17:45)

**Nicht nur DNS.** Drei Schichten:

1. **WiFi-Link instabil (Pi Zero 2 W)** â€” intermittierend 100% Ping-Loss / SSH-Timeouts trotz ARP; Power-Management war `on` â†’ Service `wlan-powersave-off` + NM `powersave=disable`; Runtime ggf. wieder `on` nach Reconnect â†’ `/sbin/iwconfig wlan0 power off` erneut.
2. **DNS fragil** â€” nur Router `192.168.8.254` â†’ **FIX:** NM `ipv4.dns=1.1.1.1 8.8.8.8`, `ignore-auto-dns=yes` (verifiziert in `/etc/resolv.conf`).
3. **Tailscale-Deb-Fetch** â€” Small HTTPS zu `pkgs.tailscale.com` OK; IPv6 CloudFront tot; groÃŸe IPv4-Downloads (~34â€¯MB) timeout / â€žNo route to hostâ€œ / ~KB/s. **Workaround:** Deb per LAN-SCP von Workstation, `dpkg -i`; `apt` mit `Acquire::ForceIPv4 true`.

Status ~18:12: SSH OK, persistent HotelAnker keyfile under `/etc`, DNS pinned, powersave off, Tailscale **1.98.9 installiert** via LAN-SCP Deb; **Join wartet auf Browser-Auth** (kein Auth-Key). Nach Login: `tailscale ip -4` â†’ Secrets `tailscale_ip` setzen.

## Offene Arbeit (PrioritÃ¤t)

1. PI02 nach SD-Rescue booten â†’ SSH â†’ **`install_fb_clock_live_service.sh`** (oder patched play verifizieren) â†’ unmask nur Live/safe path.
2. **PI01 Tailscale Auth:** https://login.tailscale.com/a/144cabd401ab72 Ã¶ffnen â†’ danach IP in `secrets/ankerpi01.credentials.yml` eintragen.
3. PI01: `install_ws2812put_service.sh` + `install_countdown_pi01_service.sh`.
4. Teensy flash (Program-Taste) wenn PI02 USB ok.
5. Original-Rahmen-JPGs nachlegen; optional NVENC `clock_24h.mp4`.

## Kontakt (Technik)

Harald Nowak Â· Modernlight Â· Harald.Nowak@modernlight.ch Â· +41 76 579 84 54 Â· Wangenstrasse 57, 3018 Bern  
Regel: `.cursor/rules/harald-nowak-modernlight.mdc`

## 2026-07-22 17:44 â€” AnkerPI02 calm LAN discovery (post-SD-rescue)

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

## Richnerstutz Anfrage (2026-07-23 ~17:27)
- Mail Offerte SEG-Bespannung Hotel Anker Flowbox an info@richnerstutz.ch **gesendet** (Workspace Web).
- OAuth/`gog` für Workspace-Send aktuell unbrauchbar (fremdes GCP-Projekt / Testing).

## Druckdaten 250 Textil / 300 optisch (2026-07-27)

- **Optisch unten dunkel (Einbau):** 300 mm = 250 mm Totzone Textil + 50 mm Alu-Stirn.
- **Drucktextil Richnerstutz:** 2000×2000 mm, Schwarz **250 mm** (Stirn nicht mitdrucken). Offerte AG 461414 = Textil 200×200 cm.
- Generator: Totzone jetzt **deckend schwarz** (kein Grautext / Fassadenüberhang).
- Script: `WerbeLEDbox-CountDown/scripts/finalize_print_pdfs.py`
- Lieferdateien: `02-druckdaten/DRUCK-Hotel-Anker-Flowbox-2000x2000.pdf` (MediaBox 2000 mm), `FREIGABE-Massblatt-2100.pdf` (MediaBox 2100 mm, Bemaßung 300 optisch), `DRUCK-Opazitaet-2000x2000.pdf`.
- Spec-Konstante: `VISUAL_BOTTOM_DARK_MM = 300` in `kendu_flowbox_spec.py`.
- Original-Rahmen-JPGs fehlen weiterhin in `06-fotos-vom-rahmen/` (nur Schemata).

## Rahmenfotos eingepflegt (2026-07-27)

- Originale in `Richnerstutz-Bespannung-Paket/06-fotos-vom-rahmen/01`–`05-*.png`.
- Foto 04: **Profiltiefe Z ≈ 80–85 mm** (nicht mit 45 mm Kavität verwechseln).
- Foto 05: **Innen Profil→LED ≈ 25 mm**.
- Foto 01: unter den 8 Modulreihen **Controllerkanal** sichtbar (ohne Textil) → bestätigt dunkle Zone unten.
- Drucklogik unverändert: Textil-Schwarz **250 mm**, optisch Einbau **300 mm** (=250+50 Stirn).

## Druckmaster korrigiert: 2100 × 2100 mm (2026-07-27)

- **Wahrheit:** User-PDF `print-ghost-hires.pdf` — MediaBox **2100.09 mm**, Schwarz unten **≈300 mm**.
- Frühere Repo-Produktion 2000 mm / 250 mm Totzone war **falsch** (widerrufen).
- Kanonisch: `02-druckdaten/DRUCK-Hotel-Anker-Flowbox-2100x2100.pdf` + `DRUCK-Opazitaet-2100x2100.pdf`.
- Spec: `PRINT_MM=2100`, `PRINT_DEAD_MM=300` in `kendu_flowbox_spec.py`.
- Offerte AG 461414 noch 200×200 cm → Nachtrag-Text in `01-anfrage/Nachtrag-Spannmass-210cm.md`.

## Finale Druckdaten-Mail an Richner (2026-07-27)

- ZIP: `~/Desktop/Hotel-Anker-Richnerstutz-Finale-Druckdaten.zip` (~20 MB) und Downloads.
- Inhalt: `DRUCK-…-2100x2100.pdf`, Opazität-PDF, 5 Rahmenfotos, PRINT_SPEC, Nachtrag.
- Mail-Entwurf: `01-anfrage/Mail-Finale-Druckdaten.md` — An `info@richnerstutz.ch`, Betreff AG 461414 / Spannmaß 210×210 cm.
- Versand: Gmail-Compose geöffnet; Body in Zwischenablage; ZIP am Desktop — Anhang + Senden manuell (OAuth/`gog` unbrauchbar).

## Git-Policy: alles Lokale tracken (2026-07-27)

- Harald: Deliverables (ZIP, Druck-PDFs, Fotos, Offerte) **müssen** im Repo sein — kein «zu groß / nur Desktop».
- `.gitignore` bereinigt: keine Ignore-Regeln mehr für print/media-Pakete; nur Scratch `_encode*` / venv / `__pycache__`.
- Spiegel: `Richnerstutz-Bespannung-Paket/versand/` (Finale ZIP + Offerte + User-PDF).
