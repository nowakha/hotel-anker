# NEXT AGENT — Sofortmaßnahmen

Stand: 2026-07-24 ~02:11 (Repo auf DESKTOP-UJ8NNE9 synchron). Lies zuerst `LEARNINGS.md` + `docs/SESSION_LOG.md`.

## Status Clock (LIVE auf AnkerPI02)

- Video: `media/clock_24h.mp4` 860×360 H.264 25fps 86400s **auf dem Pi** (nicht im Git; lokal hier oft fehlend).
- Service: `fb-clock.service` → `fb_clock_play.py` (continuous + resync 120s, HW decode, rotate 180).
- Boot: **enabled**; NTP wait in ExecStartPre.
- Live-FPS (2026-07-23): **~25 fps @ ~1.02×**, `throttled=0x0`.

## Status Print

- Richnerstutz-Anfrage gesendet (2026-07-23 ~17:27) — Offerte SEG/Keder Flowbox 2×2 m Hotel Anker.

## Jetzt tun (lokal auf diesem Rechner)

1. Bei Bedarf PI02 Reachability prüfen (LAN `.106` / eth `.112` / Tailscale `100.103.54.63`).
2. Weiterarbeit nur nach klarem User-Ziel (Clock/LED/Print/Deploy).
3. Tooling: Git-PATH setzen oder dauerhaft in User-PATH; optional `gh` installieren.

## Nicht tun

- Kein `cmdline.txt`-Experiment
- Kein apt `python3-opencv` auf dem Pi
- Kein `ffmpeg … -f null -` auf 24h/4K-Videos
- Große Media (`clock_24h.mp4`, `st24.mov`) nicht committen
