#!/bin/bash
# Disable AnkerPI02 LED/Teensy services (lightbox moved to AnkerPI01).
set -euo pipefail

for u in ws2812put-pi02.service countdown-waves.service; do
  sudo systemctl stop "$u" 2>/dev/null || true
  sudo systemctl disable "$u" 2>/dev/null || true
done
sudo systemctl daemon-reload
pkill -f 'ws2812put_pi02.py' 2>/dev/null || true
pkill -f 'countdown_waves_64.py' 2>/dev/null || true
echo "OK: LED services stopped/disabled on AnkerPI02"
systemctl is-enabled ws2812put-pi02 countdown-waves 2>&1 || true
