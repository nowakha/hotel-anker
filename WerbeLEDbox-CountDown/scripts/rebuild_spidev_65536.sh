#!/usr/bin/env bash
set -euo pipefail
cd /tmp/py-spidev-hotel-anker

python3 <<'PY'
from pathlib import Path

p = Path("spidev_module.c")
t = p.read_text()
t = t.replace('#define _VERSION_ "3.6-hotel-anker-65536"', '#define _VERSION_ "3.6.1"')
t = t.replace("#define _VERSION_ \"3.6-hotel-anker-65536\"", '#define _VERSION_ "3.6.1"')
if '_VERSION_ "3.6.1"' not in t and '_VERSION_ "3.6"' in t:
    # already ok or still stock after failed rename
    pass
t = t.replace("\tuint16_t\tii, len;", "\tuint32_t\tii, len;")
t = t.replace("\tuint16_t ii, len;", "\tuint32_t ii, len;")
# ensure transfer define present
if "SPIDEV_MAX_TRANSFER" not in t:
    raise SystemExit("SPIDEV_MAX_TRANSFER missing — rerun full patch")
p.write_text(t)

sp = Path("setup.py")
s = sp.read_text()
s = s.replace('version="3.6"', 'version="3.6.1"')
s = s.replace("version='3.6'", "version='3.6.1'")
sp.write_text(s)

print("VERSION:", [ln for ln in t.splitlines() if "_VERSION_" in ln][:2])
print("uint16 ii left:", t.count("uint16_t\tii, len") + t.count("uint16_t ii, len"))
print("uint32 ii:", t.count("uint32_t\tii, len") + t.count("uint32_t ii, len"))
PY

source "$HOME/WerbeLEDbox-CountDown/.venv/bin/activate"
pip install -q setuptools wheel
pip install --force-reinstall --no-cache-dir --no-build-isolation .

python <<'PY'
import spidev
print("file", spidev.__file__)
print("ver", getattr(spidev, "__version__", "?"))
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1_000_000
spi.mode = 0
n = 65536
payload = list(range(256)) * (n // 256)
resp = spi.xfer2(payload)
assert len(resp) == n, len(resp)
spi.writebytes(payload)
print("xfer2(list)/writebytes(list) 65536 OK")
spi.close()
print("PY_SPIDEV_65536_OK")
PY
