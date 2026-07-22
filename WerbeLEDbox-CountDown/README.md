# WerbeLEDbox CountDown

Countdown-Anzeige für die Werbe-LED-Box im Hotel Anker.

## Zielplattformen

**AnkerPI01** — Raspberry Pi Zero 2 W (`AnkerPI01.local` / currently `192.168.8.108`)  
Docs: [`docs/ANKERPI01.md`](docs/ANKERPI01.md) · Secrets: [`secrets/ankerpi01.credentials.yml`](secrets/ankerpi01.credentials.yml)

**AnkerPI02** — Raspberry Pi 4 HDMI **24h clock** player (`192.168.8.106` / `AnkerPI02.local`)  
Docs: [`docs/ANKERPI02.md`](docs/ANKERPI02.md) · Secrets: [`secrets/ankerpi02.credentials.yml`](secrets/ankerpi02.credentials.yml) · `fb_clock_play.py` → `/dev/fb0`

## Stack

- **AnkerPI01:** Python 3.13 + venv, `numpy` / `spidev` (65536) / `SharedArray`, SPI0 LED putter `ws2812put.py` (`N_LED=1179`, **25 fps**)
- **AnkerPI02:** HDMI **3440×1440@50**, fixed underclock, NTP → `fb-clock.service` (24h video seek-synced to wall clock)

## Quick start (on AnkerPI01)

```bash
ssh AnkerPI01
cd ~/WerbeLEDbox-CountDown
source .venv/bin/activate
python -c "import numpy, SharedArray, spidev; print('ok')"

# LED putter (or use systemd)
sudo systemctl start ws2812put
sudo systemctl status ws2812put
```

Producer apps write RGB into `shm://ws2812` shape `(1179, 3)` uint8. Stop putter: `sudo systemctl stop ws2812put` (sends black frame on exit).

Pixel-0 blink test (putter must be running; attach-only):

```bash
python scripts/test_pixel0_blink.py
```

## Status

SPI/SSH/Python bereit; `ws2812put` Service für 1179 LEDs @ 25 fps. Countdown-Producer folgt.
