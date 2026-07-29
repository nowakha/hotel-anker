# NEXT AGENT — Sofortmaßnahmen

Stand: 2026-07-29 ~14:01 CEST. Lies `LEARNINGS.md` + `docs/SESSION_LOG.md`.

## Priorität: Richnerstutz SEG (627 828)

- **Druckfreigabe outbound GESENDET** (~14:01 CEST) — „Sehr gut so“, zeitnah produzieren, Versand Realia AG Rorschach.
- Meta: `Richnerstutz-Bespannung-Paket/01-anfrage/MAIL-FREIGABE-META.md`
- Vorstufe hatte Gebäude noch verpixelt — Harald hat bewusst freigegeben.
- **Offen:** Produktionsstart / Liefertermin / Versandavis.
- **STOP:** Kein weiterer Outbound ohne Harald-Go / neuen `@richnerstutz.ch`-Reply.
- Zapier kann Haralds Sent-Mail erneut triggern → nicht als Druckerei-Antwort werten.
- Optionaler Entwurf (nur bei Stille): `01-anfrage/Mail-Entwurf-Nachfrage-Liefertermin-2026-07-29.md`

## Status Clock

- **LIVE** auf AnkerPI02 mit `clock_24h.mp4` (Stand 2026-07-23, ~25 fps).
- **Smooth-Patch bereit** lokal/`main`: Drift-Resync + billigeres Flip + Unit-Tuning.
- **Deploy noch offen** — PI02 oft offline (Tailscale).

## Nicht tun

- Kein `cmdline.txt`-Experiment
- Kein apt `python3-opencv`
- Kein `ffmpeg … -f null -` auf 24h/4K
- Keine Richnerstutz-Mail senden ohne Harald-Freigabe
