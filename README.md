# Hotel Anker

**Hauptprojekt** Modernlight / Realia — eine Repo-Mappe für alle Hotel-Anker-Arbeiten
(LED-Countdown, Druck/SEG, UniFi/WLAN, Gast-Portal).

Handoff: [`LEARNINGS.md`](./LEARNINGS.md) · Agent: [`AGENTS.md`](./AGENTS.md)

## Module (ein Projekt, klare Ordner)

| Modul | Pfad | Inhalt |
|-------|------|--------|
| LED / Countdown | [`WerbeLEDbox-CountDown/`](./WerbeLEDbox-CountDown) | AnkerPI01/02, Teensy, Pico-Lab, Media, Scripts |
| Gast-WLAN-Portal | [`WerbeLEDbox-CountDown/guest-email-portal/`](./WerbeLEDbox-CountDown/guest-email-portal) | E-Mail-Captive-Portal auf UDM `:9090` |
| UniFi / Netz | [`WerbeLEDbox-CountDown/docs/NETWORK_UNIFI.md`](./WerbeLEDbox-CountDown/docs/NETWORK_UNIFI.md) | UDM, VLANs, SSIDs, Portal-Betrieb |
| Druck / SEG | [`Richnerstutz-Bespannung-Paket/`](./Richnerstutz-Bespannung-Paket) | Versandfertig an Richnerstutz |
| Assets | [`assets/`](./assets) | Print-Master, Layout, Refs |

Es gibt **kein** zweites Root-Repo — alles hängt unter `Hotel Anker/` (Remote: `hotel-anker`).

## Netz & Hosts (Soll)

| SSID | Netz | Zweck |
|------|------|--------|
| `Administration` | `192.168.1.0/24` | Staff / **AnkerPI01 + AnkerPI02** (PSK in Secrets) |
| `HotelAnker` | `192.168.2.0/24` (VLAN 2) | CountDown Bar / Gäste-Staff |
| `HotelAnkerGuest` | `192.168.3.0/24` (VLAN 3) | Open + E-Mail-Portal |

| Host | Rolle | Zugang |
|------|--------|--------|
| **UDM Pro Max** | Gateway / UniFi | `192.168.1.254` · [`secrets/unifi.hotelanker.yml`](./WerbeLEDbox-CountDown/secrets/unifi.hotelanker.yml) |
| **AnkerPI01** | SPI LED putter (`ws2812put`, 1179 LEDs) | `AnkerPI01.local` · Admin-WLAN · [`ankerpi01.credentials.yml`](./WerbeLEDbox-CountDown/secrets/ankerpi01.credentials.yml) |
| **AnkerPI02** | HDMI 24h-Clock + USB Teensy 8×512 | `AnkerPI02.local` / Tailscale · Admin-WLAN · [`ankerpi02.credentials.yml`](./WerbeLEDbox-CountDown/secrets/ankerpi02.credentials.yml) |

WLAN-PSK (Administration / HotelAnker): [`wifi.hotelanker.yml`](./WerbeLEDbox-CountDown/secrets/wifi.hotelanker.yml) (`HeimatSchutz`).

## Cursor

| Pfad | Inhalt |
|------|--------|
| [`.cursor/rules/harald-nowak-modernlight.mdc`](./.cursor/rules/harald-nowak-modernlight.mdc) | Harald-Kontakt |
| [`.cursor/rules/hotel-anker-workflow.mdc`](./.cursor/rules/hotel-anker-workflow.mdc) | Dokumentieren + pushen |
| [`.cursor/skills/ubiquiti-unifi/`](./.cursor/skills/ubiquiti-unifi) | UniFi-Skill |

Credentials und Regeln liegen bewusst im Repo (privater Handoff). **Nicht** öffentlich publishen ohne Rotation.
