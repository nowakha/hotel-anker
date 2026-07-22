# Hotel Anker

Root-Repository für Hotel-Anker-Unterprojekte.

## Struktur

```
Hotel Anker/
├── README.md                 # Einstieg + Hardware-Übersicht
├── AGENTS.md                 # Diese Datei — Agent-Orientierung
├── LEARNINGS.md              # Projekt-Learnings / Handoff-Wissen
├── .cursor/rules/            # Cursor-Regeln (Kontakt, Workflow)
├── assets/                   # Arbeits-Assets (Print, Layout, Refs)
├── Richnerstutz-Bespannung-Paket/  # Versandfertig an Druckerei
└── WerbeLEDbox-CountDown/    # Countdown / Pi / Teensy / Pico (Lab)
```

## Aktuelle Architektur (Stand 2026-07-22)

| Host | Rolle | Zugang |
|------|--------|--------|
| **AnkerPI01** | Pi Zero 2 W — SPI0 LED putter `ws2812put` (`N_LED=1179` @ 25 fps) | `secrets/ankerpi01.credentials.yml` |
| **AnkerPI02** | Pi 4 — HDMI 24h-Clock (`fb-clock`) + USB **Teensy** 8×512 WS2812 | `secrets/ankerpi02.credentials.yml` |
| **Pico** (`pico/`) | **Abgelöst** — Lab/Referenz; Live-USB-Gerät ist Teensy | siehe `docs/ANKERPI02-TEENSY.md` |

## Agent-Workflow (verbindlich)

1. Jeden abgeschlossenen Schritt dokumentieren — **Erfolg und Misserfolg** — in `LEARNINGS.md` und/oder `WerbeLEDbox-CountDown/docs/SESSION_LOG.md`.
2. Danach **commit + push** (Secrets absichtlich im Repo für privaten Handoff).
3. Keine absoluten Windows-Pfade hardcoden — immer repo-relativ.
4. Harald-Kontakt nur aus `.cursor/rules/harald-nowak-modernlight.mdc`.
5. **AnkerPI02:** SD nicht entnehmbar → Boot nicht riskieren; nie volle 24h-4K mit `ffmpeg -f null` proben.

## Canonical Docs

- Root: [`README.md`](./README.md), [`LEARNINGS.md`](./LEARNINGS.md)
- Session: [`WerbeLEDbox-CountDown/docs/SESSION_LOG.md`](./WerbeLEDbox-CountDown/docs/SESSION_LOG.md)
- LED/Pi: [`WerbeLEDbox-CountDown/README.md`](./WerbeLEDbox-CountDown/README.md)
- Print: [`Richnerstutz-Bespannung-Paket/README.md`](./Richnerstutz-Bespannung-Paket/README.md)
