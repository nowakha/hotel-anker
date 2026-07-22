#!/bin/bash
# Foreground max-fps live test (vf860 + hwaccel drm). Leaves systemd masked.
set -u
DURATION="${1:-150}"
ROOT="${HOME}/WerbeLEDbox-CountDown"
LOG_PLAYER="/tmp/fb_maxfps_player.log"
LOG_THROT="/tmp/fb_maxfps_throttled.log"

cd "$ROOT" || exit 1
echo "=== BEFORE ==="
date -Is
vcgencmd get_throttled
echo "fb-clock=$(systemctl is-enabled fb-clock.service 2>&1 || true)"
echo "fb_clock_opencv=$(systemctl is-enabled fb_clock_opencv.service 2>&1 || true)"

: > "$LOG_THROT"
(
  while true; do
    echo "$(date -Is) throttled=$(vcgencmd get_throttled) load=$(cut -d' ' -f1-3 /proc/loadavg)" >> "$LOG_THROT"
    sleep 5
  done
) &
THPID=$!

set +e
timeout "$DURATION" python3 fb_clock_opencv.py \
  --video media/st24.mov \
  --tz Europe/Zurich \
  --crop-top 386 --crop-bottom 127 --crop-left 0 --crop-right 0 \
  --pipeline vf860 --hwaccel drm \
  --log-every 1 --min-interval 0 \
  2>&1 | tee "$LOG_PLAYER"
RC=${PIPESTATUS[0]}
set -e

kill "$THPID" 2>/dev/null || true
wait "$THPID" 2>/dev/null || true

echo "=== AFTER ==="
date -Is
vcgencmd get_throttled
echo "PLAYER_RC=$RC"
echo "enabled fb-clock: $(systemctl is-enabled fb-clock.service 2>&1 || true)"
echo "enabled fb_clock_opencv: $(systemctl is-enabled fb_clock_opencv.service 2>&1 || true)"
echo "=== THROTTLE LOG ==="
cat "$LOG_THROT"
echo "=== DONE ==="
exit 0
