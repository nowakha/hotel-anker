#!/usr/bin/env python3
"""Smoke-test: write a short pattern into shm://ws2812 while ws2812put is running.

Attach-only — the putter (systemd) must already own the SHMs.
Creating from this script would steal ownership and unlink on exit.
"""

from __future__ import annotations

import argparse
import sys
import time

import numpy as np
import SharedArray as sa


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--n-led", type=int, default=1179)
    p.add_argument("--seconds", type=float, default=3.0)
    args = p.parse_args()

    try:
        pixels = sa.attach("shm://ws2812")
        run = sa.attach("shm://run")
    except Exception as e:
        print(
            "smoke_ws2812put: cannot attach shm://ws2812 or shm://run — "
            "is ws2812put.service running?\n ",
            e,
            file=sys.stderr,
        )
        return 1

    if pixels.shape != (args.n_led, 3):
        print(
            f"smoke_ws2812put: shape mismatch {pixels.shape} != ({args.n_led}, 3)",
            file=sys.stderr,
        )
        return 1

    run[0] = True

    t0 = time.monotonic()
    while time.monotonic() - t0 < args.seconds:
        i = int((time.monotonic() - t0) * 30) % args.n_led
        frame = np.zeros((args.n_led, 3), dtype=np.uint8)
        for k, color in enumerate(
            (
                (20, 0, 0),
                (0, 20, 0),
                (0, 0, 20),
                (20, 20, 0),
            )
        ):
            frame[(i + k * 10) % args.n_led] = color
        pixels[:] = frame
        time.sleep(1.0 / 30.0)

    pixels[:] = 0
    print("smoke_ws2812put: wrote pattern then black OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
