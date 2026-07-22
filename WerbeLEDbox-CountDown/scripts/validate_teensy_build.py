#!/usr/bin/env python3
"""Offline Teensy firmware validation (build artifacts + source sanity).

Does not flash hardware. For live flash use:
  pwsh -File teensy/scripts/flash_from_pi02.ps1
"""

from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEX_DIR = ROOT / "teensy" / "hex"
SRC = ROOT / "teensy" / "anker_pixel_pusher" / "src" / "main.cpp"

REQUIRED = {
    "firmware_teensy32.hex": 10_000,
    "firmware_teensy40.hex": 10_000,
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def main() -> int:
    src = SRC.read_text(encoding="utf-8", errors="replace")
    checks = [
        ("ANKR magic", "WAIT_MAGIC" in src and "hdr[1] != 'N'" in src),
        ("OctoWS2811", "OctoWS2811" in src),
        ("N_LED 512", "N_LED = 512" in src),
        ("N_LINES 8", "N_LINES = 8" in src),
        ("boot banner", "anker-teensy boot" in src),
    ]
    ok = True
    print("=== source ===")
    for name, passed in checks:
        print(f"  [{'OK' if passed else 'FAIL'}] {name}")
        ok = ok and passed

    print("=== hex artifacts ===")
    for name, min_size in REQUIRED.items():
        path = HEX_DIR / name
        if not path.is_file():
            print(f"  [FAIL] missing {path}")
            ok = False
            continue
        size = path.stat().st_size
        digest = sha256(path)
        passed = size >= min_size and path.read_text(errors="ignore").lstrip().startswith(":")
        print(f"  [{'OK' if passed else 'FAIL'}] {name} bytes={size} sha256={digest[:16]}…")
        ok = ok and passed

    print("=== result ===", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
