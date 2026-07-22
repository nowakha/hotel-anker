# WerbeLEDbox CountDown

Countdown-Anzeige für die Werbe-LED-Box im Hotel Anker.

Handoff-Wissen: [`../LEARNINGS.md`](../LEARNINGS.md)

## Zielplattformen

**AnkerPI01** — Raspberry Pi Zero 2 W (`AnkerPI01.local` / DHCP oft `192.168.8.108`)  
Docs: [`docs/ANKERPI01.md`](docs/ANKERPI01.md) · Secrets: [`secrets/ankerpi01.credentials.yml`](secrets/ankerpi01.credentials.yml)

**AnkerPI02** — Raspberry Pi 4  
- HDMI **24h clock** (`fb_clock_play.py` → `/dev/fb0`) — [`docs/ANKERPI02.md`](docs/ANKERPI02.md)  
- USB **Teensy** 8×512 WS2812 — [`docs/ANKERPI02-TEENSY.md`](docs/ANKERPI02-TEENSY.md) · Firmware: [`teensy/`](teensy/)  
Secrets: [`secrets/ankerpi02.credentials.yml`](secrets/ankerpi02.credentials.yml)

**Pico** (`pico/`) — **Lab / abgelöst** (früher USB-Receiver; Live = Teensy).

## Stack

- **AnkerPI01:** Python 3.13 + venv, `numpy` / `spidev` (65536) / `SharedArray`, SPI0 LED putter `ws2812put.py` (`N_LED=1179`, **25 fps**)
- **AnkerPI02:** HDMI **3440×1440@50**, underclock, NTP → `fb-clock.service`; Teensy über USB-CDC (`ANKR`)

## Quick start (AnkerPI01)

```bash
ssh AnkerPI01
cd ~/WerbeLEDbox-CountDown
source .venv/bin/activate
sudo systemctl start ws2812put
sudo systemctl status ws2812put
```

Producer schreiben RGB in `shm://ws2812` Shape `(1179, 3)` uint8.

## Print / Bespannung

Versandpaket: [`../Richnerstutz-Bespannung-Paket/`](../Richnerstutz-Bespannung-Paket/)  
Arbeitsmaster: [`../assets/kendu-flowbox-2m-print/`](../assets/kendu-flowbox-2m-print/)

## Status

SPI/SSH/Python auf PI01 bereit; `ws2812put` @ 1179 LEDs / 25 fps. Countdown-Producer und Teensy-Flash-Validierung folgen.
