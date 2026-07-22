#!/usr/bin/env python3
"""Play a video file directly to /dev/fb0 (no X11 / Wayland).

AnkerPI02 helper around ffmpeg:
  H.264 V4L2 hw-decode → nearest upscale → fbdev RGB565

Example:
  python3 fb_play.py media/anker_860x360_25.mp4 --loop
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path


def ffmpeg_bin() -> str:
    path = shutil.which("ffmpeg")
    if not path:
        raise SystemExit("ffmpeg not found — sudo apt-get install -y ffmpeg")
    return path


def probe_size(ffmpeg: str, video: Path) -> tuple[int, int] | None:
    proc = subprocess.run(
        [ffmpeg, "-hide_banner", "-i", str(video), "-f", "null", "-"],
        capture_output=True,
        text=True,
        check=False,
    )
    m = re.search(r"Video:.*?\s(\d{2,5})x(\d{2,5})\b", proc.stderr)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))


def fb_size(fb: str = "/dev/fb0") -> tuple[int, int]:
    # sysfs is enough and avoids ioctl dependency for the common path
    raw = Path("/sys/class/graphics/fb0/virtual_size").read_text().strip()
    w_s, h_s = raw.split(",")
    return int(w_s), int(h_s)


def build_vf(src: tuple[int, int] | None, dst_w: int, dst_h: int) -> str:
    if src and dst_w % src[0] == 0 and dst_h % src[1] == 0 and (dst_w // src[0]) == (
        dst_h // src[1]
    ):
        return f"scale={dst_w}:{dst_h}:flags=neighbor,format=rgb565le"
    return (
        f"scale={dst_w}:{dst_h}:force_original_aspect_ratio=increase:flags=fast_bilinear,"
        f"crop={dst_w}:{dst_h},format=rgb565le"
    )


def main() -> int:
    p = argparse.ArgumentParser(description="Play video to /dev/fb0 via ffmpeg fbdev")
    p.add_argument("video", type=Path)
    p.add_argument("--fb", default="/dev/fb0")
    p.add_argument("--loop", action="store_true")
    p.add_argument("--no-hw", action="store_true", help="disable h264_v4l2m2m")
    p.add_argument(
        "--no-re",
        action="store_true",
        help="do not pace to realtime (decode as fast as possible)",
    )
    args = p.parse_args()

    if not args.video.is_file():
        raise SystemExit(f"video not found: {args.video}")
    if not os.access(args.fb, os.W_OK):
        raise SystemExit(f"cannot write {args.fb} (user in group video?)")

    ff = ffmpeg_bin()
    dst_w, dst_h = fb_size(args.fb)
    src = probe_size(ff, args.video)
    vf = build_vf(src, dst_w, dst_h)
    src_s = f"{src[0]}x{src[1]}" if src else "?"

    cmd = [ff, "-hide_banner", "-loglevel", "error", "-nostdin"]
    if args.loop:
        cmd += ["-stream_loop", "-1"]
    if not args.no_hw:
        cmd += ["-c:v", "h264_v4l2m2m"]
    if not args.no_re:
        cmd += ["-re"]
    cmd += [
        "-i",
        str(args.video),
        "-an",
        "-vf",
        vf,
        "-pix_fmt",
        "rgb565le",
        "-f",
        "fbdev",
        args.fb,
    ]

    print(
        f"fb_play: {args.video} ({src_s}) → {args.fb} {dst_w}x{dst_h} "
        f"hw_decode={not args.no_hw} loop={args.loop}",
        flush=True,
    )
    print(f"fb_play: {' '.join(cmd)}", flush=True)

    proc = subprocess.Popen(cmd)

    def _stop(signum: int, _frame: object) -> None:
        if proc.poll() is None:
            proc.terminate()

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    t0 = time.monotonic()
    rc = proc.wait()
    print(f"fb_play: done rc={rc} elapsed={time.monotonic() - t0:.1f}s", flush=True)
    return 0 if rc == 0 else int(rc or 1)


if __name__ == "__main__":
    raise SystemExit(main())
