# NEXT AGENT — Sofortmaßnahmen

Stand: 2026-07-22 ~19:28. Lies zuerst `LEARNINGS.md` + `docs/SESSION_LOG.md`.

## Status Clock

- **fb-clock: MASKED**; `fb_clock_opencv.service` **disabled** (Soll-Zustand).
- Player: `fb_clock_opencv.py` Default **`--pipeline vf860`** (ffmpeg crop+scale 860×360 + hflip/vflip → raw → NEAREST 3440×1440 → RGB565). Optional `--hwaccel drm` (Fallback soft).
- Bench: 4K-Decode ~12 s = Bottleneck; 860 vs 3440 Host-Resize fast egal (~0.2 s). Max nachhaltig ~**0.10–0.13 fps** auf `st24.mov`.
- **Nicht** OpenCV `VideoCapture(st24)` (SIGBUS / cv2 fehlt). **Nicht** `ffmpeg -f null` Full-Decode.
- Live Max-FPS Test: **throttled=0x0** (gut); Autostart trotzdem nicht ohne PSU-Freigabe.

## Jetzt tun (Priorität)

1. Encode fertig? Prüfe `media/clock_24h.mp4` auf MLT-NITRO5-HN → auf PI02 kopieren, `VIDEO=` auf 860×360 MP4.
2. Mit kleinem MP4: erneut Max-FPS messen (sollte deutlich >0.1 fps).
3. Erst dann unmask/enable mit `min-interval` ≥5–15 s; SSH beobachten; bei UV sofort masken.

## Nicht tun

- Kein `cmdline.txt`-Experiment
- Kein apt `python3-opencv` auf diesem 2 GB Pi
- Kein Autostart solange PSU/UV unklar oder nur 4K `st24.mov` als Quelle
