#!/usr/bin/env python3
"""Send test stripe frames to Anker Pico (USB CDC or UDP)."""

from __future__ import annotations

import argparse
import colorsys
import socket
import struct
import time

MAGIC = b"ANKR"
HDR = struct.Struct("<4sHHBB")


def pack_frame(seq: int, rgb: bytes, n_led: int, n_lines: int) -> bytes:
    return HDR.pack(MAGIC, seq & 0xFFFF, n_led, n_lines, 0) + rgb


def rainbow_frame(n_led: int, n_lines: int, t: float) -> bytes:
    out = bytearray(n_led * n_lines * 3)
    for line in range(n_lines):
        phase = t * 0.2 + line * 0.15
        for i in range(n_led):
            h = (i / max(n_led, 1) + phase) % 1.0
            r, g, b = colorsys.hsv_to_rgb(h, 1.0, 0.25)
            o = (line * n_led + i) * 3
            out[o] = int(r * 255)
            out[o + 1] = int(g * 255)
            out[o + 2] = int(b * 255)
    return bytes(out)


def main() -> int:
    p = argparse.ArgumentParser(description="Push test frames to Pico multi-line receiver")
    p.add_argument("--port", help="USB CDC COM port, e.g. COM9 or /dev/ttyACM0")
    p.add_argument("--udp", help="host:port for Pico W, e.g. 192.168.8.50:5005")
    p.add_argument("--n-led", type=int, default=512)
    p.add_argument("--n-lines", type=int, default=8)
    p.add_argument("--fps", type=float, default=25.0)
    p.add_argument("--seconds", type=float, default=5.0)
    args = p.parse_args()
    if not args.port and not args.udp:
        p.error("need --port or --udp")

    period = 1.0 / args.fps if args.fps > 0 else 0.0
    sock = None
    ser = None
    udp_addr = None
    if args.udp:
        host, port_s = args.udp.rsplit(":", 1)
        udp_addr = (host, int(port_s))
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if args.port:
        import serial

        # Construct then open with DTR low to reduce auto-reset quirks
        ser = serial.Serial()
        ser.port = args.port
        ser.baudrate = 115200
        ser.timeout = 0.2
        ser.write_timeout = 2
        ser.dsrdtr = False
        ser.rtscts = False
        ser.dtr = False
        ser.rts = False
        ser.open()
        ser.reset_input_buffer()
        # Wait for firmware ready banner (open may reset the Pico)
        deadline = time.perf_counter() + 8.0
        buf = ""
        while time.perf_counter() < deadline:
            chunk = ser.read(256)
            if chunk:
                buf += chunk.decode("utf-8", "replace")
                if "ready" in buf.lower() or "READY" in buf:
                    break
            time.sleep(0.05)
        else:
            print("warning: no ready banner, sending anyway")
        # discard remaining banner
        time.sleep(0.1)
        ser.reset_input_buffer()

    t0 = time.perf_counter()
    seq = 0
    try:
        while time.perf_counter() - t0 < args.seconds:
            frame_t0 = time.perf_counter()
            rgb = rainbow_frame(args.n_led, args.n_lines, frame_t0 - t0)
            pkt = pack_frame(seq, rgb, args.n_led, args.n_lines)
            if ser:
                # Chunked writes so Pico can drain CDC without host/device deadlock
                view = memoryview(pkt)
                for off in range(0, len(view), 256):
                    ser.write(view[off : off + 256])
                    ser.flush()
                seq += 1
                if period:
                    sleep = period - (time.perf_counter() - frame_t0)
                    if sleep > 0:
                        time.sleep(sleep)
                continue
            if sock and udp_addr:
                sock.sendto(pkt, udp_addr)
            seq += 1
            if period:
                sleep = period - (time.perf_counter() - frame_t0)
                if sleep > 0:
                    time.sleep(sleep)
    finally:
        if ser:
            ser.close()
        if sock:
            sock.close()
    print(f"sent {seq} frames")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
