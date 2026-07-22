#!/bin/bash
# Real /dev/fb0 load test for fb_clock_opencv.py (foreground, easy kill).
set -u
INTERVAL="${1:-10}"
DURATION="${2:-180}"
VIDEO="${3:-media/st24.mov}"
ROOT="${HOME}/WerbeLEDbox-CountDown"
LOG_PLAYER="/tmp/fb_loadtest_player.log"
LOG_THROT="/tmp/fb_loadtest_throttled.log"

cd "$ROOT" || exit 1

echo "=== BEFORE ==="
date -Is
vcgencmd get_throttled
systemctl is-enabled fb-clock.service 2>&1 || true
systemctl is-enabled fb_clock_opencv.service 2>&1 || true
systemctl is-active fb-clock.service 2>&1 || true
systemctl is-active fb_clock_opencv.service 2>&1 || true

pkill -f "fb_clock_opencv.py" 2>/dev/null || true
pkill -f "fb_clock_play.py" 2>/dev/null || true
pkill -f "fb_clock_live.py" 2>/dev/null || true
sleep 1

if [[ ! -f "$VIDEO" ]]; then
  if [[ -f media/clock_24h.mp4 ]]; then
    VIDEO="media/clock_24h.mp4"
  elif [[ -f media/st24.mov ]]; then
    VIDEO="media/st24.mov"
  else
    echo "No video found" >&2
    exit 2
  fi
fi

echo "=== START LOADTEST video=$VIDEO min-interval=$INTERVAL duration=${DURATION}s ==="
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
  --video "$VIDEO" \
  --tz Europe/Zurich \
  --crop-top 386 --crop-bottom 127 --crop-left 0 --crop-right 0 \
  --log-every 1 \
  --min-interval "$INTERVAL" \
  2>&1 | tee "$LOG_PLAYER"
RC=${PIPESTATUS[0]}
set -e

kill "$THPID" 2>/dev/null || true
wait "$THPID" 2>/dev/null || true

echo "=== AFTER ==="
date -Is
vcgencmd get_throttled
echo "PLAYER_RC=$RC"

# Keep autostart off
sudo systemctl stop fb_clock_opencv.service 2>/dev/null || true
sudo systemctl disable fb_clock_opencv.service 2>/dev/null || true
sudo systemctl mask fb-clock.service 2>/dev/null || true
pkill -f "fb_clock_opencv.py" 2>/dev/null || true

echo "enabled fb-clock: $(systemctl is-enabled fb-clock.service 2>&1 || true)"
echo "enabled fb_clock_opencv: $(systemctl is-enabled fb_clock_opencv.service 2>&1 || true)"
echo "=== PLAYER LOG TAIL ==="
tail -n 50 "$LOG_PLAYER" || true
echo "=== THROTTLE LOG ==="
cat "$LOG_THROT" || true
echo "=== DONE ==="
exit 0
