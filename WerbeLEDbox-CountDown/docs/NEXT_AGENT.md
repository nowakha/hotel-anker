# NEXT AGENT — Sofortmaßnahmen

Stand: 2026-08-06 ~15:54. Lies `LEARNINGS.md` + `docs/SESSION_LOG.md`.

## Print / Richnerstutz (PRIORITÄT)

- Job **SEG (627 828)** — Reklamation kein Durchlicht.
- Tanja: Musterstück Druck **~07.08. Mittag**; Harald Geometrie + Rabattfrage bereits nachgelegt (~15:53–15:54, Msg `19fd75a4a86d4e03`).
- **STOP Outbound** ohne Harald-Go. Optionaler Entwurf: `Richnerstutz-Bespannung-Paket/08-reklamation-licht/Mail-Entwurf-Followup-2026-08-06.md`.
- Bei nächstem Richner-Inbound (`@richnerstutz.ch`): Docs + Summary; kein Mail-Versand durch Agent.

## Status Clock

- **LIVE** auf AnkerPI02 mit `clock_24h.mp4` (Stand 2026-07-23, ~25 fps).
- **Smooth-Patch bereit** lokal/`main`: Drift-Resync + billigeres Flip + Unit-Tuning.
- **Deploy noch offen** — PI02 von DESKTOP-UJ8NNE9 offline (Tailscale last seen ~2h).

## Jetzt tun

1. Print: auf Tanja Muster-Ergebnis warten; nur nach Harald-Go weiter mailen.
2. Wenn PI02 online:  
   `pwsh WerbeLEDbox-CountDown/scripts/deploy_fb_clock_smooth.ps1`  
   oder `-Watch` bis SSH:22 antwortet.
3. Verify: `journalctl -u fb-clock -f` — kein `periodic resync` mehr; nur `drift=…` selten; `get_throttled=0x0`.

## Nicht tun

- Kein `cmdline.txt`-Experiment
- Kein apt `python3-opencv`
- Kein `ffmpeg … -f null -` auf 24h/4K
- Kein Mail an Richnerstutz ohne Harald-Freigabe
