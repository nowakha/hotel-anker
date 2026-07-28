# NEXT AGENT — Sofortmaßnahmen

Stand: 2026-07-28 ~17:07 CEST. Lies `LEARNINGS.md` + `docs/SESSION_LOG.md`.

## Priorität: Richnerstutz Druckdaten (AG 461414)

- Feedback Melanie Vogt: Pixelung (Upscale Gebäude/Logo), Blocker nicht deckungsgleich, keine Schnittzeichen.
- Entwurf Antwort: `Richnerstutz-Bespannung-Paket/01-anfrage/Mail-Entwurf-Antwort-Vogt-2026-07-28.md`
- **Kein Outbound ohne Harald-Go.** Danach: native Hi-Res + Blocker 1:1 neu + PDFs ohne Marken.

## Status Clock

- **LIVE** auf AnkerPI02 mit `clock_24h.mp4` (Stand 2026-07-23, ~25 fps).
- **Smooth-Patch bereit** lokal/`main`: Drift-Resync + billigeres Flip + Unit-Tuning.
- **Deploy noch offen** — PI02 oft offline (Tailscale).

## Nicht tun

- Kein `cmdline.txt`-Experiment
- Kein apt `python3-opencv`
- Kein `ffmpeg … -f null -` auf 24h/4K
- Keine Richnerstutz-Mail senden ohne Harald-Freigabe
