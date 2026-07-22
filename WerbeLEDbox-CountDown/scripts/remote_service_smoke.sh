#!/bin/bash
set -euo pipefail
cd "$HOME/WerbeLEDbox-CountDown"
source .venv/bin/activate

sudo systemctl restart ws2812put.service
sleep 1
systemctl is-active ws2812put
ls -la /dev/shm

python scripts/smoke_ws2812put.py --n-led 1179 --seconds 2

python - <<'PY'
import SharedArray as sa
a = sa.attach("shm://ws2812")
t = sa.attach("shm://ws2812dt")
r = sa.attach("shm://run")
print("shape", a.shape)
print("timing", list(t))
print("run", bool(r[0]))
assert a.shape == (1179, 3)
print("SERVICE_SMOKE_OK")
PY

ls -la /dev/shm
systemctl is-active ws2812put
