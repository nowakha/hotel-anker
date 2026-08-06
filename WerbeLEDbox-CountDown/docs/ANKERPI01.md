# AnkerPI01 — System & Dev Setup

Target machine for **WerbeLEDbox CountDown**.

## Identity

| Field | Value |
|--------|--------|
| Hostname | `AnkerPI01` / `AnkerPI01.local` |
| Tailscale | **`100.67.4.18`** (`AnkerPI01`) — prefer for remote work |
| IP (LAN) | DHCP (observed `192.168.8.102`; earlier `.108`) — prefer `AnkerPI01.local` |
| Board | Raspberry Pi Zero 2 W Rev 1.0 |
| OS | Debian 13 (trixie), aarch64 |
| Kernel (at setup) | `6.18.34+rpt-rpi-v8` |
| SSH user | `user` |
| Password | see [`../secrets/ankerpi01.credentials.yml`](../secrets/ankerpi01.credentials.yml) |

Credentials are stored in-repo by project request.

## SSH access

- **Passwordless** from this workstation via ed25519 key (`~/.ssh/id_ed25519`).
- **Password login remains enabled** (`PasswordAuthentication yes`).
- SSH drop-in on the Pi: `/etc/ssh/sshd_config.d/99-hotel-anker.conf`

### From this PC

```bash
# preferred (Tailscale)
ssh user@100.67.4.18
# or LAN
ssh user@AnkerPI01.local
```

Password: `12345678` (see secrets). From Mac without deployed key: `sshpass -e ssh …`.

Optional: merge [`../ssh/config.fragment`](../ssh/config.fragment) into `%USERPROFILE%\.ssh\config`, then:

```powershell
ssh AnkerPI01
```

### Re-install pubkey (if needed)

Public key used at setup:

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKvsQhoMz2N0gX4kWMj2/kao0mTTTGTnz1v6UY5ooEKs hotel-anker-dev@TABLETHI10MAX
```

## Hardware / SPI0

SPI0 enabled:

- Devices: `/dev/spidev0.0`, `/dev/spidev0.1`
- User `user` is in group `spi`
- `dtparam=spi=on` in `/boot/firmware/config.txt`

### SPI buffer ≥ 65536

Default Linux `spidev` buffer is often **4096**. Raised to **65536**:

1. `/etc/modprobe.d/spidev.conf` → `options spidev bufsiz=65536`
2. `/boot/firmware/cmdline.txt` → `spidev.bufsiz=65536` (survives early module load)

Verify:

```bash
cat /sys/module/spidev/parameters/bufsiz   # expect 65536
ls -l /dev/spidev0.*
cd ~/WerbeLEDbox-CountDown && source .venv/bin/activate
python scripts/test_spi0.py
```

**python-spidev:** Stock Debian `python3-spidev` caps list/`xfer2` at 4096.  
Hotel-Anker build **3.6.1** is installed into the project venv with `SPIDEV_MAX_TRANSFER=65536` (see `scripts/patch_install_spidev_65536.sh`).

```bash
cd ~/WerbeLEDbox-CountDown && source .venv/bin/activate
python -c "import spidev; print(spidev.__version__, spidev.__file__)"
python scripts/test_spi0.py
```

## WS2812 putter (`ws2812put`)

Pushes frames from SharedMemory to SPI:

| SHM | Role |
|-----|------|
| `shm://ws2812` | RGB pixels `(N_LED, 3)` uint8 — **only** pixel source |
| `shm://ws2812dt` | timing `[frame_dt, period]` float |
| `shm://run` | run flag `bool[1]` — set False to stop |

`shm://ws2812stripe` is **not** used.

### LED count for 25 fps (N_LED = 1179)

Encoding `write2812_numpy4`: **4 SPI bytes per RGB byte → 12 SPI bytes per LED**.

| Parameter | Value |
|-----------|--------|
| Target FPS | **25** (frame budget **40 ms**) |
| SPI clock | `int(4/1.05e-6)` = **3 809 523 Hz** (~3.81 MHz) |
| Wire time / LED | `12 × 8 / 3 809 523` ≈ **25.20 µs** |
| Reset / latch | **280 µs** (conservative WS2812B; spec min often ≥50 µs) |
| CPU overhead margin | **10 ms** (numpy encode + SHM + Python loop on Zero 2 W) |
| Available wire time | `40 − 0.28 − 10 = 29.72 ms` |
| **N_LED** | `floor(29.72e-3 / 25.20e-6)` = **1179** |
| SPI payload | `1179 × 12 = 14 148` bytes ≤ **bufsiz 65536** (single `xfer3`, no chunking) |

On AnkerPI01, measured putter work time is ~**33 ms**/frame (wire ≈29.7 ms + encode/overhead ≈3 ms), then sleep to the **40 ms** period → solid 25 fps.

**SHM ownership:** `ws2812put` (systemd) must be the process that *creates* the SHMs. Producers only `attach`. A second process that `create`s the same names and then exits will unlink them (SharedArray), breaking attach for everyone.

Defaults: `N_LED=1179`, `FPS=25` (CLI/env overrideable).

### systemd service

```bash
# install / restart (on Pi)
bash ~/WerbeLEDbox-CountDown/scripts/install_ws2812put_service.sh

sudo systemctl status ws2812put
sudo systemctl stop ws2812put
sudo systemctl start ws2812put
```

Unit: [`../systemd/ws2812put.service`](../systemd/ws2812put.service) — venv Python, `WorkingDirectory` project root, `Restart=on-failure`, user `user` + group `spi`.

Manual run:

```bash
cd ~/WerbeLEDbox-CountDown && source .venv/bin/activate
python ws2812put.py          # defaults N_LED=1179 FPS=25
# or: N_LED=1179 FPS=25 python ws2812put.py
```

Smoke (pattern into SHM while putter runs):

```bash
python scripts/smoke_ws2812put.py --n-led 1179 --seconds 3
```

Pixel-0 color blink (attach-only; black between each color, 1 s/step):

```bash
python scripts/test_pixel0_blink.py
# short check: python scripts/test_pixel0_blink.py --seconds 16
```

## Optimizations applied (Zero 2 W)

| Change | Why |
|--------|-----|
| `gpu_mem=16` | More CPU RAM for Python (~463 MiB total after change) |
| `camera_auto_detect=0` | Headless LED driver workload |
| `display_auto_detect=0` | Headless LED driver workload |
| `arm_boost=1` | Already present — keep |

Backups of boot files: `/boot/firmware/config.txt.bak.*`, `cmdline.txt.bak.*`

## Python development

On the Pi:

```bash
cd ~/WerbeLEDbox-CountDown
source .venv/bin/activate
```

Venv uses `--system-site-packages` so Debian `python3-numpy` / `python3-spidev` are available; **SharedArray** is installed into the venv via pip. Hotel-Anker **spidev 3.6.1** (65536) is preferred in the venv.

Expected stack:

- Python 3.13 (system)
- `numpy` (apt / system site)
- `spidev` 3.6.1 patched (venv)
- `SharedArray` (pip in `.venv`)

Smoke check:

```bash
python - <<'PY'
import numpy as np
import SharedArray as sa
import spidev
print(np.__version__, sa, spidev)
PY
```

## Setup scripts

| Script | Purpose |
|--------|---------|
| [`../scripts/ankerpi01_setup_phase1.sh`](../scripts/ankerpi01_setup_phase1.sh) | SPI on, GPU mem, SSH policy, bufsiz modprobe |
| [`../scripts/ankerpi01_fix_spi_bufsiz.sh`](../scripts/ankerpi01_fix_spi_bufsiz.sh) | Persist bufsiz via cmdline + reload |
| [`../scripts/ankerpi01_setup_phase2.sh`](../scripts/ankerpi01_setup_phase2.sh) | apt upgrade, Python deps, venv, smoke test |
| [`../scripts/install_ws2812put_service.sh`](../scripts/install_ws2812put_service.sh) | Install + enable `ws2812put.service` |
| [`../scripts/install_countdown_pi01_service.sh`](../scripts/install_countdown_pi01_service.sh) | Install + enable countdown producer |
| [`../scripts/countdown_pi01.py`](../scripts/countdown_pi01.py) | Amber progress bar → `shm://ws2812` until Baubeginn |
| [`../scripts/smoke_ws2812put.py`](../scripts/smoke_ws2812put.py) | Write test pattern to `shm://ws2812` |
| [`../scripts/test_pixel0_blink.py`](../scripts/test_pixel0_blink.py) | Cycle pixel 0 R/G/B/C/M/Y/W with black between |

### Countdown producer (LIVE 2026-08-06)

**Live path:** `countdown-waves.service` → `scripts/countdown_waves_64.py --shm --fps 25`  
→ `shm://ws2812` → `ws2812put-pi02.service` → Teensy 8×512 USB (64×64).

Legacy linear strip (`countdown_pi01` / `ws2812put`) is **not** the Flowbox face.

#### Day / night solar fade (dense Richner textile)

Print is very dark by day; night look already worked. Renderer blends:

| | Day (`day_factor→1`) | Night (`day_factor→0`) |
|--|--|--|
| Digits | full white | amber |
| Waves | luminous cyan | navy |
| Liquid glass | bright orange | gold chrome @25% |
| Chrome gain | 100% | 25% |

- Location: Rorschach `47.4789 / 9.4902`, civil twilight fade (−6°…+10° solar elevation)
- Default: `--look auto` (also `COUNTDOWN_LOOK=day|night|auto`)
- Force day test: stop service, run with `--look day`, or set env in unit
- Preview assets: `assets/kendu-64x64/countdown-waves-day*.png` (+ gold = night)

```bash
sudo systemctl status countdown-waves ws2812put-pi02
journalctl -u countdown-waves -f   # elev=…° day_factor=…
```

## Notes / constraints

- Zero 2 W has limited RAM — prefer apt wheels/`python3-numpy` over compiling large packages.
- Large SPI transfers should use chunks ≤ `bufsiz` (65536) or raise further the same way. Current strip (14 148 B) fits in one transfer.
- Keep password auth if other devices need emergency access without keys.
