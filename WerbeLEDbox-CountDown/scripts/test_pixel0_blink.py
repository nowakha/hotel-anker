#!/usr/bin/env python3
"""Cycle the first N pixels on shm://ws2812 (attach-only; ws2812put owns SHM).

Sequence (1 s each step, black between colors):
  red → black → green → black → blue → black → cyan → black →
  magenta → black → yellow → black → white → black → (repeat)

Pixels 0..count-1 are written together to the same color each step;
indices count..end are left unchanged. On Ctrl+C / exit, those pixels
are set black. Does not create or unlink SharedArray (ws2812put.service
owns create).
"""

from __future__ import annotations

import argparse
import signal
import sys
import time

import numpy as np
import SharedArray as sa

SHM_PIXELS = "shm://ws2812"
DEFAULT_N_LED = 1179
DEFAULT_COUNT = 1
BRIGHT = 64  # moderate WS2812 level (not full 255)

# Named colors at moderate brightness; black between each in STEPS
COLORS = {
    "red": (BRIGHT, 0, 0),
    "green": (0, BRIGHT, 0),
    "blue": (0, 0, BRIGHT),
    "cyan": (0, BRIGHT, BRIGHT),
    "magenta": (BRIGHT, 0, BRIGHT),
    "yellow": (BRIGHT, BRIGHT, 0),
    "white": (BRIGHT, BRIGHT, BRIGHT),
    "black": (0, 0, 0),
}

# Each entry shows for --interval seconds
STEPS = (
    "red",
    "black",
    "green",
    "black",
    "blue",
    "black",
    "cyan",
    "black",
    "magenta",
    "black",
    "yellow",
    "black",
    "white",
    "black",
)


def main() -> int:
    p = argparse.ArgumentParser(
        description=(
            "Blink first N pixels through R/G/B/C/M/Y/W with black between"
        )
    )
    p.add_argument("--n-led", type=int, default=DEFAULT_N_LED)
    p.add_argument(
        "--count",
        type=int,
        default=DEFAULT_COUNT,
        help="number of leading pixels to drive together (default: 1)",
    )
    p.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="seconds per step (color or black)",
    )
    p.add_argument(
        "--cycles",
        type=int,
        default=0,
        help="number of full color cycles then exit (0 = forever)",
    )
    p.add_argument(
        "--seconds",
        type=float,
        default=0.0,
        help="stop after N seconds (0 = ignore; overrides --cycles if set)",
    )
    args = p.parse_args()

    if args.count < 1 or args.count > args.n_led:
        print(
            f"test_pixel0_blink: --count must be 1..{args.n_led}, "
            f"got {args.count}",
            file=sys.stderr,
        )
        return 1

    try:
        pixels = sa.attach(SHM_PIXELS)
    except Exception as e:
        print(
            "test_pixel0_blink: cannot attach shm://ws2812 — "
            "is ws2812put.service running?\n ",
            e,
            file=sys.stderr,
        )
        return 1

    if pixels.shape != (args.n_led, 3) or pixels.dtype != np.uint8:
        print(
            f"test_pixel0_blink: expected shape ({args.n_led}, 3) uint8, "
            f"got {pixels.shape} {pixels.dtype}",
            file=sys.stderr,
        )
        return 1

    stop = False

    def request_stop(*_args):
        nonlocal stop
        stop = True

    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)

    t0 = time.monotonic()
    step_i = 0
    cycles_done = 0
    hi = args.count  # exclusive end index
    print(
        f"test_pixel0_blink: attached {SHM_PIXELS} shape={pixels.shape}; "
        f"driving pixels 0..{hi - 1} ({args.count} LEDs, others unchanged); "
        f"interval={args.interval}s"
    )

    try:
        while not stop:
            if args.seconds > 0 and (time.monotonic() - t0) >= args.seconds:
                break
            if args.cycles > 0 and cycles_done >= args.cycles:
                break

            name = STEPS[step_i]
            rgb = COLORS[name]
            # Touch only 0..count-1; leave rest of strip as-is
            pixels[0:hi] = rgb
            print(f"  pixels[0:{hi}]={name} {rgb}", flush=True)

            deadline = time.monotonic() + args.interval
            while not stop and time.monotonic() < deadline:
                if args.seconds > 0 and (time.monotonic() - t0) >= args.seconds:
                    stop = True
                    break
                time.sleep(min(0.05, max(0.0, deadline - time.monotonic())))

            step_i = (step_i + 1) % len(STEPS)
            if step_i == 0:
                cycles_done += 1
    finally:
        try:
            pixels[0:hi] = (0, 0, 0)
        except Exception:
            pass
        print(
            f"test_pixel0_blink: pixels 0..{hi - 1} → black; "
            "exit (SHM not unlinked)"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
