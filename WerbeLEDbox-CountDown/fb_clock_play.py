#!/usr/bin/env python3
"""24h clock video → /dev/fb0, seek-synced to local wall clock.

Video must be exactly 86400 s, content starting at 00:00:00 local time.
Monitor is mounted 180° — frames are rotated in the ffmpeg filter graph
(no KMS rotate= flag).

Optional --crop-* args apply before scale (Premiere-style margins in source pixels).
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import signal
import subprocess
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

DEFAULT_VIDEO = Path(__file__).resolve().parent / "media" / "clock_24h.mp4"
DEFAULT_TZ = "Europe/Zurich"
DAY_S = 86400.0
DEFAULT_RESYNC_S = 600


def ffmpeg_bin() -> str:
    path = shutil.which("ffmpeg")
    if not path:
        raise SystemExit("ffmpeg not found — sudo apt-get install -y ffmpeg")
    return path


def probe_size(ffmpeg: str, video: Path) -> tuple[int, int] | None:
    # Never decode the whole file — 24h 4K would hang the Pi.
    ffprobe = shutil.which("ffprobe")
    if ffprobe:
        proc = subprocess.run(
            [
                ffprobe,
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=width,height",
                "-of",
                "csv=p=0:s=x",
                str(video),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        m = re.search(r"(\d{2,5})x(\d{2,5})", proc.stdout.strip())
        if m:
            return int(m.group(1)), int(m.group(2))
    # Fallback: ffmpeg -i prints stream info on stderr and exits quickly
    proc = subprocess.run(
        [ffmpeg, "-hide_banner", "-i", str(video)],
        capture_output=True,
        text=True,
        check=False,
    )
    m = re.search(r"Video:.*?\s(\d{2,5})x(\d{2,5})\b", proc.stderr)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))


def fb_size() -> tuple[int, int]:
    raw = Path("/sys/class/graphics/fb0/virtual_size").read_text().strip()
    w_s, h_s = raw.split(",")
    return int(w_s), int(h_s)


def build_vf(
    src: tuple[int, int] | None,
    dst_w: int,
    dst_h: int,
    crop_top: int = 0,
    crop_bottom: int = 0,
    crop_left: int = 0,
    crop_right: int = 0,
) -> str:
    parts: list[str] = []
    cropped: tuple[int, int] | None = src
    if src and (crop_top or crop_bottom or crop_left or crop_right):
        cw = max(1, src[0] - crop_left - crop_right)
        ch = max(1, src[1] - crop_top - crop_bottom)
        parts.append(f"crop={cw}:{ch}:{crop_left}:{crop_top}")
        cropped = (cw, ch)

    # scale then rotate 180° for upside-down mount
    if (
        cropped
        and dst_w % cropped[0] == 0
        and dst_h % cropped[1] == 0
        and (dst_w // cropped[0]) == (dst_h // cropped[1])
    ):
        scale = f"scale={dst_w}:{dst_h}:flags=neighbor"
    else:
        scale = (
            f"scale={dst_w}:{dst_h}:force_original_aspect_ratio=increase:flags=fast_bilinear,"
            f"crop={dst_w}:{dst_h}"
        )
    parts.append(scale)
    parts.append(f"rotate=PI:ow={dst_w}:oh={dst_h}")
    parts.append("format=rgb565le")
    return ",".join(parts)


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


def wait_for_video(path: Path, should_stop) -> None:
    while not should_stop() and not path.is_file():
        print(f"fb_clock: waiting for video file {path}", flush=True)
        time.sleep(5)


def build_cmd(
    ffmpeg: str,
    video: Path,
    fb: str,
    seek_s: float,
    vf: str,
    hw: bool,
) -> list[str]:
    cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin"]
    cmd += ["-ss", format_ts(seek_s)]
    if hw:
        cmd += ["-c:v", "h264_v4l2m2m"]
    cmd += [
        "-re",
        "-i",
        str(video),
        "-an",
        "-vf",
        vf,
        "-pix_fmt",
        "rgb565le",
        "-f",
        "fbdev",
        fb,
    ]
    return cmd


def main() -> int:
    p = argparse.ArgumentParser(description="24h clock video synced to wall clock → fb0")
    p.add_argument("--video", type=Path, default=DEFAULT_VIDEO)
    p.add_argument("--fb", default="/dev/fb0")
    p.add_argument("--tz", default=DEFAULT_TZ)
    p.add_argument("--resync-every", type=int, default=DEFAULT_RESYNC_S)
    p.add_argument("--no-hw", action="store_true")
    p.add_argument("--crop-top", type=int, default=0)
    p.add_argument("--crop-bottom", type=int, default=0)
    p.add_argument("--crop-left", type=int, default=0)
    p.add_argument("--crop-right", type=int, default=0)
    args = p.parse_args()

    if not os.access(args.fb, os.W_OK):
        raise SystemExit(f"cannot write {args.fb} (user in group video?)")

    stop = False

    def _stop(signum: int, _frame: object) -> None:
        nonlocal stop
        stop = True

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    ff = ffmpeg_bin()
    wait_for_video(args.video, lambda: stop)
    if stop:
        return 0

    dst_w, dst_h = fb_size()
    src = probe_size(ff, args.video)
    crop = (args.crop_top, args.crop_bottom, args.crop_left, args.crop_right)
    vf = build_vf(src, dst_w, dst_h, *crop)
    src_s = f"{src[0]}x{src[1]}" if src else "?"
    print(
        f"fb_clock: video={args.video} ({src_s}) fb={args.fb} {dst_w}x{dst_h} "
        f"crop=T{args.crop_top},B{args.crop_bottom},L{args.crop_left},R{args.crop_right} "
        f"tz={args.tz} resync={args.resync_every}s hw={not args.no_hw} rotate=180",
        flush=True,
    )

    while not stop:
        if not args.video.is_file():
            wait_for_video(args.video, lambda: stop)
            if stop:
                break
            src = probe_size(ff, args.video)
            vf = build_vf(src, dst_w, dst_h, *crop)

        seek = seconds_since_midnight(args.tz)
        cmd = build_cmd(ff, args.video, args.fb, seek, vf, hw=not args.no_hw)
        print(
            f"fb_clock: start seek={format_ts(seek)} "
            f"(wall={datetime.now(ZoneInfo(args.tz)).isoformat(timespec='seconds')})",
            flush=True,
        )

        proc = subprocess.Popen(cmd)
        deadline = time.monotonic() + max(30, args.resync_every)
        while not stop and proc.poll() is None:
            if time.monotonic() >= deadline:
                print("fb_clock: periodic resync", flush=True)
                proc.terminate()
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=2)
                break
            time.sleep(0.25)
        else:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=2)
            elif not stop:
                print(f"fb_clock: ffmpeg exit rc={proc.returncode} — restart", flush=True)
                time.sleep(0.5)

    print("fb_clock: stopped", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
