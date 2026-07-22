# AnkerPI02 — Pi 4 HDMI 24h clock player

Headless **HDMI0** host: 24‑hour clock video seek‑synced to local time.  
Silent boot with **Hotel Anker** logo splash. Monitor mounted **180°**.

## Display / boot

| Field | Value |
|--------|--------|
| Mode | **3440×1440 @ 50 Hz** (no KMS rotate — content rotated in software) |
| Framebuffer | `/dev/fb0` RGB565 |
| Rainbow splash | off (`disable_splash=1`) |
| Console on HDMI | off (serial only, `getty@tty1` masked) |
| Boot logo | Anker+Krone, height **4/5** screen, 180° baked in, until `fb-clock` |

```bash
python3 scripts/gen_fb_splash.py   # if regenerating on a machine with Pillow
bash scripts/ankerpi02_setup_silent_boot.sh
sudo reboot
```

Splash assets: `media/boot_splash_3440x1440.{png,rgb565}`  

**If Pi won't boot after a bad `rotate=` cmdline:** mount the SD boot partition on a PC and replace `cmdline.txt` with the single line from [`../media/cmdline.recovery.txt`](../media/cmdline.recovery.txt).

## Clock video

Path: `media/clock_24h.mp4` — exactly **86400 s**, t=0 = 00:00:00, H.264, 860×360, 25 fps, `-g 25`.

Service: `fb-clock.service` (after NTP + splash).

## Underclock

Fixed ARM 1000 / GPU 300 MHz, `avoid_warnings=2` — see `scripts/ankerpi02_setup_underclock.sh`.
