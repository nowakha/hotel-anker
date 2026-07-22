#!/usr/bin/env python3
"""Paint Hotel Anker boot splash onto /dev/fb0 (RGB565)."""

from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

DEFAULT_RAW = (
    Path(__file__).resolve().parents[1] / "media" / "boot_splash_3440x1440.rgb565"
)


def fb_geom(fb: str = "/dev/fb0") -> tuple[int, int, int]:
    w_s, h_s = Path("/sys/class/graphics/fb0/virtual_size").read_text().strip().split(",")
    stride = int(Path("/sys/class/graphics/fb0/stride").read_text().strip())
    return int(w_s), int(h_s), stride


def paint(raw_path: Path, fb_path: str) -> None:
    w, h, stride = fb_geom(fb_path)
    data = raw_path.read_bytes()
    expect = w * h * 2
    if len(data) != expect:
        raise SystemExit(f"splash size {len(data)} != {w}x{h}*2 ({expect})")
    if stride < w * 2:
        raise SystemExit(f"bad stride {stride}")

    fd = os.open(fb_path, os.O_RDWR)
    try:
        if stride == w * 2:
            os.lseek(fd, 0, os.SEEK_SET)
            os.write(fd, data)
        else:
            row = w * 2
            for y in range(h):
                os.lseek(fd, y * stride, os.SEEK_SET)
                os.write(fd, data[y * row : (y + 1) * row])
    finally:
        os.close(fd)
    print(f"fb_splash: painted {raw_path} → {fb_path} ({w}x{h})", flush=True)


def main() -> int:
    p = argparse.ArgumentParser(description="Show Anker boot splash on framebuffer")
    p.add_argument("--raw", type=Path, default=DEFAULT_RAW)
    p.add_argument("--fb", default="/dev/fb0")
    p.add_argument(
        "--hold",
        action="store_true",
        help="keep process alive (optional; pixels persist without this)",
    )
    args = p.parse_args()
    if not args.raw.is_file():
        raise SystemExit(f"missing splash raw: {args.raw}")
    if not os.access(args.fb, os.W_OK):
        raise SystemExit(f"cannot write {args.fb}")
    paint(args.raw, args.fb)
    if args.hold:
        while True:
            time.sleep(3600)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
