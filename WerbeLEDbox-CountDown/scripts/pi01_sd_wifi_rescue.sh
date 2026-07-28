#!/usr/bin/env bash
# Rescue AnkerPI01 WiFi profiles on mounted rootfs (SD via usbipd/WSL).
# Usage (as root in WSL after partitions mounted at /mnt/pi01-boot /mnt/pi01-root):
#   bash pi01_sd_wifi_rescue.sh
# Or auto-find/mount first:
#   bash pi01_sd_wifi_rescue.sh --auto
#
# Soll: SSID Administration (PSK HeimatSchutz, LAN 192.168.1.x) is PRIMARY.
# HotelAnker profile is kept on disk but autoconnect=false (not preferred).

set -euo pipefail

PSK="HeimatSchutz"
SSID_ADMIN="Administration"
SSID_BAR="HotelAnker"
BOOT=/mnt/pi01-boot
ROOT=/mnt/pi01-root
NM="$ROOT/etc/NetworkManager/system-connections"

die() { echo "ERROR: $*" >&2; exit 1; }

auto_mount() {
  mkdir -p "$BOOT" "$ROOT"
  # Prefer by label
  if ! mountpoint -q "$BOOT"; then
    BOOTDEV=$(blkid -L bootfs 2>/dev/null || true)
    if [[ -z "${BOOTDEV}" ]]; then
      BOOTDEV=$(lsblk -pnro NAME,FSTYPE,SIZE | awk '$2=="vfat" && $3+0<2000000000 {print $1; exit}')
    fi
    [[ -n "${BOOTDEV}" ]] || die "boot partition not found"
    mount -t vfat -o rw,uid=0,gid=0 "$BOOTDEV" "$BOOT"
    echo "mounted boot $BOOTDEV -> $BOOT"
  fi
  if ! mountpoint -q "$ROOT"; then
    ROOTDEV=$(blkid -L rootfs 2>/dev/null || true)
    if [[ -z "${ROOTDEV}" ]]; then
      ROOTDEV=$(lsblk -pnro NAME,FSTYPE,SIZE | awk '$2=="ext4" && $3+0>10000000000 {print $1; exit}')
    fi
    [[ -n "${ROOTDEV}" ]] || die "root partition not found"
    mount -t ext4 -o rw "$ROOTDEV" "$ROOT"
    echo "mounted root $ROOTDEV -> $ROOT"
  fi
}

if [[ "${1:-}" == "--auto" ]]; then
  auto_mount
fi

mountpoint -q "$ROOT" || die "$ROOT not mounted"
[[ -d "$ROOT/etc" ]] || die "no /etc on $ROOT — wrong mount?"

# Confirm host
HOSTF="$ROOT/etc/hostname"
if [[ -f "$HOSTF" ]]; then
  HN=$(tr -d '\n' <"$HOSTF")
  echo "hostname=$HN"
  [[ "$HN" == "AnkerPI01" ]] || die "expected AnkerPI01, got $HN"
fi

mkdir -p "$NM"
TS=$(date +%Y%m%d-%H%M%S)
BACKUP="$ROOT/root/nm-backup-$TS"
mkdir -p "$BACKUP"
cp -a "$NM/." "$BACKUP/" 2>/dev/null || true
echo "NM backup -> $BACKUP"
echo "--- before ---"
ls -la "$NM" || true
for f in "$NM"/*; do
  [[ -f "$f" ]] || continue
  echo "==== $f ===="
  # redact psk
  sed -E 's/(psk=).*/\1***REDACTED***/' "$f" || true
done

# Remove broken / stale connection profiles that fight autoconnect
rm -f "$NM"/Administration.nmconnection \
      "$NM"/Administration \
      "$NM"/HotelAnker.nmconnection \
      "$NM"/HotelAnker \
      "$NM"/HotelAnker_5G.nmconnection \
      "$NM"/netplan-wlan0-HotelAnker.nmconnection \
      "$NM"/netplan-wlan0-* 2>/dev/null || true

# Also clear runtime-only leftovers if somehow persisted
rm -rf "$ROOT/run/NetworkManager/system-connections" 2>/dev/null || true
mkdir -p "$ROOT/run/NetworkManager/system-connections"

write_nm() {
  local path="$1"
  local ssid="$2"
  local prio="$3"
  local autoconnect="$4"
  cat >"$path" <<EOF
[connection]
id=${ssid}
uuid=$(cat /proc/sys/kernel/random/uuid)
type=wifi
interface-name=wlan0
autoconnect=${autoconnect}
autoconnect-priority=${prio}

[wifi]
mode=infrastructure
ssid=${ssid}
# 2 = disable powersave (critical on Pi Zero 2 W)
powersave=2

[wifi-security]
key-mgmt=wpa-psk
psk=${PSK}

[ipv4]
method=auto
dns=1.1.1.1;8.8.8.8;
ignore-auto-dns=true

[ipv6]
method=disabled
EOF
  chmod 600 "$path"
  echo "wrote $path (prio=$prio autoconnect=$autoconnect)"
}

# Primary: Administration (Soll — LAN 192.168.1.x).
# HotelAnker kept on disk for manual `nmcli connection up` only — autoconnect=false
# so the Pi never prefers Bar WiFi over Administration.
write_nm "$NM/Administration.nmconnection" "$SSID_ADMIN" 100 yes
write_nm "$NM/HotelAnker.nmconnection" "$SSID_BAR" 10 no

# Update boot cloud-init network-config: Administration FIRST (intended AP).
# Runtime NetworkManager keyfiles above are authoritative after first boot;
# HotelAnker here is optional secondary for cloud-init only.
if [[ -d "$BOOT" ]] && mountpoint -q "$BOOT" && [[ -f "$BOOT/network-config" ]]; then
  cp -a "$BOOT/network-config" "$BOOT/network-config.bak.$TS"
  cat >"$BOOT/network-config" <<EOF
# cloud-init / netplan seed only. Runtime NM uses Administration (prio 100).
# Administration listed FIRST as the intended AP (LAN 192.168.1.x).
# HotelAnker is optional secondary for cloud-init; NM has autoconnect=false for Bar.
network:
  version: 2
  ethernets:
    eth0:
      dhcp4: true
      optional: true
  wifis:
    wlan0:
      dhcp4: true
      regulatory-domain: "CH"
      access-points:
        "${SSID_ADMIN}":
          password: "${PSK}"
        "${SSID_BAR}":
          password: "${PSK}"
      optional: true
EOF
  echo "updated $BOOT/network-config (Administration FIRST; HotelAnker secondary for cloud-init)"
fi

# Ensure SSH stays enabled
mkdir -p "$ROOT/etc/systemd/system/multi-user.target.wants"
if [[ ! -e "$ROOT/etc/systemd/system/multi-user.target.wants/ssh.service" ]] && \
   [[ ! -e "$ROOT/etc/systemd/system/multi-user.target.wants/ssh.socket" ]]; then
  if [[ -f "$ROOT/lib/systemd/system/ssh.service" ]]; then
    ln -sfn /lib/systemd/system/ssh.service "$ROOT/etc/systemd/system/multi-user.target.wants/ssh.service"
    echo "enabled ssh.service symlink"
  fi
fi

sync
echo "--- after ---"
ls -la "$NM"
for f in "$NM"/*.nmconnection; do
  echo "==== $f ===="
  sed -E 's/(psk=).*/\1***REDACTED***/' "$f"
done

# Strict verify (fail if wrong)
ADMIN_F="$NM/Administration.nmconnection"
BAR_F="$NM/HotelAnker.nmconnection"
grep -q '^autoconnect=true\|^autoconnect=yes' "$ADMIN_F" || die "Administration autoconnect missing/false"
grep -q '^autoconnect-priority=100' "$ADMIN_F" || die "Administration priority not 100"
grep -q "^psk=${PSK}" "$ADMIN_F" || die "Administration PSK mismatch"
grep -q '^powersave=2' "$ADMIN_F" || die "Administration powersave not 2"
grep -q '^interface-name=wlan0' "$ADMIN_F" || die "Administration interface-name missing"
grep -qE '^autoconnect=false|^autoconnect=no' "$BAR_F" || die "HotelAnker must be autoconnect=false"
grep -q "^psk=${PSK}" "$BAR_F" || die "HotelAnker PSK mismatch"
echo "VERIFY OK: Administration autoconnect=yes prio=100 psk=HeimatSchutz; HotelAnker autoconnect=false"

cat >"$ROOT/root/WIFI_RESCUE_$TS.txt" <<EOF
AnkerPI01 SD WiFi rescue $TS
Mistake: migrate_pis_to_administration_wifi.py created Administration then set
HotelAnker autoconnect=false without verifying Admin associated + got 192.168.1.x,
so when Administration failed to associate the Pi had zero WiFi.
Fix written to SD:
  Administration.nmconnection — autoconnect=yes, prio=100, wlan0, powersave=2,
    PSK HeimatSchutz, DNS 1.1.1.1/8.8.8.8
  HotelAnker.nmconnection — kept, autoconnect=false (not preferred; manual only)
  bootfs network-config — Administration listed FIRST; comment that runtime NM uses Admin
EOF

echo "OK rescue complete. sync; umount; usbipd detach; SD back into PI01 + power on."
