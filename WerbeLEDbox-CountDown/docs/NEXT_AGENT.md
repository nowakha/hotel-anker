# NEXT AGENT — Sofortmaßnahmen

Stand: **2026-08-10 ~23:30**. Lies `LEARNINGS.md` + `docs/SESSION_LOG.md` + **`docs/VIER_GRUENDSAETZE.md`** + **`docs/DOMAINS.md`**.

## Projektgrundsätze

Vier sine-qua-non Grundsätze gelten für **jede** Arbeit in diesem Repo (Regel `hotel-anker-grundsaetze.mdc`). Nicht ignorieren bei Print/LED/Kommunikation/Konzept.

## Domains — JETZT

1. **Warten auf Remimag:** Auth-Code / Inhaberwechsel für `hotelanker.ch` (Mail 10.08. gesendet, thread `19fa8fccec8877a9`).
2. Code da → Hostpoint-Transfer-Checkliste in `docs/DOMAINS.md` abarbeiten (Auth-Code **nicht** committen).
3. Keine Antwort in ~5 Werktagen → höflich nachfassen (Willi + CC).
4. Fallback: Geo-Must-Paket; Drop-Catch Reminder **20.11.** / **28.11.2026** nur wenn Transfer scheitert.
5. `hotel-anker.ch` bleibt Remimag — nicht pushen.

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
