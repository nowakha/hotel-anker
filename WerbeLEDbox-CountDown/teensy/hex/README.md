# Built firmware hex (PlatformIO) — tracked for handoff / flash when Pi is offline.

| File | Board |
|------|--------|
| `firmware_teensy32.hex` | Teensy 3.2 |
| `firmware_teensy40.hex` | Teensy 4.0 / 4.1 (same env default) |

Validate offline:

```powershell
py -3 WerbeLEDbox-CountDown\scripts\validate_teensy_build.py
```

Flash (AnkerPI02 online + Program-Taste):

```powershell
pwsh -File WerbeLEDbox-CountDown\teensy\scripts\flash_from_pi02.ps1 -SkipBuild
```

Rebuild:

```powershell
cd WerbeLEDbox-CountDown\teensy\anker_pixel_pusher
pio run -e teensy32 -e teensy40
Copy-Item .pio\build\teensy32\firmware.hex ..\hex\firmware_teensy32.hex -Force
Copy-Item .pio\build\teensy40\firmware.hex ..\hex\firmware_teensy40.hex -Force
```
