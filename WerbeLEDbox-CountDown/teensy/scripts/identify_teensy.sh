#!/usr/bin/env bash
# Run on AnkerPI02 — identify Teensy USB / HalfKay mode.
set -euo pipefail

echo "=== USB Teensy ==="
lsusb | grep -iE '16c0|Teensy|Van Ooijen' || true
echo
echo "=== by-id ==="
ls -la /dev/serial/by-id/ 2>/dev/null || echo "(no serial by-id)"
echo
echo "=== sysfs ==="
for d in /sys/bus/usb/devices/*; do
  [[ -f "$d/idVendor" ]] || continue
  grep -qi '^16c0$' "$d/idVendor" 2>/dev/null || continue
  echo "DEV $d"
  echo -n "  idProduct="; cat "$d/idProduct"
  echo -n "  bcdDevice="; cat "$d/bcdDevice" 2>/dev/null || true
  echo -n "  product="; cat "$d/product" 2>/dev/null || true
  echo -n "  manufacturer="; cat "$d/manufacturer" 2>/dev/null || true
  echo -n "  serial="; cat "$d/serial" 2>/dev/null || true
  echo
done

pid="$(lsusb -d 16c0: 2>/dev/null | awk '{print $6}' | head -1 || true)"
case "$pid" in
  16c0:0483) echo "MODE: Teensyduino Serial (running sketch)" ;;
  16c0:0478) echo "MODE: HalfKay bootloader — ready to flash" ;;
  16c0:0486) echo "MODE: Teensy RawHID" ;;
  "") echo "MODE: no Teensy USB seen" ;;
  *) echo "MODE: unknown $pid" ;;
esac
