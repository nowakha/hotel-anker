# SESSION_LOG — Hotel Anker / WerbeLEDbox

Chronik für Cross-Machine-Handoff. Erfolg **und** Misserfolg.

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
| `probe_size()` mit `ffmpeg -f null -` | **CRITICAL FAIL** — dekodiert 24h 4K → Pi unresponsive; Power-Cycle nötig |
| PI02 nach User-Reboot (Stand ~16:08) | **noch offline** (kein Ping/SSH/Tailscale) |
| Re-Check ~16:17–16:20 LAN `.106` + TS `100.103.54.63` + mDNS | **FAIL** — ping timeout / Destination host unreachable; SSH timeout; mDNS unresolved |
| Handoff-Commit `8044f9a` → `origin/main` | OK — Docs, Secrets, probe_size-Fix, Workflow-Regel |
| Offline-Doc-Commit `2f67b57` → `origin/main` | OK |
| Continuity User-Rule + SESSION `09e5571` | OK |
| Deploy patched Player + Clock-Start | **BLOCKED** — PI02 offline; wartet auf physischen Strom/Boot-Check |
| User-Rule «Hotel Anker — Continuity / Git / Secrets» in Cursor Settings | OK — zusätzlich zu `.cursor/rules/hotel-anker-workflow.mdc` |
| Rescue: `scripts/pi02_rescue_mask_fbclock.py` + `fb_play.py` probe_size-Parity | lokal bereit → commit/push |
| Cursor zeigt zwei Repo-Namen «Hotel Anker» + «hotel-anker» | **Kein Doppel-Clone** — nur Ordner `Hotel Anker`; Remote-Slug `hotel-anker`. Kein `.code-workspace`. Kanonisch: `…\Cursor Projects\Hotel Anker` |

### Boot-Constraint

User: **SD-Karte aus AnkerPI02 nicht mehr entnehmbar.** Keine riskanten `cmdline.txt`-Änderungen. Recovery: `media/cmdline.recovery.txt`.

### Provisorisches Playback (sobald PI02 wieder da)

1. **Sofort** gepatchtes `fb_clock_play.py` deployen (`ffprobe` + `--crop-*`).
2. Service: `VIDEO=…/media/st24.mov`, `--crop-top 386 --crop-bottom 127`, `--resync-every 60`.
3. Nicht rebooten nur wegen Underclock (bereits aus config entfernt).
4. Später: echtes `clock_24h.mp4` 860×360 NVENC encode + Upload.

### Offene Punkte

- [ ] PI02 wieder online + Clock laufen
- [ ] Tailscale + DNS-Fix auf PI01 (und PI02 DNS pin 1.1.1.1/8.8.8.8)
- [ ] Produktion `clock_24h.mp4` encode
- [ ] Teensy flash/validate
