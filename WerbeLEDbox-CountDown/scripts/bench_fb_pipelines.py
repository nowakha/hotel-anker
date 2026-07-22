#!/usr/bin/env python3
"""Bench A/B/C/D pipelines for one-frame seek → fb0 (AnkerPI02).

Does NOT assume bottleneck; prints ms per stage. Writes last frame of each
pipeline to /dev/fb0 so you can see it.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
from PIL import Image

VIDEO = Path.home() / "WerbeLEDbox-CountDown" / "media" / "st24.mov"
FB = "/dev/fb0"
TZ = "Europe/Zurich"
CROP_T, CROP_B, CROP_L, CROP_R = 386, 127, 0, 0
SMALL = (860, 360)
N_RUNS = 3


def format_ts(seconds: float) -> str:
    s = max(0.0, min(seconds, 86399.999))
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = s - h * 3600 - m * 60
    return f"{h:02d}:{m:02d}:{sec:06.3f}"


def wall_seek() -> float:
    now = datetime.now(ZoneInfo(TZ))
    return (now.hour * 3600 + now.minute * 60 + now.second + now.microsecond / 1e6) % 86400


def fb_geom() -> tuple[int, int, int]:
    w, h = Path("/sys/class/graphics/fb0/virtual_size").read_text().strip().split(",")
    stride = int(Path("/sys/class/graphics/fb0/stride").read_text().strip())
    return int(w), int(h), stride


def rgb_to_rgb565(rgb: np.ndarray) -> bytes:
    r = rgb[:, :, 0].astype(np.uint16)
    g = rgb[:, :, 1].astype(np.uint16)
    b = rgb[:, :, 2].astype(np.uint16)
    pix = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    return pix.astype("<u2").tobytes()


def paint_full(raw565: bytes, w: int, h: int, stride: int) -> None:
    fd = os.open(FB, os.O_RDWR)
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


def paint_center_blit(rgb_small: np.ndarray, fb_w: int, fb_h: int, stride: int) -> None:
    """Center-blit small RGB into black full framebuffer."""
    sh, sw = rgb_small.shape[:2]
    x0 = max(0, (fb_w - sw) // 2)
    y0 = max(0, (fb_h - sh) // 2)
    canvas = np.zeros((fb_h, fb_w, 3), dtype=np.uint8)
    canvas[y0 : y0 + sh, x0 : x0 + sw] = rgb_small
    paint_full(rgb_to_rgb565(canvas), fb_w, fb_h, stride)


def run_ffmpeg(cmd: list[str], timeout_s: float = 90.0) -> tuple[float, bytes]:
    t0 = time.monotonic()
    proc = subprocess.run(cmd, capture_output=True, timeout=timeout_s, check=False)
    ms = (time.monotonic() - t0) * 1000
    if proc.returncode != 0:
        err = (proc.stderr or b"").decode("utf-8", "replace")[:300]
        raise RuntimeError(f"ffmpeg rc={proc.returncode}: {err}")
    return ms, proc.stdout


def extract_png(seek: str, out: Path, vf: str | None = None, hw: list[str] | None = None) -> float:
    ffmpeg = shutil.which("ffmpeg")
    cmd = [
        ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin",
        "-threads", "1",
    ]
    if hw:
        cmd += hw
    cmd += ["-ss", seek, "-i", str(VIDEO)]
    if vf:
        cmd += ["-vf", vf]
    cmd += ["-frames:v", "1", "-y", str(out)]
    t0 = time.monotonic()
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=90, check=False)
    ms = (time.monotonic() - t0) * 1000
    if proc.returncode != 0 or not out.is_file() or out.stat().st_size < 100:
        raise RuntimeError(f"extract failed: {(proc.stderr or '')[:300]}")
    return ms


def extract_raw_rgb(seek: str, w: int, h: int, vf: str, hw: list[str] | None = None) -> tuple[float, np.ndarray]:
    ffmpeg = shutil.which("ffmpeg")
    cmd = [
        ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin",
        "-threads", "1",
    ]
    if hw:
        cmd += hw
    cmd += [
        "-ss", seek, "-i", str(VIDEO),
        "-vf", vf,
        "-frames:v", "1",
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "pipe:1",
    ]
    ms, raw = run_ffmpeg(cmd)
    expect = w * h * 3
    if len(raw) != expect:
        raise RuntimeError(f"raw size {len(raw)} != {expect}")
    arr = np.frombuffer(raw, dtype=np.uint8).reshape((h, w, 3))
    return ms, arr


def stage_times(label: str, times: dict[str, float]) -> None:
    total = sum(times.values())
    parts = " ".join(f"{k}={v:.0f}" for k, v in times.items())
    print(f"{label}: {parts} TOTAL={total:.0f}ms ({1000/total:.2f} fps)", flush=True)


def mean_dict(runs: list[dict[str, float]]) -> dict[str, float]:
    keys = runs[0].keys()
    return {k: sum(r[k] for r in runs) / len(runs) for k in keys}


def main() -> int:
    if not VIDEO.is_file():
        raise SystemExit(f"missing {VIDEO}")
    fb_w, fb_h, stride = fb_geom()
    src_w, src_h = 3840, 2160
    crop_w = src_w - CROP_L - CROP_R
    crop_h = src_h - CROP_T - CROP_B
    # ffmpeg crop=w:h:x:y
    crop_vf = f"crop={crop_w}:{crop_h}:{CROP_L}:{CROP_T}"
    tmp = Path(tempfile.gettempdir())
    print(
        f"bench: video={VIDEO} fb={fb_w}x{fb_h} crop={crop_vf} "
        f"throttled_before={subprocess.check_output(['vcgencmd','get_throttled'], text=True).strip()}",
        flush=True,
    )

    # Probe OpenCV availability (expected broken on this Pi)
    try:
        import cv2  # noqa: F401
        cv2_ok = True
    except Exception as exc:  # noqa: BLE001
        cv2_ok = False
        print(f"opencv: UNAVAILABLE ({exc!r}) — B uses PIL resize as stand-in", flush=True)

    results: dict[str, list[dict[str, float]]] = {}

    for run in range(N_RUNS):
        seek = format_ts(wall_seek())
        print(f"\n=== run {run+1}/{N_RUNS} seek={seek} ===", flush=True)

        # A) current: full extract PNG → PIL crop/scale 3440 → rotate → rgb565 → fb
        out = tmp / "bench_A.png"
        t = {}
        t["extract"] = extract_png(seek, out)
        t0 = time.monotonic()
        img = Image.open(out).convert("RGB")
        box = (CROP_L, CROP_T, src_w - CROP_R, src_h - CROP_B)
        cropped = img.crop(box)
        scaled = cropped.resize((fb_w, fb_h), Image.Resampling.BILINEAR)
        rotated = scaled.rotate(180)
        rgb = np.asarray(rotated, dtype=np.uint8)
        t["crop_resize"] = (time.monotonic() - t0) * 1000
        t0 = time.monotonic()
        raw = rgb_to_rgb565(rgb)
        t["rgb565"] = (time.monotonic() - t0) * 1000
        t0 = time.monotonic()
        paint_full(raw, fb_w, fb_h, stride)
        t["fb"] = (time.monotonic() - t0) * 1000
        stage_times("A_full_pil", t)
        results.setdefault("A_full_pil", []).append(t)

        # B1) extract full → crop → resize 860 → center blit (full black canvas)
        out = tmp / "bench_B.png"
        t = {}
        t["extract"] = extract_png(seek, out)
        t0 = time.monotonic()
        img = Image.open(out).convert("RGB")
        cropped = img.crop(box)
        small = cropped.resize(SMALL, Image.Resampling.BILINEAR).rotate(180)
        rgb_s = np.asarray(small, dtype=np.uint8)
        t["crop_resize"] = (time.monotonic() - t0) * 1000
        t0 = time.monotonic()
        # include canvas compose in rgb565 stage for fair wall time
        canvas = np.zeros((fb_h, fb_w, 3), dtype=np.uint8)
        x0 = (fb_w - SMALL[0]) // 2
        y0 = (fb_h - SMALL[1]) // 2
        canvas[y0 : y0 + SMALL[1], x0 : x0 + SMALL[0]] = rgb_s
        raw = rgb_to_rgb565(canvas)
        t["rgb565"] = (time.monotonic() - t0) * 1000
        t0 = time.monotonic()
        paint_full(raw, fb_w, fb_h, stride)
        t["fb"] = (time.monotonic() - t0) * 1000
        stage_times("B1_860_center", t)
        results.setdefault("B1_860_center", []).append(t)

        # B2) extract full → 860 → NN upsample 3440 → fb
        out = tmp / "bench_B2.png"
        t = {}
        t["extract"] = extract_png(seek, out)
        t0 = time.monotonic()
        img = Image.open(out).convert("RGB")
        cropped = img.crop(box)
        small = cropped.resize(SMALL, Image.Resampling.NEAREST)
        up = small.resize((fb_w, fb_h), Image.Resampling.NEAREST).rotate(180)
        rgb = np.asarray(up, dtype=np.uint8)
        t["crop_resize"] = (time.monotonic() - t0) * 1000
        t0 = time.monotonic()
        raw = rgb_to_rgb565(rgb)
        t["rgb565"] = (time.monotonic() - t0) * 1000
        t0 = time.monotonic()
        paint_full(raw, fb_w, fb_h, stride)
        t["fb"] = (time.monotonic() - t0) * 1000
        stage_times("B2_860_nn_up", t)
        results.setdefault("B2_860_nn_up", []).append(t)

        # C1) ffmpeg vf crop+scale 3440 + hflip/vflip, raw pipe
        vf = f"{crop_vf},scale={fb_w}:{fb_h}:flags=bilinear,hflip,vflip"
        t = {}
        try:
            t["extract"], rgb = extract_raw_rgb(seek, fb_w, fb_h, vf)
            t["crop_resize"] = 0.0  # inside ffmpeg
            t0 = time.monotonic()
            raw = rgb_to_rgb565(rgb)
            t["rgb565"] = (time.monotonic() - t0) * 1000
            t0 = time.monotonic()
            paint_full(raw, fb_w, fb_h, stride)
            t["fb"] = (time.monotonic() - t0) * 1000
            stage_times("C1_vf_3440_raw", t)
            results.setdefault("C1_vf_3440_raw", []).append(t)
        except Exception as exc:  # noqa: BLE001
            print(f"C1_vf_3440_raw FAIL: {exc!r}", flush=True)

        # C2) ffmpeg vf crop+scale 860 + flip, raw; then NN upsample host
        vf = f"{crop_vf},scale={SMALL[0]}:{SMALL[1]}:flags=fast_bilinear,hflip,vflip"
        t = {}
        try:
            t["extract"], rgb_s = extract_raw_rgb(seek, SMALL[0], SMALL[1], vf)
            t0 = time.monotonic()
            up = Image.fromarray(rgb_s).resize((fb_w, fb_h), Image.Resampling.NEAREST)
            rgb = np.asarray(up, dtype=np.uint8)
            t["crop_resize"] = (time.monotonic() - t0) * 1000
            t0 = time.monotonic()
            raw = rgb_to_rgb565(rgb)
            t["rgb565"] = (time.monotonic() - t0) * 1000
            t0 = time.monotonic()
            paint_full(raw, fb_w, fb_h, stride)
            t["fb"] = (time.monotonic() - t0) * 1000
            stage_times("C2_vf_860_nn_up", t)
            results.setdefault("C2_vf_860_nn_up", []).append(t)
        except Exception as exc:  # noqa: BLE001
            print(f"C2_vf_860_nn_up FAIL: {exc!r}", flush=True)

        # C3) ffmpeg vf → 860 raw + center blit (tiny picture)
        t = {}
        try:
            t["extract"], rgb_s = extract_raw_rgb(
                seek, SMALL[0], SMALL[1],
                f"{crop_vf},scale={SMALL[0]}:{SMALL[1]}:flags=fast_bilinear,hflip,vflip",
            )
            t0 = time.monotonic()
            canvas = np.zeros((fb_h, fb_w, 3), dtype=np.uint8)
            x0 = (fb_w - SMALL[0]) // 2
            y0 = (fb_h - SMALL[1]) // 2
            canvas[y0 : y0 + SMALL[1], x0 : x0 + SMALL[0]] = rgb_s
            t["crop_resize"] = (time.monotonic() - t0) * 1000
            t0 = time.monotonic()
            raw = rgb_to_rgb565(canvas)
            t["rgb565"] = (time.monotonic() - t0) * 1000
            t0 = time.monotonic()
            paint_full(raw, fb_w, fb_h, stride)
            t["fb"] = (time.monotonic() - t0) * 1000
            stage_times("C3_vf_860_center", t)
            results.setdefault("C3_vf_860_center", []).append(t)
        except Exception as exc:  # noqa: BLE001
            print(f"C3_vf_860_center FAIL: {exc!r}", flush=True)

        # D) try v4l2m2m / drm hwaccel with C2-sized output
        for name, hw in (
            ("D_v4l2m2m", ["-c:v", "h264_v4l2m2m"]),
            ("D_hwaccel_drm", ["-hwaccel", "drm"]),
        ):
            t = {}
            try:
                t["extract"], rgb_s = extract_raw_rgb(
                    seek, SMALL[0], SMALL[1],
                    f"{crop_vf},scale={SMALL[0]}:{SMALL[1]}:flags=fast_bilinear,hflip,vflip",
                    hw=hw,
                )
                t0 = time.monotonic()
                up = Image.fromarray(rgb_s).resize((fb_w, fb_h), Image.Resampling.NEAREST)
                rgb = np.asarray(up, dtype=np.uint8)
                t["crop_resize"] = (time.monotonic() - t0) * 1000
                t0 = time.monotonic()
                raw = rgb_to_rgb565(rgb)
                t["rgb565"] = (time.monotonic() - t0) * 1000
                t0 = time.monotonic()
                paint_full(raw, fb_w, fb_h, stride)
                t["fb"] = (time.monotonic() - t0) * 1000
                stage_times(name, t)
                results.setdefault(name, []).append(t)
            except Exception as exc:  # noqa: BLE001
                print(f"{name} FAIL: {exc!r}", flush=True)

        th = subprocess.check_output(["vcgencmd", "get_throttled"], text=True).strip()
        print(f"throttled_after_run={th}", flush=True)

    print("\n=== MEANS ===", flush=True)
    ranking = []
    for name, runs in results.items():
        m = mean_dict(runs)
        total = sum(m.values())
        stage_times(f"MEAN_{name}", m)
        ranking.append((total, name, m))
    ranking.sort()
    print("\n=== WINNER (lowest total) ===", flush=True)
    for total, name, m in ranking:
        print(f"  {name}: {total:.0f}ms → {1000/total:.3f} fps", flush=True)
    print(f"opencv_available={cv2_ok}", flush=True)
    print(
        f"throttled_final={subprocess.check_output(['vcgencmd','get_throttled'], text=True).strip()}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
