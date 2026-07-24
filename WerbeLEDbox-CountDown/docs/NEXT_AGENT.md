# NEXT AGENT — Sofortmaßnahmen

Stand: 2026-07-24 ~02:20. Lies `LEARNINGS.md` + `docs/SESSION_LOG.md`.

## Status Clock

- **LIVE** auf AnkerPI02 mit `clock_24h.mp4` (Stand 2026-07-23, ~25 fps).
- **Smooth-Patch bereit** lokal/`main`: Drift-Resync + billigeres Flip + Unit-Tuning.
- **Deploy noch offen** — PI02 von DESKTOP-UJ8NNE9 offline (Tailscale last seen ~2h).

## Jetzt tun

1. Wenn PI02 online:  
   `pwsh WerbeLEDbox-CountDown/scripts/deploy_fb_clock_smooth.ps1`  
   oder `-Watch` bis SSH:22 antwortet.
2. Verify: `journalctl -u fb-clock -f` — kein `periodic resync` mehr; nur `drift=…` selten; `get_throttled=0x0`.
3. Optisch: keine 2‑Minuten-Hitches mehr; Rest-Jank = SD/Last → PSU prüfen.

## Nicht tun

- Kein `cmdline.txt`-Experiment
- Kein apt `python3-opencv`
- Kein `ffmpeg … -f null -` auf 24h/4K
