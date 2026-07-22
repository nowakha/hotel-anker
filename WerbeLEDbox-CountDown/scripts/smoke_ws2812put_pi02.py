#!/usr/bin/env python3
"""Write a test pattern into shm://ws2812 (64,64,3) for AnkerPI02 putter."""

from __future__ import annotations

import argparse
import time

import numpy as np
import SharedArray as sa

from layout_64x64_8x512 import FIELD_W, HEIGHT, N_FIELDS, WIDTH

SHM = "shm://ws2812"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--seconds", type=float, default=8.0)
    p.add_argument("--fps", type=float, default=25.0)
    args = p.parse_args()

    try:
        panel = sa.attach(SHM)
    except Exception:
        panel = sa.create(SHM, (HEIGHT, WIDTH, 3), dtype=np.uint8)

    if tuple(panel.shape) != (HEIGHT, WIDTH, 3):
        raise SystemExit(f"bad shm shape {panel.shape}")

    colors = [
        (255, 40, 40),
        (255, 140, 0),
        (240, 220, 40),
        (40, 200, 80),
        (40, 120, 255),
        (160, 60, 220),
        (40, 200, 220),
        (255, 60, 160),
    ]
    period = 1.0 / args.fps if args.fps > 0 else 0.04
    t0 = time.monotonic()
    n = 0
    while time.monotonic() - t0 < args.seconds:
        phase = int((time.monotonic() - t0) * 8) % HEIGHT
        for f in range(N_FIELDS):
            c0 = f * FIELD_W
            r, g, b = colors[f]
            panel[:, c0 : c0 + FIELD_W, 0] = r
            panel[:, c0 : c0 + FIELD_W, 1] = g
            panel[:, c0 : c0 + FIELD_W, 2] = b
            # moving white bar from bottom
            row = (HEIGHT - 1 - phase) % HEIGHT
            panel[row, c0 : c0 + FIELD_W] = (255, 255, 255)
        n += 1
        time.sleep(period)
    print(f"wrote {n} frames to {SHM}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
