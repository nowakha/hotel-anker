#!/usr/bin/env python3
"""24h clock video → /dev/fb0 (ffmpeg 1-frame seek + PIL/numpy paint).

Desired OpenCV VideoCapture path is NOT used: on this 2GB Pi, `import cv2`
and/or VideoCapture(st24.mov) repeatedly hit SIGBUS (undervoltage reboots
also corrupt the wheel). ffmpeg `-ss … -frames:v 1` is proven OK.

Loop (stutter OK):
  wall-clock → ffmpeg extract 1 frame → crop T386/B127 → resize 3440×1440
  → rotate 180 → RGB565 → /dev/fb0 → sleep → always jump to current time.

Never full-file null decode. Duration via ffprobe only.
"""

from __future__ import annotations

import argparse
import os
import shutil
import signal
import subprocess
import tempfile
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
from PIL import Image

DEFAULT_VIDEO = Path(__file__).resolve().parent / "media" / "st24.mov"
DEFAULT_TZ = "Europe/Zurich"
DEFAULT_FB = "/dev/fb0"
DAY_S = 86400.0


def ffprobe_duration(video: Path) -> float | None:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return None
    proc = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(video),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        return float(proc.stdout.strip())
    except ValueError:
        return None


def fb_geom(fb: str) -> tuple[int, int, int]:
    w_s, h_s = Path("/sys/class/graphics/fb0/virtual_size").read_text().strip().split(",")
    stride = int(Path("/sys/class/graphics/fb0/stride").read_text().strip())
    return int(w_s), int(h_s), stride


def seconds_since_midnight(tz_name: str) -> float:
    now = datetime.now(ZoneInfo(tz_name))
    return (
        now.hour * 3600
        + now.minute * 60
        + now.second
        + now.microsecond / 1_000_000.0
    ) % DAY_S


def format_ts(seconds: float) -> str:
    s = max(0.0, min(seconds, DAY_S - 0.001))
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = s - h * 3600 - m * 60
    return f"{h:02d}:{m:02d}:{sec:06.3f}"


def rgb_to_rgb565(rgb: np.ndarray) -> bytes:
    r = rgb[:, :, 0].astype(np.uint16)
    g = rgb[:, :, 1].astype(np.uint16)
    b = rgb[:, :, 2].astype(np.uint16)
    pix = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    return pix.astype("<u2").tobytes()


def paint_rgb565(raw565: bytes, fb_path: str, w: int, h: int, stride: int) -> None:
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


def process_image(
    img: Image.Image,
    crop_top: int,
    crop_bottom: int,
    crop_left: int,
    crop_right: int,
    dst_w: int,
    dst_h: int,
) -> np.ndarray:
    w, h = img.size
    box = (crop_left, crop_top, w - crop_right, h - crop_bottom)
    cropped = img.crop(box)
    scaled = cropped.resize((dst_w, dst_h), Image.Resampling.BILINEAR)
    rotated = scaled.rotate(180)
    return np.asarray(rotated.convert("RGB"), dtype=np.uint8)


def extract_frame_pil(video: Path, seek_s: float, out_img: Path, timeout_s: float = 90.0) -> Image.Image:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise SystemExit("ffmpeg not found")
    seek = format_ts(seek_s)
    # PNG avoids intermittent mjpeg "non full-range YUV" encoder failures on this build.
    out_img = out_img.with_suffix(".png")
    cmd = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-nostdin",
        "-threads",
        "1",
        "-ss",
        seek,
        "-i",
        str(video),
        "-frames:v",
        "1",
        "-y",
        str(out_img),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s, check=False)
    if proc.returncode != 0 or not out_img.is_file() or out_img.stat().st_size < 100:
        err = (proc.stderr or proc.stdout or "").strip()[:400]
        raise RuntimeError(f"ffmpeg extract failed rc={proc.returncode}: {err}")
    return Image.open(out_img).convert("RGB")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--video", type=Path, default=DEFAULT_VIDEO)
    p.add_argument("--fb", default=DEFAULT_FB)
    p.add_argument("--tz", default=DEFAULT_TZ)
    p.add_argument("--crop-top", type=int, default=386)
    p.add_argument("--crop-bottom", type=int, default=127)
    p.add_argument("--crop-left", type=int, default=0)
    p.add_argument("--crop-right", type=int, default=0)
    p.add_argument("--log-every", type=int, default=1)
    p.add_argument(
        "--min-interval",
        type=float,
        default=15.0,
        help="Seconds between frames (4K extract brownouts weak PSUs; 15s safer)",
    )
    args = p.parse_args()

    if not os.access(args.fb, os.W_OK):
        raise SystemExit(f"cannot write {args.fb} (user in group video?)")
    if not args.video.is_file():
        raise SystemExit(f"video missing: {args.video}")

    stop = False

    def _stop(*_a: object) -> None:
        nonlocal stop
        stop = True

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    dst_w, dst_h, stride = fb_geom(args.fb)
    duration = ffprobe_duration(args.video) or DAY_S
    tmp_jpg = Path(tempfile.gettempdir()) / "fb_clock_frame.png"

    print(
        f"fb_clock_opencv: video={args.video} duration={duration:.3f}s "
        f"fb={args.fb} {dst_w}x{dst_h} stride={stride} "
        f"crop=T{args.crop_top},B{args.crop_bottom},L{args.crop_left},R{args.crop_right} "
        f"tz={args.tz} rotate=180 backend=ffmpeg1frame+pil "
        f"min_interval={args.min_interval}s",
        flush=True,
    )

    painted = 0
    t0 = time.monotonic()
    while not stop:
        cycle0 = time.monotonic()
        seek = seconds_since_midnight(args.tz)
        seek = max(0.0, min(seek, max(0.0, duration - 0.040)))
        wall = datetime.now(ZoneInfo(args.tz)).isoformat(timespec="seconds")
        try:
            t_ex0 = time.monotonic()
            img = extract_frame_pil(args.video, seek, tmp_jpg)
            t_ex1 = time.monotonic()
            rgb = process_image(
                img,
                args.crop_top,
                args.crop_bottom,
                args.crop_left,
                args.crop_right,
                dst_w,
                dst_h,
            )
            paint_rgb565(rgb_to_rgb565(rgb), args.fb, dst_w, dst_h, stride)
            painted += 1
            now_m = time.monotonic()
            if args.log_every == 0 or painted == 1 or painted % max(1, args.log_every) == 0:
                elapsed = now_m - t0
                eff = painted / elapsed if elapsed > 0 else 0.0
                print(
                    f"fb_clock_opencv: frame#{painted} seek={format_ts(seek)} wall={wall} "
                    f"extract_ms={(t_ex1 - t_ex0) * 1000:.0f} "
                    f"cycle_ms={(now_m - cycle0) * 1000:.0f} eff_fps={eff:.2f} "
                    f"src={img.size[0]}x{img.size[1]}",
                    flush=True,
                )
        except Exception as exc:  # noqa: BLE001
            print(f"fb_clock_opencv: frame error: {exc!r}", flush=True)
            time.sleep(2.0)

        remain = args.min_interval - (time.monotonic() - cycle0)
        while remain > 0 and not stop:
            time.sleep(min(0.25, remain))
            remain = args.min_interval - (time.monotonic() - cycle0)

    print("fb_clock_opencv: stopped", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
