#!/usr/bin/env python3
"""24h clock video → /dev/fb0, seek-synced to local wall clock.

Video must be exactly 86400 s, content starting at 00:00:00 local time.
Monitor is mounted 180° — frames are flipped in the ffmpeg filter graph
(no KMS rotate= flag).

Optional --crop-* args apply before scale (Premiere-style margins in source pixels).

Playback aims for smooth continuous output:
- Flip 180° at source resolution (cheap), then integer upscale to fb.
- Resync only when wall-clock drift exceeds --max-drift (no periodic hard kill).
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
# Safety-only forced restart (seconds). 0 = never force; drift gate handles sync.
DEFAULT_FORCE_RESYNC_S = 0
DEFAULT_MAX_DRIFT_S = 0.35
DEFAULT_DRIFT_CHECK_S = 5.0


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
    """Filter graph: crop → flip180 @src → upscale → rgb565.

    Flip before upscale so rotate work stays at 860×360, not 3440×1440.
    """
    parts: list[str] = []
    cropped: tuple[int, int] | None = src
    if src and (crop_top or crop_bottom or crop_left or crop_right):
        cw = max(1, src[0] - crop_left - crop_right)
        ch = max(1, src[1] - crop_top - crop_bottom)
        parts.append(f"crop={cw}:{ch}:{crop_left}:{crop_top}")
        cropped = (cw, ch)

    # 180° mount: hflip+vflip is far cheaper than rotate=PI
    parts.append("hflip,vflip")

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


def signed_drift(wall_s: float, video_s: float) -> float:
    """Smallest signed difference wall − video on a 24h circle (seconds)."""
    return (wall_s - video_s + DAY_S / 2.0) % DAY_S - DAY_S / 2.0


def wait_for_video(path: Path, should_stop) -> None:
    while not should_stop() and not path.is_file():
        print(f"fb_clock: waiting for video file {path}", flush=True)
        time.sleep(5)


def stop_proc(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=2)


def build_cmd(
    ffmpeg: str,
    video: Path,
    fb: str,
    seek_s: float,
    vf: str,
    hw: bool,
) -> list[str]:
    # Low probe/analyze → faster restart after drift resync.
    cmd = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-nostdin",
        "-probesize",
        "32768",
        "-analyzeduration",
        "0",
        "-fflags",
        "+fastseek+genpts",
    ]
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
    p.add_argument(
        "--resync-every",
        type=int,
        default=DEFAULT_FORCE_RESYNC_S,
        help="Force ffmpeg restart after N seconds (0=never; drift gate is primary)",
    )
    p.add_argument(
        "--max-drift",
        type=float,
        default=DEFAULT_MAX_DRIFT_S,
        help="Restart only when |wall − video| exceeds this many seconds",
    )
    p.add_argument(
        "--drift-check",
        type=float,
        default=DEFAULT_DRIFT_CHECK_S,
        help="How often to compare wall clock vs expected video position",
    )
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
    use_hw = not args.no_hw
    hw_fail_streak = 0
    print(
        f"fb_clock: video={args.video} ({src_s}) fb={args.fb} {dst_w}x{dst_h} "
        f"crop=T{args.crop_top},B{args.crop_bottom},L{args.crop_left},R{args.crop_right} "
        f"tz={args.tz} max_drift={args.max_drift}s drift_check={args.drift_check}s "
        f"force_resync={args.resync_every}s hw={use_hw} flip=hflip+vflip",
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
        cmd = build_cmd(ff, args.video, args.fb, seek, vf, hw=use_hw)
        t0_mono = time.monotonic()
        print(
            f"fb_clock: start seek={format_ts(seek)} hw={use_hw} "
            f"(wall={datetime.now(ZoneInfo(args.tz)).isoformat(timespec='seconds')})",
            flush=True,
        )

        proc = subprocess.Popen(cmd)
        force_deadline = (
            t0_mono + max(30, args.resync_every) if args.resync_every > 0 else None
        )
        next_drift_check = t0_mono + max(1.0, args.drift_check)
        exited_early = False

        while not stop and proc.poll() is None:
            now = time.monotonic()
            if force_deadline is not None and now >= force_deadline:
                print("fb_clock: forced resync (resync-every)", flush=True)
                stop_proc(proc)
                exited_early = True
                break

            if now >= next_drift_check:
                elapsed = now - t0_mono
                video_pos = (seek + elapsed) % DAY_S
                wall_pos = seconds_since_midnight(args.tz)
                drift = signed_drift(wall_pos, video_pos)
                if abs(drift) > args.max_drift:
                    print(
                        f"fb_clock: drift={drift:+.3f}s > {args.max_drift}s — resync",
                        flush=True,
                    )
                    stop_proc(proc)
                    exited_early = True
                    break
                next_drift_check = now + max(1.0, args.drift_check)

            time.sleep(0.25)
        else:
            if proc.poll() is None:
                stop_proc(proc)
            elif not stop:
                rc = proc.returncode
                print(f"fb_clock: ffmpeg exit rc={rc} — restart", flush=True)
                if use_hw and rc not in (0, -15, -9):  # not clean/SIGTERM/SIGKILL
                    hw_fail_streak += 1
                    if hw_fail_streak >= 2:
                        print(
                            "fb_clock: HW decode failing — falling back to software",
                            flush=True,
                        )
                        use_hw = False
                        hw_fail_streak = 0
                else:
                    hw_fail_streak = 0
                time.sleep(0.5)
                continue

        if exited_early:
            hw_fail_streak = 0
            # Tiny pause so fbdev release completes before next open
            time.sleep(0.05)

    print("fb_clock: stopped", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
