#!/bin/bash
# Install AnkerPI02 boot services: LED putter + countdown
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
UNIT_DIR=/etc/systemd/system

sudo cp "$ROOT/systemd/ws2812put_pi02.service" "$UNIT_DIR/ws2812put-pi02.service"
sudo cp "$ROOT/systemd/countdown_waves.service" "$UNIT_DIR/countdown-waves.service"
sudo systemctl daemon-reload
sudo systemctl enable ws2812put-pi02.service countdown-waves.service

# Stop ad-hoc processes before starting units
pkill -f 'ws2812put_pi02.py' 2>/dev/null || true
pkill -f 'countdown_waves_64.py' 2>/dev/null || true
sleep 1

sudo systemctl restart ws2812put-pi02.service
sleep 2
sudo systemctl restart countdown-waves.service

echo "=== status ==="
systemctl --no-pager --full status ws2812put-pi02.service countdown-waves.service || true
echo
systemctl is-enabled ws2812put-pi02.service countdown-waves.service
echo "OK: enabled at boot"
