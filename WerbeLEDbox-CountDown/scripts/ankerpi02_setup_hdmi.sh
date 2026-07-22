#!/bin/bash
# AnkerPI02: force HDMI0 (HDMI-A-1) to 3440x1440@50 for 25 fps content.
# Requires reboot. Safe to re-run.
set -euo pipefail

MODE="${1:-3440x1440@50}"
CONN="${2:-HDMI-A-1}"
CMDLINE=/boot/firmware/cmdline.txt
MARKER="video=${CONN}:${MODE}"

if [[ ! -f "$CMDLINE" ]]; then
  echo "missing $CMDLINE" >&2
  exit 1
fi

tmp="$(mktemp)"
# drop any existing video= for this connector, keep single line
tr -s ' ' '\n' <"$CMDLINE" | sed '/^$/d' | grep -v "^video=${CONN}:" >"$tmp.words" || true
{
  # put video= early (after nothing — prepend)
  echo -n "$MARKER"
  while read -r w; do
    [[ -z "$w" ]] && continue
    echo -n " $w"
  done <"$tmp.words"
  echo
} >"$tmp"

echo "=== new cmdline ==="
cat "$tmp"
sudo cp "$CMDLINE" "${CMDLINE}.bak.$(date +%Y%m%d%H%M%S)"
sudo cp "$tmp" "$CMDLINE"
rm -f "$tmp" "$tmp.words"
# vfat boot partition: flush before reboot or the write can vanish
sync
sync

echo
echo "OK: wrote $MARKER (synced)"
echo "Reboot to apply: sudo reboot"
echo "Verify after boot:"
echo "  cat /sys/class/graphics/fb0/virtual_size"
echo "  cat /sys/class/drm/card1-HDMI-A-1/mode"
echo "  tr ' ' '\\n' </proc/cmdline | grep ^video="
