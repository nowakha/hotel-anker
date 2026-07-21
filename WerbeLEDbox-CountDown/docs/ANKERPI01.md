# AnkerPI01 — System & Dev Setup

Target machine for **WerbeLEDbox CountDown**.

## Identity

| Field | Value |
|--------|--------|
| Hostname | `AnkerPI01` / `AnkerPI01.local` |
| IP (LAN) | `192.168.8.102` |
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

```powershell
ssh user@192.168.8.102
# or
ssh user@AnkerPI01.local
```

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

Venv uses `--system-site-packages` so Debian `python3-numpy` / `python3-spidev` are available; **SharedArray** is installed into the venv via pip.

Expected stack:

- Python 3.13 (system)
- `numpy` (apt / system site)
- `spidev` (apt / system site)
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

Run on the Pi with sudo after copying to `/tmp`.

## Notes / constraints

- Zero 2 W has limited RAM — prefer apt wheels/`python3-numpy` over compiling large packages.
- Large SPI transfers should use chunks ≤ `bufsiz` (65536) or raise further the same way.
- Keep password auth if other devices need emergency access without keys.
