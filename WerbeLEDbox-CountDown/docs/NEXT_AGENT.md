# NEXT AGENT — Sofortmaßnahmen

Stand: 2026-07-28 ~17:34 CEST. Lies `LEARNINGS.md` + `docs/SESSION_LOG.md`.

## Priorität: Richnerstutz Druckdaten (AG 461414)

- **Korrektur #2 outbound GESENDET** an Melanie Vogt (~17:34 CEST) — Fassade ohne Upscale, Blocker deckungsgleich, ohne Schnittzeichen.
- Meta: `Richnerstutz-Bespannung-Paket/01-anfrage/MAIL-KORREKTUR-META.md`
- **Offen:** Vorstufen-Bestätigung Passung. Kein weiterer Outbound ohne Harald-Go / neuen `@richnerstutz.ch`-Reply.
- Zapier kann Haralds eigene Sent-Mail erneut triggern → nicht als Druckerei-Antwort werten.

## Status Clock

- **LIVE** auf AnkerPI02 mit `clock_24h.mp4` (Stand 2026-07-23, ~25 fps).
- **Smooth-Patch bereit** lokal/`main`: Drift-Resync + billigeres Flip + Unit-Tuning.
- **Deploy noch offen** — PI02 oft offline (Tailscale).

## Nicht tun

- Kein `cmdline.txt`-Experiment
- Kein apt `python3-opencv`
- Kein `ffmpeg … -f null -` auf 24h/4K
- Keine Richnerstutz-Mail senden ohne Harald-Freigabe
