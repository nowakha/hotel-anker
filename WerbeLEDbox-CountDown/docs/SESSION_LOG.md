# SESSION_LOG â€” Hotel Anker / WerbeLEDbox

Chronik fÃ¼r Cross-Machine-Handoff. Erfolg **und** Misserfolg.

## 2026-07-22 (Workstation MLT-NITRO5-HN)

### Zugang / Tooling

| Ereignis | Ergebnis |
|----------|----------|
| Git installiert (fehlte) + GitHub CLI | OK â€” Account `nowakha` |
| Repo geklont `nowakha/hotel-anker` | OK |
| SSH-Key neu `hotel-anker-dev@MLT-NITRO5-HN` auf PI01+PI02 | OK (Passwort `12345678`) |
| Tailscale auf PI02 installiert + joined | OK â€” `ankerpi02` = `100.103.54.63` |
| Tailscale auf PI01 | **FAIL** â€” apt Download `pkgs.tailscale.com` Timeout/DNS; Deb-Install unterbrochen |
| DNS nur Router `192.168.8.254` | Fragil; Fix-Skript vorbereitet, auf PI02 wegen USB-Copy **abgebrochen** (User: nicht kicken) |

### Clock-Video / AnkerPI02

| Ereignis | Ergebnis |
|----------|----------|
| Quelle `C:\Users\User\Videos\st24.mov` | 3840Ã—2160 H.264, 25 fps, **86400.08 s**, ~12.7 GB |
| Crop (Premiere): L0 T386 R0 B127 â†’ ~3840Ã—1647 (~21:9) | Spec |
| Ziel-Spec Produktion | `media/clock_24h.mp4` 860Ã—360 25fps H.264 `-g 25` |
| NVENC zuerst | **FAIL** â€” Driver 596 vs FFmpeg 8.1 braucht NVENC API 13.1; nach Driver-Update 610.62 OK |
| Full NVENC-Encode 24h | **nicht gestartet** (ETA ~6 h); User: spÃ¤ter remote |
| LAN-scp st24.mov | **FAIL/abgebrochen** bei ~2.3 GB; PI02 ging offline |
| USB `st24.mov` â†’ `/mnt/usb` â†’ rsync nach `~/â€¦/media/st24.mov` | **OK** â€” 774 s, ~16.9 MB/s, Bytes match `13687155613` |
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
- [ ] Tailscale + DNS-Fix auf PI01 (und PI02 DNS pin 1.1.1.1/8.8.8.8)
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
