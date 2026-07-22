# NEXT AGENT — Sofortmaßnahmen

Stand: 2026-07-22 ~18:55. Lies zuerst `LEARNINGS.md` + `docs/SESSION_LOG.md`.

## Status Clock

- **fb-clock: MASKED** (Soll-Zustand; ~18:51 PI02 LAN/TS **unreachable** — nicht live verifiziert).
- Hybrid-Player im Repo: `fb_clock_opencv.py` + `systemd/fb_clock_opencv.service`.
- Pipeline: wall-clock → `ffmpeg -threads 1 -ss HH:MM:SS -frames:v 1` PNG → PIL crop T386/B127 → 3440×1440 → rotate 180 → RGB565 `/dev/fb0`.
- **Nicht** OpenCV `VideoCapture(st24)` (SIGBUS). **Nicht** `ffmpeg -f null` Full-Decode.
- Blocker: **Undervoltage** (`throttled=0x50000`) → Reboots bei 4K-Extract.
- **Workstation encode RUNNING:** `media/clock_24h.mp4` NVENC 860×360 (Logs `media/_encode_clock_24h.*`, ETA ~21:00 CEST).

## Jetzt tun (Priorität)

1. Encode fertig? Prüfe `media/clock_24h.mp4` + `_encode_clock_24h.log` (SUCCESS) auf MLT-NITRO5-HN.
2. PI02 wieder erreichbar → `systemctl is-enabled fb-clock` (muss masked bleiben) bis Upload.
3. `clock_24h.mp4` auf PI02 kopieren, `VIDEO=` setzen; **PSU 5 V/≥3 A** prüfen.
4. Erst dann unmask/enable (LEARNINGS). SSH 90 s beobachten; bei Reboot sofort masken.

## Nicht tun

- Kein `cmdline.txt`-Experiment
- Kein apt `python3-opencv` auf diesem 2 GB Pi (zu schwer)
- Kein Autostart solange `throttled` Under-voltage meldet
