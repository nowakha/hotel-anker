#!/bin/bash
# Install / enable AnkerPI02 24h clock framebuffer service.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
UNIT_SRC="$ROOT/systemd/fb_clock.service"
UNIT_DST=/etc/systemd/system/fb-clock.service
MEDIA_DIR="$ROOT/media"
PLACEHOLDER="$MEDIA_DIR/clock_24h.mp4"

mkdir -p "$MEDIA_DIR"

if [[ ! -f "$PLACEHOLDER" ]]; then
  cat <<EOF
NOTE: Video not present yet:
  $PLACEHOLDER

Place your exact 24h MP4 there (starts at 00:00:00, duration 86400s).
Service will wait for the file / restart when it appears.
EOF
fi

# LF-safe copy of unit
sed 's/\r$//' "$UNIT_SRC" | sudo tee "$UNIT_DST" >/dev/null
sudo systemctl daemon-reload
sudo systemctl enable fb-clock.service

# Ensure NTP
sudo timedatectl set-ntp true || true
sudo systemctl enable --now systemd-timesyncd.service || true

if [[ -f "$PLACEHOLDER" ]]; then
  sudo systemctl restart fb-clock.service
else
  # enable only — starts on boot; manual start waits for file inside player
  sudo systemctl stop fb-clock.service 2>/dev/null || true
  echo "Service enabled; start later with: sudo systemctl start fb-clock"
fi

echo "=== status ==="
systemctl --no-pager --full status fb-clock.service || true
timedatectl status || true
echo "OK: fb-clock.service installed"
