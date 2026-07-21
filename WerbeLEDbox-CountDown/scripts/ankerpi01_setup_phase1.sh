#!/usr/bin/env bash
# Hotel Anker / WerbeLEDbox CountDown — AnkerPI01 setup
set -euo pipefail

TS="$(date +%Y%m%d%H%M%S)"
echo "==> Backup boot config ($TS)"
cp -a /boot/firmware/config.txt "/boot/firmware/config.txt.bak.${TS}"
cp -a /boot/firmware/cmdline.txt "/boot/firmware/cmdline.txt.bak.${TS}"

echo "==> Enable SPI (raspi-config)"
raspi-config nonint do_spi 0
echo "SPI status (0=on): $(raspi-config nonint get_spi)"

echo "==> Patch /boot/firmware/config.txt"
python3 - <<'PY'
from pathlib import Path
p = Path('/boot/firmware/config.txt')
text = p.read_text()
text = text.replace('#dtparam=spi=on', 'dtparam=spi=on')
if 'dtparam=spi=on' not in text:
    text += '\ndtparam=spi=on\n'
text = text.replace('camera_auto_detect=1', 'camera_auto_detect=0')
text = text.replace('display_auto_detect=1', 'display_auto_detect=0')
if 'gpu_mem=' not in text:
    block = '\n# --- Hotel Anker WerbeLEDbox ---\ngpu_mem=16\n'
    if '[all]' in text:
        text = text.replace('[all]', '[all]' + block, 1)
    else:
        text += block
p.write_text(text)
print(p.read_text())
PY

echo "==> spidev bufsiz=65536"
cat >/etc/modprobe.d/spidev.conf <<'EOF'
# Hotel Anker WerbeLEDbox CountDown
# Default spidev buffer is often 4096; raise for large LED frame transfers.
options spidev bufsiz=65536
EOF
cat /etc/modprobe.d/spidev.conf

echo "==> SSH: pubkey + password both enabled"
cat >/etc/ssh/sshd_config.d/99-hotel-anker.conf <<'EOF'
# Hotel Anker: key-based login preferred, password login remains available
PubkeyAuthentication yes
PasswordAuthentication yes
KbdInteractiveAuthentication no
EOF
sshd -t
systemctl reload ssh || systemctl reload sshd || true
cat /etc/ssh/sshd_config.d/99-hotel-anker.conf

echo "==> SETUP_PHASE1_OK"
