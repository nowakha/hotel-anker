#!/bin/bash
# 1) Fix fb-splash (no sysinit, no udev-settle)
# 2) Apply silent boot cmdline/config
# 3) Reboot
set -euo pipefail
ROOT=/home/user/WerbeLEDbox-CountDown

python3 - <<'PY'
from pathlib import Path
for s, d in [
    ("/tmp/fb_splash.service", f"{Path('/home/user/WerbeLEDbox-CountDown')}/systemd/fb_splash.service"),
    ("/tmp/ankerpi02_setup_silent_boot.sh", f"{Path('/home/user/WerbeLEDbox-CountDown')}/scripts/ankerpi02_setup_silent_boot.sh"),
]:
    Path(d).write_bytes(Path(s).read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b""))
    print("wrote", d)
PY

# Tear down any bad splash wiring first
sudo systemctl stop fb-splash.service 2>/dev/null || true
sudo systemctl disable fb-splash.service 2>/dev/null || true
sudo rm -f /etc/systemd/system/sysinit.target.wants/fb-splash.service
sudo rm -f /etc/systemd/system/multi-user.target.wants/fb-splash.service
sudo cp "$ROOT/systemd/fb_splash.service" /etc/systemd/system/fb-splash.service
# strip CR if any
sudo sed -i 's/\r$//' /etc/systemd/system/fb-splash.service

sudo systemctl daemon-reload
sudo systemctl enable fb-splash.service
sudo systemctl start fb-splash.service
echo "=== splash unit ==="
systemctl cat fb-splash.service
echo "=== wants ==="
ls /etc/systemd/system/sysinit.target.wants/fb-splash.service 2>&1 || echo "OK: not in sysinit"
ls /etc/systemd/system/multi-user.target.wants/fb-splash.service
grep -E 'udev-settle|sysinit|WantedBy' /etc/systemd/system/fb-splash.service

# Silent boot (cmdline/config) — splash already safe
bash "$ROOT/scripts/ankerpi02_setup_silent_boot.sh"

# Final safety: splash must not be in sysinit
sudo rm -f /etc/systemd/system/sysinit.target.wants/fb-splash.service
sudo systemctl daemon-reload

echo "=== final cmdline ==="
cat /boot/firmware/cmdline.txt
echo "=== final splash wants ==="
ls /etc/systemd/system/sysinit.target.wants/fb-splash.service 2>&1 || echo "OK: not in sysinit"
sync
echo REBOOT
sudo reboot
