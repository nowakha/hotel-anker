#!/usr/bin/env python3
"""24h clock video → /dev/fb0 (ffmpeg 1-frame seek + paint).

Desired OpenCV VideoCapture path is NOT used: on this 2GB Pi, `import cv2`
and/or VideoCapture(st24.mov) repeatedly hit SIGBUS (undervoltage reboots
also corrupt the wheel). ffmpeg `-ss … -frames:v 1` is proven OK.

Default pipeline (bench 2026-07-22 on AnkerPI02 / st24.mov 4K):
  wall-clock seek → ffmpeg crop+scale+flip → raw RGB24 pipe
  → optional NEAREST upsample to fb size → RGB565 → /dev/fb0
  Always jump to current wall time (never fall behind).

Bottleneck is 4K seek+decode (~9–15 s). Host resize 3440 vs 860 is only
~0.2–0.5 s; putting crop/scale into ffmpeg vf + raw pipe wins ~1.5–2 s
vs legacy PNG+PIL. OpenCV unavailable here — PIL/numpy used for upsample.

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


def crop_vf(crop_top: int, crop_bottom: int, crop_left: int, crop_right: int, src_w: int, src_h: int) -> str:
    w = src_w - crop_left - crop_right
    h = src_h - crop_top - crop_bottom
    return f"crop={w}:{h}:{crop_left}:{crop_top}"


def process_image_legacy(
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


def extract_raw_rgb(
    video: Path,
    seek_s: float,
    vf: str,
    out_w: int,
    out_h: int,
    hwaccel: str | None,
    timeout_s: float = 90.0,
) -> np.ndarray:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise SystemExit("ffmpeg not found")
    seek = format_ts(seek_s)
    cmd = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-nostdin",
        "-threads",
        "1",
    ]
    if hwaccel:
        cmd += ["-hwaccel", hwaccel]
    cmd += [
        "-ss",
        seek,
        "-i",
        str(video),
        "-vf",
        vf,
        "-frames:v",
        "1",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "pipe:1",
    ]
    proc = subprocess.run(cmd, capture_output=True, timeout=timeout_s, check=False)
    if proc.returncode != 0:
        err = (proc.stderr or b"").decode("utf-8", "replace").strip()[:400]
        raise RuntimeError(f"ffmpeg raw extract failed rc={proc.returncode}: {err}")
    expect = out_w * out_h * 3
    if len(proc.stdout) != expect:
        raise RuntimeError(f"raw size {len(proc.stdout)} != {expect} for {out_w}x{out_h}")
    return np.frombuffer(proc.stdout, dtype=np.uint8).reshape((out_h, out_w, 3)).copy()


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--video", type=Path, default=DEFAULT_VIDEO)
    p.add_argument("--fb", default=DEFAULT_FB)
    p.add_argument("--tz", default=DEFAULT_TZ)
    p.add_argument("--crop-top", type=int, default=386)
    p.add_argument("--crop-bottom", type=int, default=127)
    p.add_argument("--crop-left", type=int, default=0)
    p.add_argument("--crop-right", type=int, default=0)
    p.add_argument("--src-width", type=int, default=3840, help="Source frame width for crop vf")
    p.add_argument("--src-height", type=int, default=2160, help="Source frame height for crop vf")
    p.add_argument("--log-every", type=int, default=1)
    p.add_argument(
        "--min-interval",
        type=float,
        default=0.0,
        help="Min seconds between frames (0 = max sustainable fps)",
    )
    p.add_argument(
        "--pipeline",
        choices=("vf860", "vf3440", "legacy"),
        default="vf860",
        help="vf860=ffmpeg crop/scale 860 + NN up (fastest full-screen); "
        "vf3440=ffmpeg scale to fb; legacy=PNG+PIL",
    )
    p.add_argument(
        "--hwaccel",
        default="drm",
        help="ffmpeg -hwaccel (default drm; empty string disables)",
    )
    p.add_argument(
        "--mid-w",
        type=int,
        default=860,
        help="Intermediate width for vf860 pipeline",
    )
    p.add_argument(
        "--mid-h",
        type=int,
        default=360,
        help="Intermediate height for vf860 pipeline",
    )
    args = p.parse_args()
    hwaccel: str | None = args.hwaccel.strip() or None

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
    tmp_png = Path(tempfile.gettempdir()) / "fb_clock_frame.png"
    cvf = crop_vf(
        args.crop_top,
        args.crop_bottom,
        args.crop_left,
        args.crop_right,
        args.src_width,
        args.src_height,
    )

    print(
        f"fb_clock_opencv: video={args.video} duration={duration:.3f}s "
        f"fb={args.fb} {dst_w}x{dst_h} stride={stride} "
        f"crop=T{args.crop_top},B{args.crop_bottom},L{args.crop_left},R{args.crop_right} "
        f"tz={args.tz} rotate=180 pipeline={args.pipeline} hwaccel={hwaccel or 'off'} "
        f"mid={args.mid_w}x{args.mid_h} min_interval={args.min_interval}s",
        flush=True,
    )

    painted = 0
    t0 = time.monotonic()
    hwaccel_disabled = False

    while not stop:
        cycle0 = time.monotonic()
        seek = seconds_since_midnight(args.tz)
        seek = max(0.0, min(seek, max(0.0, duration - 0.040)))
        wall = datetime.now(ZoneInfo(args.tz)).isoformat(timespec="seconds")
        try:
            t_ex0 = time.monotonic()
            t_resize_ms = 0.0
            src_label = ""

            if args.pipeline == "legacy":
                img = extract_frame_pil(args.video, seek, tmp_png)
                t_ex1 = time.monotonic()
                t_rs0 = time.monotonic()
                rgb = process_image_legacy(
                    img,
                    args.crop_top,
                    args.crop_bottom,
                    args.crop_left,
                    args.crop_right,
                    dst_w,
                    dst_h,
                )
                t_resize_ms = (time.monotonic() - t_rs0) * 1000
                src_label = f"{img.size[0]}x{img.size[1]}"
            else:
                use_hw = None if hwaccel_disabled else hwaccel
                if args.pipeline == "vf860":
                    vf = f"{cvf},scale={args.mid_w}:{args.mid_h}:flags=fast_bilinear,hflip,vflip"
                    try:
                        mid = extract_raw_rgb(
                            args.video, seek, vf, args.mid_w, args.mid_h, use_hw
                        )
                    except RuntimeError:
                        if use_hw:
                            hwaccel_disabled = True
                            print(
                                "fb_clock_opencv: hwaccel failed — falling back to software",
                                flush=True,
                            )
                            mid = extract_raw_rgb(
                                args.video, seek, vf, args.mid_w, args.mid_h, None
                            )
                        else:
                            raise
                    t_ex1 = time.monotonic()
                    t_rs0 = time.monotonic()
                    if (args.mid_w, args.mid_h) != (dst_w, dst_h):
                        rgb = np.asarray(
                            Image.fromarray(mid).resize(
                                (dst_w, dst_h), Image.Resampling.NEAREST
                            ),
                            dtype=np.uint8,
                        )
                    else:
                        rgb = mid
                    t_resize_ms = (time.monotonic() - t_rs0) * 1000
                    src_label = f"{args.mid_w}x{args.mid_h}"
                else:  # vf3440
                    vf = f"{cvf},scale={dst_w}:{dst_h}:flags=bilinear,hflip,vflip"
                    try:
                        rgb = extract_raw_rgb(
                            args.video, seek, vf, dst_w, dst_h, use_hw
                        )
                    except RuntimeError:
                        if use_hw:
                            hwaccel_disabled = True
                            print(
                                "fb_clock_opencv: hwaccel failed — falling back to software",
                                flush=True,
                            )
                            rgb = extract_raw_rgb(
                                args.video, seek, vf, dst_w, dst_h, None
                            )
                        else:
                            raise
                    t_ex1 = time.monotonic()
                    src_label = f"{dst_w}x{dst_h}"

            t_c0 = time.monotonic()
            raw = rgb_to_rgb565(rgb)
            t_c1 = time.monotonic()
            paint_rgb565(raw, args.fb, dst_w, dst_h, stride)
            t_fb = time.monotonic()
            painted += 1
            if args.log_every == 0 or painted == 1 or painted % max(1, args.log_every) == 0:
                elapsed = t_fb - t0
                eff = painted / elapsed if elapsed > 0 else 0.0
                print(
                    f"fb_clock_opencv: frame#{painted} seek={format_ts(seek)} wall={wall} "
                    f"extract_ms={(t_ex1 - t_ex0) * 1000:.0f} "
                    f"resize_ms={t_resize_ms:.0f} "
                    f"rgb565_ms={(t_c1 - t_c0) * 1000:.0f} "
                    f"fb_ms={(t_fb - t_c1) * 1000:.0f} "
                    f"cycle_ms={(t_fb - cycle0) * 1000:.0f} eff_fps={eff:.2f} "
                    f"src={src_label}",
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
