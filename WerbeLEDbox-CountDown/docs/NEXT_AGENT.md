# NEXT AGENT — Sofortmaßnahmen

Stand: 2026-07-22 ~18:45. Lies zuerst `LEARNINGS.md` + `docs/SESSION_LOG.md`.

## Status Clock

- **fb-clock: MASKED** (`/etc/systemd/system/fb-clock.service` → `/dev/null`).
- Hybrid-Player im Repo: `fb_clock_opencv.py` + `systemd/fb_clock_opencv.service`.
- Pipeline: wall-clock → `ffmpeg -threads 1 -ss HH:MM:SS -frames:v 1` PNG → PIL crop T386/B127 → 3440×1440 → rotate 180 → RGB565 `/dev/fb0`.
- **Nicht** OpenCV `VideoCapture(st24)` (SIGBUS). **Nicht** `ffmpeg -f null` Full-Decode.
- Blocker: **Undervoltage** (`throttled=0x50000`) → Reboots bei 4K-Extract. Braucht besseres PSU und/oder `clock_24h.mp4` 860×360.

## Jetzt tun (Priorität)

1. **Netzteil prüfen** (offizielles 5 V / ≥3 A USB-C für Pi 4) — ohne das kein stabiler 4K-Clock.
2. Optional: `clock_24h.mp4` 860×360 encoden und als `VIDEO=` setzen.
3. Erst dann unmask/enable (siehe LEARNINGS Enable-Snippet). SSH 90 s beobachten; bei Reboot sofort masken.
4. PI01 Tailscale / Countdown wie zuvor.

## Nicht tun

- Kein `cmdline.txt`-Experiment
- Kein apt `python3-opencv` auf diesem 2 GB Pi (zu schwer)
- Kein Autostart solange `throttled` Under-voltage meldet
