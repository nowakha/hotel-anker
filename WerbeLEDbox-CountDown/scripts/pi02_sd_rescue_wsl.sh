#!/usr/bin/env bash
# Mask fb-clock on a mounted AnkerPI02 rootfs + optionally deploy patched player.
# Run AFTER mounting root (and optionally boot) — see docs/PI02_SD_RESCUE.md
#
# Usage:
#   sudo bash pi02_sd_rescue_wsl.sh /mnt/pi-root [/path/to/fb_clock_play.py]
#
# Does NOT touch cmdline.txt / config.txt.

set -euo pipefail

ROOT="${1:-}"
PLAYER_SRC="${2:-}"

if [[ -z "$ROOT" || ! -d "$ROOT/etc/systemd/system" ]]; then
  echo "Usage: $0 /mnt/pi-root [fb_clock_play.py]" >&2
  echo "Mount the Pi rootfs first (ext4). Do not point at the wrong disk." >&2
  exit 2
fi

SYS="$ROOT/etc/systemd/system"
UNIT="$SYS/fb-clock.service"
WANTS="$SYS/multi-user.target.wants/fb-clock.service"

echo "== mask fb-clock on $ROOT =="

if [[ -f "$UNIT" && ! -L "$UNIT" ]]; then
  mv -v "$UNIT" "$UNIT.DISABLED"
elif [[ -L "$UNIT" ]]; then
  echo "existing unit symlink: $(readlink -f "$UNIT" 2>/dev/null || readlink "$UNIT")"
fi

rm -fv "$WANTS"
ln -sfn /dev/null "$UNIT"
ls -la "$UNIT"
ls -la "$SYS/multi-user.target.wants/" 2>/dev/null | grep -i fb || echo "(no fb-clock in multi-user.wants — OK)"

if [[ -n "$PLAYER_SRC" ]]; then
  if [[ ! -f "$PLAYER_SRC" ]]; then
    echo "player not found: $PLAYER_SRC" >&2
    exit 1
  fi
  DST="$ROOT/home/user/WerbeLEDbox-CountDown/fb_clock_play.py"
  if [[ ! -d "$(dirname "$DST")" ]]; then
    echo "missing on rootfs: $(dirname "$DST")" >&2
    exit 1
  fi
  cp -v "$PLAYER_SRC" "$DST"
  # Best-effort ownership (Raspberry Pi OS user often uid 1000)
  chown 1000:1000 "$DST" 2>/dev/null || true
  echo "== probe_size check =="
  grep -nE 'ffprobe|Never decode|-f null' "$DST" | head -20 || true
  if ! grep -q 'Never decode' "$DST" || ! grep -q 'ffprobe' "$DST"; then
    echo "WARN: deployed file may not be the patched player" >&2
  else
    echo "OK: patched player markers present"
  fi
fi

sync
echo "DONE — umount both partitions, eject SD, reinsert, power on."
echo "Do NOT edit cmdline.txt unless recovering a dead boot (media/cmdline.recovery.txt)."
