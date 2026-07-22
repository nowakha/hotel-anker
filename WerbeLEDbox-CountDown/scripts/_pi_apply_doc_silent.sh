#!/bin/bash
# Apply documented silent boot + safe splash, then reboot.
set -euo pipefail
ROOT=/home/user/WerbeLEDbox-CountDown

python3 - <<'PY'
from pathlib import Path
root = Path("/home/user/WerbeLEDbox-CountDown")
pairs = [
    ("/tmp/fb_splash.service", root / "systemd" / "fb_splash.service"),
    ("/tmp/ankerpi02_setup_silent_boot.sh", root / "scripts" / "ankerpi02_setup_silent_boot.sh"),
]
for s, d in pairs:
    d.write_bytes(Path(s).read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b""))
    print("wrote", d)
raw = Path("/tmp/boot_splash_3440x1440.rgb565")
if raw.is_file():
    dst = root / "media" / "boot_splash_3440x1440.rgb565"
    dst.write_bytes(raw.read_bytes())
    print("copied splash", dst.stat().st_size)
PY

chmod +x "$ROOT/scripts/ankerpi02_setup_silent_boot.sh"

# Purge any dangerous splash wiring first
sudo systemctl stop fb-splash.service 2>/dev/null || true
sudo systemctl disable fb-splash.service 2>/dev/null || true
sudo rm -f /etc/systemd/system/sysinit.target.wants/fb-splash.service
sudo rm -f /etc/systemd/system/multi-user.target.wants/fb-splash.service

# Apply silent boot (installs safe splash unit + cmdline tty3)
bash "$ROOT/scripts/ankerpi02_setup_silent_boot.sh"

# Hard guarantee: never sysinit
sudo rm -f /etc/systemd/system/sysinit.target.wants/fb-splash.service
sudo systemctl daemon-reload

echo "=== VERIFY ==="
echo -n "cmdline: "; cat /boot/firmware/cmdline.txt
echo -n "disable_splash: "; grep '^disable_splash' /boot/firmware/config.txt || echo missing
echo -n "sysinit want: "; ls /etc/systemd/system/sysinit.target.wants/fb-splash.service 2>&1 || echo none
echo -n "multi-user want: "; ls /etc/systemd/system/multi-user.target.wants/fb-splash.service
echo "--- unit ---"
grep -E 'WantedBy|After=|udev|sysinit|ExecStart' /etc/systemd/system/fb-splash.service

# Paint once now (fb ready) so we know asset works before reboot
python3 "$ROOT/scripts/fb_show_splash.py" || true

sync
echo REBOOT
sudo reboot
