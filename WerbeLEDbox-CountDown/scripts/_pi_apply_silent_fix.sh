#!/bin/bash
set -euo pipefail
ROOT=/home/user/WerbeLEDbox-CountDown
python3 - <<'PY'
from pathlib import Path
pairs = [
    ("/tmp/fb_splash.service", "/home/user/WerbeLEDbox-CountDown/systemd/fb_splash.service"),
    ("/tmp/ankerpi02_setup_silent_boot.sh", "/home/user/WerbeLEDbox-CountDown/scripts/ankerpi02_setup_silent_boot.sh"),
]
for s, d in pairs:
    Path(d).write_bytes(Path(s).read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b""))
    print("wrote", d)
PY
chmod +x "$ROOT/scripts/ankerpi02_setup_silent_boot.sh"
bash "$ROOT/scripts/ankerpi02_setup_silent_boot.sh"
echo "=== wants ==="
ls -la /etc/systemd/system/sysinit.target.wants/fb-splash.service 2>&1 || echo "good: not in sysinit"
ls -la /etc/systemd/system/multi-user.target.wants/fb-splash.service
systemctl cat fb-splash.service | head -25
sync
echo REBOOT
sudo reboot
