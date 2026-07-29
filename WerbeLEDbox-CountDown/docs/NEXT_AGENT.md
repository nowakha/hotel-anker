# NEXT AGENT — Sofortmaßnahmen

Stand: 2026-07-29 ~14:04 CEST. Lies `LEARNINGS.md` + `docs/SESSION_LOG.md`.

## Priorität: Richnerstutz SEG (627 828)

- **Produktion gestartet** — Melanie Vogt (~14:04 CEST): GO + Lieferadresse erhalten, Produktion startet sofort.
- Vorher: Harald-Freigabe ~14:01 („Sehr gut so“, Versand Realia AG Rorschach); Gut zum Druck ~07:39 (Gebäude verpixelt, bewusst akzeptiert).
- Meta: `Richnerstutz-Bespannung-Paket/01-anfrage/MAIL-FREIGABE-META.md`
- **Offen:** Konkreter Liefer-/Versandtermin + Versandavis (~10 Tage laut Offerte).
- **STOP:** Kein Outbound ohne Harald-Go. Optional-Entwurf: `01-anfrage/Mail-Entwurf-Nachfrage-Liefertermin-2026-07-29.md`
- Zapier kann Haralds Sent-Mail erneut triggern → nicht als Druckerei-Antwort werten.

## Status Clock

- **LIVE** auf AnkerPI02 mit `clock_24h.mp4` (Stand 2026-07-23, ~25 fps).
- **Smooth-Patch bereit** lokal/`main`: Drift-Resync + billigeres Flip + Unit-Tuning.
- **Deploy noch offen** — PI02 oft offline (Tailscale).

## Nicht tun

- Kein `cmdline.txt`-Experiment
- Kein apt `python3-opencv`
- Kein `ffmpeg … -f null -` auf 24h/4K
- Keine Richnerstutz-Mail senden ohne Harald-Freigabe
