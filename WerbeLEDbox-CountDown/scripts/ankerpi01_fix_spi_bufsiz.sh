#!/usr/bin/env bash
set -euo pipefail

echo "==> Current bufsiz: $(cat /sys/module/spidev/parameters/bufsiz 2>/dev/null || echo missing)"
echo "==> modprobe.d:"
cat /etc/modprobe.d/spidev.conf

echo "==> Ensure modprobe options file (clean rewrite)"
cat >/etc/modprobe.d/spidev.conf <<'EOF'
options spidev bufsiz=65536
EOF

echo "==> Add kernel cmdline spidev.bufsiz=65536"
python3 - <<'PY'
from pathlib import Path
p = Path('/boot/firmware/cmdline.txt')
line = p.read_text().strip()
if 'spidev.bufsiz=' not in line:
    line = line + ' spidev.bufsiz=65536'
    p.write_text(line + '\n')
print(p.read_text())
PY

echo "==> Try live reload"
if rmmod spidev 2>/dev/null; then
  modprobe spidev bufsiz=65536
  echo "reloaded with bufsiz=$(cat /sys/module/spidev/parameters/bufsiz)"
else
  echo "rmmod failed (in use?) — reboot required for cmdline/modprobe"
fi

echo "==> SPI_BUFSIZ_FIX_DONE"
