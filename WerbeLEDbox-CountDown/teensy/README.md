# Anker Teensy — 8×512 WS2812 (Kendu Control Blok)

USB receiver for **AnkerPI02**. Replaces stock Kendu firmware.

| Field | Value |
|--------|--------|
| Board | Teensy on Kendu **8CH PIXEL CONTROL SLAVE** |
| Protocol | `ANKR` frames (same as Pico) |
| Geometry | `N_LED=512`, `N_LINES=8` |
| LED driver | OctoWS2811 default pins `2,14,7,8,6,20,21,5` |
| SD card | unused (was Kendu offline playback) |

## Build (Windows)

```powershell
cd WerbeLEDbox-CountDown\teensy\anker_pixel_pusher
pio run -e teensy32
pio run -e teensy40
```

## Identify + flash from AnkerPI02

```powershell
pwsh -File WerbeLEDbox-CountDown\teensy\scripts\flash_from_pi02.ps1
```

Script SSHs to AnkerPI02, installs `teensy_loader_cli` if needed, probes USB, uploads hex.

If the loader waits for HalfKay: **kurz die Program-Taste am Teensy drücken** (kleiner Taster auf dem Modul, nicht BOOTSEL wie beim Pico).
