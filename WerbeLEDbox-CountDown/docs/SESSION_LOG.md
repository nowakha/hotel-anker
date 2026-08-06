# SESSION_LOG — Hotel Anker / WerbeLEDbox

Chronik für Cross-Machine-Handoff. Erfolg **und** Misserfolg.

## 2026-08-06 — Day/Night Full-Power Waves auf AnkerPI01

| Item | Ergebnis |
|------|----------|
| Ist | PI01 `100.67.4.18`: `countdown-waves` + `ws2812put-pi02` bereits LIVE |
| Code | `countdown_waves_64.py`: Solar day_factor Rorschach; Tag=weiss/cyan/orange@100%, Nacht=alt |
| Deploy | SCP Script → `systemctl restart countdown-waves` |
| Verify | `elev≈45° day_factor=1.000`, fps≈25, render_ms≈16.6 |
| Preview | `assets/kendu-64x64/countdown-waves-day*.png` von Pi gezogen |
| Creds | `ankerpi01.credentials.yml` Tailscale-IP gefüllt |
| Misserfolg | Mac `python3` numpy kaputt (lokaler Shadow/Install) — Smoke auf Pi OK; Key-SSH Mac→Pi denied → sshpass |

## 2026-07-28 — Domain-Check Hotel Anker Rorschach

| Item | Ergebnis |
|------|----------|
| Methode | RDAP nic.ch / nic.swiss / Verisign / DNS NS |
| Belegt (kritisch) | `hotelanker.ch`, `hotel-anker.ch`, `anker-hotel.ch` (Hostpoint, Sites tot); `hotelanker.com` Afternic; `hotelanker.de`/`.eu` |
| Frei (Must) | `ankerhotel.ch`, `hotelankerrorschach.ch`, `hotel-anker-rorschach.ch`, `hotelanker.swiss` |
| Paket A Jahr 1 | ca. **CHF 105** (Hostpoint: .ch 5→15, .swiss 90, Markt-Verlängerung .swiss 100–170) |
| Canvas | `canvases/hotel-anker-domains.canvas.tsx` (Cursor IDE, neben Chat) |
| Hinweis | Luzern = `hotel-restaurant-anker.ch` — Geo-Domain Rorschach zwingend |

## 2026-07-28 — UniFi inventory + Guest portal mockup

| Item | Ergebnis |
|------|----------|
| UDM Pro Max `192.168.1.254` SSH read-only | OK — FW 5.1.27 |
| U7 Pro Wall `192.168.1.220` | OK — U7PIW 8.6.11 |
| Netze | Default `.1.0/24`, CountDown Bar VLAN2 `.2.0/24`, Guest VLAN3 `.3.0/24` |
| SSIDs | `Administration`, `HotelAnker`, `HotelAnkerGuest` (open+portal, noch UniFi-Default-Branding) |
| Skill | `.cursor/skills/ubiquiti-unifi/` |
| Docs | `docs/NETWORK_UNIFI.md` |
| Portal mockup | `guest-wifi-portal/` — **nicht live applied** (wartet Visual-OK) |
| Pi IPs | neu `.2.x` — Secrets aktualisiert |

## 2026-07-22 (Workstation MLT-NITRO5-HN)

### Zugang / Tooling

| Ereignis | Ergebnis |
|----------|----------|
| Git installiert (fehlte) + GitHub CLI | OK — Account `nowakha` |
| Repo geklont `nowakha/hotel-anker` | OK |
| SSH-Key neu `hotel-anker-dev@MLT-NITRO5-HN` auf PI01+PI02 | OK (Passwort `12345678`) |
| Tailscale auf PI02 installiert + joined | OK — `ankerpi02` = `100.103.54.63` |
| Tailscale auf PI01 | **FAIL** — apt Download `pkgs.tailscale.com` Timeout/DNS; Deb-Install unterbrochen |
| DNS nur Router `192.168.8.254` | Fragil; Fix-Skript vorbereitet, auf PI02 wegen USB-Copy **abgebrochen** (User: nicht kicken) |

### Clock-Video / AnkerPI02

| Ereignis | Ergebnis |
|----------|----------|
| Quelle `C:\Users\User\Videos\st24.mov` | 3840×2160 H.264, 25 fps, **86400.08 s**, ~12.7 GB |
| Crop (Premiere): L0 T386 R0 B127 → ~3840×1647 (~21:9) | Spec |
| Ziel-Spec Produktion | `media/clock_24h.mp4` 860×360 25fps H.264 `-g 25` |
| NVENC zuerst | **FAIL** — Driver 596 vs FFmpeg 8.1 braucht NVENC API 13.1; nach Driver-Update 610.62 OK |
| Full NVENC-Encode 24h | **nicht gestartet** (ETA ~6 h); User: später remote |
| LAN-scp st24.mov | **FAIL/abgebrochen** bei ~2.3 GB; PI02 ging offline |
| USB `st24.mov` → `/mnt/usb` → rsync nach `~/…/media/st24.mov` | **OK** — 774 s, ~16.9 MB/s, Bytes match `13687155613` |
| Runtime Underclock CPU 1000 MHz + config.txt-Block | OK (Transfer) |
| Underclock aus config entfernt + CPU 1.8 GHz | OK (nach USB-Remove) |
| `fb-clock` auf `st24.mov` + Crop + resync 60s | Unit geschrieben |
| `probe_size()` mit `ffmpeg -f null -` | **CRITICAL FAIL** â€” dekodiert 24h 4K â†’ Pi unresponsive; Power-Cycle nÃ¶tig |
| PI02 nach User-Reboot (Stand ~16:08) | **noch offline** (kein Ping/SSH/Tailscale) |
| Re-Check ~16:17â€“16:20 LAN `.106` + TS `100.103.54.63` + mDNS | **FAIL** â€” ping timeout / Destination host unreachable; SSH timeout; mDNS unresolved |
| Handoff-Commit `8044f9a` â†’ `origin/main` | OK â€” Docs, Secrets, probe_size-Fix, Workflow-Regel |
| Offline-Doc-Commit `2f67b57` â†’ `origin/main` | OK |
| Continuity User-Rule + SESSION `09e5571` | OK |
| Deploy patched Player + Clock-Start | **BLOCKED** â€” PI02 offline; wartet auf physischen Strom/Boot-Check |
| User-Rule Â«Hotel Anker â€” Continuity / Git / SecretsÂ» in Cursor Settings | OK â€” zusÃ¤tzlich zu `.cursor/rules/hotel-anker-workflow.mdc` |
| Rescue: `scripts/pi02_rescue_mask_fbclock.py` + `fb_play.py` probe_size-Parity | lokal bereit â†’ commit/push |
| Diagnose ~16:24â€“16:30: LAN `.106` + TS `100.103.54.63` TCP/22 | **FAIL** â€” dauerhaft offline (Splash-on-screen + dead net = classic probe hang) |
| `scripts/pi02_rescue_watch.ps1` | OK gestartet â€” mask+deploy sobald SSH:22 antwortet |
| Commits `f5ec3c1` + this (track `pi02_rescue_watch.ps1`, ignore `_pi02_rescue.log`) | **landed** |
| SD-Entnahme empfohlen? (16:30) | Damals Nein â€” **revidiert 17:00** wegen WiFi-late (siehe unten) |
| Cursor zeigt zwei Repo-Namen Â«Hotel AnkerÂ» + Â«hotel-ankerÂ» | **Kein Doppel-Clone** â€” nur Ordner `Hotel Anker`; Remote-Slug `hotel-anker`. Kein `.code-workspace`. Kanonisch: `â€¦\Cursor Projects\Hotel Anker` |

### Power-Cycle Rescue-Poll (~16:43–16:55)

| Ereignis | Ergebnis |
|----------|----------|
| Watcher PID **16964** (Parent 26468, seit 16:27) | **ALIVE** damals; später **Restart** auf Link-Local-Skript (Parse-Fix) → PID **7560** (~16:57) |
| Aggressiv-Poll ~7 min (`.106` + TS `.63`, TCP/22) | **FAIL** — kein Ping, kein TCP22, kein `SUCCESS` |
| ARP `.106` | **fehlt** |
| Tailscale `ankerpi02` | **offline**, last seen ~50–59 min |
| mDNS `AnkerPI02.local` | unresolved |
| DHCP-Scan `.100–.115` | `.101–.105` + Workstation `.111` alive; **kein** `.106` |
| Re-Poll ~16:57–17:01 inkl. `169.254.*` | **FAIL** — weiterhin offline (Kabel ggf. gesteckt, aber kein SSH ohne frischen Power-Cycle im NTP-Fenster) |
| SSH Verify (fb-clock mask / ffprobe Player) | **BLOCKED** — Pi nie erreichbar |
| SD-Entnahme nötig? | **Noch nicht bewiesen** — Prefer Direkt-Ethernet + Power-Cycle mit laufendem Watcher |

### Rescue-Watcher vs WiFi (~16:50–17:00)

| Ereignis | Ergebnis |
|----------|----------|
| User: ~3 Power-Cycles, PI02 **WiFi only** | Watcher greift nicht |
| `docs/_pi02_rescue.log` | Nur Start `16:27:06` — **kein** `SUCCESS` / kein RESCUE |
| Theorie NTP-Wait ≤120s vs WiFi-late | **bestätigt** — Hang vor nutzbarem SSH; alter Watcher pollte nur `.106`+TS `.63` |
| Temp. Ethernet / Link-Local `169.254.*` | **Bevorzugt** — Doc `PI02_DIRECT_ETH_RESCUE.md` + Watcher-Update |
| Serial `serial0,115200` | In cmdline; braucht UART@GPIO — oft unpraktisch |
| SD-Rescue | **Ja wenn kein Ethernet** â€” User bereit; `docs/PI02_SD_RESCUE.md` + `scripts/pi02_sd_rescue_wsl.sh` |
| Entscheidung | Parent: Ethernet-MÃ¶glichkeit bestÃ¤tigen; sonst SD |

### Direct-Ethernet Rescue (~16:55)

| Ereignis | Ergebnis |
|----------|----------|
| User: Kabel **direkt** PC (MLT-NITRO5-HN) â†” PI02 ohne DHCP? | **Ja hilfreich** â€” auto-MDIX, APIPA `169.254.*`, Link frÃ¼h vs WiFi-late |
| Doc `docs/PI02_DIRECT_ETH_RESCUE.md` | OK â€” DE-Schritte + Grenzen (Hang = kein Interface hilft) |
| `scripts/pi02_rescue_watch.ps1` | Erweitert: `.106` + TS + mDNS + `169.254.*` (Get-NetNeighbor/arp) |
| `scripts/pi02_rescue_direct_eth.ps1` | Wrapper mit Adapter/APIPA-Hinweis |
| SD weiterhin | Nur wenn Eth unmÃ¶glich oder kein SSH-Fenster trotz Power-Cycle |

### Direct-Eth Lauf (~16:58–17:04, Kabel gesteckt)

| Ereignis | Ergebnis |
|----------|----------|
| PC Ethernet | **Up 1 Gbps**, APIPA `169.254.217.255` (WiFi unberührt `192.168.8.111`) |
| Script | `pi02_rescue_direct_eth.ps1` gestartet → Watcher `linklocal=True` (PID zuletzt **9916**) |
| Scan | `.106` + TS `100.103.54.63` + `169.254.*` Nachbarn |
| Pi ARP / SSH | **FAIL** — kein echter `169.254.*`-Host-Nachbar; TCP/22 überall zu; Log ohne `SUCCESS` |
| Aggressiv-Poll ~5 min | **rescued=no** |
| Schluss | Link allein reicht nicht bei Hang → **Power-Cycle jetzt** bei laufendem Watcher; sonst erneuter Cycle / SD |
### Boot-Constraint

User: **SD-Karte aus AnkerPI02 normalerweise schwer entnehmbar** (Decken-Screen). User **bereit zur SD-Rescue**, wenn Ethernet unmÃ¶glich. Keine riskanten `cmdline.txt`-Ã„nderungen. Recovery: `media/cmdline.recovery.txt`. Anleitung: `docs/PI02_SD_RESCUE.md`.

### Provisorisches Playback (sobald PI02 wieder da)

1. **Sofort** gepatchtes `fb_clock_play.py` deployen (`ffprobe` + `--crop-*`).
2. Service: `VIDEO=â€¦/media/st24.mov`, `--crop-top 386 --crop-bottom 127`, `--resync-every 60`.
3. Nicht rebooten nur wegen Underclock (bereits aus config entfernt).
4. SpÃ¤ter: echtes `clock_24h.mp4` 860Ã—360 NVENC encode + Upload.

### Offene Punkte

- [x] SD-Rescue Mask + Player-Deploy (2026-07-22 ~17:18)
- [ ] User: SD auswerfen → PI02 → Power-On → SSH
- [ ] PI02 online: Verify mask + ffprobe-Player → dann unmask/enable Clock
- [x] DNS-Fix PI01 (1.1.1.1/8.8.8.8 + ignore-auto-dns) — OK ~17:45
- [x] WiFi powersave-off PI01 (NM + systemd) — OK, Runtime ggf. re-assert
- [ ] Tailscale Install/Join PI01 (Deb via LAN-SCP; `--accept-dns=false`)
- [ ] PI02 DNS pin 1.1.1.1/8.8.8.8
- [ ] Produktion `clock_24h.mp4` encode
- [ ] Teensy flash/validate

## 2026-07-22 — PI02 watcher abort
- User: STOP aggressive PI02 polling; SD rescue in progress — do not interfere.
- Killed `pi02_rescue_watch.ps1` PID **9916**. No `pi02_rescue_direct_eth` / ping polls running.
- Left active rescue SSH sessions untouched.

### SD-Rescue SUCCESS (~17:09–17:18, MLT-NITRO5-HN)

| Schritt | Ergebnis |
|---------|----------|
| Disk-ID | USB **Disk 2** „Mass Storage Device“ **119.4 GB** — `E:\` = **bootfs** (vfat); Part2 = **rootfs** (ext4, kein Windows-Buchstabe) |
| Mount-Weg | `wsl --mount` scheiterte (`0x8007000f`); **usbipd** bind `2-2` + `attach --wsl` → WSL `/dev/sde1`+`sde2` |
| Identity | `hostname=AnkerPI02`; Labels `bootfs`/`rootfs` |
| Mask | `fb-clock.service` → `/dev/null`; Unit → `.DISABLED`; `multi-user.target.wants/fb-clock.service` **entfernt** |
| Player | Repo `fb_clock_play.py` → `/home/user/WerbeLEDbox-CountDown/` — Marker `ffprobe` + `Never decode` **OK** |
| Unit (optional) | Repo-Unit als `fb-clock.service.REPO` abgelegt — **Service bleibt masked** (nicht enable) |
| cmdline.txt | **unberührt** (read-only geprüft) |
| Sync/Umount | `sync` + umount boot+root; usbipd detach; `E:\` wieder sichtbar |
| Nächster User-Schritt | SD sicher auswerfen → in PI02 → Strom an → SSH erwarten → **erst dann** unmask/enable nach ffprobe-Verify |

### Post-boot Verify (~17:30–17:34, calm)

| Check | Ergebnis |
|-------|----------|
| User: PI02 nach SD-Rescue gebootet | behauptet |
| TCP/22 `.106` / `AnkerPI02.local` / TS `100.103.54.63` | **FAIL** — 4 Runden ~2 min, kein Hit |
| Ping `.106` + TS | **FAIL** |
| ARP `.106` | **Incomplete** (kein MAC) |
| Tailscale `ankerpi02` | **offline**, last seen ~1h |
| Leichter Glance `.100–.115` TCP/22 | kein neuer SSH-Host |
| fb-clock / Player remote Verify | **BLOCKED** — kein SSH |
| Unmask/Start | **nicht** versucht |

**Nächster Schritt:** Netz prüfen (WiFi SSID/Passwort? Ethernet stecken?). Sobald SSH da: mask + ffprobe-Player bestätigen, Clock nur nach Freigabe unmasken.

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

## 2026-07-22 ~17:45 — AnkerPI01 Status (Netz/DNS/Tailscale)

| Punkt | Stand |
|-------|--------|
| Erreichbar | **JA** — Ping + SSH `192.168.8.102` / `AnkerPI01.local` |
| DNS vorher | nur Router `192.168.8.254` (fragil) |
| DNS jetzt | **1.1.1.1 + 8.8.8.8**, NM `ignore-auto-dns=yes` — in `/etc/resolv.conf` verifiziert |
| WiFi | Link war stark intermittent; Root: powersave + Zero-2-W. Fix: NM powersave=disable + `wlan-powersave-off.service`; Runtime ~17:45 **Power Management:off** (re-asserted) |
| apt IPv4 | `/etc/apt/apt.conf.d/99force-ipv4` gesetzt |
| Tailscale apt/curl Deb | **FAIL** — kleine HTTPS OK; große CloudFront-Downloads timeout/starve (nicht primär DNS) |
| Tailscale installiert? | **NEIN** (`dpkg` unknown; `tailscaled` inactive/not-found) |
| Tailscale joined? | **NEIN** |
| Nächster Schritt | Deb per LAN-SCP → `dpkg -i` → `tailscale up --hostname=AnkerPI01 --accept-dns=false` |

## 2026-07-22 ~18:05 — AnkerPI01 Tailscale via LAN-SCP

| Punkt | Stand |
|-------|--------|
| Deb-Download (Windows) | **OK** — `tailscale_1.98.9_arm64.deb` 34257430 B von `pkgs.tailscale.com/stable/debian/pool/` (SHA256 `66E0CBC0…9136`) |
| SCP → `/tmp/` | **OK** (Bytes match; erstes `scp` hing nach Transfer — WiFi-flaky, Retry SSH zeigte Datei komplett) |
| `dpkg -i` + `systemctl enable --now tailscaled` | **OK** — `active`, version `1.98.9` (Debian trixie / aarch64) |
| `tailscale up --hostname=AnkerPI01 --accept-dns=false` | **NeedsLogin** — Auth-URL: https://login.tailscale.com/a/144cabd401ab72 |
| Tailscale IP | **pending** (kein Auth-Key in env/secrets) |
| Auth-Key | nicht vorhanden |

## 2026-07-22 ~17:53–18:00 — AnkerPI02 LAN up + WiFi Fix

User: Ethernet gesteckt. Discovery: **nicht** `.106` zuerst — mDNS → **`192.168.8.112`** (eth0). Tailscale `ankerpi02` / `100.103.54.63` wieder online.

| Check | Ergebnis |
|-------|----------|
| SSH `.112` / `AnkerPI02.local` / TS | **OK** (Key `hotel-anker-dev@MLT-NITRO5-HN`) |
| Hostname / Modell | AnkerPI02 / Pi 4 Model B Rev 1.5 |
| Load / Mem / Disk / Temp | niedrig / ~1.6 GiB avail / 19% / ~56 °C; throttled=0x0 |
| fb-clock | **masked** + inactive (unverändert, kein Unmask) |
| `fb_clock_play.py` | gepatcht (ffprobe); mtime 17:17 SD-Rescue |
| Network stack | **NetworkManager** active; dhcpcd not-found; networkd inactive |
| config.txt WiFi | kein disable; `arm_boost=1`; cmdline unberührt (`cfg80211.ieee80211_regdom=CH`) |
| rfkill phy0 | Soft/Hard **unblocked** |
| WiFi Root Cause | `/etc/NetworkManager/system-connections/` **leer** — keine SSIDs; Radio OK, Scan sieht HotelAnker |
| Fix | Persistente Keyfiles `HotelAnker_5G` (prio 20) + `HotelAnker` (prio 10); `nmcli connection up HotelAnker_5G` |
| wlan0 | **connected HotelAnker_5G** → **`192.168.8.106`** |
| eth0 | connected → **`192.168.8.112`** |
| Secrets | `secrets/wifi.hotelanker.yml` + `ankerpi02.credentials.yml` (dual IP) |

**Misserfolg zwischendurch:** `nmcli connection add` nur nach `/run/...` (tmpfs) → Profile verschwanden; sudo-heredoc schrieb 9-Byte-Mülldateien. **Workaround:** base64 → `/etc/NetworkManager/system-connections/*.nmconnection`, chmod 600, reload.

## 2026-07-22 ~18:20–18:45 — OpenCV / Hybrid Video-Clock PI02

Goal: User-Video-Clock `st24.mov` mit Seek/Crop/Scale → fb0; Ruckeln OK.

| Schritt | Ergebnis |
|---------|----------|
| fb-clock mask vor Experiment | OK |
| apt `python3-opencv` | **FAIL** — riesige Deps, Reboot mid-dpkg (2 GB RAM) |
| venv `opencv-python-headless` | Install OK; später **`import cv2` SIGBUS**; `VideoCapture(st24)` SIGBUS |
| dmesg | **`Undervoltage detected!`** / `throttled=0x50000` |
| Hybrid `ffmpeg -frames:v 1` + PIL | **OK kurz** — Frames auf fb0; ~0.1 fps; extract 5–14 s |
| Timed Test ~65 s | frame#1…#7, SSH OK, kein Reboot |
| systemd enable (`min-interval 3`) | frame#1–#3 im Journal, dann **Reboot** → **sofort remasked** |
| Dauerbetrieb | **NEIN** — bleibt masked bis PSU / kleineres MP4 |

Code: `fb_clock_opencv.py`, `systemd/fb_clock_opencv.service` (default `min-interval` 15 s).

## 2026-07-22 ~18:12 — AnkerPI01 WiFi same-as-PI02 (persistent /etc keyfile)

Goal: mirror PI02 HotelAnker NM setup on PI01 without breaking SSH.

| Check | Ergebnis |
|-------|----------|
| Pre: active profile | `netplan-wlan0-HotelAnker` only under **`/run/...`** (tmpfs) — `/etc/NetworkManager/system-connections/` empty |
| Radio | **Band 1 only** (Pi Zero 2 W) — scan shows `HotelAnker` @ **2432 MHz**; **no** `HotelAnker_5G` |
| Fix | Persist `/etc/NetworkManager/system-connections/HotelAnker.nmconnection` (prio **20**, powersave=2, DNS 1.1.1.1/8.8.8.8, ignore-auto-dns); `nmcli reload` + `connection up HotelAnker` |
| HotelAnker_5G profile | **not created** (hardware N/A) |
| Active | wlan0 **HotelAnker** → **`192.168.8.102`** |
| Powersave | NM `disable` + runtime `Power Management:off` (+ existing `wlan-powersave-off.service`) |
| DNS | `/etc/resolv.conf` → 1.1.1.1 + 8.8.8.8 (link-local fe80 also present from IPv6 RA) |
| Misserfolg | Windows SCP initially wrote **CRLF** → fixed to LF on Pi; long SSH during `nmcli up` can timeout — use nohup remote script |

## 2026-07-22 ~18:50–19:00 — Production `clock_24h.mp4` NVENC (MLT-NITRO5-HN)

Goal: stabile 860×360 H.264-Produktion statt 4K `st24.mov` auf PI02 (Undervoltage).

| Schritt | Ergebnis |
|---------|----------|
| Driver | **610.62** (RTX 3080 Laptop) — OK für FFmpeg 8.x NVENC |
| FFmpeg PATH | fehlte in Shell — Binary: WinGet `Gyan.FFmpeg` **8.1.2** `…\ffmpeg-8.1.2-full_build\bin\ffmpeg.exe` |
| Quelle ffprobe (kein `-f null`) | `C:\Users\User\Videos\st24.mov` 3840×2160 H.264 25 fps **86400.08 s** |
| 10 s NVENC-Test | **OK** — crop `3840:1647:0:386` → scale `860×360`, `-g 25`, 250 frames, ~3.2 s wall (~3.8×) → `media/_encode_nvenc_10s_test.mp4` |
| Full 24h Encode | **RUNNING** — PID **8652**, Start ~18:52:50; Out `media/_encode_clock_24h.partial.mp4` → nach Exit → `media/clock_24h.mp4` |
| Speed / ETA (früh) | ~**11×** → ETA ~**2.1 h** (fertig ca. **~21:00 CEST**) |
| Logs | `media/_encode_clock_24h.log`, `.progress`, `.ffmpeg.err`; Watcher PID **27852** (Rename + ffprobe) |
| `.gitignore` | bereits `media/*.mp4` + `clock_24h.mp4` + `_encode*` — großes MP4 **nicht** committen |
| PI02 ping/SSH | `.106` / `.112` / TS `.63` / mDNS — **alle FAIL** (timeout); fb-clock-Mask **nicht verifizierbar** aus Netz |


## 2026-07-22 ~19:08 - AnkerPI02 Undervoltage-Check (idle, frischer Boot)

| Check | Ergebnis |
|-------|----------|
| Host | SSH `user@192.168.8.106` OK (uptime **1 min**) |
| `vcgencmd get_throttled` | **`0x0`** (vorher unter Last oft `0x50000` = sticky UV + throttle seit Boot) |
| Bedeutung jetzt | **kein** Under-voltage aktuell, **keine** History-Bits seit diesem Boot |
| Volts / Temp / Load | `0.9660V`, **47.7°C**, loadavg **0.78 0.35 0.13** |
| Config | `arm_freq=1800`, `over_voltage_avs=20000` |
| dmesg/journal UV | **keine** Undervoltage-/Throttle-Meldungen seit Boot |
| fb-clock | **masked** / **inactive** (nicht gestartet) |
| Caveat | Idle nach Reboot — Sticky-Bits gehen bei Reboot auf 0; unter opencv/ffmpeg-Last erneut prüfen |
| Empfehlung | Aktuell besser; **gutes PSU** weiter sinnvoll bis Check unter realer Last wieder `0x0` bleibt |


## 2026-07-22 ~19:11 — Statuscheck Encode + AnkerPI02
- **NVENC encode:** noch aktiv (ffmpeg PID **8652**), schreibt `WerbeLEDbox-CountDown/media/_encode_clock_24h.partial.mp4` (~1303 MB). Progress `out_time≈04:00:10` / 24h → **~16.7%**, speed **~13.1x**, ETA wall **~1h 32min**. Nicht gestoppt. Final `clock_24h.mp4` noch nicht vorhanden.
- **AnkerPI02:** LAN `192.168.8.106` OK (5ms); `.112` timeout; Tailscale `100.103.54.63` OK. SSH: `fb-clock.service` **masked** + **inactive** (Clock nicht gestartet).

## 2026-07-22 ~19:22 — Research: Pi Clock Playback (Forum/Web)

| Item | Ergebnis |
|------|----------|
| Doc | `docs/RESEARCH_PI_CLOCK_PLAYBACK.md` |
| Kernbefund | Pi 4 **H.264 HW ≤1080p**; 4K nur **HEVC** — erklärt `h264_v4l2m2m` FAIL auf `st24.mov` |
| Community-Pfad | Pre-transcode down + continuous play (mpv DRM / GStreamer→fbdev); nicht Frame-Extract |
| Anthias PR #2972 | `v4l2h264dec`→`v4l2convert`→`fbdevsink` RGB565; ffmpeg→fbdev verworfen (~6 fps CSC) |
| Top-Empfehlung | `clock_24h.mp4` deploy → continuous `--start=wall` + Resync; PSU 5.1V/3A |

## 2026-07-22 ~19:14–19:28 — Loadtest + Pipeline-Bench + Max-FPS

### Loadtest sichtbar (vorher)
- `st24.mov` only (kein `clock_24h.mp4` auf Pi); Player bereits aktuell.
- Foreground `min-interval=10`, ~16 Frames auf **/dev/fb0**, extract ~7.2–14 s, **throttled=0x0**.
- Danach `fb-clock` **masked**, `fb_clock_opencv` **disabled**.

### Bench A/B/C/D (`scripts/bench_fb_pipelines.py`, 3 Runs)
| Name | MEAN ms | Ergebnis |
|------|---------|----------|
| A_full_pil | 13905 | Baseline PNG+PIL 3440 |
| B1/B2 860 host | ~13612–13749 | kaum schneller; OpenCV N/A |
| C1 vf 3440 raw | 12341 | ffmpeg vf hilft ~1.5 s |
| C2 vf 860 + NN-up | 12155 | **Gewinner volles Bild** |
| C3 860 center | 12119 | optisch winzig |
| D drm +860 | **12081** | knapp #1; `h264_v4l2m2m` FAIL |
| Stages C2 | extract 12045 / resize 33 / rgb565 72 / fb 4 | Decode = Bottleneck |

### Implementierung
- `fb_clock_opencv.py`: Default `--pipeline vf860 --hwaccel drm --min-interval 0`; Fallback soft wenn drm failt; `--pipeline vf3440|legacy` bleibt.
- Unit: weiter `min-interval 15` + vf860 (Autostart nicht enabled).

### Live Max-FPS 150 s
- 15 Frames, seek = wall clock, `eff_fps≈0.10–0.13`, best cycle ~3.8 s.
- **throttled=0x0** vor/während/nach. systemd unverändert masked/disabled.
- Letztes Frame bleibt auf fb0.

## 2026-07-22 ~19:38–19:41 — Abfahrt: Encode pause + Clock dauerhaft

### 1) NVENC encode PAUSED (Windows MLT-NITRO5-HN)
| Item | Wert |
|------|------|
| Action | Graceful stop ffmpeg PID **8652** (Stop-Process) |
| Confirm | **FFMPEG_STOPPED_OK** — kein ffmpeg mehr |
| Partial **KEPT** | `WerbeLEDbox-CountDown/media/_encode_clock_24h.partial.mp4` (~**3931635760** B / ~3.66 GiB) |
| Progress | `out_time=09:01:50` / 86400 s → **~37.6%** (speed ~11.8× before stop) |
| Resume later | Finish encode on MLT-NITRO5-HN; final target `media/clock_24h.mp4` |
| DO NOT DELETE | `_encode_clock_24h.partial.mp4`, `.progress`, `.log`, `.ffmpeg.err` |

### 2) AnkerPI02 Clock DAUERHAFT
| Item | Wert |
|------|------|
| Host | SSH `user@192.168.8.106` (TS `100.103.54.63` ok) |
| Deploy | latest `fb_clock_opencv.py` + unit as **`fb-clock.service`** (unmasked, enabled) |
| Pipeline | **vf860** + `--hwaccel drm` + `--min-interval 0` + NN upscale |
| Video | `media/st24.mov` (clock_24h.mp4 not ready) |
| TZ | **Europe/Zurich**, NTPSynchronized=**yes** |
| systemd | `Restart=always`, `RestartSec=30` (storm-safe) |
| Verify ~36s | **active/enabled**, NRestarts=**0**, frames **#1–#3** on `/dev/fb0`, `throttled=0x0` |
| Note | User accepted stutter; UV not seen in verify window — leave running |

## 2026-07-22 ~23:03 — Encode resume (daheim) + Deploy-Plan

| Item | Ergebnis |
|------|----------|
| Altes Partial MP4 | **unbrauchbar** (`moov atom not found`) — nicht fortsetzbar |
| Re-Encode | gestartet als **MKV** nach `C:\Users\User\Videos\_encode_clock_24h.partial.mkv` (Pfad ohne Spaces) |
| Settings | crop 3840:1647:0:386 → 860×360, NVENC, `-g 25`, 25 fps |
| Speed | ~**11.2×** (Stand ~00:13 / 24h nach 1 min) → ETA wall ~**2 h** |
| PI02 | Tailscale/LAN **offline** (last seen ~1h) — Deploy-Watcher wartet |
| Unit vorbereitet | `systemd/fb_clock.service` → `clock_24h.mp4` + `fb_clock_play.py` continuous, Autostart |
| Deploy-Skript | `scripts/deploy_clock_24h_when_ready.ps1` (SCP via TS/LAN, FPS-Messung, enable) |

## 2026-07-23 ~03:45 — clock_24h.mp4 FERTIG; Deploy blockiert (PI02 offline)

| Item | Ergebnis |
|------|----------|
| Encode | **OK** — NVENC ~4h39 wall, speed ~5–11×; MKV partial dann Remux |
| Output | `media/clock_24h.mp4` — **860×360** H.264 25 fps, duration **86400.08 s**, size **12206138242** (~11.4 GiB) |
| Script-Bug | `Start-Process` ExitCode leer → Script schrieb fälschlich FAILED; Datei trotzdem valid (progress=end); manueller Remux OK |
| Unit | `systemd/fb_clock.service` zeigt auf `clock_24h.mp4` + `fb_clock_play.py` continuous |
| Deploy-Watcher | läuft, wartet auf SSH |
| **AnkerPI02** | Tailscale/LAN **offline** seit ~6h — kein SCP/Start möglich |
| Nächster Schritt | PI02 power-cycle am Hotel (vermutlich Hang von 4K-Clock) → Watcher deployed automatisch |

## 2026-07-23 ~13:49 — clock_24h DEPLOY OK + FPS

| Item | Ergebnis |
|------|----------|
| Upload | Tailscale SCP ~6 h → `media/clock_24h.mp4` **12 G** auf PI02 |
| Alte 4K-Uhr | gestoppt |
| Player | `fb_clock_play.py` continuous, video **860×360**, seek Wall-Clock `Europe/Zurich`, **hw=True**, rotate 180 |
| systemd | `fb-clock` **active + enabled** (Boot-Autostart) |
| Live-FPS (fbdev 15 s) | **~25–26 fps**, speed **~1.02×** (vorher 4K-Extract ~0.1 fps) |
| Throughput-Messung | siehe `_deploy_clock_24h_remote.txt` |
| `throttled` | **0x0** |
| Journal | `start seek=13:49:15` matching wall time |

## 2026-07-23 ~17:27 CEST — Richnerstutz Anfrage gesendet

| Ereignis | Ergebnis |
|----------|----------|
| Kontext-Korrektur | **Hotel Anker Flowbox** ≠ Hautle 1.5×4 m Absen — nicht vermischen |
| Canva Master | `Printvorlage Hotel Anker Flowbox 2x2m` — 4096², Totzone unten schwarz OK |
| OAuth/`gog` | **FAIL** — redirect_uri_mismatch + 403 testing + kein IAM auf `nowak-central-hub-auth` |
| Versandweg | Cursor-Browser → Gmail Web als `harald.nowak@modernlight.ch` |
| Mail | An `info@richnerstutz.ch`, Betreff Offerte SEG/Keder LightBox 2×2 m Anker |
| Anhang | `Hotel-Anker-Richnerstutz-Bespannung.zip` (~1.4 MB) — Gmail: Message sent |

## 2026-07-24 ~02:11 CEST — Sync DESKTOP-UJ8NNE9 (Harald)

| Ereignis | Ergebnis |
|----------|----------|
| Workspace | `C:\Users\Harald Nowak\Documents\Cursor Projects\Hotel Anker` war **leer** (kein `.git`) |
| Clone | `git clone https://github.com/nowakha/hotel-anker.git .` → **OK** |
| Stand | `main` @ `2facf83` = `origin/main`, clean |
| Host | `DESKTOP-UJ8NNE9` / user `harald nowak` |
| Tooling | Git 2.55 unter `C:\Program Files\Git\cmd\` (nicht in Default-PATH); `gh` **fehlt** |
| Media lokal | `clock_24h.mp4` / `st24.mov` **nicht** vorhanden (gitignored; liegen auf PI02 / Encode-Maschine) |
| Continuity | `LEARNINGS.md` + `NEXT_AGENT.md` auf diesen Rechner aktualisiert |

## 2026-07-24 ~02:20 CEST — Clock smooth-Optimierung (Deploy pending)

| Änderung | Warum (Ruckeln) |
|----------|-----------------|
| Resync nur bei Drift `>0.35s` (Check alle 5s); `--resync-every 0` | Harter Kill alle **120s** = sichtbarer Hitch |
| `hflip,vflip` **vor** Upscale (statt `rotate=PI` @3440) | Rotate auf Panel-Res war CPU-teuer |
| ffmpeg `-probesize 32k -analyzeduration 0 -fflags +fastseek+genpts` | Schnellerer Restart nach Drift |
| Auto-Fallback Software nach 2× HW-Fail | Vermeidet Restart-Loop bei v4l2m2m-Fail |
| Unit: `Nice=-5`, mmc `read_ahead_kb=8192`, kein periodischer Resync | Weniger SD-Stalls / Scheduling-Jank |
| Script | `scripts/deploy_fb_clock_smooth.ps1` (+ `-Watch`) |
| PI02 Reachability von DESKTOP-UJ8NNE9 | **FAIL** — TS `ankerpi02` offline (~2h); Deploy wartet |

## 2026-07-27 ~13:57 CEST — Finale Druck-PDFs (250 Textil / 300 optisch)

| Schritt | Ergebnis |
|---------|----------|
| Totzone Ghost/Lit | solid black 512 px = **250 mm** @ 4096→2000 mm (verify max=0) |
| `DRUCK-Hotel-Anker-Flowbox-2000x2000.pdf` | MediaBox **2000×2000 mm** OK |
| `DRUCK-Opazitaet-2000x2000.pdf` | MediaBox 2000 mm OK |
| `FREIGABE-Massblatt-2100.pdf` | MediaBox **2100×2100 mm**, Label optisch 300 mm |
| Spec | PRINT_SPEC + `VISUAL_BOTTOM_DARK_MM` + GEOMETRIE-3D Hinweis |
| Nicht getan | Textil-Schwarz auf 300 mm; Druck auf 2100 mit gedrucktem Rahmen |

## 2026-07-27 ~14:05 CEST — Original-Rahmenfotos analysiert

| Foto | Befund |
|------|--------|
| 01 Gesamt | 8 Modulreihen + unterer Controllerkanal |
| 04 Zollstock Z | Profiltiefe **~80–85 mm** |
| 05 Zollstock XY | Profil→LED **~25 mm** |
| Docs | FOTO-AUSWERTUNG + GEOMETRIE-3D + Spec-Konstanten aktualisiert |
| Druck | 250 Textil / 300 optisch unverändert |


## 2026-07-27 ~14:12 CEST — Druckmaster 2100×2100 / Schwarz 300 mm

| Schritt | Ergebnis |
|---------|----------|
| User-PDF Analyse | MediaBox **2100 mm**, bottom black **≈300 mm** — bestätigt |
| Import | `DRUCK-Hotel-Anker-Flowbox-2100x2100.pdf` + PNG 4200² |
| Opazität | `DRUCK-Opazitaet-2100x2100.pdf`, Totzone 300 mm rot |
| Widerruf | 2000/250-Produktion entfernt / Specs umgestellt |
| Richner | Nachtrag-Entwurf `Nachtrag-Spannmass-210cm.md` (Offerte noch 200×200) |


## 2026-07-27 ~14:18 CEST — ZIP + Mail-Entwurf finale Druckdaten

| Item | Pfad / Status |
|------|----------------|
| ZIP | `~/Desktop/Hotel-Anker-Richnerstutz-Finale-Druckdaten.zip` (~20 MB) |
| Inhalt | Druck-PDF 2100, Opazität, 5 Fotos, Specs, Nachtrag |
| Mail-Text | `01-anfrage/Mail-Finale-Druckdaten.md` |
| Gmail | Compose geöffnet an info@richnerstutz.ch; Body Clipboard; **Senden: Harald** (Anhang ZIP) |


## 2026-07-27 ~14:52 CEST — Alles Lokale nach Git

| Aktion | Ergebnis |
|--------|----------|
| `versand/` | Finale ZIP, Offerte AG 461414, User-PDF, Chat-Originalfotos |
| `.gitignore` | Media/print-Ignore entfernt (Policy: track deliverables) |
| Push | folgt |


## 2026-08-04 — Reklamation: Print ohne Durchlicht

| Item | Status |
|------|--------|
| Foto installiert | `08-reklamation-licht/2026-08-04-installiert-kein-durchlicht.png` |
| Mail Harald → Richner | gesendet; warten auf Antwort |
| Symptom | Grundmaterial wirkt voll opak / schwarz, kein LED-Durchschein |
| Soll | Backlit + selektive Opazität laut Platte |

