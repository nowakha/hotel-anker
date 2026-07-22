#!/usr/bin/env python3
"""Probe USB CDC board on Pico (MicroPython / other)."""

from __future__ import annotations

import sys
import time

import serial


def read_all(ser: serial.Serial, settle: float = 0.35) -> str:
    time.sleep(settle)
    chunks: list[bytes] = []
    while True:
        chunk = ser.read(4096)
        if not chunk:
            break
        chunks.append(chunk)
    return b"".join(chunks).decode("utf-8", "replace")


def main() -> int:
    port = sys.argv[1] if len(sys.argv) > 1 else "COM9"
    ser = serial.Serial(port, 115200, timeout=0.25, write_timeout=2)
    try:
        # Wake / interrupt soft-lock
        for _ in range(3):
            ser.write(b"\x03")
            time.sleep(0.05)
        ser.write(b"\x02")  # normal REPL
        print("=== AFTER INTERRUPT ===")
        print(read_all(ser, 0.4))

        # Soft reboot to get banner
        ser.write(b"\x04")  # Ctrl-D soft reboot (MicroPython)
        print("=== AFTER SOFT REBOOT ===")
        print(read_all(ser, 1.2))

        # Simple one-liners over normal REPL
        probes = [
            "import sys; print('VERSION', sys.version)\r\n",
            "import os; print('UNAME', os.uname())\r\n",
            "print('PLATFORM', sys.platform)\r\n",
            "import machine; print('UID', machine.unique_id().hex()); print('FREQ', machine.freq())\r\n",
            (
                "mods=[]\r\n"
                "for m in ('network','rp2','neopixel','bluetooth'):\r\n"
                " try:\r\n"
                "  __import__(m); mods.append(m+':yes')\r\n"
                " except Exception:\r\n"
                "  mods.append(m+':no')\r\n"
                "print('MODS', ' '.join(mods))\r\n"
            ),
            (
                "try:\r\n"
                " import network\r\n"
                " print('HAS_WLAN', hasattr(network,'WLAN'))\r\n"
                "except Exception as e:\r\n"
                " print('NETERR', e)\r\n"
            ),
        ]
        print("=== PROBES ===")
        for p in probes:
            ser.write(p.encode())
            print(read_all(ser, 0.5))
        return 0
    finally:
        ser.close()


if __name__ == "__main__":
    raise SystemExit(main())
