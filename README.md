# Hotel Anker

Projektmappe für Hotel Anker (Modernlight / Realia).

**Handoff:** [`LEARNINGS.md`](./LEARNINGS.md) · Agent-Hinweise: [`AGENTS.md`](./AGENTS.md)

## Unterprojekte

| Ordner | Beschreibung |
|--------|--------------|
| [`WerbeLEDbox-CountDown`](./WerbeLEDbox-CountDown) | Countdown / Pi-Hosts / Teensy / Pico-Lab |
| [`Richnerstutz-Bespannung-Paket`](./Richnerstutz-Bespannung-Paket) | Versandfertig: SEG-Textil / Druck / Opazität |
| [`assets`](./assets) | Arbeits-Assets (Print-Master, Layout, Refs) |

## Hardware

| Host | Rolle | Doku | Secrets |
|------|--------|------|---------|
| AnkerPI01 (`AnkerPI01.local` / DHCP ~`192.168.8.108`) | SPI LED putter (1179 LEDs @ 25 fps) | [`WerbeLEDbox-CountDown/docs/ANKERPI01.md`](./WerbeLEDbox-CountDown/docs/ANKERPI01.md) | [`ankerpi01.credentials.yml`](./WerbeLEDbox-CountDown/secrets/ankerpi01.credentials.yml) |
| AnkerPI02 (`192.168.8.106`) | HDMI 24h-Clock + USB Teensy 8×512 | [`ANKERPI02.md`](./WerbeLEDbox-CountDown/docs/ANKERPI02.md) · [`ANKERPI02-TEENSY.md`](./WerbeLEDbox-CountDown/docs/ANKERPI02-TEENSY.md) | [`ankerpi02.credentials.yml`](./WerbeLEDbox-CountDown/secrets/ankerpi02.credentials.yml) |

Credentials und Cursor-Regeln liegen bewusst im Repo (privater Handoff). Repo **nicht** öffentlich machen ohne Rotation.

## Cursor

| Pfad | Inhalt |
|------|--------|
| [`.cursor/rules/harald-nowak-modernlight.mdc`](./.cursor/rules/harald-nowak-modernlight.mdc) | Harald-Kontakt Modernlight |
| [`.cursor/rules/hotel-anker-workflow.mdc`](./.cursor/rules/hotel-anker-workflow.mdc) | Dokumentieren + nach jedem Schritt pushen |
