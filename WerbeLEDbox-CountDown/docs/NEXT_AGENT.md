# NEXT AGENT — Sofortmaßnahmen

Stand: 2026-07-22 ~19:41. Lies zuerst `LEARNINGS.md` + `docs/SESSION_LOG.md`.

## Status Clock (LIVE)

- **fb-clock: ENABLED + ACTIVE** (dauerhaft) — unit = opencv/hybrid player.
- Pipeline: `--pipeline vf860 --hwaccel drm --min-interval 0`; Video `media/st24.mov`.
- TZ Europe/Zurich + NTP yes. `Restart=always` / `RestartSec=30`.
- Bei UV-Reboot-Storm: `min-interval 5` setzen oder masken (`scripts/_pi02_emergency_mask.sh`).

## Status Encode (PAUSED)

- ffmpeg gestoppt. Partial: `media/_encode_clock_24h.partial.mp4` @ **~37.6%** (`out_time≈09:01:50`).
- **Nicht löschen.** Resume/Finish auf MLT-NITRO5-HN → dann `clock_24h.mp4` auf PI02, `VIDEO=` umstellen.

## Jetzt tun

1. Encode fertigmachen → deploy `clock_24h.mp4` → continuous play Experiment (Research).
2. Unter Dauerlast `vcgencmd get_throttled` beobachten; bei sticky UV PSU prüfen.

## Nicht tun

- Kein `cmdline.txt`-Experiment
- Kein apt `python3-opencv`
- Partial encode nicht löschen
