#!/bin/bash
# Install/enable ws2812put.service on AnkerPI01. Run on the Pi as user with sudo.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
UNIT_SRC="${ROOT}/systemd/ws2812put.service"
UNIT_DST="/etc/systemd/system/ws2812put.service"

if [[ ! -f "$UNIT_SRC" ]]; then
  echo "missing unit: $UNIT_SRC" >&2
  exit 1
fi

sudo cp "$UNIT_SRC" "$UNIT_DST"
sudo systemctl daemon-reload
sudo systemctl enable ws2812put.service
sudo systemctl restart ws2812put.service
sudo systemctl --no-pager --full status ws2812put.service
echo "install_ws2812put_service: done"
