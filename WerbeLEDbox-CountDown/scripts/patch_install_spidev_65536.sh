#!/usr/bin/env bash
# Build and install python-spidev with list/xfer limit raised to 65536.
# Installs into ~/WerbeLEDbox-CountDown/.venv (takes precedence over apt package).
set -euo pipefail

SRC_DIR="${1:-/tmp/py-spidev-hotel-anker}"
VENV="${HOME}/WerbeLEDbox-CountDown/.venv"
LIMIT=65536

rm -rf "$SRC_DIR"
git clone --depth 1 --branch v3.6 https://github.com/doceme/py-spidev.git "$SRC_DIR"
cd "$SRC_DIR"

python3 - <<PY
from pathlib import Path
p = Path("spidev_module.c")
text = p.read_text()

# Keep SPIDEV_MAXPATH for /dev path strings; add dedicated transfer limit.
old = '''#define _VERSION_ "3.6"
#define SPIDEV_MAXPATH 4096

#define BLOCK_SIZE_CONTROL_FILE "/sys/module/spidev/parameters/bufsiz"
// The xfwr3 function attempts to use large blocks if /sys/module/spidev/parameters/bufsiz setting allows it.
// However where we cannot get a value from that file, we fall back to this safe default.
#define XFER3_DEFAULT_BLOCK_SIZE SPIDEV_MAXPATH
// Largest block size for xfer3 - even if /sys/module/spidev/parameters/bufsiz allows bigger
// blocks, we won't go above this value. As I understand, DMA is not used for anything bigger so why bother.
#define XFER3_MAX_BLOCK_SIZE 65535
'''

new = '''#define _VERSION_ "3.6.1"
#define SPIDEV_MAXPATH 4096
/* Hotel Anker: raise python-spidev list/xfer ceiling to match kernel bufsiz. */
#define SPIDEV_MAX_TRANSFER 65536

#define BLOCK_SIZE_CONTROL_FILE "/sys/module/spidev/parameters/bufsiz"
// The xfwr3 function attempts to use large blocks if /sys/module/spidev/parameters/bufsiz setting allows it.
// However where we cannot get a value from that file, we fall back to this safe default.
#define XFER3_DEFAULT_BLOCK_SIZE SPIDEV_MAX_TRANSFER
// Largest block size for xfer3 - match kernel bufsiz target for WerbeLEDbox.
#define XFER3_MAX_BLOCK_SIZE SPIDEV_MAX_TRANSFER
'''

if old not in text:
    raise SystemExit('header block not found — upstream source changed')
text = text.replace(old, new, 1)

# Transfer size checks / buffers used SPIDEV_MAXPATH; point them at SPIDEV_MAX_TRANSFER.
# Do NOT replace path snprintf uses (those stay on SPIDEV_MAXPATH).
replacements = [
    ('\tuint8_t\tbuf[SPIDEV_MAXPATH];', '\tuint8_t\tbuf[SPIDEV_MAX_TRANSFER];'),
    ('\tuint8_t\trxbuf[SPIDEV_MAXPATH];', '\tuint8_t\trxbuf[SPIDEV_MAX_TRANSFER];'),
    ('\t/* read at least 1 byte, no more than SPIDEV_MAXPATH */',
     '\t/* read at least 1 byte, no more than SPIDEV_MAX_TRANSFER */'),
]
for a, b in replacements:
    if a not in text:
        raise SystemExit(f'missing fragment: {a!r}')
    text = text.replace(a, b)

# len > SPIDEV_MAXPATH checks for transfers (not path)
text = text.replace(
    'if (len > SPIDEV_MAXPATH) {\n\t\tsnprintf(wrmsg_text, sizeof (wrmsg_text) - 1, wrmsg_listmax, SPIDEV_MAXPATH);',
    'if (len > SPIDEV_MAX_TRANSFER) {\n\t\tsnprintf(wrmsg_text, sizeof (wrmsg_text) - 1, wrmsg_listmax, SPIDEV_MAX_TRANSFER);',
)
text = text.replace(
    'if (len > SPIDEV_MAXPATH) {\n\t\tsnprintf(wrmsg_text, sizeof(wrmsg_text) - 1, wrmsg_listmax, SPIDEV_MAXPATH);',
    'if (len > SPIDEV_MAX_TRANSFER) {\n\t\tsnprintf(wrmsg_text, sizeof(wrmsg_text) - 1, wrmsg_listmax, SPIDEV_MAX_TRANSFER);',
)

# uint16_t cannot hold 65536 — widen loop/length counters on transfer APIs.
for old_decl, new_decl in [
    ('\tuint16_t\tii, len;', '\tuint32_t\tii, len;'),
    ('\tuint16_t ii, len;', '\tuint32_t ii, len;'),
]:
    text = text.replace(old_decl, new_decl)

# readbytes uses SPIDEV_MAXPATH as max length constant in code body
text = text.replace(
    'if (len > SPIDEV_MAXPATH)\n\t\tlen = SPIDEV_MAXPATH;',
    'if (len > SPIDEV_MAX_TRANSFER)\n\t\tlen = SPIDEV_MAX_TRANSFER;',
)
# alternate formatting
text = text.replace(
    'if (len > SPIDEV_MAXPATH)\n                len = SPIDEV_MAXPATH;',
    'if (len > SPIDEV_MAX_TRANSFER)\n                len = SPIDEV_MAX_TRANSFER;',
)

p.write_text(text)
print('patched spidev_module.c')
# sanity
assert 'SPIDEV_MAX_TRANSFER 65536' in p.read_text()
assert p.read_text().count('SPIDEV_MAX_TRANSFER') >= 5
print('sanity OK')
PY

# Also fix readbytes if pattern differs
python3 - <<'PY'
from pathlib import Path
import re
text = Path('spidev_module.c').read_text()
# catch remaining transfer-limit uses that still reference SPIDEV_MAXPATH near len comparisons
# except path[] declarations
def repl_readbytes(m):
    return m.group(0).replace('SPIDEV_MAXPATH', 'SPIDEV_MAX_TRANSFER')
text2 = re.sub(
    r'if \(len > SPIDEV_MAXPATH\)\s*len = SPIDEV_MAXPATH;',
    'if (len > SPIDEV_MAX_TRANSFER)\n\t\tlen = SPIDEV_MAX_TRANSFER;',
    text,
)
Path('spidev_module.c').write_text(text2)
print('readbytes clamp check done')
PY

grep -n 'SPIDEV_MAX_TRANSFER\|SPIDEV_MAXPATH\|XFER3_MAX\|_tuint32_t\tii\|_tuint16_t\tii' spidev_module.c | head -60

. "$VENV/bin/activate"
python -m pip install --force-reinstall --no-cache-dir .

python - <<'PY'
import spidev, pathlib
print('spidev file', spidev.__file__)
print('version attr', getattr(spidev, '__version__', '?'))
# verify list xfer2 65536 works
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000
spi.mode = 0
n = 65536
payload = list(range(256)) * (n // 256)
resp = spi.xfer2(payload)
assert len(resp) == n
spi.writebytes(payload)
print('xfer2(list) 65536 OK')
print('writebytes(list) 65536 OK')
spi.close()
print('PY_SPIDEV_65536_OK')
PY
