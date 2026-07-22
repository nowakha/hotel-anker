# AnkerPI02 — Pi 4 HDMI clock + USB Teensy

Zugang: [`../secrets/ankerpi02.credentials.yml`](../secrets/ankerpi02.credentials.yml) · SSH-Fragment: [`../ssh/config.fragment`](../ssh/config.fragment)

**USB Teensy** 8×512 WS2812 — [`ANKERPI02-TEENSY.md`](ANKERPI02-TEENSY.md) · Firmware: [`../teensy/`](../teensy/) · Hex: [`../teensy/hex/`](../teensy/hex/)

## HDMI clock (default: live)

Headless **HDMI0** host. Monitor mounted **180°** (rotation in software).

| Field | Value |
|--------|--------|
| Mode | **3440×1440 @ 50 Hz** |
| Framebuffer | `/dev/fb0` RGB565 |
| Default player | **`fb_clock_live.py`** (digital clock, NTP-synced) |
| Optional | `fb_clock_play.py` + `media/clock_24h.mp4` (designed animation) |

```bash
# on AnkerPI02
bash scripts/install_fb_clock_live_service.sh
# unit installed as fb-clock.service
```

Splash assets: `media/boot_splash_3440x1440.{png,rgb565}`  
Generate optional MP4: `scripts/gen_clock_24h.py` (see `media/README.md`).

**If Pi won't boot after a bad `rotate=` cmdline:** mount the SD boot partition on a PC and replace `cmdline.txt` with the single line from [`../media/cmdline.recovery.txt`](../media/cmdline.recovery.txt).

## Underclock

Fixed ARM 1000 / GPU 300 MHz, `avoid_warnings=2` — see `scripts/ankerpi02_setup_underclock.sh`.
