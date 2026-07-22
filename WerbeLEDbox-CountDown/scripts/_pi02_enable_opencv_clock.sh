#!/bin/bash
set -uo pipefail
ROOT=/home/user/WerbeLEDbox-CountDown
echo "unmask+install"
echo 12345678 | sudo -S rm -f /etc/systemd/system/fb-clock.service
echo 12345678 | sudo -S cp "$ROOT/systemd/fb_clock_opencv.service" /etc/systemd/system/fb-clock.service
echo 12345678 | sudo -S chmod 644 /etc/systemd/system/fb-clock.service
echo 12345678 | sudo -S systemctl daemon-reload
echo 12345678 | sudo -S systemctl enable fb-clock
echo 12345678 | sudo -S systemctl start fb-clock
sleep 4
echo "enabled=$(systemctl is-enabled fb-clock)"
echo "active=$(systemctl is-active fb-clock)"
ls -la /etc/systemd/system/fb-clock.service
echo 12345678 | sudo -S journalctl -u fb-clock -n 25 --no-pager
pgrep -a -f '/fb_clock_opencv.py' || echo 'no player yet'
echo DONE
