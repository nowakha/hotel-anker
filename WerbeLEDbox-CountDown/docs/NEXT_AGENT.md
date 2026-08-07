# NEXT AGENT — Sofortmaßnahmen

Stand: **2026-08-07 ~15:43 CEST**. Lies `LEARNINGS.md` + `docs/SESSION_LOG.md`.

## Print / Richnerstutz (PRIORITÄT)

- Job **SEG (627 828)** — Thread `19fac62d97c94e3d` · Tanja Msg `19fdc43b49050a5c` · Harald Rechnung Msg `19fdc76bfbe994bb`.
- **Ergebnis:** Richnerstutz kein Flowbox-/Beamer-Material; Nachdruck gleiches Material sinnlos; Textil beim Hersteller.
- **Kulanz:** 30 %+10 % Material; Arbeit verrechnen. Video Acrobat `IMG_1987.MOV`.
- **Harald ~15:43:** Outbound «Realia AG als Rechnungsanschrift ist richtig» — Adresse erledigt.
- **Offen:** explizite Kulanz-Akzeptanz (kurzer Outbound nur Adresse); Plan B Material (Kendu); Totzone 300 mm / 2100 mm Nachfolger.
- Optionaler Nachzieh-Entwurf: `08-reklamation-licht/Mail-Entwurf-Antwort-2026-08-07.md` (nur wenn Harald mehr als Adresse bestätigen will).
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
