#!/bin/bash
set -euo pipefail
systemctl status ws2812put --no-pager -l || true
echo "---- /dev/shm ----"
ls -la /dev/shm || true
echo "---- process ----"
ps aux | grep -E '[w]s2812put|[p]ython.*ws2812' || true
echo "---- recent journal ----"
journalctl -u ws2812put -n 40 --no-pager || true
echo "---- try run manually briefly ----"
cd "$HOME/WerbeLEDbox-CountDown"
source .venv/bin/activate
timeout 2 python ws2812put.py || true
ls -la /dev/shm || true
