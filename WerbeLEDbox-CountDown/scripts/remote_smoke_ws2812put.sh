#!/bin/bash
# Smoke-test ws2812put on AnkerPI01 (run on the Pi).
set -euo pipefail
cd "$HOME/WerbeLEDbox-CountDown"
# shellcheck disable=SC1091
source .venv/bin/activate

chmod +x scripts/install_ws2812put_service.sh scripts/smoke_ws2812put.py || true

echo "== import check =="
python -c "import ws2812, ws2812put, spidev, SharedArray, numpy; print('imports ok')"

echo "== start putter (background) =="
# Do not delete SHMs if a service already holds them; only clear when starting a fresh manual putter
python - <<'PY'
import SharedArray as sa
# Best-effort cleanup of orphan names (ignore errors)
for name in ("ws2812", "ws2812dt", "ws2812stripe", "run"):
    try:
        sa.delete(name)
        print("deleted", name)
    except Exception:
        pass
PY

# Stop systemd putter for exclusive smoke if present
sudo systemctl stop ws2812put.service 2>/dev/null || true
sleep 0.5

python ws2812put.py --n-led 1179 --fps 25 >/tmp/ws2812put-smoke.log 2>&1 &
PUT_PID=$!
sleep 1
if ! kill -0 "$PUT_PID" 2>/dev/null; then
  echo "putter failed to start:" >&2
  cat /tmp/ws2812put-smoke.log >&2
  exit 1
fi

echo "== smoke pattern =="
python scripts/smoke_ws2812put.py --n-led 1179 --seconds 3

echo "== stop putter =="
kill -TERM "$PUT_PID" || true
wait "$PUT_PID" 2>/dev/null || true
sleep 0.5
echo "putter log:"
cat /tmp/ws2812put-smoke.log || true
echo "SMOKE_OK"
# Leave service stopped; install script will start it
