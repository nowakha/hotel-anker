# Hotel Anker

Agent-Orientierung für das **Hauptprojekt** Hotel Anker (ein Repo, mehrere Module).

## Struktur

```
Hotel Anker/                          ← Hauptprojekt (Remote: hotel-anker)
├── README.md                         # Einstieg
├── AGENTS.md                         # Diese Datei
├── LEARNINGS.md                      # Handoff-Wissen
├── .cursor/rules/ + skills/          # Cursor-Regeln / UniFi-Skill
├── assets/                           # Arbeits-Assets
├── Richnerstutz-Bespannung-Paket/    # Druck / SEG Versand
└── WerbeLEDbox-CountDown/            # LED, Pis, Teensy, UniFi-Docs, Gast-Portal
    ├── guest-email-portal/           # Captive Portal (UDM :9090)
    ├── guest-wifi-portal/            # Branding-Exports
    ├── docs/NETWORK_UNIFI.md         # Netzplan
    └── secrets/                      # Pi + UniFi + WLAN (privat)
```

## Architektur (Stand 2026-07-28)

| Host | Rolle | Netz |
|------|--------|------|
| **UDM Pro Max** | Gateway, Gast-Portal-Dienst | `192.168.1.254` |
| **AnkerPI01** | Pi Zero 2 W — SPI0 LED putter (`N_LED=1179` @ 25 fps) | **Administration** `192.168.1.x` |
| **AnkerPI02** | Pi 4 — HDMI `fb-clock` + USB Teensy 8×512 WS2812 | **Administration** `192.168.1.x` (+ Tailscale) |
| **Pico** (`pico/`) | Abgelöst — Lab/Referenz | — |

SSIDs: `Administration` (Staff/Pis) · `HotelAnker` (Bar VLAN2) · `HotelAnkerGuest` (Portal VLAN3).  
PSK Staff: Secrets `wifi.hotelanker.yml` (`HeimatSchutz`).

## Agent-Workflow (verbindlich)

1. Abgeschlossene Schritte in `LEARNINGS.md` und/oder `WerbeLEDbox-CountDown/docs/SESSION_LOG.md` dokumentieren (Erfolg **und** Misserfolg).
2. Danach **commit + push** (Secrets absichtlich im Repo für privaten Handoff).
3. Keine absoluten Windows-Pfade hardcoden — repo-relativ.
4. Harald-Kontakt nur aus `.cursor/rules/harald-nowak-modernlight.mdc`.
5. **AnkerPI02:** SD nicht entnehmbar → Boot nicht riskieren; nie volle 24h-4K mit `ffmpeg -f null` proben.
6. UniFi: Skill `.cursor/skills/ubiquiti-unifi/` — kein Factory-Reset, kein Mongo-Schreiben für Branding.

## Canonical Docs

- Root: [`README.md`](./README.md), [`LEARNINGS.md`](./LEARNINGS.md)
- Session: [`WerbeLEDbox-CountDown/docs/SESSION_LOG.md`](./WerbeLEDbox-CountDown/docs/SESSION_LOG.md)
- LED/Pi: [`WerbeLEDbox-CountDown/README.md`](./WerbeLEDbox-CountDown/README.md)
- UniFi/WLAN: [`WerbeLEDbox-CountDown/docs/NETWORK_UNIFI.md`](./WerbeLEDbox-CountDown/docs/NETWORK_UNIFI.md)
- Print: [`Richnerstutz-Bespannung-Paket/README.md`](./Richnerstutz-Bespannung-Paket/README.md)
- Gast-Portal: `scripts/install_guest_email_portal.py`, `scripts/export_guest_emails.py`
