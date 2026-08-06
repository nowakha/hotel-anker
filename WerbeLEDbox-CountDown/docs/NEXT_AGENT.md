# NEXT AGENT — Sofortmaßnahmen

Stand: **2026-08-07 ~14:47 CEST**. Lies `LEARNINGS.md` + `docs/SESSION_LOG.md`.

## Print / Richnerstutz (PRIORITÄT)

- Job **SEG (627 828)** — Thread `19fac62d97c94e3d` · Msg Tanja `19fdc43b49050a5c` (2026-08-07).
- **Ergebnis Muster/Prüfung:** Richnerstutz hat **kein** Flowbox-/Beamer-geeignetes Material; Nachdruck gleiches Material sinnlos; Empfehlung: Textil beim Flowbox-Hersteller.
- **Kulanz:** bereits 30 % Materialrabatt; zusätzlich **+10 %** auf Material; **Arbeitsleistungen** werden verrechnet. Rechnungsadresse angefragt (Realia AG bereits bekannt).
- Video Richner: Adobe Acrobat `IMG_1987.MOV` (URN `aaid:sc:EU:86ef1c12-08be-4d61-9000-dff8b2a2ae6e`).
- **STOP Outbound** ohne Harald-Go. Entwurf: `Richnerstutz-Bespannung-Paket/08-reklamation-licht/Mail-Entwurf-Antwort-2026-08-07.md`.
- Bei weiterem Richner-Inbound: Docs + Summary; **kein** Mail-Versand durch Agent.

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
