#!/usr/bin/env bash
# Hotel Anker / WerbeLEDbox CountDown — packages + verify after reboot
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

echo "==> apt update/upgrade"
apt-get update -y
apt-get -y full-upgrade
apt-get -y autoremove --purge
apt-get -y autoclean

echo "==> Install Python / SPI / build deps"
apt-get install -y \
  python3-pip \
  python3-venv \
  python3-dev \
  python3-numpy \
  python3-spidev \
  build-essential \
  pkg-config \
  git

echo "==> Create project venv"
install -d -o user -g user /home/user/WerbeLEDbox-CountDown
sudo -u user bash <<'EOS'
set -euo pipefail
cd /home/user/WerbeLEDbox-CountDown
python3 -m venv --system-site-packages .venv
. .venv/bin/activate
python -m pip install --upgrade pip
# SharedArray needs POSIX shared memory + numpy
python -m pip install SharedArray
python - <<'PY'
import numpy as np
import SharedArray as sa
import spidev
print('numpy', np.__version__)
print('SharedArray OK', sa)
print('spidev OK', spidev)
# smoke SharedArray create/delete
name = 'shm://hotel_anker_smoke'
try:
    sa.delete(name)
except Exception:
    pass
arr = sa.create(name, 1024, dtype=np.uint8)
arr[:] = 7
assert arr[0] == 7
sa.delete(name)
print('SharedArray smoke OK')
PY
EOS

echo "==> Verify SPI devices / buffer"
ls -la /dev/spidev* || echo 'NO_SPIDEV_YET'
if [[ -f /sys/module/spidev/parameters/bufsiz ]]; then
  echo -n 'spidev bufsiz='; cat /sys/module/spidev/parameters/bufsiz; echo
else
  echo 'spidev module param file missing (module not loaded?)'
  modprobe spidev || true
  sleep 1
  if [[ -f /sys/module/spidev/parameters/bufsiz ]]; then
    echo -n 'spidev bufsiz='; cat /sys/module/spidev/parameters/bufsiz; echo
  fi
fi
lsmod | grep -i spi || true
dmesg | grep -i spi | tail -20 || true

echo "==> Memory after setup"
free -h
vcgencmd get_mem arm; vcgencmd get_mem gpu

echo "==> SETUP_PHASE2_OK"
