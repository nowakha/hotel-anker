#!/bin/bash
# Switch AnkerPI02 fb-clock to live renderer (no MP4 required).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
UNIT_SRC="${ROOT}/systemd/fb_clock_live.service"
UNIT_DST="/etc/systemd/system/fb-clock.service"

sudo cp "$UNIT_SRC" "$UNIT_DST"
sudo systemctl daemon-reload
sudo systemctl disable --now fb-clock.service 2>/dev/null || true
# Old unit name may differ; enable the live one as fb-clock
sudo systemctl enable fb-clock.service
sudo systemctl restart fb-clock.service
sudo systemctl --no-pager --full status fb-clock.service
echo "install_fb_clock_live_service: done (unit InstalledAs=fb-clock.service)"
