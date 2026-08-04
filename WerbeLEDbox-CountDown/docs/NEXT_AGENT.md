# NEXT AGENT — Sofortmaßnahmen

Stand: 2026-08-04 ~15:51 CEST. Lies `LEARNINGS.md` + `docs/SESSION_LOG.md`.

## Priorität: Richnerstutz SEG (627 828) — Material

- **Ware angekommen** (2026-08-04). Harald outbound: Grundmaterial wirkt **komplett lichtundurchlässig / schwarz**.
- Job **SEG (627 828)** · Thread `19fac62d97c94e3d` · Msg `19fcd0b616ae405c`
- Soll: Backlit / transluzentes SEG (Offerte Lumina + Multilayer) mit **selektivem** Blockout (Opazitätsplatte: schwarz=durchlässig, rot=Blockout). Totzone unten nur partiell.
- Meta: `Richnerstutz-Bespannung-Paket/01-anfrage/MAIL-MATERIAL-META.md`
- Entwurf Reklamation/Nachdruck: `01-anfrage/Mail-Entwurf-Material-Reklamation-2026-08-04.md`
- **STOP:** Kein Outbound ohne Harald-Go. Prüfen ob Gmail Draft oder bereits Sent.
- Zapier kann Haralds Sent-Mail erneut triggern → nicht als Druckerei-Antwort werten.
- Nächster echter Trigger: Reply von `@richnerstutz.ch` zu Material/Nachdruck.

## Status Clock

- **LIVE** auf AnkerPI02 mit `clock_24h.mp4` (Stand 2026-07-23, ~25 fps).
- **Smooth-Patch bereit** lokal/`main`: Drift-Resync + billigeres Flip + Unit-Tuning.
- **Deploy noch offen** — PI02 oft offline (Tailscale).

## Nicht tun

- Kein `cmdline.txt`-Experiment
- Kein apt `python3-opencv`
- Kein `ffmpeg … -f null -` auf 24h/4K
- Keine Richnerstutz-Mail senden ohne Harald-Freigabe
