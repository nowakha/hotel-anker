#!/bin/bash
set -euo pipefail
cd "$HOME/WerbeLEDbox-CountDown"
# shellcheck disable=SC1091
source .venv/bin/activate

# Ensure only the systemd putter owns the SHMs
sudo systemctl restart ws2812put.service
sleep 1
systemctl is-active ws2812put
systemctl is-enabled ws2812put

python - <<'PY'
import SharedArray as sa
a = sa.attach("shm://ws2812")
print("shm shape", a.shape, a.dtype)
assert a.shape == (1179, 3), a.shape
t = sa.attach("shm://ws2812dt")
print("timing", list(t))
r = sa.attach("shm://run")
print("run", bool(r[0]))
print("VERIFY_OK")
PY

journalctl -u ws2812put -n 8 --no-pager
ls -la /dev/shm
