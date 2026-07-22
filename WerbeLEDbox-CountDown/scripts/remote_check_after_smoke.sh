#!/bin/bash
set -euo pipefail
systemctl status ws2812put --no-pager -l || true
ls -la /dev/shm || true
journalctl -u ws2812put -n 30 --no-pager || true
cd "$HOME/WerbeLEDbox-CountDown"
source .venv/bin/activate
python - <<'PY'
import SharedArray as sa
import os
print("files", os.listdir("/dev/shm"))
for n in ("ws2812", "ws2812dt", "run"):
    try:
        a = sa.attach("shm://" + n)
        print(n, "OK", getattr(a, "shape", None), a.dtype)
    except Exception as e:
        print(n, "FAIL", e)
PY
