#!/usr/bin/env python3
"""AnkerPI02 putter: shm://ws2812 (64,64,3) → Pico USB 8×512 PIO.

Creates/attaches SharedArray, maps serpentine layout, pushes ANKR frames
to /dev/ttyACM0 (MicroPython Pico receiver).
"""

from __future__ import annotations

import argparse
import os
import signal
import struct
import sys
import threading
import time

import numpy as np
import SharedArray as sa
import serial

from layout_64x64_8x512 import HEIGHT, N_FIELDS, N_LED, WIDTH, map_panel_to_lines

SHM_PIXELS = "shm://ws2812"
SHM_TIMING = "shm://ws2812dt"
SHM_RUN = "shm://run"

MAGIC = b"ANKR"
HDR = struct.Struct("<4sHHBB")
DEFAULT_FPS = 25
DEFAULT_PORT = "/dev/ttyACM0"


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


def _env_str(name: str, default: str) -> str:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    return raw


def _norm_shape(shape):
    if isinstance(shape, int):
        return (shape,)
    return tuple(shape)


def create_or_attach(name: str, shape, dtype):
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


def pack_frame(seq: int, lines: np.ndarray) -> bytes:
    """lines (8, 512, 3) → ANKR frame bytes."""
    body = np.ascontiguousarray(lines, dtype=np.uint8).reshape(-1).tobytes()
    return HDR.pack(MAGIC, seq & 0xFFFF, N_LED, N_FIELDS, 0) + body


def resolve_port(port: str) -> str:
    """Prefer explicit path; fall back to Teensy by-id / ttyACM0."""
    candidates = [
        port,
        "/dev/serial/by-id/usb-Teensyduino_USB_Serial_2923720-if00",
        "/dev/ttyACM0",
    ]
    seen: set[str] = set()
    for c in candidates:
        if not c or c in seen:
            continue
        seen.add(c)
        if os.path.exists(c):
            return c
    return port


def open_pico(port: str) -> serial.Serial:
    resolved = resolve_port(port)
    ser = serial.Serial()
    ser.port = resolved
    ser.baudrate = 115200
    ser.timeout = 0.05
    ser.write_timeout = 2.0
    ser.dsrdtr = False
    ser.rtscts = False
    ser.dtr = False
    ser.rts = False
    ser.open()
    # Drain boot banner; avoid blocking forever
    t0 = time.monotonic()
    buf = b""
    while time.monotonic() - t0 < 2.0:
        chunk = ser.read(256)
        if chunk:
            buf += chunk
            if b"ready" in buf.lower():
                break
        else:
            time.sleep(0.02)
    ser.reset_input_buffer()
    return ser


def write_frame(ser: serial.Serial, pkt: bytes, chunk: int = 512) -> None:
    view = memoryview(pkt)
    for off in range(0, len(view), chunk):
        ser.write(view[off : off + chunk])
    ser.flush()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="AnkerPI02: shm 64x64 → Pico 8x512")
    p.add_argument("--port", default=_env_str("PICO_PORT", DEFAULT_PORT))
    p.add_argument("--fps", type=float, default=_env_float("FPS", DEFAULT_FPS))
    p.add_argument("--chunk", type=int, default=_env_int("USB_CHUNK", 512))
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    frame_period = 1.0 / args.fps if args.fps > 0 else 0.0

    panel = create_or_attach(SHM_PIXELS, (HEIGHT, WIDTH, 3), np.uint8)
    timing = create_or_attach(SHM_TIMING, 2, float)
    run = create_or_attach(SHM_RUN, 1, bool)
    run[0] = True

    ser = open_pico(args.port)
    stop = threading.Event()
    seq = 0

    def request_stop(*_a):
        run[0] = False
        stop.set()

    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)

    def light():
        nonlocal seq
        pixels = sa.attach(SHM_PIXELS)
        dt_buf = sa.attach(SHM_TIMING)
        run_flag = sa.attach(SHM_RUN)
        t = time.monotonic()
        while run_flag[0] and not stop.is_set():
            t0 = time.monotonic()
            lines = map_panel_to_lines(pixels)
            pkt = pack_frame(seq, lines)
            write_frame(ser, pkt, chunk=args.chunk)
            seq = (seq + 1) & 0xFFFF
            now = time.monotonic()
            elapsed = now - t
            if frame_period > 0 and elapsed < frame_period:
                time.sleep(frame_period - elapsed)
            after = time.monotonic()
            dt_buf[:] = [now - t0, after - t]
            t = after

    thread = threading.Thread(target=light, name="ws2812put-pi02", daemon=False)
    thread.start()
    print(
        f"ws2812put_pi02: shm {HEIGHT}x{WIDTH}x3 → {N_FIELDS}x{N_LED} @ {args.fps} fps via {args.port}",
        flush=True,
    )

    try:
        while run[0] and not stop.is_set():
            stop.wait(0.2)
    finally:
        run[0] = False
        stop.set()
        thread.join(timeout=5.0)
        try:
            black = np.zeros((N_FIELDS, N_LED, 3), dtype=np.uint8)
            write_frame(ser, pack_frame(seq, black), chunk=args.chunk)
        except Exception:
            pass
        try:
            ser.close()
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
