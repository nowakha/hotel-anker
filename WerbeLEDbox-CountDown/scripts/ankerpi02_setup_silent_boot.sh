#!/bin/bash
# AnkerPI02 silent HDMI boot (Pi OS / KMS).
#
# Per Raspberry Pi docs + common Bookworm practice:
#   - disable_splash=1 in config.txt          (no rainbow)
#   - console=tty3 (not remove console!)     (kernel msgs off HDMI)
#   - quiet logo.nologo vt.global_cursor_default=0 loglevel=3
#   - fb-splash ONLY on multi-user, after /dev/fb0 exists
# Never: KMS rotate=, underclock here, sysinit splash, udev-settle.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CFG=/boot/firmware/config.txt
CMDLINE=/boot/firmware/cmdline.txt

if [[ ! -f "$CFG" || ! -f "$CMDLINE" ]]; then
  echo "missing boot firmware files" >&2
  exit 1
fi

# --- config.txt: rainbow off ---
if ! grep -q '^disable_splash=1' "$CFG"; then
  printf '\ndisable_splash=1\n' | sudo tee -a "$CFG" >/dev/null
fi

# --- cmdline: silent on HDMI, keep a real console on tty3 ---
tmp="$(mktemp)"
tr -s ' ' '\n' <"$CMDLINE" | sed '/^$/d' \
  | grep -v '^console=tty1$' \
  | grep -v '^console=tty3$' \
  | grep -v '^quiet$' \
  | grep -v '^splash$' \
  | grep -v '^logo.nologo$' \
  | grep -v '^vt.global_cursor_default=' \
  | grep -v '^loglevel=' \
  | grep -v '^video=' \
  >"$tmp.words" || true

{
  # serial debug + unused VT for kernel console (keeps init happy; not on HDMI fbcon focus)
  echo -n "console=serial0,115200 console=tty3"
  echo -n " quiet loglevel=3 logo.nologo vt.global_cursor_default=0"
  while read -r w; do
    [[ -z "$w" ]] && continue
    [[ "$w" == console=serial0,* || "$w" == console=ttyAMA0,* ]] && continue
    echo -n " $w"
  done <"$tmp.words"
  echo
} >"$tmp"

sudo cp "$CMDLINE" "${CMDLINE}.bak.$(date +%Y%m%d%H%M%S)"
sudo cp "$tmp" "$CMDLINE"
sync; sync
rm -f "$tmp" "$tmp.words"

echo "=== cmdline ==="
cat "$CMDLINE"

# --- getty: no login prompt on HDMI tty1; optional getty on tty3 unused ---
sudo systemctl mask getty@tty1.service 2>/dev/null || true
sudo systemctl stop getty@tty1.service 2>/dev/null || true

# --- splash unit: safe install ---
sudo systemctl disable fb-splash.service 2>/dev/null || true
sudo rm -f /etc/systemd/system/sysinit.target.wants/fb-splash.service
sudo rm -f /etc/systemd/system/multi-user.target.wants/fb-splash.service
sed 's/\r$//' "$ROOT/systemd/fb_splash.service" | sudo tee /etc/systemd/system/fb-splash.service >/dev/null
sudo systemctl daemon-reload
sudo systemctl enable fb-splash.service
sudo rm -f /etc/systemd/system/sysinit.target.wants/fb-splash.service

if [[ -f /etc/systemd/system/fb-clock.service ]]; then
  if ! grep -q '^After=.*fb-splash.service' /etc/systemd/system/fb-clock.service; then
    sudo sed -i '/^\[Unit\]/a After=fb-splash.service' /etc/systemd/system/fb-clock.service
  fi
  sudo systemctl daemon-reload
fi

echo
echo "OK: silent boot configured (console=tty3, disable_splash, safe fb-splash)"
echo "Reboot: sudo reboot"
