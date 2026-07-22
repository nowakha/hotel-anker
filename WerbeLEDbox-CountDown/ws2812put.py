#!/usr/bin/env python3
"""Push shm://ws2812 frames to WS2812 LEDs via SPI.

AnkerPI01 (Zero 2 W): this file — shm (N_LED,3) → SPI0.
AnkerPI02 (Pi 4 + Pico): use ws2812put_pi02.py — shm (64,64,3) → 8×512 USB/PIO.
"""

from __future__ import annotations

import argparse
import os
import signal
import sys
import threading
import time

import numpy as np
import SharedArray as sa
import spidev
import ws2812

# Max LEDs for guaranteed 25 fps on Pi Zero 2 W (see docs/ANKERPI01.md):
# wire ≈ 25.2 µs/LED @ 3.809523 MHz, reset 280 µs, CPU overhead 10 ms → floor = 1179
DEFAULT_N_LED = 1179
DEFAULT_FPS = 25
DEFAULT_SPI_BUS = 0
DEFAULT_SPI_DEV = 0
DEFAULT_SPI_HZ = int(4 / 1.05e-6)

SHM_PIXELS = "shm://ws2812"
SHM_TIMING = "shm://ws2812dt"
SHM_RUN = "shm://run"


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    return int(raw)


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    return float(raw)


def _norm_shape(shape):
    if isinstance(shape, int):
        return (shape,)
    return tuple(shape)


def create_or_attach(name: str, shape, dtype):
    """Attach existing SHM, or create if missing. Avoid delete unless shape mismatches."""
    short = name.replace("shm://", "")
    want = _norm_shape(shape)
    try:
        arr = sa.attach(name)
        if _norm_shape(arr.shape) != want:
            try:
                sa.delete(short)
            except Exception:
                pass
            return sa.create(name, shape, dtype=dtype)
        return arr
    except Exception:
        pass
    try:
        return sa.create(name, shape, dtype=dtype)
    except FileExistsError:
        return sa.attach(name)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="WS2812 putter: shm://ws2812 → SPI")
    p.add_argument("--n-led", type=int, default=_env_int("N_LED", DEFAULT_N_LED))
    p.add_argument("--fps", type=float, default=_env_float("FPS", DEFAULT_FPS))
    p.add_argument("--spi-bus", type=int, default=_env_int("SPI_BUS", DEFAULT_SPI_BUS))
    p.add_argument("--spi-dev", type=int, default=_env_int("SPI_DEV", DEFAULT_SPI_DEV))
    p.add_argument("--spi-hz", type=int, default=_env_int("SPI_HZ", DEFAULT_SPI_HZ))
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    n_led = args.n_led
    frame_period = 1.0 / args.fps if args.fps > 0 else 0.0

    stripe = create_or_attach(SHM_PIXELS, (n_led, 3), np.uint8)
    timing = create_or_attach(SHM_TIMING, 2, float)
    run = create_or_attach(SHM_RUN, 1, bool)
    run[0] = True

    spi = spidev.SpiDev()
    spi.open(args.spi_bus, args.spi_dev)
    stop = threading.Event()

    def request_stop(*_args):
        run[0] = False
        stop.set()

    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)

    def light():
        pixels = sa.attach(SHM_PIXELS)
        dt_buf = sa.attach(SHM_TIMING)
        run_flag = sa.attach(SHM_RUN)
        t = time.monotonic()
        while run_flag[0] and not stop.is_set():
            ws2812.write2812_numpy4(spi, pixels, hz=args.spi_hz)
            now = time.monotonic()
            elapsed = now - t
            if frame_period > 0 and elapsed < frame_period:
                time.sleep(frame_period - elapsed)
            after = time.monotonic()
            dt_buf[:] = [elapsed, after - t]
            t = after

    thread = threading.Thread(target=light, name="ws2812put", daemon=False)
    thread.start()

    try:
        while run[0] and not stop.is_set():
            stop.wait(0.2)
    finally:
        run[0] = False
        stop.set()
        thread.join(timeout=5.0)
        try:
            ws2812.write2812_numpy4(
                spi, np.zeros((n_led, 3), dtype=np.uint8), hz=args.spi_hz
            )
        except Exception:
            pass
        try:
            spi.close()
        except Exception:
            pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
