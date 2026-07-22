# Anker Pico — WS2812 USB receiver (LAB / ARCHIV)

> **Status 2026-07-22:** Am Hotel-Setup **nicht mehr Live**. USB-Gerät an AnkerPI02 ist der **Teensy** (Kendu 8CH).  
> Dieser Ordner bleibt als Protokoll-Referenz (`ANKR`) und Lab-Fallback.  
> Live-Pfad: [`../teensy/`](../teensy/) · Discovery: [`../docs/ANKERPI02-TEENSY.md`](../docs/ANKERPI02-TEENSY.md)

Historisch (vor Teensy):

| Field | Value |
|--------|--------|
| Host | `AnkerPI02` / `192.168.8.106` |
| Device | `/dev/ttyACM0` |
| USB | `VID_2E8A` / `PID_0005` (MicroPython) |
| Board | Raspberry Pi Pico (RP2040, kein WLAN) |
| Firmware | MicroPython v1.28.0 |

Geometrie in `src/config.py`: `N_LINES=8`, `N_LED` je Linie — siehe Source, nicht ältere „4-line“-Notizen.

Build/Flash nur für Lab: `pico/scripts/flash_micropython.ps1`. WiFi/`secrets.py` optional und ungenutzt im Hotel-Install.
