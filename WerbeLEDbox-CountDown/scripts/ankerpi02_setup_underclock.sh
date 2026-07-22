#!/bin/bash
# AnkerPI02: fixed underclock + ignore undervoltage warnings (config.txt).
# Requires reboot. Safe to re-run.
set -euo pipefail

CFG=/boot/firmware/config.txt
MARKER_BEGIN="# --- ankerpi02 underclock begin ---"
MARKER_END="# --- ankerpi02 underclock end ---"

if [[ ! -f "$CFG" ]]; then
  echo "missing $CFG" >&2
  exit 1
fi

tmp="$(mktemp)"
# drop previous block and conflicting turbo/boost lines we manage
awk -v b="$MARKER_BEGIN" -v e="$MARKER_END" '
  $0==b {skip=1; next}
  $0==e {skip=0; next}
  skip {next}
  /^arm_boost=/ {next}
  /^force_turbo=/ {next}
  /^arm_freq=/ {next}
  /^arm_freq_min=/ {next}
  /^gpu_freq=/ {next}
  /^core_freq=/ {next}
  /^core_freq_min=/ {next}
  /^avoid_warnings=/ {next}
  {print}
' "$CFG" >"$tmp"

# Ensure [all] section exists for our knobs
if ! grep -q '^\[all\]' "$tmp"; then
  printf '\n[all]\n' >>"$tmp"
fi

block=$(cat <<'EOF'
# --- ankerpi02 underclock begin ---
# Fixed clocks (no DVFS). Tuned for 860x360 H.264 hw-decode → 3440x1440 fbdev.
# ignore undervoltage UI / turbo inhibit
avoid_warnings=2
arm_boost=0
force_turbo=1
arm_freq=1000
arm_freq_min=1000
gpu_freq=300
core_freq=300
core_freq_min=300
# --- ankerpi02 underclock end ---
EOF
)

# append block after last [all]
awk -v block="$block" '
  BEGIN {done=0}
  /^\[all\]/ {print; if (!done) {print block; done=1; next}}
  {print}
  END {if (!done) {print "[all]"; print block}}
' "$tmp" >"${tmp}.out"

sudo cp "$CFG" "${CFG}.bak.$(date +%Y%m%d%H%M%S)"
sudo cp "${tmp}.out" "$CFG"
sync
sync
rm -f "$tmp" "${tmp}.out"

echo "=== underclock block ==="
awk -v b="$MARKER_BEGIN" -v e="$MARKER_END" '
  $0==b {p=1} p{print} $0==e{p=0}
' "$CFG"
echo
echo "OK: wrote fixed underclock (arm=1000 MHz, gpu/core=300 MHz, avoid_warnings=2)"
echo "Reboot to apply: sudo reboot"
echo "Verify: vcgencmd measure_clock arm; vcgencmd measure_clock core; vcgencmd get_throttled"
