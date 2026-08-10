# NEXT AGENT — Sofortmaßnahmen

Stand: **2026-08-10 ~23:15**. Lies `LEARNINGS.md` + `docs/SESSION_LOG.md` + **`docs/VIER_GRUENDSAETZE.md`** (Projekt-DNA, alwaysApply).

## Projektgrundsätze

Vier sine-qua-non Grundsätze gelten für **jede** Arbeit in diesem Repo (Regel `hotel-anker-grundsaetze.mdc`). Nicht ignorieren bei Print/LED/Kommunikation/Konzept.

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
- Keine Inhalte, die den vier Grundsätzen widersprechen (reines Lodging-Framing, etc.)
