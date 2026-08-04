# NEXT AGENT — Sofortmaßnahmen

Stand: 2026-08-04 ~15:45 CEST. Lies `LEARNINGS.md` + `docs/SESSION_LOG.md`.

## Priorität: Richnerstutz SEG (627 828)

- **Ware angekommen** (Harald-Outbound / Zapier-Echo 2026-08-04 ~15:45).
- Webhook-Body abgebrochen: Dank + Kritik am **Grundmaterial** („wirkt komp…“).
- **Kein** Richnerstutz-Reply → Watcher setzt Status und stoppt.
- Entwurf: `Richnerstutz-Bespannung-Paket/01-anfrage/Mail-Entwurf-Material-Feedback-2026-08-04.md`
- Meta: `Richnerstutz-Bespannung-Paket/01-anfrage/MAIL-FREIGABE-META.md`
- **STOP:** Kein Outbound ohne Harald-Go. Harald muss Wortlaut („kompakt“?) + LED-Test/Fotos bestätigen.
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
