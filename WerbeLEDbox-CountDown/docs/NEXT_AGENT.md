# NEXT AGENT — Sofortmaßnahmen

Stand: **2026-08-10 ~23:30**. Lies `LEARNINGS.md` + `docs/SESSION_LOG.md` + **`docs/VIER_GRUENDSAETZE.md`** + **`docs/DOMAINS.md`**.

## Projektgrundsätze

Vier sine-qua-non Grundsätze gelten für **jede** Arbeit in diesem Repo (Regel `hotel-anker-grundsaetze.mdc`). Nicht ignorieren bei Print/LED/Kommunikation/Konzept.

## Domains — JETZT

1. **Willi OOO bis 24.08.** — Eskalation an `marketing-werbung@remimag.ch` bereits gesendet (`19fed927e2d59894`).
2. Auth-Code / Inhaberwechsel abwarten (Marketing oder Eberle/Bullakaj).
3. Code da → Hostpoint-Transfer-Checkliste in `docs/DOMAINS.md` (Auth-Code **nicht** committen).
4. Stille >2–3 Werktage → erneut Marketing + CC nachfassen; ab 25.08. auch Willi.
5. Fallback: Geo-Must; Drop-Catch **20.11.** / **28.11.2026** nur wenn Transfer scheitert.
6. `hotel-anker.ch` bleibt Remimag — nicht pushen.

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
