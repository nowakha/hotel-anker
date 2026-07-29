# Hotel Anker — Agent Handoff (kanonisch)

Stand: **2026-07-29**. Ein Repo (`nowakha/hotel-anker`).  
Diese Datei ersetzt frühere Split-Docs (`NEXT_AGENT.md`) und fasst alle Cursor-Agent-Sessions zusammen. Roh-Transkripte wurden nach dieser Konsolidierung entfernt.

---

## 1. Projekt-Orientierung

```
Hotel Anker/
├── README.md
├── AGENTS.md                 # diese Datei — Orientierung + Session-Chronik + Next
├── LEARNINGS.md              # technische Learnings / Fallen
├── .cursor/rules/ | skills/
├── assets/
├── Richnerstutz-Bespannung-Paket/
└── WerbeLEDbox-CountDown/    # Pi / Teensy / Pico(Lab) / UniFi / Clock / Guest-Portal
```

### Architektur (Soll)

| Host | Rolle | Zugang |
|------|--------|--------|
| **AnkerPI01** | Pi Zero 2 W — SPI0 LED putter `ws2812put` (`N_LED=1179` @ 25 fps) | `WerbeLEDbox-CountDown/secrets/ankerpi01.credentials.yml` |
| **AnkerPI02** | Pi 4 — HDMI 24h-Clock (`fb-clock`) + USB **Teensy** 8×512 WS2812 | `…/secrets/ankerpi02.credentials.yml` |
| **Pico** (`pico/`) | Abgelöst — Lab/Referenz | `docs/ANKERPI02-TEENSY.md` |
| **UDM Pro Max** | `192.168.1.254` — UniFi + Guest-Portal | `…/secrets/unifi.hotelanker.yml` |
| **U7 Pro Wall** | `192.168.1.220` | dito |

### Agent-Workflow (verbindlich)

1. Erfolg **und** Misserfolg in `LEARNINGS.md` und/oder `WerbeLEDbox-CountDown/docs/SESSION_LOG.md`.
2. Commit + **`git push origin HEAD`** (Secrets absichtlich getrackt).
3. Keine absoluten Windows-Pfade hardcoden.
4. Harald-Kontakt nur aus `.cursor/rules/harald-nowak-modernlight.mdc`.
5. **AnkerPI02:** SD nicht entnehmbar → Boot nicht riskieren; nie `ffmpeg … -f null -` auf 24h/4K; Recovery: `WerbeLEDbox-CountDown/media/cmdline.recovery.txt`.

### Canonical Docs

- Root: `README.md`, `LEARNINGS.md`, **diese Datei**
- Session-Detail: `WerbeLEDbox-CountDown/docs/SESSION_LOG.md`
- Netz: `WerbeLEDbox-CountDown/docs/NETWORK_UNIFI.md`
- Print: `Richnerstutz-Bespannung-Paket/README.md`

---

## 2. Aktueller Status / Nächste Schritte

### Netz / Clock LIVE

- **PI01:** Administration `192.168.1.91`, Tailscale `100.67.4.18` — NM `key-mgmt=wpa-psk` (Zero 2 W ≠ WPA3-only).
- **PI02:** Administration `192.168.1.222`, Tailscale `100.103.54.63`.
- **Clock:** `fb-clock.service` **enabled** — `fb_clock_play.py --max-drift 0.35 --resync-every 0`, Video `media/clock_24h.mp4`.
- **WLAN-Staff-PSK:** `HeimatSchutz` → `secrets/wifi.hotelanker.yml` (Administration + HotelAnker).
- **SSIDs:** `Administration` (`.1.x`) · `HotelAnker` (Bar `.2.x`) · `HotelAnkerGuest` (Portal `.3.x`).
- **Administration:** `wpa3_transition=true`, `pmf_mode=optional` (Scan `WPA2 WPA3`) — **nicht** WPA3-only.

### Optional Verify

```bash
ssh user@100.103.54.63
systemctl status fb-clock
journalctl -u fb-clock -f
# erwartet: kein periodic resync; selten drift=…; get_throttled beachten (0x80008 gesehen)
```

### Nicht tun

- Kein `cmdline.txt`-Experiment (`rotate=` etc.)
- Kein apt `python3-opencv`
- Kein `ffmpeg … -f null -` auf 24h/4K
- Administration nicht auf WPA3-only (bricht PI01)
- Nie `HotelAnker` `autoconnect=no`, bevor Administration + `192.168.1.x` stabil sind

### Offen / Follow-ups

- Guest-E-Mails: UDM `/data/hotel-anker/guest-emails/` · Export `scripts/export_guest_emails.py`
- Domains: Kaufanfrage Remimag gesendet; Geo-Paket Hostpoint noch kaufen
- Richnerstutz: Finale Druckdaten / Offerte im Versand-Paket; Antwort abwarten
- PI02 Throttling `0x80008` beobachten (PSU/Kühlung)
- Pico bleibt Lab; Live-Pusher = Teensy

---

## 3. Chronik aller Top-Level-Agent-Sessions

Kurz-UUID = erste 8 Zeichen.  
Arbeit **2026-07-22 abend – 2026-07-27** und **2026-07-29 ~00:00–00:50** steht stark in `SESSION_LOG`/`LEARNINGS` (teilweise ohne eigenes Transkript-UUID).

### `c9c99448` — 2026-07-21 — Projektstart + AnkerPI01 SPI

- Repo **Hotel Anker** + WerbeLEDbox CountDown auf Git.
- AnkerPI01: SSH, Secrets, SPI0, Buffer ≥65536, `ws2812put`, **N_LED=1179** @ 25 fps.
- Pixel-Blink-Tests; Shutdown für echte WS2812-Verkabelung.

### `7279dbf9` — 2026-07-21 — AnkerPI01 sauber herunterfahren

- Blink + `ws2812put` gestoppt; `shutdown -h now`; Host offline bestätigt.

### `3cd4be5c` — 2026-07-21 — Historie + Kendu-Print/Countdown-Design

- Recherche Hotel Anker Rorschach; Ghost-`888` / Blueprint-Fassade; Assets unter `assets/kendu-flowbox-2m-print/`.

### `c5e8fb22` — 2026-07-21→22 — Pico→Teensy, Countdown LIVE, Print *(größte Session)*

- Pico Lab; Live = **Teensy 3.2** 8×512 Serpentine auf PI02, später PI01.
- Countdown: Amber, Wellen, Blueprint, Anker gold; Ziel **2026-10-01 13:00 Europe/Zurich**.
- Canva-Layer / Opacity-Maske; SHM-Freeze gefixt.

### `4d2aa62d` / `81b39a6d` / `7f590b71` — 2026-07-21 — 9-Pixel-Blink PI01

- Start erst unter **`192.168.8.108`** (`.102` tot); Service-Restart + Blink PID ok.

### `e3d6dda7` — 2026-07-22 — PI01 Teensy-Stack wie PI02

- SPI-`ws2812put` disabled; Teensy-Stack deployed; USB damals noch fehlend → Retry.

### `df4060fa` — 2026-07-22→28 — HDMI-Clock + UniFi/Guest + WLAN-Migrate

- PI02 HDMI-Clock **860×360** / `fb_clock_play`; **cmdline rotate=180 = Boot-Brick** → nur Software-Rotation.
- Guest-E-Mail-Portal live auf UDM (`:9090`, SQLite/CSV, DE/EN/FR/IT/RM, 120 min).
- WLAN-Migrate zu Administration: Pis offline → Power-Cycle; später Rescue/WPA3-Transition.

### `21850826` — 2026-07-22 — Aufräumen, Handoff-Push

- Specs/Skills/Learnings; Workflow „jeder Schritt → push“; Live-Clock-Default.

### `fd1000ea` — 2026-07-28 — Domains Rorschach + Remimag-Mail

- Geo-Domain-Paket ~CHF 105; Kaufanfrage an `info@remimag.ch` (ohne Ablöse).

### `1e630efe` — 2026-07-29 — Konsolidierung

- Alle Agent-Sessions → diese Datei; Transkripte entfernt; Guest-Mails exportiert; Gesamtprojekt push.

---

## 4. Repo-Nachträge ohne Transkript-UUID

| Zeitraum | Thema | Kern |
|----------|--------|------|
| 2026-07-22 abend | NVENC `clock_24h`, WiFi/Tailscale | Encode pause/resume; Clock dauerhaft |
| 2026-07-23 | Deploy clock_24h LIVE; Richnerstutz | ~25 fps; Mail Offerte |
| 2026-07-24 | Smooth-Patch im Repo | Deploy damals pending |
| 2026-07-27 | Finale Druck-PDFs 2100/300 mm | `Richnerstutz-Bespannung-Paket/versand/` |
| 2026-07-29 ~00:06 | PI01 SD-WiFi-Rescue | usbipd **6-2**; Admin primary |
| 2026-07-29 ~00:35 | WPA3 Transition | PI01 wieder `192.168.1.91` |
| 2026-07-29 ~00:50 | Smooth `fb-clock` autostart LIVE | PI02 `192.168.1.222` / TS `.63` |

---

## 5. Credentials / Hosts (Endzustand)

| Ressource | Pfad / Wert |
|-----------|-------------|
| PI01 Creds | `WerbeLEDbox-CountDown/secrets/ankerpi01.credentials.yml` |
| PI02 Creds | `WerbeLEDbox-CountDown/secrets/ankerpi02.credentials.yml` |
| WiFi Staff | `WerbeLEDbox-CountDown/secrets/wifi.hotelanker.yml` |
| UniFi | `WerbeLEDbox-CountDown/secrets/unifi.hotelanker.yml` |
| SSH-Fragmente | `WerbeLEDbox-CountDown/ssh/` |
| PI01 | LAN `192.168.1.91` · TS `100.67.4.18` |
| PI02 | LAN `192.168.1.222` · TS `100.103.54.63` |
| UDM | `192.168.1.254` |
| U7 | `192.168.1.220` |
| Guest-Mails | UDM `/data/hotel-anker/guest-emails/` |
| Boot-Recovery | `WerbeLEDbox-CountDown/media/cmdline.recovery.txt` |

Historische Bar/Alt-IPs: PI01 `.8.102`/`.108`/`.2.91`; PI02 `.8.106`/`.8.112`/`.2.222`.

---

## 6. Transkript-Index (archiviert in dieser Datei)

| Kurz | UUID | Datum |
|------|------|-------|
| c9c99448 | `c9c99448-3b89-4fcd-bbab-9ad9d82e12e2` | 2026-07-21 |
| 7279dbf9 | `7279dbf9-74a9-4901-9077-9c1ff4004883` | 2026-07-21 |
| 3cd4be5c | `3cd4be5c-cfbf-478e-b913-9fa9b21487b0` | 2026-07-21 |
| c5e8fb22 | `c5e8fb22-bc2d-4f31-a531-45bffbc4c0cb` | 2026-07-21→22 |
| 4d2aa62d | `4d2aa62d-ad17-434a-aa0d-72725dda37ed` | 2026-07-21 |
| 81b39a6d | `81b39a6d-7a71-47ba-9211-abd0c70a40c4` | 2026-07-21 |
| 7f590b71 | `7f590b71-3568-4405-91af-b6aab5fba6a9` | 2026-07-21 |
| e3d6dda7 | `e3d6dda7-d305-4d4e-83a9-28e38ed28e6a` | 2026-07-22 |
| df4060fa | `df4060fa-b89b-49bb-94bc-4467294f8d52` | 2026-07-22→28 |
| 21850826 | `21850826-2ce0-4661-a256-5581cd37138e` | 2026-07-22 |
| fd1000ea | `fd1000ea-178d-47ec-ad60-f479dfbaefdd` | 2026-07-28 |
| 1e630efe | `1e630efe-b06f-4e2b-90d1-c455576a12dc` | 2026-07-29 |
