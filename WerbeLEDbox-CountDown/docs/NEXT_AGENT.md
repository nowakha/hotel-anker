# NEXT AGENT — Sofortmaßnahmen

Stand: **2026-08-06**. Lies `LEARNINGS.md` + `docs/SESSION_LOG.md`.

## LIVE jetzt

- **Flowbox Countdown:** AnkerPI01 Tailscale `100.67.4.18`
  - `countdown-waves.service` (`countdown_waves_64.py --shm --fps 25`)
  - `ws2812put-pi02.service` → Teensy 64×64
- **Day/Night:** Solar-Fade auto (Rorschach). Tag = full-power weiss/cyan/orange; Nacht = bisheriger Amber/Navy@25%.
- Check: `journalctl -u countdown-waves -n 20` → `day_factor=`

## Jetzt tun (optional)

1. Optisch am Hotel prüfen: Tag heller genug? Wenn nein: Day-Palette in `countdown_waves_64.py` noch heißer (DAY_NAVY_HI / DAY_GOLD*).
2. Dämmerung beobachten (~civil twilight): sanfter Fade Tag→Nacht.
3. Richnerstutz-Antwort abwarten (Reklamation Material) — parallel LED-Power kompensiert.

## Nicht tun

- Waves nicht auf PI02 umziehen ohne Grund (LIVE ist PI01).
- Kein `cmdline.txt`-Experiment
- Kein `ffmpeg … -f null -` auf 24h/4K
- Clock smooth-patch PI02 nur wenn extra Auftrag
