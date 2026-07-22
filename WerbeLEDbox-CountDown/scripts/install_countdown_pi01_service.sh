#!/bin/bash
# Install/enable countdown_pi01.service on AnkerPI01 (after ws2812put).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
UNIT_SRC="${ROOT}/systemd/countdown_pi01.service"
UNIT_DST="/etc/systemd/system/countdown_pi01.service"

if [[ ! -f "$UNIT_SRC" ]]; then
  echo "missing unit: $UNIT_SRC" >&2
  exit 1
fi

sudo cp "$UNIT_SRC" "$UNIT_DST"
sudo systemctl daemon-reload
sudo systemctl enable countdown_pi01.service
sudo systemctl restart countdown_pi01.service
sudo systemctl --no-pager --full status countdown_pi01.service
echo "install_countdown_pi01_service: done"
