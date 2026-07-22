#!/bin/bash
set -euo pipefail
echo "=== MASK fb-clock ==="
echo 12345678 | sudo -S bash -c '
  systemctl stop fb-clock 2>/dev/null || true
  systemctl disable fb-clock 2>/dev/null || true
  rm -f /etc/systemd/system/fb-clock.service
  ln -sf /dev/null /etc/systemd/system/fb-clock.service
  systemctl daemon-reload
'
pkill -f 'fb_clock' 2>/dev/null || true
pkill -f 'ffmpeg.*st24' 2>/dev/null || true
pkill -f 'ffmpeg.*fbdev' 2>/dev/null || true
sleep 1
echo "enabled=$(systemctl is-enabled fb-clock 2>&1 || true)"
echo "active=$(systemctl is-active fb-clock 2>&1 || true)"
ls -la /etc/systemd/system/fb-clock.service
ps aux | grep -E '[f]b_clock|[f]fmpeg' || echo procs_clean
hostname
uptime
echo "=== MASK_OK ==="
