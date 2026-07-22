#!/bin/bash
set -euo pipefail
PID=$(systemctl show -p MainPID --value ws2812put)
echo "PID=$PID"
echo "---- unit properties ----"
systemctl show ws2812put -p PrivateTmp,ProtectSystem,ProtectHome,ReadWritePaths,TemporaryFileSystem,MountFlags,RootDirectory --no-pager
echo "---- proc root /dev/shm ----"
sudo ls -la "/proc/$PID/root/dev/shm" || true
echo "---- proc fd (shm-ish) ----"
sudo ls -la "/proc/$PID/fd" | head -50 || true
echo "---- maps grep shm ----"
sudo grep -E 'shm|ws2812|/dev/shm' "/proc/$PID/maps" || true
echo "---- env ----"
sudo tr '\0' '\n' < "/proc/$PID/environ" | grep -E 'N_LED|FPS|SPI' || true
