# NEXT AGENT — Sofortmaßnahmen

Stand: 2026-08-05 ~14:50 CEST. Lies `LEARNINGS.md` + `docs/SESSION_LOG.md`.

## Print / Richnerstutz (aktiv)

- Job **SEG (627 828)** — geliefert, Material **opak / kein Durchlicht** (Reklamation Harald 2026-08-04).
- **Tanja Jelk 2026-08-05:** prüft morgen mit Produktion, meldet sich. Thread `19fac62d97c94e3d`.
- **STOP Outbound** ohne Harald-Go. Entwurf: `Richnerstutz-Bespannung-Paket/08-reklamation-licht/Mail-Entwurf-Antwort-2026-08-05.md`.
- Offen: Materialname, Nachdruck Backlit/Lumina, Termin, Kosten, optional Muster.

## Status Clock

- **LIVE** auf AnkerPI02 mit `clock_24h.mp4` (Stand 2026-07-23, ~25 fps).
- **Smooth-Patch bereit** lokal/`main`: Drift-Resync + billigeres Flip + Unit-Tuning.
- **Deploy noch offen** — PI02 von DESKTOP-UJ8NNE9 offline (Tailscale last seen ~2h).

## Jetzt tun

1. Print: auf Tanja-Rückmeldung warten; nur nach Harald-Go outbound.
2. Wenn PI02 online:  
   `pwsh WerbeLEDbox-CountDown/scripts/deploy_fb_clock_smooth.ps1`  
   oder `-Watch` bis SSH:22 antwortet.
3. Verify: `journalctl -u fb-clock -f` — kein `periodic resync` mehr; nur `drift=…` selten; `get_throttled=0x0`.

## Nicht tun

- Kein Outbound an Richnerstutz ohne Harald-Go
- Kein `cmdline.txt`-Experiment
- Kein apt `python3-opencv`
- Kein `ffmpeg … -f null -` auf 24h/4K
