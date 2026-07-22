#!/usr/bin/env python3
"""Generate a seekable 24h clock MP4 for fb_clock_play.py (optional).

Default: 860×360, 1 fps, H.264, 86400 s, keyframe every frame (-g 1).
Content at t shows HH:MM:SS for that second after midnight.

Full encode takes a while; use --seconds for a smoke clip first.
Prefer fb_clock_live.py on AnkerPI02 unless a designed animation MP4 exists.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "media" / "clock_24h.mp4"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p.add_argument("--width", type=int, default=860)
    p.add_argument("--height", type=int, default=360)
    p.add_argument("--fps", type=int, default=1, help="1 fps is enough for a clock")
    p.add_argument("--seconds", type=int, default=86400)
    p.add_argument("--crf", type=int, default=28)
    args = p.parse_args()

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        print("ffmpeg not found", file=sys.stderr)
        return 1

    # Portable fonts: prefer Windows Consolas/Arial when present
    font_mono = r"C:\Windows\Fonts\consola.ttf"
    font_sans = r"C:\Windows\Fonts\arial.ttf"
    if Path(font_mono).is_file() and Path(font_sans).is_file():
        vf = (
            f"drawtext=fontfile={font_mono}:"
            f"fontsize=96:fontcolor=0xFFDC78:x=(w-text_w)/2:y=(h-text_h)/2-20:"
            f"text='%{{eif\\:mod(floor(t/3600)\\,24)\\:d\\:2}}\\:"
            f"%{{eif\\:mod(floor(t/60)\\,60)\\:d\\:2}}\\:"
            f"%{{eif\\:mod(floor(t)\\,60)\\:d\\:2}}',"
            f"drawtext=fontfile={font_sans}:"
            f"fontsize=28:fontcolor=0xC8AA5A:x=(w-text_w)/2:y=40:text='HOTEL ANKER'"
        )
    else:
        vf = (
            "drawtext=fontsize=96:fontcolor=0xFFDC78:x=(w-text_w)/2:y=(h-text_h)/2-20:"
            "text='%{eif\\:mod(floor(t/3600)\\,24)\\:d\\:2}\\:"
            "%{eif\\:mod(floor(t/60)\\,60)\\:d\\:2}\\:"
            "%{eif\\:mod(floor(t)\\,60)\\:d\\:2}',"
            "drawtext=fontsize=28:fontcolor=0xC8AA5A:x=(w-text_w)/2:y=40:text='HOTEL ANKER'"
        )

    cmd = [
        ffmpeg,
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-stats",
        "-f",
        "lavfi",
        "-i",
        f"color=c=0x040A1C:s={args.width}x{args.height}:d={args.seconds}:r={args.fps}",
        "-vf",
        vf,
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-preset",
        "ultrafast",
        "-crf",
        str(args.crf),
        "-g",
        str(args.fps),
        "-an",
        "-movflags",
        "+faststart",
        str(args.out),
    ]
    print("running:", " ".join(cmd), flush=True)
    subprocess.check_call(cmd)
    print(f"wrote {args.out} ({args.out.stat().st_size} bytes)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
