# NEXT AGENT — Sofortmaßnahmen

Stand: **2026-08-10 ~09:36 CEST**. Lies `LEARNINGS.md` + `docs/SESSION_LOG.md`.

## Print / Richnerstutz (PRIORITÄT)

- Job **SEG (627 828)** — Thread `19fac62d97c94e3d` · Tanja Msg `19fea99db1247123` (Antwort auf Harald Opera Msg `19fdc78284723f62`).
- **Ergebnis Tanja 10.08.:** weisser Stoff nicht zielführend (opak oder streut); **Opera Folie nicht im Sortiment**; kann Material-Thema nicht weiterhelfen; Danke für Rechnungsadresse.
- **Vorher (07.08.):** kein Flowbox-/Beamer-Material; Kulanz 30 %+10 % Material; Arbeit verrechnen; Textil beim Hersteller.
- **Offen:** Plan B Kendu/Hersteller-Material; Totzone 300 mm / 2100×2100 mm Nachfolger; Kulanz-Schriftlichkeit / Rechnungseingang; ob Harald kurze Abschluss-Mail schickt.
- Optionaler Entwurf: `Richnerstutz-Bespannung-Paket/08-reklamation-licht/Mail-Entwurf-Antwort-2026-08-10.md` (nur nach Harald-Go).
- **STOP Outbound** ohne Harald-Go. Bei Richner-Inbound: Docs + Summary; **kein** Mail-Versand durch Agent.

## LIVE jetzt

- **Flowbox Countdown:** AnkerPI01 Tailscale `100.67.4.18`
  - `ws2812put-pi02.service` erstellt `shm://ws2812`
  - `countdown-waves.service` **attach-only** → Teensy 64×64
- **2026-08-07 Fix:** SHM split-brain behoben; Milch-Ghost; hellerer Countdown-First Look.

## Restart-Reihenfolge (PFLICHT)

```bash
sudo systemctl stop countdown-waves
sudo systemctl restart ws2812put-pi02
# wait until /dev/shm/ws2812 exists
sudo systemctl start countdown-waves
# verify: grep ws2812 /proc/$(systemctl show -p MainPID --value ws2812put-pi02)/maps
#         and waves PID — same inode, NOT "(deleted)" with different numbers
```

**Nie** Waves allein restarten und hoffen — Producer darf SHM nie `create`n.

## Nicht tun

- Kein `sa.create` im Countdown-Producer
- Kein `cmdline.txt`-Experiment
- Kein `ffmpeg … -f null -` auf 24h/4K
- Kein Mail an Richnerstutz ohne Harald-Freigabe
