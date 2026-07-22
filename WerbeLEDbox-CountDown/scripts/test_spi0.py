#!/usr/bin/env python3
"""SPI0 smoke test + spidev buffer verification for AnkerPI01.

Requires patched python-spidev (>=3.6.1 hotel-anker build) with
SPIDEV_MAX_TRANSFER=65536, matching kernel spidev.bufsiz.
"""
from __future__ import annotations

import array
import sys
from pathlib import Path

import numpy as np
import spidev

BUFSIZ_PATH = Path("/sys/module/spidev/parameters/bufsiz")


def ok(label: str) -> None:
    print(f"{label} -> OK")


def fail(label: str, exc: BaseException) -> None:
    print(f"{label} -> FAIL {type(exc).__name__}: {exc}")


def main() -> int:
    sysfs_buf = int(BUFSIZ_PATH.read_text().strip())
    print(f"sysfs spidev.bufsiz = {sysfs_buf}")
    print(f"spidev module = {spidev.__file__}")
    print(f"spidev version = {getattr(spidev, '__version__', '?')}")
    if sysfs_buf < 65536:
        print(f"FAIL: bufsiz {sysfs_buf} < 65536", file=sys.stderr)
        return 1

    spi = spidev.SpiDev()
    spi.open(0, 0)
    spi.max_speed_hz = 1_000_000
    spi.mode = 0
    spi.bits_per_word = 8
    print(
        f"opened /dev/spidev0.0 mode={spi.mode} "
        f"speed={spi.max_speed_hz} bits={spi.bits_per_word}"
    )

    errors = 0
    n = 65536
    payload = bytes((i * 17) & 0xFF for i in range(n))
    arr = array.array("B", payload)
    np_buf = np.frombuffer(payload, dtype=np.uint8).copy()
    payload_list = list(payload)

    checks = [
        ("xfer2 list 4096", lambda: spi.xfer2(payload_list[:4096])),
        ("xfer2 list 65536", lambda: spi.xfer2(payload_list)),
        ("writebytes list 65536", lambda: spi.writebytes(payload_list)),
        ("writebytes2 bytes 65536", lambda: spi.writebytes2(payload)),
        ("writebytes2 array 65536", lambda: spi.writebytes2(arr)),
        ("writebytes2 numpy 65536", lambda: spi.writebytes2(np_buf)),
        ("readbytes 65536", lambda: spi.readbytes(n)),
        ("xfer3 bytes 65536", lambda: spi.xfer3(payload)),
        ("xfer3 array 65536", lambda: spi.xfer3(arr)),
    ]
    for label, fn in checks:
        try:
            fn()
            ok(label)
        except Exception as exc:  # noqa: BLE001
            fail(label, exc)
            errors += 1

    spi1 = spidev.SpiDev()
    try:
        spi1.open(0, 1)
        ok("opened /dev/spidev0.1")
    except Exception as exc:  # noqa: BLE001
        fail("opened /dev/spidev0.1", exc)
        errors += 1
    finally:
        spi1.close()
        spi.close()

    print("---")
    print(f"BUFFER_VERIFY sysfs={sysfs_buf} python_spidev={'OK' if errors == 0 else 'FAIL'}")
    if errors:
        print(f"SPI0_PYTHON_TEST_FAIL errors={errors}")
        return 1
    print("SPI0_PYTHON_TEST_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
