# WerbeLEDbox CountDown

Countdown-Anzeige für die Werbe-LED-Box im Hotel Anker.

## Zielplattform

**AnkerPI01** — Raspberry Pi Zero 2 W (`192.168.8.102` / `AnkerPI01.local`)

Vollständige Systemdokumentation: [`docs/ANKERPI01.md`](docs/ANKERPI01.md)  
Zugangsdaten: [`secrets/ankerpi01.credentials.yml`](secrets/ankerpi01.credentials.yml)

## Stack

- Python 3.13 + venv (`~/WerbeLEDbox-CountDown/.venv` on Pi)
- `numpy`, `spidev`, `SharedArray`
- SPI0: `/dev/spidev0.0` / `/dev/spidev0.1`, buffer **65536**

## Quick start (on AnkerPI01)

```bash
ssh AnkerPI01
cd ~/WerbeLEDbox-CountDown
source .venv/bin/activate
python -c "import numpy, SharedArray, spidev; print('ok')"
```

## Status

System vorbereitet (SPI, SSH, Python). Countdown-App folgt.
