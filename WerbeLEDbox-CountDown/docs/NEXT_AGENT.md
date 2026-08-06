# NEXT AGENT — Sofortmaßnahmen

Stand: 2026-08-06. Lies `LEARNINGS.md` + `docs/SESSION_LOG.md`.

## Print / Richnerstutz (aktuell heiss)

- Job **SEG (627 828)** — gelieferte Bespannung **opak**, reklamiert 2026-08-04.
- Tanja Jelk 2026-08-06: fragt LED-Screen vs. Leuchtkasten; **Muster** Druck ~2026-08-07 Mittag.
- Wahrheit: Kendu-SEG-Leuchtkasten, ~45 mm Luft Textil→LED, Lumina + selektiver Multilayer.
- **STOP Outbound** ohne Harald-Go. Entwurf: `../../Richnerstutz-Bespannung-Paket/08-reklamation-licht/Mail-Entwurf-Antwort-2026-08-06.md`.

## Status Clock

- **LIVE** auf AnkerPI02 mit `clock_24h.mp4` (Stand 2026-07-23, ~25 fps).
- **Smooth-Patch bereit** lokal/`main`: Drift-Resync + billigeres Flip + Unit-Tuning.
- **Deploy noch offen** — PI02 Reachability prüfen (Tailscale).

## Jetzt tun

1. Harald: Go/No-Go für Entwurf 2026-08-06 (Geometrie klären vor/mit Muster).
2. Wenn PI02 online:  
   `pwsh WerbeLEDbox-CountDown/scripts/deploy_fb_clock_smooth.ps1`  
   oder `-Watch` bis SSH:22 antwortet.
3. Verify Clock: `journalctl -u fb-clock -f` — kein `periodic resync` mehr; `get_throttled=0x0`.

## Nicht tun

- Kein Outbound an Richnerstutz ohne Harald-Go
- Kein `cmdline.txt`-Experiment
- Kein apt `python3-opencv`
- Kein `ffmpeg … -f null -` auf 24h/4K
