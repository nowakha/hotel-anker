# NEXT AGENT — Sofortmaßnahmen

Stand: **2026-08-07 ~15:44 CEST**. Lies `LEARNINGS.md` + `docs/SESSION_LOG.md`.

## Print / Richnerstutz (PRIORITÄT)

- Job **SEG (627 828)** — Thread `19fac62d97c94e3d` · Tanja Msg `19fdc43b49050a5c` · Harald Opera Msg `19fdc78284723f62` (zuvor Rechnung `19fdc76bfbe994bb`).
- **Ergebnis Tanja:** kein Flowbox-/Beamer-Material; Nachdruck gleiches Material sinnlos; Textil beim Hersteller; Kulanz 30 %+10 % Material; Arbeit verrechnen.
- **Harald ~15:44:** Realia AG Rechnungsanschrift bestätigt **+** fragt Opera / dünnes helles (weisses) lichtdurchlässiges Material.
- **Offen:** Antwort Richner auf Opera; Plan B Kendu/Hersteller falls Nein; Totzone 300 mm / 2100 mm Nachfolger; Kulanz-Schriftlichkeit; Rechnungseingang.
- Optionaler Nachzieh-Entwurf: `08-reklamation-licht/Mail-Entwurf-Antwort-2026-08-07.md` (nur nach Harald-Go).
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
