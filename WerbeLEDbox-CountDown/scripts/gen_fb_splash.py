#!/usr/bin/env python3
"""Build Hotel Anker boot splash for 3440x1440 fb (logo height = 4/5 screen)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
LOGO_CANDIDATES = [
    REPO / "assets" / "hotel-anker-historic-anchor.png",
    ROOT / "assets" / "hotel-anker-historic-anchor.png",
]
OUT_DIR = ROOT / "media"
W, H = 3440, 1440
LOGO_H_FRAC = 4 / 5


def main() -> None:
    logo_path = next((p for p in LOGO_CANDIDATES if p.is_file()), None)
    if logo_path is None:
        raise SystemExit(f"logo not found in {LOGO_CANDIDATES}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    logo_h = int(H * LOGO_H_FRAC)

    logo = Image.open(logo_path).convert("RGBA")
    bbox = logo.split()[-1].getbbox()
    if bbox:
        logo = logo.crop(bbox)
    lw, lh = logo.size
    new_w = max(1, int(round(lw * (logo_h / lh))))
    logo = logo.resize((new_w, logo_h), Image.Resampling.LANCZOS)

    canvas = Image.new("RGB", (W, H), (0, 0, 0))
    x = (W - new_w) // 2
    y = (H - logo_h) // 2
    canvas.paste(logo.convert("RGB"), (x, y), logo)
    # Monitor is mounted 180°; no DRM rotate (KMS-safe) — bake orientation in.
    canvas = canvas.rotate(180)

    png_path = OUT_DIR / "boot_splash_3440x1440.png"
    canvas.save(png_path, optimize=True)

    rgb = canvas.tobytes()
    out = bytearray(W * H * 2)
    ri = 0
    oi = 0
    for _ in range(W * H):
        r = rgb[ri]
        g = rgb[ri + 1]
        b = rgb[ri + 2]
        ri += 3
        v = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
        out[oi] = v & 0xFF
        out[oi + 1] = (v >> 8) & 0xFF
        oi += 2
    raw_path = OUT_DIR / "boot_splash_3440x1440.rgb565"
    raw_path.write_bytes(out)

    print(f"logo_src={logo_path}")
    print(f"png={png_path} size={canvas.size} logo={new_w}x{logo_h} at=({x},{y})")
    print(f"raw={raw_path} bytes={len(out)}")


if __name__ == "__main__":
    main()
