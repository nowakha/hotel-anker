# NEXT AGENT — Sofortmaßnahmen

Stand: 2026-07-29 ~00:50. Lies `LEARNINGS.md` + `docs/SESSION_LOG.md`.

## Status Clock / Netz

- **PI01:** Administration `192.168.1.91`, Tailscale `100.67.4.18` (wpa-psk; Zero 2 W ≠ WPA3-only).
- **PI02:** Administration `192.168.1.222`, Tailscale `100.103.54.63`.
- **Clock LIVE:** smooth `fb-clock.service` **enabled** — `fb_clock_play.py` `--max-drift 0.35 --resync-every 0`, video `clock_24h.mp4`.

## Verify (optional)

```bash
ssh user@100.103.54.63
systemctl status fb-clock
journalctl -u fb-clock -f
# erwartet: kein periodic resync; selten drift=…; get_throttled beachten (0x80008 gesehen)
```

## Nicht tun

- Kein `cmdline.txt`-Experiment
- Kein apt `python3-opencv`
- Kein `ffmpeg … -f null -` auf 24h/4K
- Administration nicht auf WPA3-only stellen (bricht PI01)
