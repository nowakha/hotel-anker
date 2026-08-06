# NEXT AGENT — Sofortmaßnahmen

Stand: 2026-08-06 ~15:51 CEST. Lies `LEARNINGS.md` + `docs/SESSION_LOG.md`.

## Print / Richnerstutz (PRIORITÄT)

- Job **SEG (627 828)** — Reklamation: gelieferter Print **kein Durchlicht**.
- Tanja 2026-08-06: Screen vs. Leuchtkasten-Unsicherheit; **Musterstück** Druck morgen Mittag.
- Harald outbound bereits: Kendu-Link + LED ~4.5 cm — **kein weiteres Outbound ohne Harald-Go**.
- Entwurf: `Richnerstutz-Bespannung-Paket/08-reklamation-licht/Mail-Entwurf-Followup-2026-08-06.md`.

## Status Clock

- **LIVE** auf AnkerPI02 mit `clock_24h.mp4` (Stand 2026-07-23, ~25 fps).
- **Smooth-Patch bereit** lokal/`main`: Drift-Resync + billigeres Flip + Unit-Tuning.
- **Deploy noch offen** — PI02 ggf. offline (Tailscale).

## Jetzt tun

1. Print: auf Tanja Muster-Rückmeldung warten; Follow-up nur nach Harald-Go.
2. Wenn PI02 online:  
   `pwsh WerbeLEDbox-CountDown/scripts/deploy_fb_clock_smooth.ps1`  
   oder `-Watch` bis SSH:22 antwortet.
3. Verify: `journalctl -u fb-clock -f` — kein `periodic resync` mehr; nur `drift=…` selten; `get_throttled=0x0`.

## Nicht tun

- Kein Mail an Richnerstutz ohne explizites Harald-Go
- Kein `cmdline.txt`-Experiment
- Kein apt `python3-opencv`
- Kein `ffmpeg … -f null -` auf 24h/4K
