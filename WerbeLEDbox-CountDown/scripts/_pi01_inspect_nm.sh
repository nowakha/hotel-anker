#!/usr/bin/env bash
set -euo pipefail
mkdir -p /mnt/pi01-boot /mnt/pi01-root
mountpoint -q /mnt/pi01-boot || mount -t vfat -o rw /dev/sde1 /mnt/pi01-boot
mountpoint -q /mnt/pi01-root || mount -t ext4 -o rw /dev/sde2 /mnt/pi01-root
echo "HOST=$(cat /mnt/pi01-root/etc/hostname)"
echo "=== NM dir ==="
ls -la /mnt/pi01-root/etc/NetworkManager/system-connections/
echo "=== NM files (psk redacted) ==="
for f in /mnt/pi01-root/etc/NetworkManager/system-connections/*; do
  [ -f "$f" ] || continue
  echo "---- $f ----"
  sed -E 's/(psk=).*/\1***REDACTED***/' "$f"
done
echo "=== journal hint (last NetworkManager if present) ==="
ls /mnt/pi01-root/var/log/journal 2>/dev/null | head || true
