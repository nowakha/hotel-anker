#!/usr/bin/env bash
set -euo pipefail
lsblk -o NAME,SIZE,FSTYPE,LABEL,MOUNTPOINT
BOOTDEV=$(blkid -L bootfs)
ROOTDEV=$(blkid -L rootfs)
echo "BOOTDEV=$BOOTDEV ROOTDEV=$ROOTDEV"
[[ -n "$BOOTDEV" && -n "$ROOTDEV" ]] || { echo "partitions missing"; exit 1; }
mkdir -p /mnt/pi01-boot /mnt/pi01-root
mountpoint -q /mnt/pi01-boot || mount -t vfat -o rw "$BOOTDEV" /mnt/pi01-boot
mountpoint -q /mnt/pi01-root || mount -t ext4 -o rw "$ROOTDEV" /mnt/pi01-root
echo "hostname=$(tr -d '\n' </mnt/pi01-root/etc/hostname)"
NM=/mnt/pi01-root/etc/NetworkManager/system-connections
echo "=== Administration ==="
grep -E '^(ssid|psk|autoconnect|autoconnect-priority|powersave|interface-name|dns)=' "$NM/Administration.nmconnection"
echo "=== HotelAnker ==="
grep -E '^(ssid|psk|autoconnect|autoconnect-priority)=' "$NM/HotelAnker.nmconnection"
echo "=== network-config ==="
head -n 25 /mnt/pi01-boot/network-config
grep -q '^autoconnect=yes' "$NM/Administration.nmconnection"
grep -q '^autoconnect-priority=100' "$NM/Administration.nmconnection"
grep -q '^psk=HeimatSchutz' "$NM/Administration.nmconnection"
grep -qE '^autoconnect=no|^autoconnect=false' "$NM/HotelAnker.nmconnection"
grep -q '^psk=HeimatSchutz' "$NM/HotelAnker.nmconnection"
echo REVERIFY_OK
sync
sync
umount /mnt/pi01-boot
umount /mnt/pi01-root
echo UMOUNT_OK
