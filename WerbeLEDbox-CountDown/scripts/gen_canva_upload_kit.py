#!/usr/bin/env python3
"""Export tight (content-cropped) transparent layers for Canva."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
PROJ = ROOT / "WerbeLEDbox-CountDown"
OUT = ROOT / "assets" / "kendu-flowbox-2m-print" / "canva-upload"
OVERLAY_SRC = ROOT / "assets" / "kendu-flowbox-2m-print" / "canva-layers"

if str(PROJ) not in sys.path:
    sys.path.insert(0, str(PROJ))

sys.path.insert(0, str(PROJ / "scripts"))
import gen_flowbox_print_hires as P  # noqa: E402
from layout_countdown_view import (  # noqa: E402
    DH,
    DW,
    HMS_BAR_Y,
    LABEL_H,
    LOGO_H,
    LOGO_Y0,
    ST,
    TAGE_BAR_Y,
    TITLE_BAR_Y,
    TITLE_H,
    TITLE_LINES,
    layout_origins_cells,
)

PAD = 32  # px around alpha bbox — keep rightmost gold outline inside crop


def alpha_bbox(im: Image.Image, pad: int = PAD) -> tuple[int, int, int, int] | None:
    """Return (left, top, right, bottom) inclusive of non-zero alpha, plus pad."""
    a = np.asarray(im.split()[-1])
    ys, xs = np.where(a > 0)
    if len(xs) == 0:
        return None
    l, t, r, b = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
    l = max(0, l - pad)
    t = max(0, t - pad)
    r = min(im.width, r + pad)
    b = min(im.height, b + pad)
    return l, t, r, b


def crop_tight(im: Image.Image, pad: int = PAD) -> tuple[Image.Image, dict]:
    bb = alpha_bbox(im, pad=pad)
    if bb is None:
        empty = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
        return empty, {"left": 0, "top": 0, "width": 1, "height": 1}
    l, t, r, b = bb
    cropped = im.crop((l, t, r, b))
    return cropped, {"left": l, "top": t, "width": r - l, "height": b - t}


def save_layer(full: Image.Image, name: str, manifest: list[dict], *, full_canvas: bool = False) -> None:
    """Save only the upload PNG (no @preview siblings — avoids wrong uploads)."""
    if full_canvas:
        full.save(OUT / name)
        entry = {
            "file": name,
            "left": 0,
            "top": 0,
            "width": full.width,
            "height": full.height,
            "full_canvas": True,
        }
    else:
        cropped, pos = crop_tight(full)
        cropped.save(OUT / name)
        entry = {"file": name, "full_canvas": False, **pos}
    manifest.append(entry)
    print(f"  {name}  {entry['width']}×{entry['height']} @ ({entry['left']},{entry['top']})")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for p in OUT.glob("*"):
        if p.is_file():
            p.unlink()

    SIZE = P.SIZE
    CELL = P.CELL
    manifest: list[dict] = []

    # 01 facade — full canvas background
    facade = P.load_blueprint().convert("RGBA")
    save_layer(facade, "01-facade-blueprint.png", manifest, full_canvas=True)

    # 02 logo alone — Canva scale/placement (tall, centered, may clip top)
    logo_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    anchor = P.extract_anchor_mark()
    ah = int(round(783.1648448692365))
    aspect = anchor.width / max(1, anchor.height)
    aw = int(round(ah * aspect))
    max_w = int(SIZE * 0.20)
    if aw > max_w:
        aw, ah = max_w, int(max_w / aspect)
    anchor = anchor.resize((aw, ah), Image.Resampling.LANCZOS)
    ax = (SIZE - aw) // 2
    ay = int(round(-40.0))
    # paste with clip at canvas top
    logo_layer.paste(anchor, (ax, ay), anchor)
    save_layer(logo_layer, "02-logo-anker.png", manifest)

    # 03–05 liquid glass bars (full width strip, tight height)
    for name, y_cell, h in (
        ("03-bar-title-liquid-glass.png", TITLE_BAR_Y, TITLE_H),
        ("04-bar-tage-liquid-glass.png", TAGE_BAR_Y, LABEL_H),
        ("05-bar-hms-liquid-glass.png", HMS_BAR_Y, LABEL_H),
    ):
        bar = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        y0, y1 = P.cell_to_px(y_cell), P.cell_to_px(y_cell + h)
        tmp = Image.new("RGB", (SIZE, SIZE), (0, 0, 0))
        # paint with facade under for glass refraction look
        tmp.paste(facade.convert("RGB"), (0, 0))
        P.paint_liquid_glass_bar(tmp, y0, y1, phase=0.5)
        arr = np.asarray(tmp)
        a = np.zeros((SIZE, SIZE), dtype=np.uint8)
        a[y0:y1, :] = 255
        rgba = np.dstack([arr, a])
        rgba[:y0, :, 3] = 0
        rgba[y1:, :, 3] = 0
        save_layer(Image.fromarray(rgba, "RGBA"), name, manifest)

    # 06 title text (3 lines)
    title = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    td = ImageDraw.Draw(title)
    cx = SIZE // 2
    ty0, ty1 = P.cell_to_px(TITLE_BAR_Y), P.cell_to_px(TITLE_BAR_Y + TITLE_H)
    font_title = P.find_font(max(96, int(CELL * 2.85)), bold=True)
    font_sub = P.find_sans(max(52, int(CELL * 1.55)), bold=True)
    font_bis = P.find_sans(max(64, int(CELL * 1.90)), bold=True)
    fonts = (font_title, font_sub, font_bis)
    fills = ((250, 248, 244, 255), (250, 248, 244, 255), (0, 0, 0, 255))
    heights = []
    for line, fnt in zip(TITLE_LINES, fonts):
        bb = td.textbbox((0, 0), line, font=fnt)
        heights.append(bb[3] - bb[1])
    gap = max(6, CELL // 8)
    block = sum(heights) + gap * (len(TITLE_LINES) - 1)
    mid = (ty0 + ty1) // 2
    y_cursor = mid - block // 2
    for line, fnt, fill, hh in zip(TITLE_LINES, fonts, fills, heights):
        P.text_centered(td, line, cx, y_cursor + hh // 2, fnt, fill)
        y_cursor += hh + gap
    save_layer(title, "06-title-text-3lines.png", manifest)

    # 07 ghost digits (7×13) — day / time as separate tight layers
    days, day_y, time_digits, time_y, colons = layout_origins_cells()
    dig_days = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dig_days)
    for ox in days:
        P.paint_digit(dd, ox, day_y, None, ghost=True, lit=False, overlay=dig_days)
    save_layer(dig_days, "07a-digits-days-888.png", manifest)

    dig_time = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    dt = ImageDraw.Draw(dig_time)
    for ox in time_digits:
        P.paint_digit(dt, ox, time_y, None, ghost=True, lit=False, overlay=dig_time)
    for cox, coy in colons:
        P.paint_colon(dt, cox, coy, lit=False, overlay=dig_time)
    save_layer(dig_time, "07b-digits-hms-888.png", manifest)

    # 08 labels — separate layers so crops stay tight
    font_label = P.find_sans(max(64, int(CELL * 1.7)), bold=True)
    shadow = (12, 16, 28, 160)
    tage_lab = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    td_lab = ImageDraw.Draw(tage_lab)
    y0, y1 = P.cell_to_px(TAGE_BAR_Y), P.cell_to_px(TAGE_BAR_Y + LABEL_H)
    # Canva: Tage label centered under day digits (shifted right with DAY_X_SHIFT)
    day_mid_px = (P.cell_to_px(days[0]) + P.cell_to_px(days[-1] + DW)) // 2
    P.text_centered(
        td_lab, "Tage", day_mid_px, (y0 + y1) // 2, font_label, (250, 248, 244, 255), shadow=shadow
    )
    save_layer(tage_lab, "08a-label-tage.png", manifest)

    hms_lab = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hms_lab)
    y0, y1 = P.cell_to_px(HMS_BAR_Y), P.cell_to_px(HMS_BAR_Y + LABEL_H)
    mid_y = (y0 + y1) // 2
    for x_a, x_b, name in (
        (time_digits[0], time_digits[1] + DW, "Stunden"),
        (time_digits[2], time_digits[3] + DW, "Minuten"),
        (time_digits[4], time_digits[5] + DW, "Sekunden"),
    ):
        midx = (P.cell_to_px(x_a) + P.cell_to_px(x_b)) // 2
        P.text_centered(hd, name, midx, mid_y, font_label, (250, 248, 244, 255), shadow=shadow)
    save_layer(hms_lab, "08b-labels-hms.png", manifest)

    # 09 solid totzone strip only
    dead = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    dd2 = ImageDraw.Draw(dead)
    dd2.rectangle([0, P.ACTIVE_PX, SIZE - 1, SIZE - 1], fill=(0, 0, 0, 255))
    save_layer(dead, "09-totzone-8of64-solid.png", manifest)

    # 10 reference composite (full canvas guide — keep for alignment)
    ghost = P.compose(lit=False).convert("RGBA")
    save_layer(ghost, "10-reference-ghost-composite.png", manifest, full_canvas=True)

    (OUT / "layers_manifest.json").write_text(
        json.dumps(
            {
                "canvas": {"width": SIZE, "height": SIZE},
                "digit_cells": {"DW": DW, "DH": DH, "ST": ST},
                "stack_bottom_to_top": [m["file"] for m in manifest],
                "layers": manifest,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    overlay_dst = OUT / "overlays-kendu"
    if overlay_dst.exists():
        shutil.rmtree(overlay_dst)
    if OVERLAY_SRC.exists():
        shutil.copytree(OVERLAY_SRC, overlay_dst)

    from layout_countdown_view import COLON_W

    (OUT / "README_UPLOAD.md").write_text(
        f"""# Canva Upload-Kit (tight crops) — Hotel Anker Flowbox 2×2 m

**Neu generiert — bitte alten Canva-Ordner löschen und diesen Ordner komplett neu hochladen.**

Canvas: **{SIZE}×{SIZE} px**. Layer PNGs are **cropped to content** (no `@preview` clutter).
Positions: `layers_manifest.json` (`left`/`top`/`width`/`height`).

Digits: **{DW}×{DH}** cells · `COLON_W={COLON_W}` · time-row side margins clear · crop pad **{PAD}px**.

## Stack (bottom → top)
1. 01-facade-blueprint.png — full canvas
2. 03/04/05 bars — full-width strips
3. 02-logo-anker.png
4. 06-title-text-3lines.png
5. 07a-digits-days-888.png · 07b-digits-hms-888.png
6. 08a-label-tage.png · 08b-labels-hms.png
7. 09-totzone-8of64-solid.png — bottom strip
8. 10-reference (optional guide)

Place each layer at the `left`/`top` from the manifest; do not stretch to full canvas.
""",
        encoding="utf-8",
    )
    print("wrote", OUT)


if __name__ == "__main__":
    main()
