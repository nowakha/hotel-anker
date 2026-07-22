# WerbeLEDbox CountDown

Countdown-Anzeige für die Werbe-LED-Box im Hotel Anker.

Handoff-Wissen: [`../LEARNINGS.md`](../LEARNINGS.md)

## Zielplattformen

**AnkerPI01** — Raspberry Pi Zero 2 W (`AnkerPI01.local` / DHCP oft `192.168.8.102`)  
Docs: [`docs/ANKERPI01.md`](docs/ANKERPI01.md) · Secrets: [`secrets/ankerpi01.credentials.yml`](secrets/ankerpi01.credentials.yml)  
Services: `ws2812put` + `countdown_pi01` (Producer → Baubeginn 2026-10-01 13:00)

**AnkerPI02** — Raspberry Pi 4  
- HDMI clock — **live** `fb_clock_live.py` (Default) — [`docs/ANKERPI02.md`](docs/ANKERPI02.md)  
- USB **Teensy** 8×512 — [`docs/ANKERPI02-TEENSY.md`](docs/ANKERPI02-TEENSY.md) · Hex: [`teensy/hex/`](teensy/hex/)  
Secrets: [`secrets/ankerpi02.credentials.yml`](secrets/ankerpi02.credentials.yml)

**Pico** (`pico/`) — **Lab / abgelöst** (früher USB-Receiver; Live = Teensy).

## Stack

- **AnkerPI01:** Python 3.13 + venv, `numpy` / `spidev` (65536) / `SharedArray`, SPI0 LED putter `ws2812put.py` (`N_LED=1179`, **25 fps**) + `countdown_pi01.py`
- **AnkerPI02:** HDMI **3440×1440@50**, live clock; Teensy über USB-CDC (`ANKR`)

## Quick start (AnkerPI01)

```bash
ssh AnkerPI01
cd ~/WerbeLEDbox-CountDown
source .venv/bin/activate
bash scripts/install_ws2812put_service.sh
bash scripts/install_countdown_pi01_service.sh
sudo systemctl status ws2812put countdown_pi01
```

## Print / Bespannung

Versandpaket: [`../Richnerstutz-Bespannung-Paket/`](../Richnerstutz-Bespannung-Paket/)  
Arbeitsmaster: [`../assets/kendu-flowbox-2m-print/`](../assets/kendu-flowbox-2m-print/)

## Status

SPI/SSH/Python auf PI01 bereit; Countdown-Producer + Teensy-Hex (offline validiert) im Repo. Live-Deploy/Flash wenn die Pis im LAN sind.
