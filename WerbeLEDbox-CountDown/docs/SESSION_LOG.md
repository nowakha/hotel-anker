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
| Watcher PID **16964** (Parent 26468, seit 16:27) | **ALIVE** — nicht neu gestartet bis Doc-Ende; danach Restart auf Link-Local-Skript |
| Aggressiv-Poll ~7 min (`.106` + TS `.63`, TCP/22) | **FAIL** — kein Ping, kein TCP22, kein `SUCCESS` |
| ARP `.106` | **fehlt** |
| Tailscale `ankerpi02` | **offline**, last seen ~50–54 min |
| mDNS `AnkerPI02.local` | unresolved |
| DHCP-Scan `.100–.115` | `.101–.105` + Workstation `.111` alive; **kein** `.106` |
| SSH Verify (fb-clock mask / ffprobe Player) | **BLOCKED** — Pi nie erreichbar |
| SD-Entnahme nötig? | **Noch nicht bewiesen** — WiFi-late Hang bleibt Hauptverdacht; Prefer Direkt-Ethernet |

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

### Boot-Constraint

User: **SD-Karte aus AnkerPI02 normalerweise schwer entnehmbar** (Decken-Screen). User **bereit zur SD-Rescue**, wenn Ethernet unmÃ¶glich. Keine riskanten `cmdline.txt`-Ã„nderungen. Recovery: `media/cmdline.recovery.txt`. Anleitung: `docs/PI02_SD_RESCUE.md`.

### Provisorisches Playback (sobald PI02 wieder da)

1. **Sofort** gepatchtes `fb_clock_play.py` deployen (`ffprobe` + `--crop-*`).
2. Service: `VIDEO=â€¦/media/st24.mov`, `--crop-top 386 --crop-bottom 127`, `--resync-every 60`.
3. Nicht rebooten nur wegen Underclock (bereits aus config entfernt).
4. SpÃ¤ter: echtes `clock_24h.mp4` 860Ã—360 NVENC encode + Upload.

### Offene Punkte

- [ ] User: Direct-Eth laut `PI02_DIRECT_ETH_RESCUE.md` â†’ Watcher + Power-Cycle; sonst SD
- [ ] PI02 wieder online + Clock laufen (nach Mask + gepatchtem Player)
- [ ] Tailscale + DNS-Fix auf PI01 (und PI02 DNS pin 1.1.1.1/8.8.8.8)
- [ ] Produktion `clock_24h.mp4` encode
- [ ] Teensy flash/validate
