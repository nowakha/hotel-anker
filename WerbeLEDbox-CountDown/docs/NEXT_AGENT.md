# NEXT AGENT — Sofortmaßnahmen

Stand: 2026-08-04 ~15:48 CEST. Lies `LEARNINGS.md` + `docs/SESSION_LOG.md`.

## Priorität: Richnerstutz SEG (627 828) — Material-Reklamation

- **Ware angekommen** (heute). Harald-Outbound: Grundmaterial **komplett lichtundurchlässig/schwarz** → sofort Nacharbeit auf Backlit-Untergrund (Lumina / gemischte Opazität).
- Msg `19fcd089dbb2ade6` / Thread `19fac62d97c94e3d`. Meta: `Richnerstutz-Bespannung-Paket/01-anfrage/MAIL-FREIGABE-META.md`
- Entwurf Nachfassung: `01-anfrage/Mail-Entwurf-Material-Nacharbeit-2026-08-04.md` (nur bei Harald-Go / wenn Druckerei nachfragt).
- **STOP:** Kein weiterer Outbound ohne Harald-Go. Nächster sinnvoller Trigger = **Reply von @richnerstutz.ch**.
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
