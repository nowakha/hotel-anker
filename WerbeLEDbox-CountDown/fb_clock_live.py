#!/usr/bin/env python3
"""Live digital clock → /dev/fb0 (RGB565), wall-clock synced.

Default for AnkerPI02 when no fancy 24h MP4 is available.
Renders HH:MM:SS (+ date) every second; monitor mount is 180° → rotate baked in.
"""

from __future__ import annotations

import argparse
import os
import signal
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

DEFAULT_TZ = "Europe/Zurich"
DEFAULT_FB = "/dev/fb0"


def get_tz(name: str):
    try:
        from zoneinfo import ZoneInfo

        return ZoneInfo(name)
    except Exception:
        # Windows without tzdata package — CET/CEST approx
        return timezone(timedelta(hours=2), name="CEST")



def fb_geom(fb: str) -> tuple[int, int, int]:
    w_s, h_s = Path("/sys/class/graphics/fb0/virtual_size").read_text().strip().split(",")
    stride = int(Path("/sys/class/graphics/fb0/stride").read_text().strip())
    return int(w_s), int(h_s), stride


def rgb888_to_rgb565(rgb: bytes) -> bytes:
    # Full 3440×1440 in pure Python pegs a core (~1s+/frame). Prefer numpy.
    try:
        import numpy as np

        arr = np.frombuffer(rgb, dtype=np.uint8).reshape(-1, 3).astype(np.uint16)
        r, g, b = arr[:, 0], arr[:, 1], arr[:, 2]
        pix = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
        return pix.astype("<u2").tobytes()
    except Exception:
        out = bytearray(len(rgb) // 3 * 2)
        j = 0
        for i in range(0, len(rgb), 3):
            r, g, b = rgb[i], rgb[i + 1], rgb[i + 2]
            pix = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
            out[j] = pix & 0xFF
            out[j + 1] = (pix >> 8) & 0xFF
            j += 2
        return bytes(out)


def load_font(size: int) -> ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        r"C:\Windows\Fonts\consola.ttf",
        r"C:\Windows\Fonts\arialbd.ttf",
    ]
    for path in candidates:
        if Path(path).is_file():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def render_frame(w: int, h: int, now: datetime) -> Image.Image:
    img = Image.new("RGB", (w, h), (4, 10, 28))
    draw = ImageDraw.Draw(img)
    time_s = now.strftime("%H:%M:%S")
    date_s = now.strftime("%A  %d.%m.%Y")
    brand = "HOTEL ANKER"

    # Scale fonts to ultrawide 3440×1440 (or whatever fb reports)
    f_time = load_font(max(48, h // 3))
    f_date = load_font(max(24, h // 12))
    f_brand = load_font(max(20, h // 16))

    def center(text: str, font, y: int, fill: tuple[int, int, int]) -> None:
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        draw.text(((w - tw) // 2, y), text, font=font, fill=fill)

    center(brand, f_brand, h // 10, (200, 170, 90))
    center(time_s, f_time, h // 2 - h // 6, (255, 220, 120))
    center(date_s, f_date, h // 2 + h // 5, (160, 180, 210))

    # Monitor is mounted upside-down
    return img.rotate(180)


def paint_rgb565(img: Image.Image, fb_path: str, stride: int) -> None:
    w, h = img.size
    raw565 = rgb888_to_rgb565(img.tobytes("raw", "RGB"))
    fd = os.open(fb_path, os.O_RDWR)
    try:
        row = w * 2
        if stride == row:
            os.lseek(fd, 0, os.SEEK_SET)
            os.write(fd, raw565)
        else:
            for y in range(h):
                os.lseek(fd, y * stride, os.SEEK_SET)
                os.write(fd, raw565[y * row : (y + 1) * row])
    finally:
        os.close(fd)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--fb", default=DEFAULT_FB)
    p.add_argument("--tz", default=DEFAULT_TZ)
    p.add_argument(
        "--preview",
        type=Path,
        default=None,
        help="Write one PNG preview instead of painting framebuffer",
    )
    args = p.parse_args()
    tz = get_tz(args.tz)

    stop = False

    def _stop(*_a):
        nonlocal stop
        stop = True

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)

    if args.preview:
        # Default preview size matches PI02 HDMI mode
        w, h = 3440, 1440
        frame = render_frame(w, h, datetime.now(tz))
        args.preview.parent.mkdir(parents=True, exist_ok=True)
        frame.save(args.preview)
        print(f"wrote preview {args.preview}", flush=True)
        return 0

    if not os.access(args.fb, os.W_OK):
        raise SystemExit(f"cannot write {args.fb}")

    w, h, stride = fb_geom(args.fb)
    print(f"fb_clock_live: {w}x{h} stride={stride} tz={args.tz}", flush=True)
    last_second = -1
    while not stop:
        now = datetime.now(tz)
        if now.second != last_second:
            last_second = now.second
            paint_rgb565(render_frame(w, h, now), args.fb, stride)
        time.sleep(0.05)
    print("fb_clock_live: stopped", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
