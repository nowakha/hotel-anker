#!/usr/bin/env python3
"""AnkerPI01 countdown producer → shm://ws2812 (N_LED, 3).

Linear LED strip visualization until Baubeginn 2026-10-01 13:00 Europe/Zurich:
  - Progress fill (elapsed/total) in amber
  - Remaining tip blinks white once per second
  - After target: solid soft gold

Attach-only: ws2812put.service must own/create the SharedArrays.
"""

from __future__ import annotations

import argparse
import os
import signal
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

try:
    from zoneinfo import ZoneInfo

    TZ = ZoneInfo("Europe/Zurich")
except Exception:
    TZ = timezone(timedelta(hours=2))

DEFAULT_N_LED = 1179
DEFAULT_FPS = 25
TARGET = datetime(2026, 10, 1, 13, 0, 0, tzinfo=TZ)
# Rough project start for progress ratio (when strip first went live)
EPOCH = datetime(2026, 7, 1, 0, 0, 0, tzinfo=TZ)

SHM_PIXELS = "shm://ws2812"
SHM_RUN = "shm://run"

NAVY = np.array([0, 8, 40], dtype=np.uint8)
AMBER = np.array([255, 96, 0], dtype=np.uint8)
AMBER_DIM = np.array([80, 28, 0], dtype=np.uint8)
WHITE = np.array([255, 255, 255], dtype=np.uint8)
GOLD = np.array([200, 150, 40], dtype=np.uint8)


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    return int(raw)


def attach_pixels(n_led: int):
    try:
        import SharedArray as sa
    except ImportError as e:  # pragma: no cover
        raise SystemExit("SharedArray required on AnkerPI01") from e
    try:
        pixels = sa.attach(SHM_PIXELS)
        run = sa.attach(SHM_RUN)
    except Exception as e:
        raise SystemExit(
            f"cannot attach {SHM_PIXELS}/{SHM_RUN} — start ws2812put first ({e})"
        ) from e
    if tuple(pixels.shape) != (n_led, 3):
        raise SystemExit(f"shm shape {pixels.shape} != ({n_led}, 3)")
    return pixels, run


def render(n_led: int, now: datetime) -> np.ndarray:
    frame = np.zeros((n_led, 3), dtype=np.uint8)
    frame[:] = NAVY

    if now >= TARGET:
        frame[:] = GOLD
        return frame

    total = (TARGET - EPOCH).total_seconds()
    left = (TARGET - now).total_seconds()
    elapsed = max(0.0, total - left)
    frac = 0.0 if total <= 0 else min(1.0, elapsed / total)
    filled = max(1, int(round(frac * (n_led - 1))))

    frame[:filled] = AMBER
    # Dim trail behind the tip
    trail = max(0, filled - 40)
    if filled > trail:
        frame[trail:filled] = AMBER
        for i, led in enumerate(range(trail, filled)):
            t = i / max(1, filled - trail - 1)
            frame[led] = (
                AMBER_DIM.astype(np.float32) * (1 - t) + AMBER.astype(np.float32) * t
            ).astype(np.uint8)

    tip = min(n_led - 1, filled)
    if now.microsecond < 500_000:
        frame[tip] = WHITE
    else:
        frame[tip] = AMBER
    return frame


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--n-led", type=int, default=_env_int("N_LED", DEFAULT_N_LED))
    p.add_argument("--fps", type=float, default=float(os.environ.get("FPS", DEFAULT_FPS)))
    p.add_argument("--seconds", type=float, default=None, help="optional run limit")
    p.add_argument(
        "--preview",
        type=Path,
        default=None,
        help="write 1×N RGB PNG strip preview instead of SHM",
    )
    args = p.parse_args()

    if args.preview:
        from PIL import Image

        strip = render(args.n_led, datetime.now(TZ))
        img = Image.fromarray(strip.reshape(1, args.n_led, 3), "RGB").resize(
            (args.n_led, 32), Image.Resampling.NEAREST
        )
        args.preview.parent.mkdir(parents=True, exist_ok=True)
        img.save(args.preview)
        print(f"wrote {args.preview}", flush=True)
        return 0

    pixels, run = attach_pixels(args.n_led)
    stop = False

    def _stop(*_a):
        nonlocal stop
        stop = True

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)

    period = 1.0 / max(1e-6, args.fps)
    t0 = time.perf_counter()
    n = 0
    print(
        f"countdown_pi01: n_led={args.n_led} fps={args.fps} target={TARGET.isoformat()}",
        flush=True,
    )
    while not stop and bool(run[0]):
        if args.seconds is not None and (time.perf_counter() - t0) >= args.seconds:
            break
        pixels[:] = render(args.n_led, datetime.now(TZ))
        n += 1
        next_t = t0 + n * period
        delay = next_t - time.perf_counter()
        if delay > 0:
            time.sleep(delay)

    pixels[:] = 0
    print(f"countdown_pi01: stopped after {n} frames", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
